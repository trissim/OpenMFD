#!/usr/bin/env python3

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from openmfd.devices import PDMSConfiguration

from generate_openmfd_design_figure import (
    AxisBox,
    Bounds,
    COLORS,
    DxfDrawing,
    StlMesh,
    StlRenderSpec,
    TextRole,
    add_arrow,
    add_bounds_background,
    add_inset,
    add_text,
    draw_dxf_layer_raw,
    draw_stl_mesh_raw_equal,
    panel_badge,
    rounded_box,
    setup_axis,
    setup_raw_dxf_axis,
)

ROOT = Path(__file__).resolve().parents[3]
FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig6_generalizability"

CURE_TEMP = 100
PDMS_SCALE = PDMSConfiguration(cure_temp=CURE_TEMP).scale_factor()
PIN_INSET = -0.5
PIN_DIMS = (1.85, 1.85)
PIN_HEIGHT = 0.14
PIN_INNER_HEIGHT = 2.0
SKIRT_HEIGHT = 0.70
INSERT_HEIGHT = 3.8
DIAMOND_PIN_ROTATION = 45.0
WALL_THICKNESS = 7.0
WALL_PAD = 9.0


@dataclass(frozen=True)
class GeneralizabilityDesign:
    label: str
    title: str
    stem: str
    design_dir: Path
    dims: tuple[float, float, float]
    grid_size: tuple[int, int]
    pin_positions: tuple[tuple[float, float], ...]
    pin_rotation: float
    summary_rows: tuple[tuple[str, str], ...]
    layout_note: str
    single_top: DxfDrawing
    single_bottom: DxfDrawing
    aligned: DxfDrawing
    single_insert: StlMesh

    @classmethod
    def from_assets(
        cls,
        *,
        label: str,
        title: str,
        stem: str,
        design_dir: Path,
        dims: tuple[float, float, float],
        grid_size: tuple[int, int],
        pin_positions: tuple[tuple[float, float], ...],
        pin_rotation: float,
        summary_rows: tuple[tuple[str, str], ...],
        layout_note: str,
    ) -> "GeneralizabilityDesign":
        return cls(
            label=label,
            title=title,
            stem=stem,
            design_dir=design_dir,
            dims=dims,
            grid_size=grid_size,
            pin_positions=pin_positions,
            pin_rotation=pin_rotation,
            summary_rows=summary_rows,
            layout_note=layout_note,
            single_top=DxfDrawing.from_file(design_dir / f"{stem}_single_top.dxf"),
            single_bottom=DxfDrawing.from_file(design_dir / f"{stem}_single_bottom.dxf"),
            aligned=DxfDrawing.from_file(design_dir / f"{stem}_aligned.dxf"),
            single_insert=StlMesh.from_file(design_dir / f"{stem}_single_insert.stl"),
        )


def make_designs() -> tuple[GeneralizabilityDesign, GeneralizabilityDesign]:
    base = ROOT / "designs" / "open_chamber" / "openmfd_legacy_ports"
    unit_dims = (18.0, 18.0, 0.0)
    grid_size = (6, 4)
    diamond_well = 6.36 / math.sqrt(2.0)
    diamond_pins = tuple(
        inset_toward_origin(position)
        for position in (
            (-diamond_well, -diamond_well),
            (diamond_well, -diamond_well),
            (-diamond_well, diamond_well),
            (diamond_well, diamond_well),
        )
    )
    myelination = GeneralizabilityDesign.from_assets(
        label="A",
        title="Myelination assay",
        stem="myelination",
        design_dir=base / "myelination",
        dims=unit_dims,
        grid_size=grid_size,
        pin_positions=diamond_pins,
        pin_rotation=DIAMOND_PIN_ROTATION,
        summary_rows=(
            ("unit pitch", "18 x 18 mm"),
            ("array", "6 x 4 units"),
            ("well radius", "3.47 mm"),
            ("microchannels", "173 at 10 um"),
            ("pin / hole", "1.85 / 2.00 mm"),
            ("outer taper", "16 deg, 3.8 mm tall"),
            ("PDMS scale", f"x{PDMS_SCALE:.4f}"),
        ),
        layout_note="legacy open-chamber build with an oligo branch and the same pin/skirt system as Fig. 1",
    )
    axon_guidance = GeneralizabilityDesign.from_assets(
        label="D",
        title="Axon guidance assay",
        stem="axon_guidance",
        design_dir=base / "axon_guidance",
        dims=unit_dims,
        grid_size=grid_size,
        pin_positions=diamond_pins,
        pin_rotation=DIAMOND_PIN_ROTATION,
        summary_rows=(
            ("unit pitch", "18 x 18 mm"),
            ("array", "6 x 4 units"),
            ("well radius", "3.47 mm"),
            ("microchannels", "115 at 10 um"),
            ("pin / hole", "1.85 / 2.00 mm"),
            ("outer taper", "16 deg, 3.8 mm tall"),
            ("PDMS scale", f"x{PDMS_SCALE:.4f}"),
        ),
        layout_note="legacy open-chamber build with symmetric crossing gradient arms and the same pin/skirt system as Fig. 1",
    )
    return myelination, axon_guidance


def point_key(point: tuple[float, float]) -> tuple[float, float]:
    return (round(point[0], 4), round(point[1], 4))


def inset_toward_origin(position: tuple[float, float]) -> tuple[float, float]:
    x, y = position
    radius = math.hypot(x, y)
    if radius == 0.0:
        return position
    adjusted_radius = radius + PIN_INSET
    if adjusted_radius <= 0.0:
        raise ValueError(f"pin inset {PIN_INSET} collapses position {position}")
    scale = adjusted_radius / radius
    return (x * scale, y * scale)


def polygon_area(points: np.ndarray) -> float:
    x = points[:, 0]
    y = points[:, 1]
    return float(0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def closed_dxf_loops(drawing: DxfDrawing) -> list[np.ndarray]:
    """Recover the closed loops emitted by OpenSCAD's DXF exporter."""
    loops: list[np.ndarray] = []
    current: list[tuple[float, float]] = []
    start: tuple[float, float] | None = None
    last: tuple[float, float] | None = None

    for segment_start, segment_end in drawing.segments:
        if not current:
            current = [segment_start, segment_end]
            start = point_key(segment_start)
            last = point_key(segment_end)
        elif point_key(segment_start) == last:
            current.append(segment_end)
            last = point_key(segment_end)
        elif point_key(segment_end) == last:
            current.append(segment_start)
            last = point_key(segment_start)
        else:
            if len(current) >= 3:
                loops.append(np.array(current, dtype=float))
            current = [segment_start, segment_end]
            start = point_key(segment_start)
            last = point_key(segment_end)

        if len(current) > 3 and last == start:
            loops.append(np.array(current[:-1], dtype=float))
            current = []
            start = None
            last = None

    if len(current) >= 3:
        loops.append(np.array(current, dtype=float))
    return loops


def scale_about_center(points: np.ndarray, factor: float) -> np.ndarray:
    center = points.mean(axis=0)
    return center + (points - center) * factor


def prism_from_polygon(
    polygon: np.ndarray,
    *,
    z0: float,
    z1: float,
    taper: float = 0.0,
) -> np.ndarray:
    if len(polygon) < 3:
        return np.empty((0, 3, 3), dtype=float)

    points = polygon[:-1] if np.allclose(polygon[0], polygon[-1]) else polygon
    if polygon_area(points) < 0:
        points = points[::-1]

    bottom_xy = scale_about_center(points, 1.0 + taper)
    bottom = np.column_stack((bottom_xy, np.full(len(points), z0)))
    top = np.column_stack((points, np.full(len(points), z1)))

    triangles: list[np.ndarray] = []
    for idx in range(1, len(points) - 1):
        triangles.append(np.array([top[0], top[idx], top[idx + 1]], dtype=float))
        triangles.append(np.array([bottom[0], bottom[idx + 1], bottom[idx]], dtype=float))

    for idx in range(len(points)):
        nxt = (idx + 1) % len(points)
        triangles.append(np.array([bottom[idx], bottom[nxt], top[nxt]], dtype=float))
        triangles.append(np.array([bottom[idx], top[nxt], top[idx]], dtype=float))

    return np.array(triangles, dtype=float)


def rotated_square(
    center: tuple[float, float],
    dims: tuple[float, float],
    rotation: float,
) -> np.ndarray:
    half_x = dims[0] / 2.0
    half_y = dims[1] / 2.0
    points = np.array(
        [
            [-half_x, -half_y],
            [half_x, -half_y],
            [half_x, half_y],
            [-half_x, half_y],
        ],
        dtype=float,
    )
    radians = math.radians(rotation)
    matrix = np.array(
        [
            [math.cos(radians), -math.sin(radians)],
            [math.sin(radians), math.cos(radians)],
        ]
    )
    return points @ matrix.T + np.array(center, dtype=float)


def translated_prisms(
    loops: list[np.ndarray],
    offset: tuple[float, float],
    *,
    z0: float,
    z1: float,
    taper: float,
) -> list[np.ndarray]:
    offset_array = np.array(offset, dtype=float)
    return [prism_from_polygon(loop + offset_array, z0=z0, z1=z1, taper=taper) for loop in loops]


def unit_offsets(design: GeneralizabilityDesign, *, array: bool) -> list[tuple[float, float]]:
    rows, cols = design.grid_size if array else (1, 1)
    offsets: list[tuple[float, float]] = []
    for col in range(cols):
        for row in range(rows):
            offsets.append(
                (
                    row * design.dims[0] + design.dims[0] / 2.0,
                    col * design.dims[1] + design.dims[1] / 2.0,
                )
            )
    return offsets


def insert_preview_mesh(design: GeneralizabilityDesign, *, array: bool) -> StlMesh:
    if not array:
        return design.single_insert

    base_offset = np.array(unit_offsets(design, array=False)[0], dtype=float)
    triangles: list[np.ndarray] = []
    for offset in unit_offsets(design, array=True):
        delta = (np.array(offset, dtype=float) - base_offset) * PDMS_SCALE
        translated = design.single_insert.triangles.copy()
        translated[:, :, :2] += delta
        triangles.append(translated)
    return StlMesh(np.concatenate(triangles, axis=0))


def frame_preview_mesh(design: GeneralizabilityDesign) -> StlMesh:
    width = design.grid_size[0] * design.dims[0] + WALL_PAD * 2.0
    height = design.grid_size[1] * design.dims[1] + WALL_PAD * 2.0
    center_x = design.grid_size[0] * design.dims[0] / 2.0
    center_y = design.grid_size[1] * design.dims[1] / 2.0
    x0 = center_x - width / 2.0
    x1 = center_x + width / 2.0
    y0 = center_y - height / 2.0
    y1 = center_y + height / 2.0
    t = WALL_THICKNESS
    bars = (
        np.array([(x0, y0), (x1, y0), (x1, y0 + t), (x0, y0 + t)], dtype=float),
        np.array([(x0, y1 - t), (x1, y1 - t), (x1, y1), (x0, y1)], dtype=float),
        np.array([(x0, y0), (x0 + t, y0), (x0 + t, y1), (x0, y1)], dtype=float),
        np.array([(x1 - t, y0), (x1, y0), (x1, y1), (x1 - t, y1)], dtype=float),
    )
    triangles = np.concatenate(
        [prism_from_polygon(bar, z0=0.0, z1=10.0, taper=0.0) for bar in bars],
        axis=0,
    )
    return StlMesh(triangles)


def draw_summary_panel(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    setup_axis(ax)
    panel_badge(ax, design.label)
    add_text(ax, 0.11, 0.956, design.title, TextRole.PANEL_TITLE)

    rounded_box(ax, (0.055, 0.11), 0.52, 0.78, "white", COLORS["grid"], linewidth=1.0)
    add_text(ax, 0.08, 0.825, "OpenMFD preset", TextRole.PRESET_TITLE)
    add_text(ax, 0.08, 0.765, "editable legacy layout", TextRole.MUTED_LEFT)

    y = 0.685
    for key, value in design.summary_rows:
        add_text(ax, 0.085, y, key, TextRole.TABLE_KEY)
        add_text(ax, 0.545, y, value, TextRole.TABLE_VALUE)
        ax.plot([0.08, 0.555], [y - 0.030, y - 0.030], color="#edf1f6", lw=0.8)
        y -= 0.070

    add_text(
        ax,
        0.08,
        0.155,
        f"{design.layout_note}\nall outputs share the Fig. 1 coordinate system.",
        TextRole.NOTE,
    )

    outputs = (
        ((0.66, 0.715), "photomask\nDXFs", COLORS["bottom"]),
        ((0.66, 0.575), "insert\nCAD/STL", COLORS["insert"]),
        ((0.66, 0.435), "wall\nCAD/STL", COLORS["frame"]),
        ((0.66, 0.295), "wafer-mask\nCAD", COLORS["top"]),
    )
    for (x, y_out), label, color in outputs:
        rounded_box(ax, (x, y_out), 0.255, 0.102, "white", color, linewidth=1.6)
        add_text(ax, x + 0.1275, y_out + 0.051, label, TextRole.OUTPUT_BOX)
        add_arrow(ax, (0.585, 0.50), (x, y_out + 0.051), color)


def draw_dxf_panel(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    setup_axis(ax)
    panel_badge(ax, chr(ord(design.label) + 1))
    add_text(ax, 0.11, 0.956, f"{design.title} DXF outputs", TextRole.PANEL_TITLE)

    single_box = AxisBox(0.03, 0.16, 0.40, 0.68)
    aligned_box = AxisBox(0.46, 0.10, 0.51, 0.78)

    single_ax = add_inset(ax, single_box)
    aligned_ax = add_inset(ax, aligned_box)

    single_bounds = Bounds.combine((design.single_top, design.single_bottom))
    single_pad_x = max(single_bounds.width * 0.05, 0.55)
    single_pad_y = max(single_bounds.height * 0.05, 0.55)
    setup_raw_dxf_axis(single_ax, single_bounds, single_pad_x, single_pad_y)
    add_bounds_background(single_ax, single_bounds, single_pad_x, single_pad_y)
    draw_dxf_layer_raw(single_ax, design.single_bottom, COLORS["bottom"], 0.12, 0.60)
    draw_dxf_layer_raw(single_ax, design.single_top, COLORS["top"], 1.10, 0.94)

    aligned_bounds = design.aligned.bounds
    aligned_pad_x = max(aligned_bounds.width * 0.035, 0.55)
    aligned_pad_y = max(aligned_bounds.height * 0.035, 0.55)
    setup_raw_dxf_axis(aligned_ax, aligned_bounds, aligned_pad_x, aligned_pad_y)
    add_bounds_background(aligned_ax, aligned_bounds, aligned_pad_x, aligned_pad_y)
    draw_dxf_layer_raw(aligned_ax, design.aligned, "#0f8ea5", 0.28, 0.92)

    add_text(ax, 0.16, 0.085, "single unit", TextRole.SMALL_MUTED)
    add_text(ax, 0.65, 0.085, "wafer-scale mask", TextRole.SMALL_MUTED)


def draw_output_panel(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    setup_axis(ax)
    panel_badge(ax, chr(ord(design.label) + 2))
    add_text(ax, 0.11, 0.956, f"{design.title} insert outputs", TextRole.PANEL_TITLE)

    single_ax = add_inset(ax, AxisBox(0.035, 0.315, 0.295, 0.545))
    array_ax = add_inset(ax, AxisBox(0.355, 0.315, 0.295, 0.545))
    wall_ax = add_inset(ax, AxisBox(0.675, 0.315, 0.295, 0.545))

    draw_stl_mesh_raw_equal(
        single_ax,
        StlRenderSpec(
            insert_preview_mesh(design, array=False),
            26000,
            azimuth=-44.0,
            elevation=24.0,
            z_scale=1.0,
            edge_alpha=0.32,
            linewidth=0.018,
            base_color="#d8871f",
            highlight_color="#ffe2a3",
            edge_color="#593100",
        ),
    )
    draw_stl_mesh_raw_equal(
        array_ax,
        StlRenderSpec(
            insert_preview_mesh(design, array=True),
            70000,
            azimuth=-48.0,
            elevation=28.0,
            z_scale=1.0,
            edge_alpha=0.48,
            linewidth=0.008,
            base_color="#d8871f",
            highlight_color="#ffe2a3",
            edge_color="#593100",
        ),
    )
    draw_stl_mesh_raw_equal(
        wall_ax,
        StlRenderSpec(
            frame_preview_mesh(design),
            2000,
            azimuth=-36.0,
            elevation=25.0,
            z_scale=1.35,
            edge_alpha=0.52,
            linewidth=0.020,
            base_color="#485466",
            highlight_color="#d3d9e2",
            edge_color="#070b12",
        ),
    )

    add_text(ax, 0.182, 0.245, "single insert", TextRole.SMALL_MUTED)
    add_text(ax, 0.502, 0.245, "array insert", TextRole.SMALL_MUTED)
    add_text(ax, 0.822, 0.245, "wall frame", TextRole.SMALL_MUTED)

    add_text(
        ax,
        0.085,
        0.125,
        "Rendered through the Figure 1 STL projection style from the generated insert geometry,\n"
        "with matching unit pitch, PDMS scale, skirts, and rotated lock-and-key pins.",
        TextRole.NOTE,
    )


def build_figure() -> plt.Figure:
    myelination, axon_guidance = make_designs()

    fig = plt.figure(figsize=(13.6, 8.8))
    fig.patch.set_facecolor("white")
    grid = fig.add_gridspec(
        2,
        3,
        width_ratios=(1.16, 1.06, 1.18),
        height_ratios=(1.0, 1.0),
        left=0.025,
        right=0.985,
        bottom=0.035,
        top=0.945,
        wspace=0.05,
        hspace=0.08,
    )

    axes = {
        "A": fig.add_subplot(grid[0, 0]),
        "B": fig.add_subplot(grid[0, 1]),
        "C": fig.add_subplot(grid[0, 2]),
        "D": fig.add_subplot(grid[1, 0]),
        "E": fig.add_subplot(grid[1, 1]),
        "F": fig.add_subplot(grid[1, 2]),
    }
    for ax in axes.values():
        ax.set_facecolor(COLORS["paper"])

    draw_summary_panel(axes["A"], myelination)
    draw_dxf_panel(axes["B"], myelination)
    draw_output_panel(axes["C"], myelination)
    draw_summary_panel(axes["D"], axon_guidance)
    draw_dxf_panel(axes["E"], axon_guidance)
    draw_output_panel(axes["F"], axon_guidance)

    fig.suptitle(
        "OpenMFD renders legacy myelination and axon-guidance layouts with the same file-generation pipeline used in Figure 1",
        fontsize=12.0,
        fontweight="bold",
        color=COLORS["ink"],
        y=0.985,
    )
    return fig


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = build_figure()
    fig.savefig(OUTPUT_DIR / "draft_figure.pdf", bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "draft_figure.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
