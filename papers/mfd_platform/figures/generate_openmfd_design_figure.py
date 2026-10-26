#!/usr/bin/env python3

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import ezdxf
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.collections import PolyCollection
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.text import Text
from matplotlib.transforms import Transform
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[3]
FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig1_openmfd_design"
SUBFIGURE_DPI = 600
DESIGN_DIR = ROOT / "designs" / "open_chamber" / "2_compartment_96_well_300um_suex200_v27"
DESIGN_STEM = "2_compartment_96_well_300um_suex200_v27"
FRAME_STL = ROOT / "plates" / "96_well_plate_reservoirs_print_hips_2" / "96_well_plate_reservoirs_print_hips_2.stl"
ASSEMBLED_DEVICE_PHOTO = OUTPUT_DIR / "assembled_device_photo.png"
STL_DISPLAY_Z_SCALE = 1.0
PANEL_BACKGROUND = "#e9eef3"

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


class TextStyle:
    """Point-sized text drawn by its style, at the manuscript figure width."""

    fontsize = 8.5
    color = COLORS["ink"]
    ha = "center"
    va = "center"
    fontweight = "normal"
    linespacing = 1.25
    zorder = 3

    @classmethod
    def transform(cls, ax: plt.Axes) -> Transform:
        return ax.transData

    @classmethod
    def background(cls) -> dict[str, object] | None:
        return None

    @classmethod
    def draw(cls, ax: plt.Axes, x: float, y: float, label: str, *, rotation: float = 0.0) -> Text:
        return ax.text(
            x, y, label,
            fontsize=cls.fontsize, color=cls.color,
            ha=cls.ha, va=cls.va, fontweight=cls.fontweight,
            linespacing=cls.linespacing, bbox=cls.background(),
            transform=cls.transform(ax), rotation=rotation,
            clip_on=False, zorder=cls.zorder,
        )


class AxesText(TextStyle):
    @classmethod
    def transform(cls, ax: plt.Axes) -> Transform:
        return ax.transAxes


class LeftText(TextStyle):
    ha = "left"


class RightText(TextStyle):
    ha = "right"


class MutedText(TextStyle):
    color = COLORS["muted"]


class LeftMutedText(MutedText, LeftText):
    pass


class HeadingText(TextStyle):
    fontsize = 10.5
    fontweight = "bold"


class PresetTitle(HeadingText, LeftText):
    pass


class LargeText(TextStyle):
    fontsize = 10.0


class PresetLabel(LargeText, LeftText):
    pass


class PresetValue(LargeText, RightText):
    pass


class ParameterTitle(PresetTitle):
    fontsize = 9.5


class ParameterText(TextStyle):
    fontsize = 8.0


class ParameterLabel(ParameterText, LeftText):
    pass


class ParameterValue(ParameterText, RightText):
    pass


class PanelTitle(PresetTitle, AxesText):
    va = "bottom"


class PanelBadge(PanelTitle):
    zorder = 100


class BackedText(TextStyle):
    @classmethod
    def background(cls) -> dict[str, object]:
        return {"boxstyle": "round,pad=0.10", "facecolor": "white", "edgecolor": "none", "alpha": 0.92}


class InsetBadge(PanelBadge, BackedText):
    va = "top"


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

    @property
    def center_x(self) -> float:
        return self.left + self.width / 2

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
    grid_widths: tuple[float, ...]
    grid_heights: tuple[float, ...]
    column_gap: float
    row_gap: float
    cell_padding_inches: float
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
            "top": 0.985,
            "wspace": self.column_gap,
            "hspace": self.row_gap,
        }


FIGURE_ONE_LAYOUT = FigureOneLayout(
    figsize=(6.5, 5.8),
    grid_widths=(1.0, 1.0, 1.0),
    grid_heights=(1.65, 1.35, 1.55),
    column_gap=0.08,
    row_gap=0.08,
    cell_padding_inches=0.04,
    insets=FigureOneInsets(
        unit_dxf=AxisBox(0.035, 0.040, 0.930, 0.850),
        wafer_mask=AxisBox(0.055, 0.025, 0.890, 0.900),
        insert_single=AxisBox(0.040, 0.035, 0.920, 0.880),
        insert_array=AxisBox(0.040, 0.035, 0.920, 0.880),
        frame_stl=AxisBox(0.035, 0.025, 0.930, 0.900),
        device_photo=AxisBox(0.035, 0.025, 0.930, 0.900),
    ),
)


def add_inset(ax: plt.Axes, box: AxisBox) -> plt.Axes:
    inset = ax.inset_axes(box.mpl())
    inset.set_zorder(0)
    return inset


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
    radius_inches: float = 0.025,
    alpha: float = 1.0,
) -> FancyBboxPatch:
    position = ax.get_position()
    width_inches = position.width * ax.figure.get_figwidth()
    height_inches = position.height * ax.figure.get_figheight()
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle=f"round,pad=0,rounding_size={radius_inches / width_inches}",
        mutation_aspect=width_inches / height_inches,
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
    InsetBadge.draw(ax, 0.02, 0.96, "A")

    input_left, input_width = 0.055, 0.52
    rounded_box(ax, (input_left, 0.11), input_width, 0.75,
                "white", COLORS["grid"], linewidth=1.0)
    ParameterTitle.draw(ax, input_left + 0.025, 0.82, "Inputs to OpenMFD")
    ParameterLabel.draw(ax, input_left + 0.025, 0.74, "Neuronal plate layout")

    channels = cfg.channels_config()
    rows, columns = cfg.grid_size
    rows_text = f"{rows} × {columns} units"
    values = [
        ("Device spacing", f"{cfg.casing_x:.0f} × {cfg.casing_y:.0f} mm"),
        ("Array", f"{rows_text}; {rows * columns * 2} wells"),
        ("Well radius", f"{cfg.well_radius:.2f} mm"),
        ("Microchannels", f"{channels.num_channels} at {channels.width * 1000:.0f} µm"),
        ("Pin / hole", f"{cfg.insert_pin_dims[0]:.2f} / {cfg.insert_hole_dims[0]:.2f} mm"),
        ("Sidewall taper", f"{cfg.outer_taper_degrees:.0f}°; {cfg.insert_height:.1f} mm tall"),
        ("PDMS shrinkage scale", f"×{cfg.pdms_config().scale_factor():.4f} at {cfg.cure_temp}°C"),
    ]
    label_x = input_left + 0.03
    value_x = input_left + input_width - 0.02
    y = 0.650
    for name, value in values:
        ParameterLabel.draw(ax, label_x, y, name)
        ParameterValue.draw(ax, value_x, y, value)
        ax.plot([label_x, value_x], [y - 0.034, y - 0.034], color="#edf1f6", lw=0.8)
        y -= 0.064

    output_left, output_width, output_height = 0.655, 0.30, 0.12
    outputs = (
        (0.650, "Photomasks: DXF (B, C)", COLORS["bottom"]),
        (0.425, "Well inserts: STL (D, E)", COLORS["insert"]),
        (0.200, "Plate frame: STL (F)", COLORS["frame"]),
    )
    for y_out, label, color in outputs:
        rounded_box(ax, (output_left, y_out), output_width, output_height,
                    "white", color, linewidth=1.6)
        LargeText.draw(ax, output_left + output_width / 2,
                       y_out + output_height / 2, label)
        add_arrow(ax, (input_left + input_width + 0.01, 0.49),
                  (output_left, y_out + output_height / 2), color)



def draw_unit_geometry(ax: plt.Axes, _cfg: TwoCompartmentDeviceConfig, dxf: DxfSources) -> None:
    setup_axis(ax)
    InsetBadge.draw(ax, 0.02, 0.96, "B")

    bounds = Bounds.combine((dxf.single_top, dxf.single_bottom))
    pad_x = 0.55
    pad_y = 0.45
    drawing_ax = add_inset(ax, FIGURE_ONE_LAYOUT.insets.unit_dxf)
    setup_raw_dxf_axis(drawing_ax, bounds, pad_x, pad_y)
    add_bounds_background(drawing_ax, bounds, pad_x, pad_y)
    draw_dxf_layer_raw(drawing_ax, dxf.single_bottom, COLORS["bottom"], 0.10, 0.55)
    draw_dxf_layer_raw(drawing_ax, dxf.single_top, COLORS["top"], 1.15, 0.92)


def draw_insert_view(
    ax: plt.Axes,
    spec: StlRenderSpec,
    inset: AxisBox,
    *,
    label: str,
) -> None:
    setup_axis(ax)
    InsetBadge.draw(ax, 0.02, 0.96, label)
    draw_stl_mesh_raw_equal(add_inset(ax, inset), spec)


def draw_single_insert(ax: plt.Axes, stl: StlSources) -> None:
    draw_insert_view(
        ax,
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
        FIGURE_ONE_LAYOUT.insets.insert_single,
        label="D",
    )


def draw_insert_array(ax: plt.Axes, stl: StlSources) -> None:
    draw_insert_view(
        ax,
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
        FIGURE_ONE_LAYOUT.insets.insert_array,
        label="E",
    )


def draw_frame_cad(ax: plt.Axes, stl: StlSources) -> None:
    setup_axis(ax)
    InsetBadge.draw(ax, 0.02, 0.96, "F")

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


@dataclass(frozen=True)
class Photo:
    path: Path

    def read(self) -> Image.Image:
        with Image.open(self.path) as source:
            return self.process(source.convert("RGB"))

    def process(self, image: Image.Image) -> Image.Image:
        return image


class ContrastPhoto(Photo):
    def process(self, image: Image.Image) -> Image.Image:
        return ImageOps.autocontrast(super().process(image), cutoff=1)


@dataclass(frozen=True)
class CroppedPhoto(Photo):
    aspect: float

    def process(self, image: Image.Image) -> Image.Image:
        return crop_to_aspect(super().process(image), self.aspect)


@dataclass(frozen=True)
class CroppedContrastPhoto(ContrastPhoto, CroppedPhoto):
    """Keep the authoring policy: crop first, then 1% autocontrast."""


def draw_assembled_device(ax: plt.Axes) -> None:
    setup_axis(ax)
    InsetBadge.draw(ax, 0.02, 0.96, "G")

    image_ax = add_inset(ax, FIGURE_ONE_LAYOUT.insets.device_photo)
    image = ContrastPhoto(ASSEMBLED_DEVICE_PHOTO).read()
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
    InsetBadge.draw(ax, 0.02, 0.96, "C")

    pad_x = dxf.aligned.bounds.width * 0.035
    pad_y = dxf.aligned.bounds.height * 0.035
    mask_ax = add_inset(ax, FIGURE_ONE_LAYOUT.insets.wafer_mask)
    setup_raw_dxf_axis(mask_ax, dxf.aligned.bounds, pad_x, pad_y)
    add_bounds_background(mask_ax, dxf.aligned.bounds, pad_x, pad_y)
    draw_dxf_layer_raw(mask_ax, dxf.aligned, "#bfe7ee", 0.48, 0.42)
    draw_dxf_layer_raw(mask_ax, dxf.aligned, "#0f8ea5", 0.24, 0.92)


def save_subfigure_images(
    fig: plt.Figure,
    panels: dict[str, plt.Axes],
    output_dir: Path,
) -> None:
    """Export declared panel axes and restore their visibility afterward."""
    subfigure_dir = output_dir / "subfigures"
    subfigure_dir.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    visibility = {ax: ax.get_visible() for ax in panels.values()}
    try:
        for label, ax in panels.items():
            for panel in panels.values():
                panel.set_visible(panel is ax and visibility[panel])
            bbox = ax.get_tightbbox(renderer).expanded(1.03, 1.05)
            bbox_inches = bbox.transformed(fig.dpi_scale_trans.inverted())
            fig.savefig(subfigure_dir / f"{label}.png", dpi=SUBFIGURE_DPI,
                        bbox_inches=bbox_inches, pad_inches=0.02)
    finally:
        for ax, visible in visibility.items():
            ax.set_visible(visible)


def build_figure() -> tuple[plt.Figure, dict[str, plt.Axes]]:
    cfg = TwoCompartmentDeviceConfig()
    dxf = DxfSources.from_generated_design()
    stl = StlSources.from_generated_design()

    fig = plt.figure(figsize=FIGURE_ONE_LAYOUT.figsize)
    grid = fig.add_gridspec(
        3,
        3,
        **FIGURE_ONE_LAYOUT.gridspec_kwargs(),
    )
    fig.patch.set_facecolor("white")
    a_ax = fig.add_subplot(grid[0, :])
    b_ax = fig.add_subplot(grid[1, 0])
    c_ax = fig.add_subplot(grid[1, 1])
    d_single_ax = fig.add_subplot(grid[1, 2])
    d_array_ax = fig.add_subplot(grid[2, 0])
    e_ax = fig.add_subplot(grid[2, 1])
    f_ax = fig.add_subplot(grid[2, 2])
    all_axes = (a_ax, b_ax, c_ax, d_single_ax, d_array_ax, e_ax, f_ax)
    panels = {
        "A": a_ax,
        "B": b_ax,
        "C": c_ax,
        "D": d_single_ax,
        "E": d_array_ax,
        "F": e_ax,
        "G": f_ax,
    }
    for ax in all_axes:
        ax.set_facecolor("none")

    fig.subplots_adjust(**FIGURE_ONE_LAYOUT.subplot_adjust_kwargs())
    pad_x = FIGURE_ONE_LAYOUT.cell_padding_inches / fig.get_figwidth()
    pad_y = FIGURE_ONE_LAYOUT.cell_padding_inches / fig.get_figheight()
    background_groups = (
        (PANEL_BACKGROUND, 1.0, (a_ax, f_ax)),
        (COLORS["bottom"], 0.07, (b_ax, c_ax)),
        (COLORS["insert"], 0.07, (d_single_ax, d_array_ax)),
        (COLORS["frame"], 0.07, (e_ax,)),
    )
    for color, opacity, members in background_groups:
        for ax in members:
            bounds = ax.get_position()
            fig.add_artist(Rectangle(
                (bounds.x0 - pad_x, bounds.y0 - pad_y),
                bounds.width + 2 * pad_x,
                bounds.height + 2 * pad_y,
                transform=fig.transFigure,
                facecolor=color,
                alpha=opacity,
                edgecolor="none",
                clip_on=False,
                zorder=-10,
            ))

    draw_parameter_panel(a_ax, cfg)
    draw_unit_geometry(b_ax, cfg, dxf)
    draw_plate_outputs(c_ax, cfg, dxf)
    draw_single_insert(d_single_ax, stl)
    draw_insert_array(d_array_ax, stl)
    draw_frame_cad(e_ax, stl)
    draw_assembled_device(f_ax)

    return fig, panels


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = build_figure()
    fig.savefig(OUTPUT_DIR / "draft_figure.pdf", dpi=SUBFIGURE_DPI, bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "draft_figure.png", dpi=300, bbox_inches="tight")
    save_subfigure_images(fig, axes, OUTPUT_DIR)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
