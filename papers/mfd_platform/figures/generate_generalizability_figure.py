#!/usr/bin/env python3

from __future__ import annotations

import math
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from openmfd.devices import PDMSConfiguration

from generate_openmfd_design_figure import (
    AxisBox,
    Bounds,
    COLORS,
    DxfDrawing,
    HeadingText,
    PanelBadge,
    PanelTitle,
    StlMesh,
    StlRenderSpec,
    add_bounds_background,
    add_inset,
    draw_dxf_layer_raw,
    draw_stl_mesh_raw_equal,
    draw_stl_polygons,
    project_stl_render,
    setup_axis,
    setup_raw_dxf_axis,
    SUBFIGURE_DPI,
)

FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig6_generalizability"
SUBFIGURE_DIR = OUTPUT_DIR / "subfigures"
INDIVIDUAL_SUBFIGURE_DIR = SUBFIGURE_DIR / "individual"

CURE_TEMP = 100
PDMS_SCALE = PDMSConfiguration(cure_temp=CURE_TEMP).scale_factor()
SINGLE_INSERT_AZIMUTH = 0.0
ARRAY_INSERT_AZIMUTH = 0.0
ARRAY_INSERT_ELEVATION = 28.0


@dataclass(frozen=True)
class GeneralizabilityDesign:
    title: str
    stem: str
    design_dir: Path
    dims: tuple[float, float, float]
    grid_size: tuple[int, int]
    single_top: DxfDrawing
    single_bottom: DxfDrawing
    multi_top: DxfDrawing
    multi_bottom: DxfDrawing
    wafer_top: DxfDrawing
    wafer_bottom: DxfDrawing
    single_insert: StlMesh

    @classmethod
    def from_assets(
        cls,
        *,
        title: str,
        stem: str,
        design_dir: Path,
        dims: tuple[float, float, float],
        grid_size: tuple[int, int],
    ) -> "GeneralizabilityDesign":
        return cls(
            title=title,
            stem=stem,
            design_dir=design_dir,
            dims=dims,
            grid_size=grid_size,
            single_top=DxfDrawing.from_file(design_dir / f"{stem}_single_top.dxf"),
            single_bottom=DxfDrawing.from_file(design_dir / f"{stem}_single_bottom.dxf"),
            multi_top=DxfDrawing.from_file(design_dir / f"{stem}_multi_top.dxf"),
            multi_bottom=DxfDrawing.from_file(design_dir / f"{stem}_multi_bottom.dxf"),
            wafer_top=DxfDrawing.from_file(design_dir / f"{stem}_top.dxf"),
            wafer_bottom=DxfDrawing.from_file(design_dir / f"{stem}_bottom.dxf"),
            single_insert=StlMesh.from_file(design_dir / f"{stem}_single_insert.stl"),
        )

    def single_insert_spec(self) -> StlRenderSpec:
        return StlRenderSpec(
            self.single_insert,
            26000,
            azimuth=SINGLE_INSERT_AZIMUTH,
            elevation=24.0,
            z_scale=1.0,
            edge_alpha=0.32,
            linewidth=0.018,
            base_color="#d8871f",
            highlight_color="#ffe2a3",
            edge_color="#593100",
        )


def make_designs() -> tuple[GeneralizabilityDesign, ...]:
    base = ROOT / "designs" / "open_chamber" / "openmfd_legacy_ports"
    diamond_unit_dims = (18.0, 18.0, 0.0)
    diamond_grid_size = (6, 4)
    linear_unit_dims = (27.0, 9.0, 0.0)
    linear_grid_size = (4, 8)
    myelination = GeneralizabilityDesign.from_assets(
        title="Myelination assay",
        stem="myelination",
        design_dir=base / "myelination",
        dims=diamond_unit_dims,
        grid_size=diamond_grid_size,
    )
    axon_guidance = GeneralizabilityDesign.from_assets(
        title="Axon guidance assay",
        stem="axon_guidance",
        design_dir=base / "axon_guidance",
        dims=diamond_unit_dims,
        grid_size=diamond_grid_size,
    )
    three_compartment = GeneralizabilityDesign.from_assets(
        title="Three-compartment assay",
        stem="three_compartment",
        design_dir=base / "three_compartment",
        dims=linear_unit_dims,
        grid_size=linear_grid_size,
    )
    return myelination, axon_guidance, three_compartment


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


def array_insert_render_spec(design: GeneralizabilityDesign) -> StlRenderSpec:
    return StlRenderSpec(
        design.single_insert,
        26000,
        azimuth=ARRAY_INSERT_AZIMUTH,
        elevation=ARRAY_INSERT_ELEVATION,
        z_scale=1.0,
        edge_alpha=0.0,
        linewidth=0.0,
        base_color="#d2932c",
        highlight_color="#f2ca78",
        edge_color="#593100",
    )


def draw_insert_array_preview(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    spec = array_insert_render_spec(design)
    polygons, depth, normals = project_stl_render(spec)
    unit_bounds = Bounds.from_points(polygons.reshape((-1, 2)))
    base_offset = np.array(unit_offsets(design, array=False)[0], dtype=float)
    projected_centers: list[tuple[float, float]] = []
    y_projection_scale = math.cos(math.radians(ARRAY_INSERT_ELEVATION))
    for offset in unit_offsets(design, array=True):
        delta = (np.array(offset, dtype=float) - base_offset) * PDMS_SCALE
        projected_centers.append((float(delta[0]), float(delta[1] * y_projection_scale)))

    min_x = min(center_x + unit_bounds.min_x for center_x, _ in projected_centers)
    max_x = max(center_x + unit_bounds.max_x for center_x, _ in projected_centers)
    min_y = min(center_y + unit_bounds.min_y for _, center_y in projected_centers)
    max_y = max(center_y + unit_bounds.max_y for _, center_y in projected_centers)
    bounds = Bounds(min_x, min_y, max_x, max_y)
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
    for center_x, center_y in projected_centers:
        draw_stl_polygons(
            ax,
            polygons + np.array([center_x, center_y], dtype=float),
            depth,
            normals,
            spec,
            zorder=2,
        )


class DesignPanel(ABC):
    def __call__(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        setup_axis(ax)
        self.draw_content(ax, design)
        self.decorate(ax, design)

    @abstractmethod
    def draw_content(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        raise NotImplementedError

    def decorate(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        pass

    def title(self, design: GeneralizabilityDesign) -> str:
        return design.title


class DxfPanel(DesignPanel):
    single_box = AxisBox(0.025, 0.05, 0.43, 0.90)
    aligned_box = AxisBox(0.50, 0.03, 0.475, 0.94)

    def draw_content(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        single_ax = add_inset(ax, self.single_box)
        aligned_ax = add_inset(ax, self.aligned_box)
        single_bounds = Bounds.combine((design.single_top, design.single_bottom))
        single_pad_x = max(single_bounds.width * 0.05, 0.55)
        single_pad_y = max(single_bounds.height * 0.05, 0.55)
        setup_raw_dxf_axis(single_ax, single_bounds, single_pad_x, single_pad_y)
        add_bounds_background(single_ax, single_bounds, single_pad_x, single_pad_y)
        draw_dxf_layer_raw(single_ax, design.single_bottom, COLORS["bottom"], 0.12, 0.60)
        draw_dxf_layer_raw(single_ax, design.single_top, COLORS["top"], 1.10, 0.94)
        aligned_bounds = Bounds.combine((design.wafer_top, design.wafer_bottom))
        aligned_pad_x = max(aligned_bounds.width * 0.035, 0.55)
        aligned_pad_y = max(aligned_bounds.height * 0.035, 0.55)
        setup_raw_dxf_axis(aligned_ax, aligned_bounds, aligned_pad_x, aligned_pad_y)
        add_bounds_background(aligned_ax, aligned_bounds, aligned_pad_x, aligned_pad_y)
        draw_dxf_layer_raw(aligned_ax, design.wafer_bottom, COLORS["bottom"], 0.16, 0.58)
        draw_dxf_layer_raw(aligned_ax, design.wafer_top, COLORS["top"], 0.34, 0.92)


class InsertPanel(DesignPanel):
    single_box = AxisBox(0.025, 0.06, 0.43, 0.88)
    array_box = AxisBox(0.50, 0.06, 0.475, 0.88)

    def draw_content(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        single_ax = add_inset(ax, self.single_box)
        array_ax = add_inset(ax, self.array_box)
        draw_stl_mesh_raw_equal(single_ax, design.single_insert_spec())
        draw_insert_array_preview(array_ax, design)

    def title(self, design: GeneralizabilityDesign) -> str:
        return "Printable inserts"


@dataclass(frozen=True)
class LabeledPanel(DesignPanel):
    label: str
    caption_y = 0.055

    def decorate(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        PanelBadge.draw(ax, 0.02, 0.96, self.label)
        PanelTitle.draw(ax, 0.11, 0.956, self.title(design))
        self.captions(ax)

    @property
    @abstractmethod
    def single_box(self) -> AxisBox:
        raise NotImplementedError

    def captions(self, ax: plt.Axes) -> None:
        HeadingText.draw(ax, self.single_box.center_x, self.caption_y, "Single unit")


class LabeledDxfPanel(LabeledPanel, DxfPanel):
    single_box = AxisBox(0.03, 0.07, 0.40, 0.86)
    aligned_box = AxisBox(0.46, 0.07, 0.51, 0.86)

    def captions(self, ax: plt.Axes) -> None:
        super().captions(ax)
        HeadingText.draw(ax, self.aligned_box.center_x, self.caption_y, "Wafer-scale mask")


class LabeledInsertPanel(LabeledPanel, InsertPanel):
    single_box = AxisBox(0.035, 0.07, 0.430, 0.86)
    array_box = AxisBox(0.535, 0.07, 0.430, 0.86)

    def captions(self, ax: plt.Axes) -> None:
        super().captions(ax)
        HeadingText.draw(ax, self.array_box.center_x, self.caption_y, "Arrayed inserts")


def draw_single_unit_dxf_asset(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    bounds = Bounds.combine((design.single_top, design.single_bottom))
    pad_x = max(bounds.width * 0.06, 0.55)
    pad_y = max(bounds.height * 0.06, 0.55)
    setup_raw_dxf_axis(ax, bounds, pad_x, pad_y)
    add_bounds_background(ax, bounds, pad_x, pad_y)
    draw_dxf_layer_raw(ax, design.single_bottom, COLORS["bottom"], 0.14, 0.60)
    draw_dxf_layer_raw(ax, design.single_top, COLORS["top"], 1.25, 0.94)


def draw_wafer_mask_dxf_asset(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    bounds = Bounds.combine((design.wafer_top, design.wafer_bottom))
    pad_x = max(bounds.width * 0.035, 0.55)
    pad_y = max(bounds.height * 0.035, 0.55)
    setup_raw_dxf_axis(ax, bounds, pad_x, pad_y)
    add_bounds_background(ax, bounds, pad_x, pad_y)
    draw_dxf_layer_raw(ax, design.wafer_bottom, COLORS["bottom"], 0.18, 0.58)
    draw_dxf_layer_raw(ax, design.wafer_top, COLORS["top"], 0.36, 0.92)


def draw_plate_layout_dxf_asset(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    bounds = Bounds.combine((design.multi_top, design.multi_bottom))
    pad_x = max(bounds.width * 0.025, 0.55)
    pad_y = max(bounds.height * 0.025, 0.55)
    setup_raw_dxf_axis(ax, bounds, pad_x, pad_y)
    add_bounds_background(ax, bounds, pad_x, pad_y)
    draw_dxf_layer_raw(ax, design.multi_bottom, COLORS["bottom"], 0.18, 0.58)
    draw_dxf_layer_raw(ax, design.multi_top, COLORS["top"], 0.36, 0.92)


def draw_single_insert_asset(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    draw_stl_mesh_raw_equal(
        ax,
        design.single_insert_spec(),
    )


def draw_array_insert_asset(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    draw_insert_array_preview(ax, design)


def save_individual_subfigure(
    output_path: Path,
    design: GeneralizabilityDesign,
    draw_function: Callable[[plt.Axes, GeneralizabilityDesign], None],
    *,
    figsize: tuple[float, float],
) -> None:
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(COLORS["paper"])
    draw_function(ax, design)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def export_clean_subfigures(designs: tuple[GeneralizabilityDesign, ...]) -> None:
    SUBFIGURE_DIR.mkdir(parents=True, exist_ok=True)
    exports = (
        ("A", "dxf_outputs", designs[0], DxfPanel()),
        ("B", "insert_outputs", designs[0], InsertPanel()),
        ("C", "dxf_outputs", designs[1], DxfPanel()),
        ("D", "insert_outputs", designs[1], InsertPanel()),
        ("E", "dxf_outputs", designs[2], DxfPanel()),
        ("F", "insert_outputs", designs[2], InsertPanel()),
    )
    for label, suffix, design, draw_function in exports:
        output_path = SUBFIGURE_DIR / f"{label}_{design.stem}_{suffix}.png"
        save_individual_subfigure(output_path, design, draw_function, figsize=(6.8, 3.3))


def export_individual_subfigures(designs: tuple[GeneralizabilityDesign, ...]) -> None:
    INDIVIDUAL_SUBFIGURE_DIR.mkdir(parents=True, exist_ok=True)
    exports = (
        ("myelination", designs[0]),
        ("axon_guidance", designs[1]),
        ("three_compartment", designs[2]),
    )
    for prefix, design in exports:
        save_individual_subfigure(
            INDIVIDUAL_SUBFIGURE_DIR / f"{prefix}_single_unit_dxf.png",
            design,
            draw_single_unit_dxf_asset,
            figsize=(3.8, 3.8),
        )
        save_individual_subfigure(
            INDIVIDUAL_SUBFIGURE_DIR / f"{prefix}_wafer_mask_dxf.png",
            design,
            draw_wafer_mask_dxf_asset,
            figsize=(4.8, 4.8),
        )
        save_individual_subfigure(
            INDIVIDUAL_SUBFIGURE_DIR / f"{prefix}_plate_layout_dxf.png",
            design,
            draw_plate_layout_dxf_asset,
            figsize=(5.2, 3.4),
        )
        save_individual_subfigure(
            INDIVIDUAL_SUBFIGURE_DIR / f"{prefix}_single_insert.png",
            design,
            draw_single_insert_asset,
            figsize=(3.8, 3.8),
        )
        save_individual_subfigure(
            INDIVIDUAL_SUBFIGURE_DIR / f"{prefix}_array_insert.png",
            design,
            draw_array_insert_asset,
            figsize=(5.2, 3.4),
        )


def build_figure() -> plt.Figure:
    myelination, axon_guidance, three_compartment = make_designs()

    fig = plt.figure(figsize=(6.5, 5.2))
    fig.patch.set_facecolor("white")
    grid = fig.add_gridspec(
        3,
        2,
        width_ratios=(1.0, 1.0),
        height_ratios=(1.0, 1.0, 1.0),
        left=0.025,
        right=0.985,
        bottom=0.03,
        top=0.98,
        wspace=0.07,
        hspace=0.06,
    )

    layout = (
        ("A", "B", myelination),
        ("C", "D", axon_guidance),
        ("E", "F", three_compartment),
    )
    for row, (dxf_label, insert_label, design) in enumerate(layout):
        dxf_ax = fig.add_subplot(grid[row, 0])
        insert_ax = fig.add_subplot(grid[row, 1])
        dxf_ax.set_facecolor(COLORS["paper"])
        insert_ax.set_facecolor(COLORS["paper"])
        LabeledDxfPanel(dxf_label)(dxf_ax, design)
        LabeledInsertPanel(insert_label)(insert_ax, design)

    return fig


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    designs = make_designs()
    export_clean_subfigures(designs)
    export_individual_subfigures(designs)
    fig = build_figure()
    fig.savefig(OUTPUT_DIR / "draft_figure.pdf", dpi=SUBFIGURE_DPI, bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "draft_figure.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
