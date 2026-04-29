#!/usr/bin/env python3

from __future__ import annotations

import sys
from io import BytesIO
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from zipfile import ZipFile

import ezdxf
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[3]
FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig1_openmfd_design"
SUBFIGURE_DPI = 600
DESIGN_DIR = ROOT / "designs" / "open_chamber" / "2_compartment_96_well_300um_suex200_v27"
DESIGN_STEM = "2_compartment_96_well_300um_suex200_v27"
FRAME_STL = ROOT / "plates" / "96_well_plate_reservoirs_print_hips_2" / "96_well_plate_reservoirs_print_hips_2.stl"
WORKFLOW_ODP = FIGURE_DIR / "final_drop" / "Fig1_workflow" / "draft_figure.odp"
WORKFLOW_ASSEMBLED_PHOTO = "Pictures/100000000000120000000D80C7A47E4B.jpg"
STL_DISPLAY_Z_SCALE = 1.0

sys.path.insert(0, str(ROOT))

from openmfd.devices.presets import TwoCompartmentDeviceConfig  # noqa: E402


COLORS = {
    "ink": "#1d2633",
    "muted": "#687583",
    "grid": "#d8dee8",
    "paper": "#f7f9fb",
    "bottom": "#1d6fbc",
    "top": "#32a889",
    "insert": "#f2a33a",
    "lock": "#7657d8",
    "frame": "#303a52",
    "wafer": "#e8edf4",
    "dark_card": "#111827",
}


@dataclass(frozen=True)
class TextStyle:
    fontsize: float
    color: str
    ha: str = "center"
    va: str = "center"
    fontweight: str | None = None
    linespacing: float | None = None
    bbox: dict[str, object] | None = None
    axes: bool = False

    def kwargs(self, ax: plt.Axes) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "fontsize": self.fontsize,
            "color": self.color,
            "ha": self.ha,
            "va": self.va,
        }
        if self.fontweight is not None:
            kwargs["fontweight"] = self.fontweight
        if self.linespacing is not None:
            kwargs["linespacing"] = self.linespacing
        if self.bbox is not None:
            kwargs["bbox"] = dict(self.bbox)
        if self.axes:
            kwargs["transform"] = ax.transAxes
        return kwargs


@dataclass(frozen=True)
class PatchStyle:
    facecolor: str
    edgecolor: str
    linewidth: float = 1.0
    alpha: float = 1.0

    def kwargs(self) -> dict[str, object]:
        return {
            "facecolor": self.facecolor,
            "edgecolor": self.edgecolor,
            "linewidth": self.linewidth,
            "alpha": self.alpha,
        }


@dataclass(frozen=True)
class Bounds:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @classmethod
    def from_segments(cls, segments: tuple[tuple[tuple[float, float], tuple[float, float]], ...]) -> "Bounds":
        xs = tuple(point[0] for segment in segments for point in segment)
        ys = tuple(point[1] for segment in segments for point in segment)
        return cls(min(xs), min(ys), max(xs), max(ys))

    @classmethod
    def from_points(cls, points: np.ndarray) -> "Bounds":
        return cls(
            float(points[:, 0].min()),
            float(points[:, 1].min()),
            float(points[:, 0].max()),
            float(points[:, 1].max()),
        )

    @classmethod
    def combine(cls, drawings: tuple["DxfDrawing", ...]) -> "Bounds":
        return cls(
            min(drawing.bounds.min_x for drawing in drawings),
            min(drawing.bounds.min_y for drawing in drawings),
            max(drawing.bounds.max_x for drawing in drawings),
            max(drawing.bounds.max_y for drawing in drawings),
        )

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y


@dataclass(frozen=True)
class DxfDrawing:
    segments: tuple[tuple[tuple[float, float], tuple[float, float]], ...]
    bounds: Bounds

    @classmethod
    def from_file(cls, path: Path) -> "DxfDrawing":
        doc = ezdxf.readfile(path)
        segments = tuple(line_segment(entity) for entity in doc.modelspace())
        if not segments:
            raise ValueError(f"DXF contains no drawable line segments: {path}")
        return cls(segments=segments, bounds=Bounds.from_segments(segments))


@dataclass(frozen=True)
class DxfSources:
    single_top: DxfDrawing
    single_bottom: DxfDrawing
    aligned: DxfDrawing

    @classmethod
    def from_generated_design(cls) -> "DxfSources":
        return cls(
            single_top=DxfDrawing.from_file(DESIGN_DIR / f"{DESIGN_STEM}_single_top.dxf"),
            single_bottom=DxfDrawing.from_file(DESIGN_DIR / f"{DESIGN_STEM}_single_bottom.dxf"),
            aligned=DxfDrawing.from_file(DESIGN_DIR / f"{DESIGN_STEM}_aligned.dxf"),
        )


@dataclass(frozen=True)
class StlMesh:
    triangles: np.ndarray

    @classmethod
    def from_file(cls, path: Path) -> "StlMesh":
        data = path.read_bytes()
        if len(data) >= 84:
            triangle_count = int(np.frombuffer(data[80:84], dtype="<u4")[0])
            if 84 + triangle_count * 50 == len(data):
                return cls.from_binary(data, triangle_count)
        return cls.from_ascii(data, path)

    @classmethod
    def from_binary(cls, data: bytes, triangle_count: int) -> "StlMesh":
        triangles = np.empty((triangle_count, 3, 3), dtype=float)
        offset = 84
        for index in range(triangle_count):
            offset += 12
            triangles[index] = np.frombuffer(data[offset : offset + 36], dtype="<f4").reshape(3, 3)
            offset += 38
        return cls(triangles)

    @classmethod
    def from_ascii(cls, data: bytes, path: Path) -> "StlMesh":
        vertices = []
        for line in data.decode("utf-8", errors="strict").splitlines():
            fields = line.strip().split()
            if fields[:1] == ["vertex"]:
                vertices.append(tuple(float(value) for value in fields[1:4]))
        if len(vertices) % 3 != 0:
            raise ValueError(f"ASCII STL has incomplete triangles: {path}")
        return cls(np.array(vertices, dtype=float).reshape((-1, 3, 3)))


@dataclass(frozen=True)
class StlSources:
    single_insert: StlMesh
    array_insert: StlMesh
    frame: StlMesh

    @classmethod
    def from_generated_design(cls) -> "StlSources":
        return cls(
            single_insert=StlMesh.from_file(DESIGN_DIR / f"{DESIGN_STEM}_single_insert.stl"),
            array_insert=StlMesh.from_file(DESIGN_DIR / f"{DESIGN_STEM}_wells_insert.stl"),
            frame=StlMesh.from_file(FRAME_STL),
        )


@dataclass(frozen=True)
class StlRenderSpec:
    mesh: StlMesh
    max_faces: int
    azimuth: float = -38.0
    elevation: float = 26.0
    z_scale: float = 1.0
    invert_z: bool = False
    edge_alpha: float = 0.18
    linewidth: float = 0.025
    base_color: str = COLORS["insert"]
    highlight_color: str = "#ffe0a0"
    edge_color: str = "#7a4308"


@dataclass(frozen=True)
class AxisBox:
    left: float
    bottom: float
    width: float
    height: float

    def mpl(self) -> list[float]:
        return [self.left, self.bottom, self.width, self.height]


@dataclass(frozen=True)
class FigureOneInsets:
    unit_dxf: AxisBox
    wafer_mask: AxisBox
    insert_single: AxisBox
    insert_array: AxisBox
    frame_stl: AxisBox
    device_photo: AxisBox


@dataclass(frozen=True)
class FigureOneLayout:
    figsize: tuple[float, float]
    grid_widths: tuple[float, float]
    grid_heights: tuple[float, float, float, float]
    column_gap: float
    row_gap: float
    insets: FigureOneInsets

    def gridspec_kwargs(self) -> dict[str, tuple[float, ...]]:
        return {
            "width_ratios": self.grid_widths,
            "height_ratios": self.grid_heights,
        }

    def subplot_adjust_kwargs(self) -> dict[str, float]:
        return {
            "left": 0.035,
            "right": 0.985,
            "bottom": 0.035,
            "top": 0.950,
            "wspace": self.column_gap,
            "hspace": self.row_gap,
        }


FIGURE_ONE_LAYOUT = FigureOneLayout(
    figsize=(9.25, 12.2),
    grid_widths=(1.0, 1.02),
    grid_heights=(1.78, 1.70, 2.70, 3.00),
    column_gap=0.025,
    row_gap=0.075,
    insets=FigureOneInsets(
        unit_dxf=AxisBox(0.025, 0.075, 0.950, 0.820),
        wafer_mask=AxisBox(0.020, 0.030, 0.960, 0.900),
        insert_single=AxisBox(0.035, 0.035, 0.455, 0.900),
        insert_array=AxisBox(0.510, 0.035, 0.455, 0.900),
        frame_stl=AxisBox(0.010, 0.030, 0.980, 0.900),
        device_photo=AxisBox(0.015, 0.035, 0.970, 0.895),
    ),
)


def add_inset(ax: plt.Axes, box: AxisBox) -> plt.Axes:
    inset = ax.inset_axes(box.mpl())
    inset.set_zorder(0)
    return inset


class TextRole(Enum):
    PANEL_BADGE = auto()
    PANEL_TITLE = auto()
    PRESET_TITLE = auto()
    MUTED_LEFT = auto()
    TABLE_KEY = auto()
    TABLE_VALUE = auto()
    NOTE = auto()
    OUTPUT_BOX = auto()
    BOX_NOTE = auto()
    CAPTION = auto()
    CHANNEL_LABEL = auto()
    TOP_LABEL = auto()
    LOCK_LABEL = auto()
    LEGEND = auto()
    SECTION_TITLE = auto()
    LOCK_VALUE = auto()
    LOCK_CAPTION = auto()
    SMALL_MUTED = auto()
    SMALL_LIGHT = auto()
    TAPER_LABEL = auto()
    RULE_NOTE = auto()
    PLATE_TITLE = auto()
    PLATE_CAPTION = auto()
    EXPORT_LABEL = auto()


class PatchRole(Enum):
    DEVICE_OUTLINE = auto()
    CHAMBER = auto()
    TOP_WELL = auto()
    LOCK_OUTLINE = auto()
    LOCK_HOLE = auto()
    INSERT_PIN = auto()
    INSERT_SIDE_PIN = auto()
    WAFER_SLAB = auto()
    WAFER_MASK = auto()
    WAFER_FLAT = auto()
    UNIT_CELL = auto()


TEXT_STYLES = {
    TextRole.PANEL_BADGE: TextStyle(
        11.5,
        "white",
        ha="left",
        va="top",
        fontweight="bold",
        bbox={"boxstyle": "round,pad=0.25", "facecolor": COLORS["ink"], "edgecolor": "none"},
        axes=True,
    ),
    TextRole.PANEL_TITLE: TextStyle(10.8, COLORS["ink"], ha="left", va="top", fontweight="bold", axes=True),
    TextRole.PRESET_TITLE: TextStyle(10.0, COLORS["ink"], ha="left", fontweight="bold"),
    TextRole.MUTED_LEFT: TextStyle(8.5, COLORS["muted"], ha="left"),
    TextRole.TABLE_KEY: TextStyle(7.7, COLORS["muted"], ha="left"),
    TextRole.TABLE_VALUE: TextStyle(7.9, COLORS["ink"], ha="right"),
    TextRole.NOTE: TextStyle(7.8, COLORS["ink"], ha="left", linespacing=1.25),
    TextRole.OUTPUT_BOX: TextStyle(9.0, COLORS["ink"]),
    TextRole.BOX_NOTE: TextStyle(8.8, COLORS["ink"]),
    TextRole.CAPTION: TextStyle(9.0, COLORS["muted"]),
    TextRole.CHANNEL_LABEL: TextStyle(
        8.2,
        COLORS["bottom"],
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.4},
    ),
    TextRole.TOP_LABEL: TextStyle(8.4, COLORS["top"]),
    TextRole.LOCK_LABEL: TextStyle(8.4, COLORS["lock"]),
    TextRole.LEGEND: TextStyle(8.2, COLORS["ink"], ha="left"),
    TextRole.SECTION_TITLE: TextStyle(9.0, COLORS["ink"], fontweight="bold"),
    TextRole.LOCK_VALUE: TextStyle(9.0, COLORS["ink"]),
    TextRole.LOCK_CAPTION: TextStyle(8.6, COLORS["lock"]),
    TextRole.SMALL_MUTED: TextStyle(8.2, COLORS["muted"]),
    TextRole.SMALL_LIGHT: TextStyle(8.1, "white"),
    TextRole.TAPER_LABEL: TextStyle(8.7, COLORS["ink"]),
    TextRole.RULE_NOTE: TextStyle(8.5, COLORS["ink"], ha="left"),
    TextRole.PLATE_TITLE: TextStyle(9.0, COLORS["ink"], fontweight="bold"),
    TextRole.PLATE_CAPTION: TextStyle(8.5, COLORS["muted"]),
    TextRole.EXPORT_LABEL: TextStyle(8.2, COLORS["muted"]),
}


PATCH_STYLES = {
    PatchRole.DEVICE_OUTLINE: PatchStyle("white", COLORS["grid"], 1.4),
    PatchRole.CHAMBER: PatchStyle("#caefe8", "none", 1.0, 0.85),
    PatchRole.TOP_WELL: PatchStyle("#caefe8", COLORS["top"], 2.0),
    PatchRole.LOCK_OUTLINE: PatchStyle("none", COLORS["lock"], 1.8),
    PatchRole.LOCK_HOLE: PatchStyle("#f5f1ff", COLORS["lock"], 2.2),
    PatchRole.INSERT_PIN: PatchStyle("#ffe2ae", COLORS["insert"], 2.0),
    PatchRole.INSERT_SIDE_PIN: PatchStyle("#ffe2ae", COLORS["insert"], 1.5),
    PatchRole.WAFER_SLAB: PatchStyle(COLORS["wafer"], "#bac5d2", 1.2),
    PatchRole.WAFER_MASK: PatchStyle(COLORS["wafer"], "#b8c4d1", 1.4),
    PatchRole.WAFER_FLAT: PatchStyle("white", "white"),
    PatchRole.UNIT_CELL: PatchStyle("white", COLORS["grid"], 0.55),
}


def add_text(ax: plt.Axes, x: float, y: float, label: str, style: TextRole) -> None:
    kwargs = TEXT_STYLES[style].kwargs(ax)
    if style is TextRole.PANEL_BADGE:
        kwargs["clip_on"] = False
        kwargs["zorder"] = 100
    ax.text(x, y, label, **kwargs)


def add_rect(ax: plt.Axes, xy: tuple[float, float], width: float, height: float, style: PatchRole) -> None:
    ax.add_patch(Rectangle(xy, width, height, **PATCH_STYLES[style].kwargs()))


def add_circle(ax: plt.Axes, center: tuple[float, float], radius: float, style: PatchRole) -> None:
    ax.add_patch(Circle(center, radius, **PATCH_STYLES[style].kwargs()))


def add_colored_rect(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    color: str,
    alpha: float = 1.0,
) -> None:
    ax.add_patch(Rectangle(xy, width, height, facecolor=color, edgecolor="none", alpha=alpha))


def add_colored_circle(
    ax: plt.Axes,
    center: tuple[float, float],
    radius: float,
    color: str,
) -> None:
    ax.add_patch(Circle(center, radius, facecolor=color, edgecolor="none"))


def line_segment(entity: object) -> tuple[tuple[float, float], tuple[float, float]]:
    if entity.dxftype() != "LINE":
        raise ValueError(f"Unsupported DXF entity type: {entity.dxftype()}")
    return (
        (float(entity.dxf.start.x), float(entity.dxf.start.y)),
        (float(entity.dxf.end.x), float(entity.dxf.end.y)),
    )


def transformed_segments(
    drawing: DxfDrawing,
    bounds: Bounds,
    frame: tuple[float, float, float, float],
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    frame_x, frame_y, frame_w, frame_h = frame
    scale = min(frame_w / bounds.width, frame_h / bounds.height)
    x_pad = (frame_w - bounds.width * scale) / 2
    y_pad = (frame_h - bounds.height * scale) / 2

    def transform(point: tuple[float, float]) -> tuple[float, float]:
        return (
            frame_x + x_pad + (point[0] - bounds.min_x) * scale,
            frame_y + y_pad + (point[1] - bounds.min_y) * scale,
        )

    return [(transform(start), transform(end)) for start, end in drawing.segments]


def draw_dxf_layer(
    ax: plt.Axes,
    drawing: DxfDrawing,
    bounds: Bounds,
    frame: tuple[float, float, float, float],
    color: str,
    linewidth: float,
    alpha: float,
) -> None:
    ax.add_collection(line_collection(transformed_segments(drawing, bounds, frame), color, linewidth, alpha))


def draw_dxf_layer_raw(
    ax: plt.Axes,
    drawing: DxfDrawing,
    color: str,
    linewidth: float,
    alpha: float,
) -> None:
    ax.add_collection(line_collection(drawing.segments, color, linewidth, alpha))


def line_collection(
    segments: object,
    color: str,
    linewidth: float,
    alpha: float,
) -> LineCollection:
    return LineCollection(segments, colors=color, linewidths=linewidth, alpha=alpha, capstyle="round")


def setup_raw_dxf_axis(ax: plt.Axes, bounds: Bounds, x_pad: float, y_pad: float) -> None:
    ax.set_xlim(bounds.min_x - x_pad, bounds.max_x + x_pad)
    ax.set_ylim(bounds.min_y - y_pad, bounds.max_y + y_pad)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")


def add_bounds_background(ax: plt.Axes, bounds: Bounds, x_pad: float, y_pad: float) -> None:
    ax.add_patch(
        Rectangle(
            (bounds.min_x - x_pad, bounds.min_y - y_pad),
            bounds.width + 2 * x_pad,
            bounds.height + 2 * y_pad,
            facecolor="white",
            edgecolor=COLORS["grid"],
            linewidth=0.9,
            zorder=0,
        )
    )


def setup_card_axis(ax: plt.Axes, width_units: float = 1.0) -> None:
    ax.set_xlim(0, width_units)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")


def add_axis_text(ax: plt.Axes, x: float, y: float, label: str, style: TextRole) -> None:
    kwargs = TEXT_STYLES[style].kwargs(ax)
    kwargs["transform"] = ax.transAxes
    ax.text(x, y, label, **kwargs)


def sampled_triangles(mesh: StlMesh, max_faces: int) -> np.ndarray:
    if len(mesh.triangles) <= max_faces:
        return mesh.triangles
    indices = np.linspace(0, len(mesh.triangles) - 1, max_faces, dtype=int)
    return mesh.triangles[indices]


def rotation_matrix(azimuth: float, elevation: float) -> np.ndarray:
    azimuth_rad = np.deg2rad(azimuth)
    elevation_rad = np.deg2rad(elevation)
    z_rotation = np.array(
        [
            [np.cos(azimuth_rad), -np.sin(azimuth_rad), 0.0],
            [np.sin(azimuth_rad), np.cos(azimuth_rad), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    x_rotation = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, np.cos(elevation_rad), -np.sin(elevation_rad)],
            [0.0, np.sin(elevation_rad), np.cos(elevation_rad)],
        ]
    )
    return z_rotation.T @ x_rotation.T


def triangle_normals(triangles: np.ndarray) -> np.ndarray:
    edges_a = triangles[:, 1] - triangles[:, 0]
    edges_b = triangles[:, 2] - triangles[:, 0]
    normals = np.cross(edges_a, edges_b)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    return normals / np.maximum(lengths, 1e-12)


def display_triangles(mesh: StlMesh, max_faces: int, z_scale: float, invert_z: bool) -> np.ndarray:
    triangles = sampled_triangles(mesh, max_faces)
    triangles = triangles.copy()
    if invert_z:
        z_min = triangles[:, :, 2].min()
        z_max = triangles[:, :, 2].max()
        triangles[:, :, 2] = z_min + z_max - triangles[:, :, 2]
    if z_scale != 1.0:
        z_min = triangles[:, :, 2].min()
        triangles[:, :, 2] = z_min + (triangles[:, :, 2] - z_min) * z_scale
    return triangles


def project_stl_triangles(
    mesh: StlMesh,
    max_faces: int,
    azimuth: float = -38.0,
    elevation: float = 26.0,
    z_scale: float = 1.0,
    invert_z: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    triangles = display_triangles(mesh, max_faces, z_scale, invert_z)
    points = triangles.reshape((-1, 3))
    centered = points - (points.min(axis=0) + points.max(axis=0)) / 2
    rotated = (centered @ rotation_matrix(azimuth, elevation)).reshape((-1, 3, 3))
    projected = rotated[:, :, :2]
    depth = rotated[:, :, 2].mean(axis=1)
    return projected, depth, triangle_normals(rotated)


def fit_polygons_to_frame(polygons: np.ndarray, frame: tuple[float, float, float, float]) -> np.ndarray:
    frame_x, frame_y, frame_w, frame_h = frame
    min_xy = polygons.reshape((-1, 2)).min(axis=0)
    max_xy = polygons.reshape((-1, 2)).max(axis=0)
    size = max_xy - min_xy
    scale = min(frame_w / size[0], frame_h / size[1])
    offset = np.array([frame_x, frame_y]) + (np.array([frame_w, frame_h]) - size * scale) / 2
    return (polygons - min_xy) * scale + offset


def project_stl_render(spec: StlRenderSpec) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return project_stl_triangles(
        spec.mesh,
        spec.max_faces,
        spec.azimuth,
        spec.elevation,
        spec.z_scale,
        spec.invert_z,
    )


def draw_stl_polygons(
    ax: plt.Axes,
    polygons: np.ndarray,
    depth: np.ndarray,
    normals: np.ndarray,
    spec: StlRenderSpec,
    zorder: float = 1.0,
) -> None:
    light = np.array([-0.35, -0.45, 0.82])
    light = light / np.linalg.norm(light)
    illumination = np.abs(normals @ light)
    normalized_depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-9)
    shade = np.clip(0.08 + 0.76 * illumination + 0.22 * normalized_depth, 0.0, 1.0)
    base = np.array(mcolors.to_rgb(spec.base_color))
    shadow = base * 0.48
    highlight = np.array(mcolors.to_rgb(spec.highlight_color))
    facecolors = [tuple(shadow * (1 - value) + highlight * value) + (1.0,) for value in shade]
    order = np.argsort(depth)[::-1]
    ax.add_collection(
        PolyCollection(
            polygons[order],
            facecolors=[facecolors[index] for index in order],
            edgecolors=[mcolors.to_rgba(spec.edge_color, spec.edge_alpha)],
            linewidths=spec.linewidth,
            alpha=1.0,
            zorder=zorder,
        )
    )


def draw_stl_mesh(
    ax: plt.Axes,
    spec: StlRenderSpec,
    frame: tuple[float, float, float, float],
) -> None:
    polygons, depth, normals = project_stl_render(spec)
    fitted = fit_polygons_to_frame(polygons, frame)
    draw_stl_polygons(ax, fitted, depth, normals, spec)


def draw_stl_mesh_raw_equal(ax: plt.Axes, spec: StlRenderSpec) -> None:
    polygons, depth, normals = project_stl_render(spec)
    bounds = Bounds.from_points(polygons.reshape((-1, 2)))
    x_pad = bounds.width * 0.08
    y_pad = bounds.height * 0.10
    ax.set_xlim(bounds.min_x - x_pad, bounds.max_x + x_pad)
    ax.set_ylim(bounds.min_y - y_pad, bounds.max_y + y_pad)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.add_patch(
        Rectangle(
            (bounds.min_x - x_pad, bounds.min_y - y_pad),
            bounds.width + 2 * x_pad,
            bounds.height + 2 * y_pad,
            facecolor=COLORS["dark_card"],
            edgecolor=COLORS["frame"],
            linewidth=1.1,
            zorder=0,
        )
    )
    draw_stl_polygons(ax, polygons, depth, normals, spec, zorder=2)


def panel_label(ax: plt.Axes, label: str, title: str) -> None:
    add_text(ax, 0.02, 0.96, label, TextRole.PANEL_BADGE)
    add_text(ax, 0.11, 0.956, title, TextRole.PANEL_TITLE)


def panel_badge(ax: plt.Axes, label: str) -> None:
    add_text(ax, 0.02, 0.96, label, TextRole.PANEL_BADGE)


def setup_axis(ax: plt.Axes) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def rounded_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    facecolor: str,
    edgecolor: str,
    linewidth: float = 1.2,
    radius: float = 0.03,
    alpha: float = 1.0,
) -> FancyBboxPatch:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle=f"round,pad=0.014,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        alpha=alpha,
    )
    ax.add_patch(box)
    return box


def add_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=1.6,
        color=color,
        shrinkA=4,
        shrinkB=4,
        connectionstyle="arc3,rad=0.0",
    )
    ax.add_patch(arrow)


def draw_parameter_panel(ax: plt.Axes, cfg: TwoCompartmentDeviceConfig) -> None:
    setup_axis(ax)
    panel_badge(ax, "A")

    rounded_box(ax, (0.055, 0.11), 0.52, 0.75, "white", COLORS["grid"], linewidth=1.0)
    add_text(ax, 0.08, 0.805, "OpenMFD preset", TextRole.PRESET_TITLE)
    add_text(ax, 0.08, 0.735, "editable defaults", TextRole.MUTED_LEFT)

    channels = cfg.channels_config()
    rows, columns = cfg.grid_size
    rows_text = f"{rows} x {columns} units"
    values = [
        ("unit pitch", f"{cfg.casing_x:.0f} x {cfg.casing_y:.0f} mm"),
        ("array", f"{rows_text}; {rows * columns * 2} wells"),
        ("well radius", f"{cfg.well_radius:.2f} mm"),
        ("microchannels", f"{channels.num_channels} at {channels.width * 1000:.0f} um"),
        ("pin / hole", f"{cfg.insert_pin_dims[0]:.2f} / {cfg.insert_hole_dims[0]:.2f} mm"),
        ("outer taper", f"{cfg.outer_taper_degrees:.0f} deg, {cfg.insert_height:.1f} mm tall"),
        ("PDMS scale", f"x{cfg.pdms_config().scale_factor():.4f} at {cfg.cure_temp} deg C"),
    ]
    y = 0.650
    for name, value in values:
        add_text(ax, 0.085, y, name, TextRole.TABLE_KEY)
        add_text(ax, 0.555, y, value, TextRole.TABLE_VALUE)
        ax.plot([0.08, 0.555], [y - 0.034, y - 0.034], color="#edf1f6", lw=0.8)
        y -= 0.064

    add_text(
        ax,
        0.08,
        0.155,
        "Demonstrated-device defaults;\neditable, not fixed constants.",
        TextRole.NOTE,
    )

    outputs = [
        ((0.68, 0.705), "matched\nphotomask DXFs", COLORS["bottom"]),
        ((0.68, 0.550), "printed\ninsert STLs", COLORS["insert"]),
        ((0.68, 0.395), "printed\nframe STL", COLORS["frame"]),
        ((0.68, 0.240), "wafer-scale\nmask CAD", COLORS["top"]),
    ]
    for (x, y_out), label, color in outputs:
        rounded_box(ax, (x, y_out), 0.25, 0.105, "white", color, linewidth=1.6)
        add_text(ax, x + 0.125, y_out + 0.053, label, TextRole.OUTPUT_BOX)
        add_arrow(ax, (0.585, 0.49), (x, y_out + 0.053), color)

    rounded_box(ax, (0.65, 0.10), 0.31, 0.12, "#fff8ea", "#f2c46d", linewidth=1.0)
    add_text(ax, 0.805, 0.16, "same coordinates\nfor every output", TextRole.BOX_NOTE)


def draw_unit_geometry(ax: plt.Axes, _cfg: TwoCompartmentDeviceConfig, dxf: DxfSources) -> None:
    setup_axis(ax)
    panel_badge(ax, "B")

    bounds = Bounds.combine((dxf.single_top, dxf.single_bottom))
    pad_x = 0.55
    pad_y = 0.45
    drawing_ax = add_inset(ax, FIGURE_ONE_LAYOUT.insets.unit_dxf)
    setup_raw_dxf_axis(drawing_ax, bounds, pad_x, pad_y)
    add_bounds_background(drawing_ax, bounds, pad_x, pad_y)
    draw_dxf_layer_raw(drawing_ax, dxf.single_bottom, COLORS["bottom"], 0.10, 0.55)
    draw_dxf_layer_raw(drawing_ax, dxf.single_top, COLORS["top"], 1.15, 0.92)


def draw_insert_stls(
    ax: plt.Axes,
    _cfg: TwoCompartmentDeviceConfig,
    stl: StlSources,
    label: str = "A",
    _title: str = "Generated insert STLs",
) -> None:
    setup_axis(ax)
    panel_badge(ax, label)

    single_ax = add_inset(ax, FIGURE_ONE_LAYOUT.insets.insert_single)
    array_ax = add_inset(ax, FIGURE_ONE_LAYOUT.insets.insert_array)
    draw_stl_mesh_raw_equal(
        single_ax,
        StlRenderSpec(
            stl.single_insert,
            5000,
            azimuth=-44.0,
            elevation=24.0,
            z_scale=STL_DISPLAY_Z_SCALE,
            edge_alpha=0.28,
            linewidth=0.026,
            base_color="#d8871f",
            highlight_color="#ffe2a3",
            edge_color="#593100",
        ),
    )
    draw_stl_mesh_raw_equal(
        array_ax,
        StlRenderSpec(
            stl.array_insert,
            100000,
            azimuth=-48.0,
            elevation=28.0,
            z_scale=STL_DISPLAY_Z_SCALE,
            edge_alpha=0.58,
            linewidth=0.013,
            base_color="#d8871f",
            highlight_color="#ffe2a3",
            edge_color="#593100",
        ),
    )


def draw_frame_cad(ax: plt.Axes, stl: StlSources) -> None:
    setup_axis(ax)
    panel_badge(ax, "E")

    card_ax = add_inset(ax, FIGURE_ONE_LAYOUT.insets.frame_stl)
    draw_stl_mesh_raw_equal(
        card_ax,
        StlRenderSpec(
            stl.frame,
            18000,
            azimuth=-36.0,
            elevation=25.0,
            z_scale=1.45,
            edge_alpha=0.52,
            linewidth=0.024,
            base_color="#485466",
            highlight_color="#d3d9e2",
            edge_color="#070b12",
        ),
    )

def crop_to_aspect(image: Image.Image, aspect: float) -> Image.Image:
    width, height = image.size
    current = width / height
    if current > aspect:
        new_width = int(height * aspect)
        left = (width - new_width) // 2
        return image.crop((left, 0, left + new_width, height))
    new_height = int(width / aspect)
    top = max(0, (height - new_height) // 2)
    return image.crop((0, top, width, top + new_height))


def read_assembled_device_photo() -> Image.Image:
    with ZipFile(WORKFLOW_ODP) as archive:
        image = Image.open(BytesIO(archive.read(WORKFLOW_ASSEMBLED_PHOTO))).convert("RGB")
    return ImageOps.autocontrast(image, cutoff=1)


def draw_assembled_device(ax: plt.Axes) -> None:
    setup_axis(ax)
    panel_badge(ax, "F")

    image_ax = add_inset(ax, FIGURE_ONE_LAYOUT.insets.device_photo)
    image = read_assembled_device_photo()
    image_ax.imshow(image)
    image_ax.set_aspect("equal", adjustable="box")
    image_ax.axis("off")
    image_ax.add_patch(
        Rectangle(
            (0, 0),
            image.size[0] - 1,
            image.size[1] - 1,
            facecolor="none",
            edgecolor=COLORS["grid"],
            linewidth=0.8,
        )
    )

def draw_plate_outputs(ax: plt.Axes, _cfg: TwoCompartmentDeviceConfig, dxf: DxfSources) -> None:
    setup_axis(ax)
    panel_badge(ax, "C")

    pad_x = dxf.aligned.bounds.width * 0.035
    pad_y = dxf.aligned.bounds.height * 0.035
    mask_ax = add_inset(ax, FIGURE_ONE_LAYOUT.insets.wafer_mask)
    setup_raw_dxf_axis(mask_ax, dxf.aligned.bounds, pad_x, pad_y)
    add_bounds_background(mask_ax, dxf.aligned.bounds, pad_x, pad_y)
    draw_dxf_layer_raw(mask_ax, dxf.aligned, "#bfe7ee", 0.48, 0.42)
    draw_dxf_layer_raw(mask_ax, dxf.aligned, "#0f8ea5", 0.24, 0.92)


def save_subfigure_images(fig: plt.Figure, axes: dict[str, plt.Axes]) -> None:
    subfigure_dir = OUTPUT_DIR / "subfigures"
    subfigure_dir.mkdir(parents=True, exist_ok=True)
    for path in subfigure_dir.glob("*.png"):
        path.unlink()

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for label, ax in axes.items():
        bbox = ax.get_tightbbox(renderer).expanded(1.03, 1.05)
        bbox_inches = bbox.transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(subfigure_dir / f"{label}.png", dpi=SUBFIGURE_DPI, bbox_inches=bbox_inches, pad_inches=0.02)


def build_figure() -> tuple[plt.Figure, dict[str, plt.Axes]]:
    cfg = TwoCompartmentDeviceConfig()
    dxf = DxfSources.from_generated_design()
    stl = StlSources.from_generated_design()

    fig = plt.figure(figsize=FIGURE_ONE_LAYOUT.figsize)
    grid = fig.add_gridspec(
        4,
        2,
        **FIGURE_ONE_LAYOUT.gridspec_kwargs(),
    )
    fig.patch.set_facecolor("white")
    axes = {
        "A": fig.add_subplot(grid[0, 0]),
        "B": fig.add_subplot(grid[1, 0]),
        "C": fig.add_subplot(grid[0:2, 1]),
        "D": fig.add_subplot(grid[2, :]),
        "E": fig.add_subplot(grid[3, 0]),
        "F": fig.add_subplot(grid[3, 1]),
    }
    for ax in axes.values():
        ax.set_facecolor(COLORS["paper"])

    draw_parameter_panel(axes["A"], cfg)
    draw_unit_geometry(axes["B"], cfg, dxf)
    draw_plate_outputs(axes["C"], cfg, dxf)
    draw_insert_stls(axes["D"], cfg, stl, "D", "Generated insert STLs")
    draw_frame_cad(axes["E"], stl)
    draw_assembled_device(axes["F"])

    fig.suptitle(
        "OpenMFD turns one parameterized design into masks, printed parts, and a packaged device",
        fontsize=12.0,
        fontweight="bold",
        color=COLORS["ink"],
        y=0.982,
    )
    fig.subplots_adjust(**FIGURE_ONE_LAYOUT.subplot_adjust_kwargs())
    return fig, axes


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = build_figure()
    fig.savefig(OUTPUT_DIR / "draft_figure.pdf", bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "draft_figure.png", dpi=300, bbox_inches="tight")
    save_subfigure_images(fig, axes)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
