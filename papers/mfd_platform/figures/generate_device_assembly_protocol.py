#!/usr/bin/env python3

from __future__ import annotations

import math
import json
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch
from PIL import Image

from generate_openmfd_design_figure import StlMesh, rotation_matrix, triangle_normals


ROOT = Path(__file__).resolve().parents[3]
FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig4_mold_casts_package"
OUTPUT_STEM = "assembly_protocol_schematic"
DPI = 720
MIN_CAMERA_MARGIN = 1.18
CAMERA_EDGE_GUARD_PX = 24
MAX_CAMERA_FIT_PASSES = 6

DESIGN_DIR = ROOT / "designs" / "open_chamber" / "2_compartment_96_well_300um_suex200_v27"
DESIGN_STEM = "2_compartment_96_well_300um_suex200_v27"
ARRAY_INSERT_STL = DESIGN_DIR / f"{DESIGN_STEM}_wells_insert.stl"
SINGLE_BOTTOM_DXF = DESIGN_DIR / f"{DESIGN_STEM}_single_bottom.dxf"
SINGLE_TOP_DXF = DESIGN_DIR / f"{DESIGN_STEM}_single_top.dxf"
TOP_DXF = DESIGN_DIR / f"{DESIGN_STEM}_top.dxf"
WAFER_DXF = DESIGN_DIR / "wafer.dxf"
FRAME_STL = ROOT / "plates" / "96_well_plate_reservoirs_print_hips_2" / "96_well_plate_reservoirs_print_hips_2.stl"
RACK_STEP = ROOT / "orders" / "wafer_rack_send_cut_send_dec_9_2024" / "Wafer Rack 2 v5.step"
BLENDER_RENDERER = FIGURE_DIR / "blender_render_mesh_parts.py"
BLENDER_BOOLEAN = FIGURE_DIR / "blender_boolean_mesh.py"
SINGLE_DEVICE_NEGATIVE_STL = FIGURE_DIR / "generated_assets/single_device_pdms_negative.stl"
# Current v27 mask and insert outputs are generated from the same compensated
# coordinate system and use the same wafer center.
GENERATED_WAFER_ORIGIN = np.array([55.2204, 36.8136])
# The top DXF contains four nested handling perimeters.  Complementing it
# within this bound retains the two narrow SUEX guide strips while excluding
# the broad outer handling field.
TOP_LAYER_COMPLEMENT_SIZE = (112.4856, 75.6724)

COLORS = {
    "ink": "#20242b",
    "muted": "#606a76",
    "accent": "#1669a8",
    "wafer": "#626b73",
    "insert": "#b64d4f",
    "pdms": "#8eb6d9",
    "frame": "#252b31",
    "adhesive": "#d8aa37",
    "blade": "#69717a",
    "tape": "#3d8fc4",
    "foil": "#aeb5ba",
    "paper": "#ffffff",
}


class Step(ABC):
    """One protocol step owns its scene, view and process annotations."""

    azimuth = -38.0
    elevation = -32.0
    z_scale = 1.7
    annotation_size = 8.5

    @property
    @abstractmethod
    def title(self) -> str: ...

    @property
    @abstractmethod
    def detail(self) -> str: ...

    @abstractmethod
    def scene_parts(self) -> tuple[MeshPart, ...]: ...

    def draw_marks(self, ax: plt.Axes, frame: tuple[float, float, float, float]) -> None:
        pass

    def annotate(self, ax: plt.Axes, x: float, y: float, text: str, *, color: str = COLORS["accent"]) -> None:
        ax.text(x, y, text, ha="center", va="bottom", fontsize=self.annotation_size,
                fontweight="bold", color=color, zorder=6)

    def draw(self, ax: plt.Axes, frame: tuple[float, float, float, float], number: int) -> None:
        draw_scene_blender(ax, self.scene_parts(), frame, azimuth=self.azimuth,
                           elevation=self.elevation, z_scale=self.z_scale)
        self.draw_marks(ax, frame)
        x, y, width, height = frame
        title_y = y + height + 0.025
        ax.text(x, title_y, str(number), ha="left", va="bottom", fontsize=10.5,
                fontweight="bold", color=COLORS["accent"])
        ax.text(x + 0.045, title_y, self.title, ha="left", va="bottom", fontsize=10.5,
                fontweight="bold", color=COLORS["ink"])
        ax.text(x + width / 2, y - 0.018, self.detail, ha="center", va="top",
                fontsize=self.annotation_size, color=COLORS["muted"])


@dataclass(frozen=True)
class MeshPart:
    mesh: StlMesh
    base_color: str
    alpha: float = 1.0
    roughness: float = 0.48
    metallic: float = 0.0
    emission_strength: float = 0.0
    transparency_overlap: bool = True
    dissolve_coplanar: bool = False
    transmission_weight: float | None = None


def mesh_from_triangles(triangles: list[np.ndarray] | np.ndarray) -> StlMesh:
    if isinstance(triangles, list):
        arrays = [np.asarray(triangle, dtype=float) for triangle in triangles]
        arrays = [array[None, :, :] if array.ndim == 2 else array for array in arrays]
        return StlMesh(np.concatenate(arrays, axis=0))
    return StlMesh(np.asarray(triangles, dtype=float))


def transform_mesh(
    mesh: StlMesh,
    *,
    translation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
    rotation_x: float = 0.0,
    rotation_y: float = 0.0,
    rotation_z: float = 0.0,
    pivot: tuple[float, float, float] | None = None,
) -> StlMesh:
    triangles = mesh.triangles.copy()
    points = triangles.reshape((-1, 3))
    center = (
        (points.min(axis=0) + points.max(axis=0)) / 2
        if pivot is None
        else np.asarray(pivot, dtype=float)
    )
    points -= center
    points *= np.asarray(scale)
    for angle_degrees, matrix_factory in (
        (rotation_x, lambda c, s: np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])),
        (rotation_y, lambda c, s: np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])),
        (rotation_z, lambda c, s: np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])),
    ):
        if angle_degrees:
            angle = math.radians(angle_degrees)
            points[:] = points @ matrix_factory(math.cos(angle), math.sin(angle)).T
    points += np.asarray(translation)
    return StlMesh(points.reshape((-1, 3, 3)))


def box_mesh(
    width: float,
    depth: float,
    height: float,
    *,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> StlMesh:
    x0, x1 = -width / 2, width / 2
    y0, y1 = -depth / 2, depth / 2
    z0, z1 = -height / 2, height / 2
    vertices = np.array(
        [
            [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
            [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
        ],
        dtype=float,
    )
    faces = (
        (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
        (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7),
    )
    triangles = vertices[np.asarray(faces)]
    triangles += np.asarray(center)
    return StlMesh(triangles)


def cylinder_mesh(
    radius: float,
    height: float,
    *,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    segments: int = 72,
) -> StlMesh:
    z0, z1 = -height / 2, height / 2
    triangles: list[np.ndarray] = []
    for index in range(segments):
        a0 = 2 * math.pi * index / segments
        a1 = 2 * math.pi * (index + 1) / segments
        p0 = np.array([radius * math.cos(a0), radius * math.sin(a0), z0])
        p1 = np.array([radius * math.cos(a1), radius * math.sin(a1), z0])
        p2 = np.array([radius * math.cos(a1), radius * math.sin(a1), z1])
        p3 = np.array([radius * math.cos(a0), radius * math.sin(a0), z1])
        triangles.extend((np.array([p0, p1, p2]), np.array([p0, p2, p3])))
        triangles.append(np.array([[0.0, 0.0, z1], p2, p3]))
        triangles.append(np.array([[0.0, 0.0, z0], p1, p0]))
    mesh = mesh_from_triangles(triangles)
    mesh.triangles[:] += np.asarray(center)
    return mesh


def circular_ring_mesh(
    outer_radius: float,
    inner_radius: float,
    height: float,
    *,
    center: tuple[float, float, float],
    segments: int = 128,
) -> StlMesh:
    z0 = center[2] - height / 2
    z1 = center[2] + height / 2
    triangles: list[np.ndarray] = []
    for index in range(segments):
        a0 = 2 * math.pi * index / segments
        a1 = 2 * math.pi * (index + 1) / segments
        outer0 = np.array([outer_radius * math.cos(a0), outer_radius * math.sin(a0), z0])
        outer1 = np.array([outer_radius * math.cos(a1), outer_radius * math.sin(a1), z0])
        outer2 = np.array([outer_radius * math.cos(a1), outer_radius * math.sin(a1), z1])
        outer3 = np.array([outer_radius * math.cos(a0), outer_radius * math.sin(a0), z1])
        inner0 = np.array([inner_radius * math.cos(a0), inner_radius * math.sin(a0), z0])
        inner1 = np.array([inner_radius * math.cos(a1), inner_radius * math.sin(a1), z0])
        inner2 = np.array([inner_radius * math.cos(a1), inner_radius * math.sin(a1), z1])
        inner3 = np.array([inner_radius * math.cos(a0), inner_radius * math.sin(a0), z1])
        triangles.extend(
            (
                np.array([outer0, outer1, outer2]), np.array([outer0, outer2, outer3]),
                np.array([inner0, inner2, inner1]), np.array([inner0, inner3, inner2]),
                np.array([outer3, outer2, inner2]), np.array([outer3, inner2, inner3]),
                np.array([outer0, inner1, outer1]), np.array([outer0, inner0, inner1]),
            )
        )
    mesh = mesh_from_triangles(triangles)
    mesh.triangles[:, :, 0] += center[0]
    mesh.triangles[:, :, 1] += center[1]
    return mesh


def rounded_rectangle_points(width: float, depth: float, radius: float, samples: int = 4) -> np.ndarray:
    points: list[tuple[float, float]] = []
    corners = (
        (width / 2 - radius, depth / 2 - radius, 0.0),
        (-width / 2 + radius, depth / 2 - radius, 90.0),
        (-width / 2 + radius, -depth / 2 + radius, 180.0),
        (width / 2 - radius, -depth / 2 + radius, 270.0),
    )
    for cx, cy, start in corners:
        for angle in np.linspace(start, start + 90.0, samples, endpoint=False):
            radians = math.radians(angle)
            points.append((cx + radius * math.cos(radians), cy + radius * math.sin(radians)))
    return np.asarray(points)


def ring_mesh(
    outer: tuple[float, float],
    inner: tuple[float, float],
    height: float,
    *,
    center: tuple[float, float, float],
) -> StlMesh:
    outer_points = rounded_rectangle_points(outer[0], outer[1], min(outer) * 0.28)
    inner_points = rounded_rectangle_points(inner[0], inner[1], min(inner) * 0.28)
    z0 = center[2] - height / 2
    z1 = center[2] + height / 2
    triangles: list[np.ndarray] = []
    for index in range(len(outer_points)):
        nxt = (index + 1) % len(outer_points)
        o0 = np.array([*outer_points[index], z0])
        o1 = np.array([*outer_points[nxt], z0])
        o2 = np.array([*outer_points[nxt], z1])
        o3 = np.array([*outer_points[index], z1])
        i0 = np.array([*inner_points[index], z0])
        i1 = np.array([*inner_points[nxt], z0])
        i2 = np.array([*inner_points[nxt], z1])
        i3 = np.array([*inner_points[index], z1])
        triangles.extend(
            (
                np.array([o0, o1, o2]), np.array([o0, o2, o3]),
                np.array([i0, i2, i1]), np.array([i0, i3, i2]),
                np.array([o3, o2, i2]), np.array([o3, i2, i3]),
            )
        )
    mesh = mesh_from_triangles(triangles)
    mesh.triangles[:, :, 0] += center[0]
    mesh.triangles[:, :, 1] += center[1]
    return mesh


def frustum_mesh(
    bottom: tuple[float, float],
    top: tuple[float, float],
    height: float,
    *,
    center: tuple[float, float, float],
) -> StlMesh:
    bottom_points = rounded_rectangle_points(bottom[0], bottom[1], min(bottom) * 0.24)
    top_points = rounded_rectangle_points(top[0], top[1], min(top) * 0.24)
    z0 = center[2] - height / 2
    z1 = center[2] + height / 2
    triangles: list[np.ndarray] = []
    bottom_center = np.array([0.0, 0.0, z0])
    top_center = np.array([0.0, 0.0, z1])
    for index in range(len(bottom_points)):
        nxt = (index + 1) % len(bottom_points)
        b0 = np.array([*bottom_points[index], z0])
        b1 = np.array([*bottom_points[nxt], z0])
        t0 = np.array([*top_points[index], z1])
        t1 = np.array([*top_points[nxt], z1])
        triangles.extend(
            (
                np.array([b0, b1, t1]), np.array([b0, t1, t0]),
                np.array([top_center, t0, t1]), np.array([bottom_center, b1, b0]),
            )
        )
    mesh = mesh_from_triangles(triangles)
    mesh.triangles[:, :, 0] += center[0]
    mesh.triangles[:, :, 1] += center[1]
    return mesh


@lru_cache(maxsize=1)
def generated_insert_mesh() -> StlMesh:
    """Load the exact OpenMFD array insert rendered in Figure 1."""
    if not ARRAY_INSERT_STL.exists():
        raise FileNotFoundError(f"Generated OpenMFD insert not found: {ARRAY_INSERT_STL}")
    return StlMesh.from_file(ARRAY_INSERT_STL)


def centered_generated_insert(*, z_bottom: float) -> StlMesh:
    triangles = generated_insert_mesh().triangles.copy()
    points = triangles.reshape((-1, 3))
    points[:, :2] -= GENERATED_WAFER_ORIGIN
    points[:, 2] += z_bottom - points[:, 2].min()
    return StlMesh(triangles)


def exposed_insert_mesh(*, z_bottom: float, pdms_top: float) -> StlMesh:
    mesh = centered_generated_insert(z_bottom=z_bottom)
    centroids = mesh.triangles[:, :, 2].mean(axis=1)
    return StlMesh(mesh.triangles[centroids >= pdms_top - 0.12])


@lru_cache(maxsize=1)
def thick_layer_mesh() -> StlMesh:
    """Extrude the positive 200 um SUEX geometry from the negative top mask."""
    if not TOP_DXF.exists():
        raise FileNotFoundError(f"Generated OpenMFD thick-layer DXF not found: {TOP_DXF}")
    with tempfile.TemporaryDirectory(prefix="openmfd-top-dxf-") as directory:
        directory_path = Path(directory)
        scad_path = directory_path / "top_layer.scad"
        stl_path = directory_path / "top_layer.stl"
        scad_path.write_text(
            "linear_extrude(height=0.20) difference() {\n"
            f"  translate([{GENERATED_WAFER_ORIGIN[0]:.12f}, {GENERATED_WAFER_ORIGIN[1]:.12f}]) "
            f"square([{TOP_LAYER_COMPLEMENT_SIZE[0]:.12f}, "
            f"{TOP_LAYER_COMPLEMENT_SIZE[1]:.12f}], center=true);\n"
            f"  import({json.dumps(str(TOP_DXF))});\n"
            "}\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["openscad", "-o", str(stl_path), str(scad_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        triangles = StlMesh.from_file(stl_path).triangles.copy()
    triangles[:, :, :2] -= GENERATED_WAFER_ORIGIN
    return StlMesh(triangles)


def positioned_thick_layer(*, z_bottom: float) -> StlMesh:
    triangles = thick_layer_mesh().triangles.copy()
    points = triangles.reshape((-1, 3))
    points[:, 2] += z_bottom - points[:, 2].min()
    return StlMesh(triangles)


@lru_cache(maxsize=1)
def wafer_mesh() -> StlMesh:
    """Extrude the physical wafer outline used to generate the mask."""
    if not WAFER_DXF.exists():
        raise FileNotFoundError(f"Generated OpenMFD wafer DXF not found: {WAFER_DXF}")
    with tempfile.TemporaryDirectory(prefix="openmfd-wafer-dxf-") as directory:
        directory_path = Path(directory)
        scad_path = directory_path / "wafer.scad"
        stl_path = directory_path / "wafer.stl"
        scad_path.write_text(
            f"linear_extrude(height=1.4) import({json.dumps(str(WAFER_DXF))});\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["openscad", "-o", str(stl_path), str(scad_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return StlMesh.from_file(stl_path)


def positioned_wafer(*, z_center: float, radius: float = 75.0) -> StlMesh:
    """Position a mask-derived wafer while retaining its orientation flat."""
    return notched_wafer_solid(radius=radius, height=1.4, z_center=z_center)


def notched_wafer_solid(*, radius: float, height: float, z_center: float) -> StlMesh:
    """Scale the mask-derived wafer profile without losing its orientation flat."""
    mesh = wafer_mesh()
    scale_xy = radius / 75.0
    return transform_mesh(
        mesh,
        scale=(scale_xy, scale_xy, height / 1.4),
        translation=(0.0, 0.0, z_center),
        pivot=(0.0, 0.0, 0.7),
    )


@lru_cache(maxsize=8)
def notched_perimeter_ring_mesh(
    outer_radius: float,
    inner_radius: float,
    height: float,
) -> StlMesh:
    """Extrude a perimeter wall from the same notched wafer outline as the mask."""
    with tempfile.TemporaryDirectory(prefix="openmfd-notched-ring-") as directory:
        directory_path = Path(directory)
        scad_path = directory_path / "notched_ring.scad"
        stl_path = directory_path / "notched_ring.stl"
        scad_path.write_text(
            f"linear_extrude(height={height:.12f}) difference() {{\n"
            f"  scale([{outer_radius / 75.0:.12f}, {outer_radius / 75.0:.12f}]) "
            f"import({json.dumps(str(WAFER_DXF))});\n"
            f"  scale([{inner_radius / 75.0:.12f}, {inner_radius / 75.0:.12f}]) "
            f"import({json.dumps(str(WAFER_DXF))});\n"
            "}\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["openscad", "-o", str(stl_path), str(scad_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return StlMesh.from_file(stl_path)


def positioned_notched_ring(
    *,
    outer_radius: float,
    inner_radius: float,
    height: float,
    z_center: float,
) -> StlMesh:
    mesh = notched_perimeter_ring_mesh(outer_radius, inner_radius, height)
    return transform_mesh(
        mesh,
        translation=(0.0, 0.0, z_center),
        pivot=(0.0, 0.0, height / 2.0),
    )


@lru_cache(maxsize=1)
def native_channel_array_mesh() -> StlMesh:
    """Extrude only the microchannels exposed between the finished chambers."""
    missing = [path for path in (SINGLE_BOTTOM_DXF, SINGLE_TOP_DXF) if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Generated OpenMFD layer DXF not found: {missing[0]}")
    with tempfile.TemporaryDirectory(prefix="openmfd-channel-array-") as directory:
        directory_path = Path(directory)
        scad_path = directory_path / "channel_array.scad"
        stl_path = directory_path / "channel_array.stl"
        scad_path.write_text(
            "linear_extrude(height=0.24)\n"
            "  scale([1.0226, 1.0226])\n"
            "    translate([-54, -36])\n"
            "      union() {\n"
            "        for (row = [0:7], column = [0:5])\n"
            "          translate([column * 18, row * 9])\n"
            "            intersection() {\n"
            "              difference() {\n"
            f"                import({json.dumps(str(SINGLE_BOTTOM_DXF))});\n"
            # Shrinking the top mask by 10 um leaves a small cutter overlap at
            # each chamber mouth, avoiding a coincident Boolean boundary.
            "                offset(delta=-0.01)\n"
            f"                  import({json.dumps(str(SINGLE_TOP_DXF))});\n"
            "              }\n"
            # The long bottom mask also leaves two peripheral fragments after
            # subtraction. Only the central component is part of the finished
            # chamber-to-chamber microchannel span.
            "              translate([9, 4.5]) square([1, 9], center=true);\n"
            "            }\n"
            "      }\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["openscad", "-o", str(stl_path), str(scad_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return StlMesh.from_file(stl_path)


@lru_cache(maxsize=1)
def filled_well_floor_array_mesh() -> StlMesh:
    """Fill the pin holes beneath each insert so the PDMS cavity is continuous."""
    if not SINGLE_TOP_DXF.exists():
        raise FileNotFoundError(f"Generated OpenMFD top-layer DXF not found: {SINGLE_TOP_DXF}")
    with tempfile.TemporaryDirectory(prefix="openmfd-filled-well-floors-") as directory:
        directory_path = Path(directory)
        scad_path = directory_path / "filled_well_floors.scad"
        stl_path = directory_path / "filled_well_floors.stl"
        scad_path.write_text(
            "linear_extrude(height=0.62)\n"
            "  scale([1.0226, 1.0226])\n"
            "    translate([-54, -36])\n"
            "      union() {\n"
            "        for (row = [0:7], column = [0:5])\n"
            "          translate([column * 18, row * 9])\n"
            "            union() {\n"
            f"              import({json.dumps(str(SINGLE_TOP_DXF))});\n"
            # The v27 top DXF subtracts 2 mm square registration holes at
            # x=5 and x=13 mm in each 18 x 9 mm unit. Re-adding those squares
            # yields the complete chamber footprint below the seated insert.
            "              translate([5, 4.5]) square([2, 2], center=true);\n"
            "              translate([13, 4.5]) square([2, 2], center=true);\n"
            "            }\n"
            "      }\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["openscad", "-o", str(stl_path), str(scad_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return StlMesh.from_file(stl_path)


def perimeter_ring_mesh(width: float, depth: float, strip: float, height: float, *, z: float) -> StlMesh:
    parts = (
        box_mesh(width, strip, height, center=(0.0, depth / 2 - strip / 2, z)),
        box_mesh(width, strip, height, center=(0.0, -depth / 2 + strip / 2, z)),
        box_mesh(strip, depth - 2 * strip, height, center=(width / 2 - strip / 2, 0.0, z)),
        box_mesh(strip, depth - 2 * strip, height, center=(-width / 2 + strip / 2, 0.0, z)),
    )
    return mesh_from_triangles([part.triangles for part in parts])


def rectangular_shell_mesh(
    outer_width: float,
    outer_depth: float,
    inner_width: float,
    inner_depth: float,
    height: float,
    *,
    z: float,
) -> StlMesh:
    side_width = (outer_width - inner_width) / 2
    end_depth = (outer_depth - inner_depth) / 2
    parts = (
        box_mesh(outer_width, end_depth, height, center=(0.0, inner_depth / 2 + end_depth / 2, z)),
        box_mesh(outer_width, end_depth, height, center=(0.0, -inner_depth / 2 - end_depth / 2, z)),
        box_mesh(side_width, inner_depth, height, center=(inner_width / 2 + side_width / 2, 0.0, z)),
        box_mesh(side_width, inner_depth, height, center=(-inner_width / 2 - side_width / 2, 0.0, z)),
    )
    return mesh_from_triangles([part.triangles for part in parts])


def device_mesh(*, z: float = 0.0, trimmed: bool = True) -> StlMesh:
    return (
        box_mesh(108.0, 72.0, 5.0, center=(0.0, 0.0, z + 2.5))
        if trimmed
        else notched_wafer_solid(radius=76.2, height=5.0, z_center=z + 2.5)
    )


@lru_cache(maxsize=2)
def cavity_device_mesh(*, trimmed: bool = True) -> StlMesh:
    """Create the PDMS negative of the complete generated hybrid mold."""
    if not ARRAY_INSERT_STL.exists():
        raise FileNotFoundError(f"Generated OpenMFD insert not found: {ARRAY_INSERT_STL}")
    with tempfile.TemporaryDirectory(prefix="openmfd-pdms-cavities-") as directory:
        directory_path = Path(directory)
        base_path = directory_path / "pdms_slab.stl"
        inserts_path = directory_path / "well_inserts.stl"
        thick_layer_path = directory_path / "native_top_layer.stl"
        filled_floors_path = directory_path / "filled_well_floors.stl"
        channels_path = directory_path / "native_channels.stl"
        stl_path = directory_path / "pdms_complete_negative.stl"
        # Extend the exact generated inserts through the cast top. In the
        # physical process their tops remain exposed, so demolding must leave
        # complete through-openings rather than shallow residual insert caps.
        inserts = centered_generated_insert(z_bottom=-0.5).triangles.copy()
        insert_points = inserts.reshape((-1, 3))
        insert_z_min = float(insert_points[:, 2].min())
        insert_z_max = float(insert_points[:, 2].max())
        insert_points[:, 2] = (
            (insert_points[:, 2] - insert_z_min)
            * (6.0 / (insert_z_max - insert_z_min))
            - 0.5
        )
        thick_layer = thick_layer_mesh().triangles.copy()
        thick_layer[:, :, 2] -= 0.02
        filled_floors = filled_well_floor_array_mesh().triangles.copy()
        filled_floors[:, :, 2] -= 0.02
        channels = native_channel_array_mesh().triangles.copy()
        channels[:, :, 2] -= 0.02
        write_binary_stl(base_path, device_mesh(trimmed=trimmed).triangles)
        write_binary_stl(inserts_path, inserts)
        write_binary_stl(thick_layer_path, thick_layer)
        write_binary_stl(filled_floors_path, filled_floors)
        write_binary_stl(channels_path, channels)
        try:
            subprocess.run(
                [
                    "blender", "--background", "--factory-startup", "--python-exit-code", "1", "--python",
                    str(BLENDER_BOOLEAN), "--", str(base_path), str(inserts_path),
                    str(filled_floors_path), str(thick_layer_path),
                    str(channels_path), str(stl_path),
                ],
                check=True,
            )
        except FileNotFoundError as error:
            raise RuntimeError("Blender is required to generate the complete PDMS negative") from error
        return StlMesh.from_file(stl_path)


@lru_cache(maxsize=1)
def single_device_cavity_mesh() -> StlMesh:
    """Load the true one-device PDMS Boolean negative used for the close-up."""
    if not SINGLE_DEVICE_NEGATIVE_STL.exists():
        raise FileNotFoundError(
            f"Generated single-device PDMS negative not found: {SINGLE_DEVICE_NEGATIVE_STL}"
        )
    return StlMesh.from_file(SINGLE_DEVICE_NEGATIVE_STL)


def tape_guide_mesh(*, z: float) -> StlMesh:
    strips = (
        box_mesh(246.0, 7.0, 0.7, center=(0.0, 39.5, z)),
        box_mesh(246.0, 7.0, 0.7, center=(0.0, -39.5, z)),
        box_mesh(7.0, 186.0, 0.7, center=(57.5, 0.0, z)),
        box_mesh(7.0, 186.0, 0.7, center=(-57.5, 0.0, z)),
    )
    return mesh_from_triangles([strip.triangles for strip in strips])


def foil_reservoir_mesh(*, z: float) -> StlMesh:
    # A slight overlap with the PDMS pool prevents a visible seam at the foil interface.
    return positioned_notched_ring(
        outer_radius=78.0,
        inner_radius=74.7,
        height=11.0,
        z_center=z + 5.5,
    )


def cutter_platform_mesh() -> StlMesh:
    bed = box_mesh(280.0, 220.0, 5.0, center=(0.0, 0.0, -4.0))
    bed_top = -1.5
    cutting_strip = box_mesh(7.0, 204.0, 0.8, center=(54.0, 0.0, bed_top + 0.4))
    # A raised side beam leaves an open throat for the taped cast while its
    # end supports and hinge cheeks remain seated on the cutter bed.
    rail_bottom = bed_top + 6.5
    fixed_rail = box_mesh(14.0, 216.0, 6.0, center=(68.0, 0.0, rail_bottom + 3.0))
    rail_supports = (
        box_mesh(14.0, 18.0, rail_bottom - bed_top, center=(68.0, -99.0, (rail_bottom + bed_top) / 2)),
        box_mesh(14.0, 18.0, rail_bottom - bed_top, center=(68.0, 99.0, (rail_bottom + bed_top) / 2)),
    )
    hinge_mounts = (
        box_mesh(8.0, 30.0, 19.0, center=(43.0, 94.0, bed_top + 9.5)),
        box_mesh(8.0, 30.0, 19.0, center=(65.0, 94.0, bed_top + 9.5)),
    )
    return mesh_from_triangles(
        [
            bed.triangles,
            cutting_strip.triangles,
            fixed_rail.triangles,
            *(support.triangles for support in rail_supports),
            *(mount.triangles for mount in hinge_mounts),
        ]
    )


def raised_cutter_mesh(mesh: StlMesh) -> StlMesh:
    pivot = (54.0, 96.0, 8.0)
    return transform_mesh(
        mesh,
        pivot=pivot,
        translation=pivot,
        rotation_x=-72.0,
    )


def cutter_blade_mesh() -> StlMesh:
    return raised_cutter_mesh(
        box_mesh(9.0, 194.0, 14.0, center=(54.0, -1.0, 11.0))
    )


def cutter_edge_mesh() -> StlMesh:
    # Broad steel cutting plate attached beneath the dark operating arm. Its
    # lower edge remains centered on the fixed cutting strip at x=54 mm.
    return raised_cutter_mesh(
        box_mesh(16.0, 184.0, 20.0, center=(54.0, -1.0, 0.0))
    )


def cutter_grip_mesh() -> StlMesh:
    return raised_cutter_mesh(
        box_mesh(24.0, 42.0, 16.0, center=(54.0, -116.0, 8.0))
    )


def cutter_hinge_mesh() -> StlMesh:
    return transform_mesh(
        cylinder_mesh(8.0, 30.0, center=(54.0, 96.0, 8.0), segments=64),
        pivot=(54.0, 96.0, 8.0),
        translation=(54.0, 96.0, 8.0),
        rotation_y=90.0,
    )


@lru_cache(maxsize=1)
def rack_mesh() -> StlMesh:
    if not RACK_STEP.exists():
        raise FileNotFoundError(f"Wafer-rack STEP model not found: {RACK_STEP}")
    with tempfile.TemporaryDirectory(prefix="openmfd-wafer-rack-") as directory:
        directory_path = Path(directory)
        macro_path = directory_path / "export_rack.py"
        stl_path = directory_path / "wafer_rack.stl"
        macro_path.write_text(
            "\n".join(
                (
                    "import FreeCAD as App",
                    "import Import",
                    "import Mesh",
                    f"source = {str(RACK_STEP)!r}",
                    f"target = {str(stl_path)!r}",
                    "document = App.newDocument('WaferRack')",
                    "Import.insert(source, document.Name)",
                    "document.recompute()",
                    "objects = [obj for obj in document.Objects "
                    "if getattr(obj, 'Label', '') in ('Side', 'Side001') "
                    "and hasattr(obj, 'Shape') and not obj.Shape.isNull()]",
                    "Mesh.export(objects, target)",
                )
            ),
            encoding="utf-8",
        )
        try:
            subprocess.run(
                ["FreeCADCmd", str(macro_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError as error:
            raise RuntimeError("FreeCADCmd is required to render the wafer-rack STEP model") from error
        return StlMesh.from_file(stl_path)


def rack_load_meshes() -> tuple[StlMesh, StlMesh, StlMesh]:
    wafers: list[np.ndarray] = []
    casts: list[np.ndarray] = []
    foil_walls: list[np.ndarray] = []
    rack_center_z = (-12.7 + 177.1015) / 2
    for shelf in range(6):
        shelf_z = shelf * 31.75 - rack_center_z
        wafers.append(positioned_wafer(z_center=shelf_z, radius=72.5).triangles)
        casts.append(
            notched_wafer_solid(
                radius=71.5, height=4.0, z_center=shelf_z + 2.7,
            ).triangles
        )
        foil_walls.append(
            positioned_notched_ring(
                outer_radius=72.8,
                inner_radius=71.4,
                height=5.4,
                z_center=shelf_z + 2.7,
            ).triangles
        )
    return mesh_from_triangles(wafers), mesh_from_triangles(casts), mesh_from_triangles(foil_walls)


@lru_cache(maxsize=1)
def rack_shelf_mesh() -> StlMesh:
    """Export the six formed sheet-metal shelf bodies from the rack STEP assembly."""
    if not RACK_STEP.exists():
        raise FileNotFoundError(f"Wafer-rack STEP model not found: {RACK_STEP}")
    with tempfile.TemporaryDirectory(prefix="openmfd-wafer-rack-shelves-") as directory:
        directory_path = Path(directory)
        macro_path = directory_path / "export_rack_shelves.py"
        stl_path = directory_path / "wafer_rack_shelves.stl"
        macro_path.write_text(
            "\n".join(
                (
                    "import FreeCAD as App",
                    "import Import",
                    "import Mesh",
                    f"source = {str(RACK_STEP)!r}",
                    f"target = {str(stl_path)!r}",
                    "document = App.newDocument('WaferRackShelves')",
                    "Import.insert(source, document.Name)",
                    "document.recompute()",
                    "labels = {'Plate', 'Plate001', 'Plate002', 'Plate003', 'Plate004', 'Plate005'}",
                    "objects = [obj for obj in document.Objects "
                    "if getattr(obj, 'Label', '') in labels "
                    "and hasattr(obj, 'Shape') and not obj.Shape.isNull()]",
                    "Mesh.export(objects, target)",
                )
            ),
            encoding="utf-8",
        )
        try:
            subprocess.run(
                ["FreeCADCmd", str(macro_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError as error:
            raise RuntimeError("FreeCADCmd is required to render the wafer-rack STEP model") from error
        return StlMesh.from_file(stl_path)


def rack_insert_load_mesh() -> StlMesh:
    inserts: list[np.ndarray] = []
    rack_center_z = (-12.7 + 177.1015) / 2
    for shelf in range(6):
        shelf_z = shelf * 31.75 - rack_center_z
        inserts.append(centered_generated_insert(z_bottom=shelf_z + 0.7).triangles)
    return mesh_from_triangles(inserts)


def rack_insert_cap_load_mesh() -> StlMesh:
    caps: list[np.ndarray] = []
    rack_center_z = (-12.7 + 177.1015) / 2
    for shelf in range(6):
        shelf_z = shelf * 31.75 - rack_center_z
        caps.append(
            exposed_insert_mesh(
                z_bottom=shelf_z + 0.7,
                pdms_top=shelf_z + 4.7,
            ).triangles
        )
    return mesh_from_triangles(caps)










def write_binary_stl(path: Path, triangles: np.ndarray) -> None:
    normals = triangle_normals(triangles).astype("<f4")
    records = np.zeros(
        len(triangles),
        dtype=np.dtype(
            [
                ("normal", "<f4", (3,)),
                ("vertices", "<f4", (3, 3)),
                ("attribute", "<u2"),
            ]
        ),
    )
    records["normal"] = normals
    records["vertices"] = triangles.astype("<f4")
    with path.open("wb") as stream:
        stream.write(b"OpenMFD Blender scene".ljust(80, b"\0"))
        stream.write(np.asarray([len(triangles)], dtype="<u4").tobytes())
        stream.write(records.tobytes())


def draw_scene_blender(
    ax: plt.Axes,
    parts: tuple[MeshPart, ...],
    frame: tuple[float, float, float, float],
    *,
    azimuth: float,
    elevation: float,
    z_scale: float,
    framing_margin: float = MIN_CAMERA_MARGIN,
) -> None:
    frame_x, frame_y, frame_w, frame_h = frame
    sampled_parts: list[tuple[MeshPart, np.ndarray]] = []
    for part in parts:
        # Blender has a real depth buffer and can render the complete solids.
        # Face sampling was only an optimization for Matplotlib's painter and
        # turns closed STEP/STL bodies into meshes with large missing regions.
        triangles = part.mesh.triangles.copy()
        triangles[:, :, 2] *= z_scale
        sampled_parts.append((part, triangles))

    all_points = np.concatenate(
        [triangles.reshape((-1, 3)) for _, triangles in sampled_parts], axis=0
    )
    center = (all_points.min(axis=0) + all_points.max(axis=0)) / 2
    rotation = rotation_matrix(azimuth, elevation)
    transformed_parts = [
        (part, ((triangles.reshape((-1, 3)) - center) @ rotation).reshape((-1, 3, 3)))
        for part, triangles in sampled_parts
    ]
    transformed_points = np.concatenate(
        [triangles.reshape((-1, 3)) for _, triangles in transformed_parts], axis=0
    )
    minimum = transformed_points.min(axis=0)
    maximum = transformed_points.max(axis=0)
    projected_center = (minimum[:2] + maximum[:2]) / 2
    transformed_parts = [
        (
            part,
            triangles - np.array((projected_center[0], projected_center[1], 0.0)),
        )
        for part, triangles in transformed_parts
    ]
    transformed_points = np.concatenate(
        [triangles.reshape((-1, 3)) for _, triangles in transformed_parts], axis=0
    )
    minimum = transformed_points.min(axis=0)
    maximum = transformed_points.max(axis=0)
    size = np.maximum(maximum - minimum, 1e-6)

    with tempfile.TemporaryDirectory(prefix="openmfd-blender-scene-") as directory:
        directory_path = Path(directory)
        output_path = directory_path / "scene.png"
        manifest_parts = []
        for index, (part, triangles) in enumerate(transformed_parts):
            stl_path = directory_path / f"part-{index:02d}.stl"
            write_binary_stl(stl_path, triangles)
            manifest_parts.append(
                {
                    "path": str(stl_path),
                    "color": part.base_color,
                    "alpha": part.alpha,
                    "roughness": part.roughness,
                    "metallic": part.metallic,
                    "emission_strength": part.emission_strength,
                    "transparency_overlap": part.transparency_overlap,
                    "dissolve_coplanar": part.dissolve_coplanar,
                    "transmission_weight": part.transmission_weight,
                }
            )
        # Normalized coordinates are not physical lengths on a rectangular
        # canvas. Fit to the actual destination pixels, including axes scaling.
        lower, upper = ax.transData.transform(
            ((frame_x, frame_y), (frame_x + frame_w, frame_y + frame_h))
        )
        frame_aspect = (upper[0] - lower[0]) / (upper[1] - lower[1])
        render_height = max(1200, math.ceil(640 / frame_aspect))
        render_width = round(render_height * frame_aspect)
        aspect = render_width / render_height
        fitted_scale = max(size[1], size[0] / aspect)
        pixel_guard_scale = 1.0 + 2.0 * CAMERA_EDGE_GUARD_PX / min(render_width, render_height)
        camera_margin = max(framing_margin, MIN_CAMERA_MARGIN, pixel_guard_scale)
        ortho_scale = fitted_scale * camera_margin
        camera_z = float(maximum[2] + max(size) * 2.5)
        manifest = {
            "parts": manifest_parts,
            "output": str(output_path),
            "width": render_width,
            "height": render_height,
            "camera_z": camera_z,
            "camera_clip_end": float(camera_z - minimum[2] + max(size) * 2.0),
            "ortho_scale": float(ortho_scale),
        }
        manifest_path = directory_path / "scene.json"
        for fit_pass in range(MAX_CAMERA_FIT_PASSES):
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            subprocess.run(
                [
                    "blender", "--background", "--factory-startup", "--python-exit-code", "1", "--python",
                    str(BLENDER_RENDERER), "--", str(manifest_path),
                ],
                check=True,
            )
            rendered = Image.open(output_path).convert("RGBA")
            visible_alpha = rendered.getchannel("A").point(
                lambda alpha: 255 if alpha >= 8 else 0
            )
            content_bounds = visible_alpha.getbbox()
            if content_bounds is None:
                raise RuntimeError("Blender produced an empty scene")
            left, top, right, bottom = content_bounds
            edge_clearance = min(left, top, render_width - right, render_height - bottom)
            if edge_clearance >= CAMERA_EDGE_GUARD_PX:
                break
            if fit_pass == MAX_CAMERA_FIT_PASSES - 1:
                raise RuntimeError(
                    f"Scene still violates the {CAMERA_EDGE_GUARD_PX}px camera guard "
                    f"after {MAX_CAMERA_FIT_PASSES} fit passes: bounds={content_bounds}, "
                    f"render={render_width}x{render_height}, clearance={edge_clearance}px, "
                    f"ortho_scale={manifest['ortho_scale']:.3f}"
                )
            content_width = max(right - left, 1)
            content_height = max(bottom - top, 1)
            allowed_width = render_width - 2 * CAMERA_EDGE_GUARD_PX
            allowed_height = render_height - 2 * CAMERA_EDGE_GUARD_PX
            measured_growth = max(
                content_width / allowed_width,
                content_height / allowed_height,
                1.0,
            )
            manifest["ortho_scale"] *= measured_growth * 1.04
        white = Image.new("RGBA", rendered.size, (255, 255, 255, 255))
        image = np.asarray(Image.alpha_composite(white, rendered).convert("RGB"))
    ax.imshow(
        image,
        extent=(frame_x, frame_x + frame_w, frame_y, frame_y + frame_h),
        interpolation="lanczos",
        aspect="auto",
        zorder=2,
    )




def wafer_part(z: float = 0.0) -> MeshPart:
    return MeshPart(
        positioned_wafer(z_center=z),
        COLORS["wafer"],
    )


def insert_part(z: float = 0.7) -> MeshPart:
    return MeshPart(
        centered_generated_insert(z_bottom=z), COLORS["insert"],
    )


def insert_cap_part(z: float = 0.7, pdms_top: float = 4.85) -> MeshPart:
    return MeshPart(
        exposed_insert_mesh(z_bottom=z, pdms_top=pdms_top),
        COLORS["insert"],
    )


def thick_layer_part(z: float = 0.7) -> MeshPart:
    return MeshPart(
        positioned_thick_layer(z_bottom=z),
        "#2c8f86",
        alpha=1.0,
    )


def device_part(z: float = 0.0, alpha: float = 0.66, *, trimmed: bool = True) -> MeshPart:
    return MeshPart(
        device_mesh(z=z, trimmed=trimmed),
        COLORS["pdms"], alpha=alpha,
    )


def cavity_device_part(
    z: float,
    *,
    upside_down: bool = False,
    trimmed: bool = True,
    alpha: float = 0.76,
) -> MeshPart:
    mesh = transform_mesh(
        cavity_device_mesh(trimmed=trimmed),
        translation=(0.0, 0.0, z),
        rotation_x=180.0 if upside_down else 0.0,
        pivot=(0.0, 0.0, 0.0),
    )
    return MeshPart(
        mesh,
        "#79a7ca",
        alpha=alpha,   roughness=0.48,
        transparency_overlap=False,
    )


def cavity_device_render_parts(
    z: float,
    *,
    upside_down: bool = False,
    trimmed: bool = True,
    alpha: float = 0.44,
) -> tuple[MeshPart, MeshPart]:
    """Partition one Boolean PDMS mesh into outer and cavity faces."""
    source = cavity_device_mesh(trimmed=trimmed)
    triangles = source.triangles
    centroids = triangles.mean(axis=1)
    z_min = float(triangles[:, :, 2].min())
    z_max = float(triangles[:, :, 2].max())
    tolerance = 1e-3
    on_outer_plane = (
        np.all(np.abs(triangles[:, :, 2] - z_min) < tolerance, axis=1)
        | np.all(np.abs(triangles[:, :, 2] - z_max) < tolerance, axis=1)
    )
    if trimmed:
        inside_device_field = (
            (np.abs(centroids[:, 0]) < 53.4)
            & (np.abs(centroids[:, 1]) < 35.4)
        )
    else:
        # The native top-layer field, including both trimming guides, is
        # bounded by 56.25 x 37.84 mm and remains well inside the wafer edge.
        inside_device_field = (
            (np.abs(centroids[:, 0]) < 60.0)
            & (np.abs(centroids[:, 1]) < 42.0)
        )
    # Every non-exterior face in the device field belongs to the molded
    # negative. This includes the horizontal floors of the tapered wells and
    # microchannels as well as their sidewalls; leaving those floors in the
    # translucent outer skin makes the cavities appear as small insert caps.
    internal = inside_device_field & ~on_outer_plane

    def positioned(face_mask: np.ndarray) -> StlMesh:
        return transform_mesh(
            StlMesh(triangles[face_mask]),
            translation=(0.0, 0.0, z),
            rotation_x=180.0 if upside_down else 0.0,
            pivot=(0.0, 0.0, 0.0),
        )

    outer = MeshPart(
        positioned(~internal),
        "#79a7ca",
        alpha=alpha,   roughness=0.48,
        transparency_overlap=False, dissolve_coplanar=True,
        transmission_weight=0.0,
    )
    cavities = MeshPart(
        positioned(internal),
        "#274f68",
        alpha=0.78,
         roughness=0.34, transparency_overlap=False,
        dissolve_coplanar=True, transmission_weight=0.0,
    )
    return outer, cavities


def single_device_cavity_render_parts(
    z: float = 0.0,
    *,
    upside_down: bool = True,
) -> tuple[MeshPart, MeshPart]:
    """Partition the true inverted PDMS negative into outer and cavity faces."""
    source = single_device_cavity_mesh()
    triangles = source.triangles
    points = triangles.reshape((-1, 3))
    minimum = points.min(axis=0)
    maximum = points.max(axis=0)
    tolerance = 1e-3
    centroids = triangles.mean(axis=1)
    normals = np.cross(
        triangles[:, 1] - triangles[:, 0],
        triangles[:, 2] - triangles[:, 0],
    )
    normal_lengths = np.linalg.norm(normals, axis=1)
    horizontal = np.divide(
        np.abs(normals[:, 2]),
        normal_lengths,
        out=np.zeros_like(normal_lengths),
        where=normal_lengths > 0,
    ) > 0.999
    # The shallow chamber-footprint cutter leaves coplanar shoulder faces at
    # 0.6 mm. The reservoirs themselves are through-openings, so drawing those
    # shoulders as dark cavity faces makes each opening look falsely capped.
    # Suppress only the shallow cutter shoulder that reads as a false well
    # floor. Keep the slab skins so the surrounding PDMS remains visibly solid.
    visible_faces = ~(
        horizontal
        & (np.abs(centroids[:, 2] - 0.6) < tolerance)
    )
    outer_faces = np.zeros(len(triangles), dtype=bool)
    for axis in range(3):
        outer_faces |= np.all(
            np.abs(triangles[:, :, axis] - minimum[axis]) < tolerance,
            axis=1,
        )
        outer_faces |= np.all(
            np.abs(triangles[:, :, axis] - maximum[axis]) < tolerance,
            axis=1,
        )

    def positioned(mask: np.ndarray) -> StlMesh:
        return transform_mesh(
            StlMesh(triangles[mask]),
            translation=(0.0, 0.0, z),
            rotation_x=180.0 if upside_down else 0.0,
            pivot=(0.0, 0.0, 2.5),
        )

    outer = MeshPart(
        positioned(outer_faces & visible_faces),
        "#79a7ca",
        alpha=0.58,   roughness=0.42,
        transparency_overlap=False, dissolve_coplanar=True,
        transmission_weight=0.0,
    )
    cavities = MeshPart(
        positioned(~outer_faces & visible_faces),
        "#507d98",
        alpha=0.72,   roughness=0.30,
        transparency_overlap=False, dissolve_coplanar=True,
        transmission_weight=0.0,
    )
    return outer, cavities


def foil_part(z: float = 0.7) -> MeshPart:
    return MeshPart(
        foil_reservoir_mesh(z=z),
        COLORS["foil"],
        alpha=0.72,
    )


def paper_part(z: float = -0.5) -> MeshPart:
    return MeshPart(
        box_mesh(246.0, 186.0, 0.6, center=(0.0, 0.0, z)),
        COLORS["paper"],
        alpha=1.0,  roughness=0.92, emission_strength=0.28,
    )


def glass_part(
    z: float = 0.0,
    *,
    width: float = 110.0,
    depth: float = 74.0,
    alpha: float = 0.07,
) -> MeshPart:
    return MeshPart(
        box_mesh(width, depth, 0.8, center=(0.0, 0.0, z)),
        "#b9dce9", alpha=alpha,
        roughness=0.18, transparency_overlap=False, transmission_weight=0.0,
    )


BONDED_PDMS_THICKNESS = 5.0
BONDED_GLASS_THICKNESS = 0.8
BONDED_GLASS_SIZE = (112.0, 76.0)


def bonded_device_parts(
    *,
    pdms_bottom: float,
    upside_down: bool = False,
    pdms_alpha: float = 0.48,
) -> tuple[MeshPart, ...]:
    """Return one canonical trimmed PDMS slab bonded directly to one glass plate."""
    if upside_down:
        # After rotation the PDMS spans [pdms_bottom, pdms_bottom + 5].
        pdms_transform_z = pdms_bottom + BONDED_PDMS_THICKNESS
        glass_z = pdms_bottom + BONDED_PDMS_THICKNESS + BONDED_GLASS_THICKNESS / 2
    else:
        pdms_transform_z = pdms_bottom
        glass_z = pdms_bottom - BONDED_GLASS_THICKNESS / 2

    parts: list[MeshPart] = [
        *cavity_device_render_parts(
            pdms_transform_z,
            upside_down=upside_down,
            alpha=pdms_alpha,
        ),
    ]
    parts.append(
        glass_part(
            glass_z,
            width=BONDED_GLASS_SIZE[0],
            depth=BONDED_GLASS_SIZE[1],
            alpha=0.24,
        )
    )
    return tuple(parts)


def frame_part(z: float = 0.0, *, upside_down: bool = False) -> MeshPart:
    mesh = transform_mesh(
        StlMesh.from_file(FRAME_STL),
        translation=(0.0, 0.0, z),
        rotation_x=180.0 if upside_down else 0.0,
    )
    return MeshPart(
        mesh, COLORS["frame"],
    )


def frame_shell_part(z: float = 0.0) -> MeshPart:
    """Opaque source-dimension shell used where the exterior frame is exposed."""
    return MeshPart(
        rectangular_shell_mesh(127.5, 85.35, 112.2, 76.2, 17.0, z=z),
        COLORS["frame"],
        alpha=1.0,
    )


def rack_part(*, rotation_z: float = 0.0, translation_z: float = 0.0) -> MeshPart:
    return MeshPart(
        transform_mesh(
            rack_mesh(),
            scale=(1.0, 1.0, 1.24),
            rotation_z=rotation_z,
            translation=(0.0, 0.0, translation_z),
            pivot=(0.0, 0.0, (-12.7 + 177.1015) / 2),
        ),
        "#aeb8bd",
          metallic=0.28, roughness=0.38,
    )


def rack_shelf_part(*, rotation_z: float = 0.0, translation_z: float = 0.0) -> MeshPart:
    return MeshPart(
        transform_mesh(
            rack_shelf_mesh(), scale=(1.0, 1.0, 1.24), rotation_z=rotation_z,
            translation=(0.0, 0.0, translation_z),
            pivot=(0.0, 0.0, (-12.7 + 177.1015) / 2),
        ),
        "#c2c9cd",
        alpha=1.0,   metallic=0.22, roughness=0.40,
    )


def rack_wafer_load_part(*, rotation_z: float = 0.0, translation_z: float = 0.0) -> MeshPart:
    wafers, _, _ = rack_load_meshes()
    return MeshPart(
        transform_mesh(
            wafers, scale=(1.0, 1.0, 1.24), rotation_z=rotation_z,
            translation=(0.0, 0.0, translation_z),
            pivot=(0.0, 0.0, 0.0),
        ),
        COLORS["wafer"],
        alpha=1.0,
    )


def rack_insert_load_part(*, rotation_z: float = 0.0, translation_z: float = 0.0) -> MeshPart:
    return MeshPart(
        transform_mesh(
            rack_insert_load_mesh(), scale=(1.0, 1.0, 1.24), rotation_z=rotation_z,
            translation=(0.0, 0.0, translation_z),
            pivot=(0.0, 0.0, 0.0),
        ),
        COLORS["insert"],
        alpha=1.0,
    )


def rack_insert_cap_load_part(*, rotation_z: float = 0.0, translation_z: float = 0.0) -> MeshPart:
    return MeshPart(
        transform_mesh(
            rack_insert_cap_load_mesh(), scale=(1.0, 1.0, 1.24), rotation_z=rotation_z,
            translation=(0.0, 0.0, translation_z),
            pivot=(0.0, 0.0, 0.0),
        ),
        "#b83e43",
        alpha=1.0,
    )


def rack_cast_load_part(*, rotation_z: float = 0.0, translation_z: float = 0.0) -> MeshPart:
    _, casts, _ = rack_load_meshes()
    return MeshPart(
        transform_mesh(
            casts, scale=(1.0, 1.0, 1.24), rotation_z=rotation_z,
            translation=(0.0, 0.0, translation_z),
            pivot=(0.0, 0.0, 0.0),
        ),
        "#689bc7",
        alpha=1.0,
    )


def rack_foil_load_part(*, rotation_z: float = 0.0, translation_z: float = 0.0) -> MeshPart:
    _, _, foil_walls = rack_load_meshes()
    return MeshPart(
        transform_mesh(
            foil_walls, scale=(1.0, 1.0, 1.24), rotation_z=rotation_z,
            translation=(0.0, 0.0, translation_z),
            pivot=(0.0, 0.0, 0.0),
        ),
        COLORS["foil"],
        alpha=1.0,
    )


def desiccator_part() -> MeshPart:
    wall = circular_ring_mesh(126.0, 123.5, 250.0, center=(0.0, 0.0, 0.0), segments=64)
    lid = cylinder_mesh(130.0, 6.0, center=(0.0, 0.0, 128.0), segments=64)
    base = cylinder_mesh(130.0, 8.0, center=(0.0, 0.0, -129.0), segments=64)
    fitting = cylinder_mesh(7.0, 24.0, center=(0.0, 0.0, 143.0), segments=32)
    return MeshPart(
        mesh_from_triangles([wall.triangles, lid.triangles, base.triangles, fitting.triangles]),
        "#c4d8df",
        alpha=0.16,
    )


def desiccator_gasket_part() -> MeshPart:
    return MeshPart(
        circular_ring_mesh(130.0, 123.0, 4.0, center=(0.0, 0.0, 125.0), segments=96),
        "#2f3538",
        alpha=1.0,
    )


def vacuum_valve_part() -> MeshPart:
    stem = cylinder_mesh(5.0, 23.0, center=(0.0, 0.0, 147.5), segments=32)
    valve_body = box_mesh(25.0, 9.0, 8.0, center=(0.0, 0.0, 157.0))
    handle = box_mesh(34.0, 4.0, 3.5, center=(0.0, 0.0, 164.0))
    handle_stem = cylinder_mesh(2.8, 9.0, center=(0.0, 0.0, 160.5), segments=24)
    gauge_neck = cylinder_mesh(2.8, 14.0, center=(13.0, 0.0, 170.0), segments=24)
    gauge_case = transform_mesh(
        cylinder_mesh(13.0, 4.0, segments=64),
        translation=(13.0, -8.0, 176.0),
        rotation_x=90.0,
    )
    return MeshPart(
        mesh_from_triangles(
            [
                stem.triangles, valve_body.triangles, handle.triangles,
                handle_stem.triangles, gauge_neck.triangles, gauge_case.triangles,
            ]
        ),
        "#686f74",
        alpha=1.0,
    )


def vacuum_gauge_face_part() -> MeshPart:
    face = transform_mesh(
        cylinder_mesh(11.0, 0.7, segments=64),
        translation=(13.0, -10.25, 176.0),
        rotation_x=90.0,
    )
    return MeshPart(
        face, "#f4f4f0",
        alpha=1.0,
    )


def oven_frame_part() -> MeshPart:
    frame_meshes = (
        box_mesh(240.0, 220.0, 12.0, center=(0.0, 0.0, -142.0)),
        box_mesh(240.0, 220.0, 12.0, center=(0.0, 0.0, 142.0)),
        box_mesh(12.0, 220.0, 272.0, center=(-114.0, 0.0, 0.0)),
        box_mesh(12.0, 220.0, 272.0, center=(114.0, 0.0, 0.0)),
        box_mesh(216.0, 12.0, 272.0, center=(0.0, 104.0, 0.0)),
        box_mesh(216.0, 10.0, 14.0, center=(0.0, -112.0, -129.0)),
        box_mesh(216.0, 10.0, 14.0, center=(0.0, -112.0, 129.0)),
    )
    return MeshPart(
        transform_mesh(
            mesh_from_triangles([mesh.triangles for mesh in frame_meshes]),
            rotation_z=90.0,
            pivot=(0.0, 0.0, 0.0),
        ),
        "#42494e",
        alpha=1.0,   roughness=0.60,
    )


def oven_window_part() -> MeshPart:
    return MeshPart(
        transform_mesh(
            box_mesh(188.0, 2.0, 226.0, center=(0.0, -118.0, 0.0)),
            rotation_z=90.0,
            pivot=(0.0, 0.0, 0.0),
        ),
        "#8eabb7",
        alpha=0.16,
    )


def oven_handle_part() -> MeshPart:
    handle_meshes = (
        box_mesh(8.0, 8.0, 96.0, center=(84.0, -126.0, 0.0)),
        box_mesh(15.0, 12.0, 12.0, center=(84.0, -121.0, -42.0)),
        box_mesh(15.0, 12.0, 12.0, center=(84.0, -121.0, 42.0)),
    )
    return MeshPart(
        transform_mesh(
            mesh_from_triangles([mesh.triangles for mesh in handle_meshes]),
            rotation_z=90.0,
            pivot=(0.0, 0.0, 0.0),
        ),
        "#aeb6ba",
        alpha=1.0,   roughness=0.24, metallic=0.58,
    )


class MoldView(Step):
    z_scale = 1.35


class LoadedRack(Step):
    azimuth = -65.0
    elevation = -76.0
    z_scale = 1.0
    translation_z = 0.0

    def scene_parts(self) -> tuple[MeshPart, ...]:
        load_rotation = 180.0
        return (
            rack_part(translation_z=self.translation_z),
            rack_shelf_part(translation_z=self.translation_z),
            rack_wafer_load_part(rotation_z=load_rotation, translation_z=self.translation_z),
            rack_insert_load_part(rotation_z=load_rotation, translation_z=self.translation_z),
            rack_cast_load_part(rotation_z=load_rotation, translation_z=self.translation_z),
            rack_insert_cap_load_part(rotation_z=load_rotation, translation_z=self.translation_z),
            rack_foil_load_part(rotation_z=load_rotation, translation_z=self.translation_z),
        )


class PreparedMold(MoldView):
    title = "Hybrid mold ready"
    detail = "Parylene-coated mold"

    def scene_parts(self) -> tuple[MeshPart, ...]:
        return wafer_part(0.0), thick_layer_part(0.7), insert_part(0.9)


class PourPDMS(MoldView):
    title = "Pour PDMS"
    detail = "Fill below insert tops"

    def scene_parts(self) -> tuple[MeshPart, ...]:
        pdms_top = 4.85
        pdms_pool = MeshPart(
            notched_wafer_solid(
                radius=74.8,
                height=pdms_top - 0.7,
                z_center=(pdms_top + 0.7) / 2,
            ),
            COLORS["pdms"], alpha=0.48,
        )
        return (
            wafer_part(0.0), thick_layer_part(0.7), insert_part(0.9), pdms_pool,
            insert_cap_part(0.9, pdms_top), foil_part(0.7),
        )
    def draw_marks(self, ax: plt.Axes, frame: tuple[float, float, float, float]) -> None:
        x, y, width, height = frame
        ax.add_patch(FancyArrowPatch(
            (x + width * 0.83, y + height * 0.92),
            (x + width * 0.62, y + height * 0.60),
            arrowstyle="-|>", mutation_scale=12, linewidth=1.5,
            color=COLORS["accent"], zorder=6,
        ))


class Degas(LoadedRack):
    title = "Degas in rack"
    detail = "Until bubbles clear"

    def scene_parts(self) -> tuple[MeshPart, ...]:
        # Render the vessel before its contents so the rack remains solid.
        return (desiccator_part(), desiccator_gasket_part(), vacuum_valve_part(),
                vacuum_gauge_face_part(), *super().scene_parts())


class Cure(LoadedRack):
    title = "Cure in rack"
    detail = "100 °C for 1 h"
    translation_z = -18.0

    def scene_parts(self) -> tuple[MeshPart, ...]:
        return (oven_frame_part(), oven_window_part(), oven_handle_part(),
                *super().scene_parts())

    def draw_marks(self, ax: plt.Axes, frame: tuple[float, float, float, float]) -> None:
        x, y, width, height = frame
        for fraction in (0.40, 0.50, 0.60):
            xs = np.linspace(x + width * fraction, x + width * (fraction + 0.015), 30)
            ys = np.linspace(y + height * 0.76, y + height * 0.98, 30)
            ax.plot(xs + np.sin(np.linspace(0, 2 * math.pi, 30)) * width * 0.014, ys,
                    color="#9c5a68", linewidth=1.2, zorder=6)


class Demold(Step):
    title = "Demold cast"
    detail = "Peel from the corners"

    def scene_parts(self) -> tuple[MeshPart, ...]:
        return cavity_device_render_parts(0.0, trimmed=False)


class Trim(Step):
    title = "Tape and trim"
    detail = "108 × 72 mm"
    z_scale = 1.3

    def scene_parts(self) -> tuple[MeshPart, ...]:
        paper_center_z = -1.2
        # Keep the flipped cast just above the paper surface. Exact coplanar
        # contact makes the circular STL's triangulated underside z-fight with
        # the paper and produces false radial lines from the wafer perimeter.
        cast_bottom_z = -0.86
        cast_top_z = cast_bottom_z + BONDED_PDMS_THICKNESS
        cutter_platform = MeshPart(
            cutter_platform_mesh(),
            "#aeb8bd",
            alpha=1.0,
        )
        tape = MeshPart(
            tape_guide_mesh(z=cast_top_z + 0.35),
            COLORS["tape"],
            alpha=0.88,
        )
        cutter_blade = MeshPart(
            cutter_blade_mesh(), "#25292c",
             roughness=0.30, metallic=0.18,
        )
        cutter_edge = MeshPart(
            cutter_edge_mesh(), "#b6bdc1",
             roughness=0.24, metallic=0.62,
        )
        cutter_grip = MeshPart(
            cutter_grip_mesh(), "#17191b",
             roughness=0.52,
        )
        cutter_hinge = MeshPart(
            cutter_hinge_mesh(), "#9ca5aa",
             roughness=0.22, metallic=0.68,
        )
        return (
            cutter_platform,
            paper_part(paper_center_z),
            *cavity_device_render_parts(
                cast_bottom_z + BONDED_PDMS_THICKNESS,
                upside_down=True,
                trimmed=False,
            ),
            tape, cutter_blade, cutter_edge, cutter_grip, cutter_hinge,
        )
    def draw_marks(self, ax: plt.Axes, frame: tuple[float, float, float, float]) -> None:
        x, y, width, height = frame
        self.annotate(ax, x + width * 0.22, y + height * 0.94, "Masking tape")
        self.annotate(ax, x + width * 0.80, y + height * 0.94, "Cutter", color=COLORS["blade"])


class BondAndAutoclave(Step):
    title = "Bond and autoclave"
    detail = "121 °C for 15 min"

    def scene_parts(self) -> tuple[MeshPart, ...]:
        return bonded_device_parts(pdms_bottom=0.0)

    def draw_marks(self, ax: plt.Axes, frame: tuple[float, float, float, float]) -> None:
        x, y, width, height = frame
        for fraction in (0.34, 0.50, 0.66):
            ax.plot([x + width * fraction, x + width * (fraction + 0.03)],
                    [y + height * 0.96, y + height * 0.82],
                    color=COLORS["accent"], linewidth=1.5, zorder=6)


class AssembleFrame(Step):
    title = "Frame assembly"
    detail = "Seat glass-side up"

    def scene_parts(self) -> tuple[MeshPart, ...]:
        adhesive = MeshPart(
            perimeter_ring_mesh(117.0, 81.0, 3.2, 0.8, z=6.6),
            COLORS["adhesive"], alpha=0.92,
        )
        return (
            *bonded_device_parts(
                pdms_bottom=7.0,
                upside_down=True,
                pdms_alpha=0.48,
            ),
            frame_part(0.0, upside_down=True), adhesive,
        )
    def draw_marks(self, ax: plt.Axes, frame: tuple[float, float, float, float]) -> None:
        x, y, width, height = frame
        # The tip terminates on the visible right-hand adhesive groove.
        start = np.array((x + width * 0.78, y + height * 0.95))
        target = np.array((x + width * 0.79, y + height * 0.47))
        direction = target - start
        direction /= np.linalg.norm(direction)
        barrel_end = start + (target - start) * 0.52
        ax.plot([start[0], barrel_end[0]], [start[1], barrel_end[1]], color="#4f5a63",
                linewidth=8.0, solid_capstyle="round", zorder=8)
        ax.plot([start[0], barrel_end[0]], [start[1], barrel_end[1]], color="#d7e9ef",
                linewidth=5.2, solid_capstyle="round", zorder=9)
        ax.plot([barrel_end[0], target[0]], [barrel_end[1], target[1]], color="#4f5a63",
                linewidth=1.2, zorder=9)
        normal = np.array((-direction[1], direction[0]))
        flange_a = start - normal * width * 0.030
        flange_b = start + normal * width * 0.030
        ax.plot([flange_a[0], flange_b[0]], [flange_a[1], flange_b[1]],
                color="#4f5a63", linewidth=2.0, zorder=9)
        ax.plot(target[0], target[1], marker="o", markersize=6.5,
                markerfacecolor=COLORS["adhesive"], markeredgecolor="#8f6515",
                markeredgewidth=0.7, linestyle="none", zorder=10)
        self.annotate(ax, x + width * 0.72, y + height * 0.96,
                      "Adhesive", color="#8f6515")


class PrepareCulture(Step):
    title = "Cure and prepare"
    detail = "3 d cure; then plasma"

    def scene_parts(self) -> tuple[MeshPart, ...]:
        adhesive = MeshPart(
            perimeter_ring_mesh(113.0, 77.0, 2.4, 0.8, z=-6.6),
            COLORS["adhesive"], alpha=0.92,
        )
        return (
            *bonded_device_parts(pdms_bottom=-6.2),
            adhesive,
            frame_part(0.0),
        )
# Protocol order is declared once; labels and serpentine placement derive from it.
STEPS = (PreparedMold(), PourPDMS(), Degas(), Cure(), Demold(), Trim(),
         BondAndAutoclave(), AssembleFrame(), PrepareCulture())


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    connectionstyle: str = "arc3,rad=0",
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=17,
            linewidth=2.0,
            color=COLORS["ink"],
            connectionstyle=connectionstyle,
            shrinkA=2,
            shrinkB=2,
            zorder=8,
        )
    )


def draw_workflow() -> None:
    # Author at manuscript width so labels retain their physical point sizes.
    fig, ax = plt.subplots(figsize=(6.5, 6.2))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    frames = []
    for number, step in enumerate(STEPS, 1):
        row, column = divmod(number - 1, 3)
        column = 2 - column if row % 2 else column
        frame = (0.035 + column * 0.325, 0.69 - row * 0.30, 0.28, 0.20)
        print(f"Rendering step {number}: {step.title}", flush=True)
        step.draw(ax, frame, number)
        frames.append(frame)

    for previous, following in zip(frames, frames[1:]):
        px, py, width, height = previous
        nx, ny, _, _ = following
        if py == ny:
            direction = math.copysign(1.0, nx - px)
            edge = (1 + direction) / 2
            add_arrow(ax, (px + width * edge + direction * 0.005, py + height / 2),
                      (nx + width * (1 - edge) - direction * 0.005, ny + height / 2))
        else:
            outer_x = px + width / 2 + math.copysign(0.16, px + width / 2 - 0.5)
            add_arrow(ax, (outer_x, py), (outer_x, ny + height))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / f"{OUTPUT_STEM}.pdf", dpi=DPI)
    fig.savefig(OUTPUT_DIR / f"{OUTPUT_STEM}.png", dpi=DPI)
    plt.close(fig)


def main() -> int:
    draw_workflow()
    print(f"Wrote {OUTPUT_DIR / f'{OUTPUT_STEM}.pdf'}")
    print(f"Wrote {OUTPUT_DIR / f'{OUTPUT_STEM}.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
