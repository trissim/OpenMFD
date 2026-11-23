#!/usr/bin/env python3

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from generate_openmfd_design_figure import (
    AxisBox,
    Bounds,
    COLORS,
    DxfDrawing,
    PanelBadge,
    PanelTitle,
    add_inset,
    draw_dxf_layer_raw,
    setup_axis,
    setup_raw_dxf_axis,
    SUBFIGURE_DPI,
)

FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig6_generalizability"
SUBFIGURE_DIR = OUTPUT_DIR / "subfigures"
INDIVIDUAL_SUBFIGURE_DIR = SUBFIGURE_DIR / "individual"

BASE_ROW_GAP = 0.11
ROW_GAP_SCALE = 1.20
ROW_SPACING_INCREASE = 1.45
HEADER_PADDING_INCHES = 0.08


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
        )


def make_designs() -> tuple[GeneralizabilityDesign, ...]:
    base = ROOT / "designs" / "open_chamber" / "openmfd_legacy_ports"
    diamond_unit_dims = (18.0, 18.0, 0.0)
    diamond_grid_size = (6, 4)
    linear_unit_dims = (27.0, 9.0, 0.0)
    linear_grid_size = (4, 8)
    myelination = GeneralizabilityDesign.from_assets(
        title="Myelination layout",
        stem="myelination",
        design_dir=base / "myelination",
        dims=diamond_unit_dims,
        grid_size=diamond_grid_size,
    )
    axon_guidance = GeneralizabilityDesign.from_assets(
        title="Axon-guidance layout",
        stem="axon_guidance",
        design_dir=base / "axon_guidance",
        dims=diamond_unit_dims,
        grid_size=diamond_grid_size,
    )
    three_compartment = GeneralizabilityDesign.from_assets(
        title="Three-compartment layout",
        stem="three_compartment",
        design_dir=base / "three_compartment",
        dims=linear_unit_dims,
        grid_size=linear_grid_size,
    )
    return myelination, axon_guidance, three_compartment


class DesignPanel(ABC):
    def __call__(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        setup_axis(ax)
        self.draw_content(ax, design)
        self.decorate(ax, design)

    @classmethod
    @abstractmethod
    def image_boxes(cls) -> tuple[AxisBox, AxisBox]:
        raise NotImplementedError

    @abstractmethod
    def draw_content(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        raise NotImplementedError

    def decorate(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        pass

    def title(self, design: GeneralizabilityDesign) -> str:
        return design.title


class DxfPanel(DesignPanel):
    COLUMN_TITLES = ("Single-unit mask", "Wafer-scale mask")
    single_box = AxisBox(0.025, 0.05, 0.43, 0.90)
    aligned_box = AxisBox(0.50, 0.03, 0.475, 0.94)

    @classmethod
    def image_boxes(cls) -> tuple[AxisBox, AxisBox]:
        return cls.single_box, cls.aligned_box

    def draw_content(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        single_ax = add_inset(ax, self.single_box)
        aligned_ax = add_inset(ax, self.aligned_box)
        single_bounds = Bounds.combine((design.single_top, design.single_bottom))
        single_pad_x = max(single_bounds.width * 0.05, 0.55)
        single_pad_y = max(single_bounds.height * 0.05, 0.55)
        setup_raw_dxf_axis(single_ax, single_bounds, single_pad_x, single_pad_y)
        draw_dxf_layer_raw(single_ax, design.single_bottom, COLORS["bottom"], 0.14, 0.60)
        draw_dxf_layer_raw(single_ax, design.single_top, COLORS["top"], 1.15, 0.94)
        aligned_bounds = Bounds.combine((design.wafer_top, design.wafer_bottom))
        aligned_pad_x = max(aligned_bounds.width * 0.035, 0.55)
        aligned_pad_y = max(aligned_bounds.height * 0.035, 0.55)
        setup_raw_dxf_axis(aligned_ax, aligned_bounds, aligned_pad_x, aligned_pad_y)
        draw_dxf_layer_raw(aligned_ax, design.wafer_bottom, COLORS["bottom"], 0.18, 0.58)
        draw_dxf_layer_raw(aligned_ax, design.wafer_top, COLORS["top"], 0.38, 0.92)


@dataclass(frozen=True)
class LabeledPanel(DesignPanel):
    label: str
    image_band = AxisBox(0.0, 0.02, 1.0, 0.87)

    def decorate(self, ax: plt.Axes, design: GeneralizabilityDesign) -> None:
        PanelBadge.draw(ax, 0.015, 0.97, self.label)
        PanelTitle.draw(ax, 0.068, 0.966, self.title(design))

    @property
    @abstractmethod
    def single_box(self) -> AxisBox:
        raise NotImplementedError


class LabeledDxfPanel(LabeledPanel, DxfPanel):
    single_box = replace(LabeledPanel.image_band, left=0.04, width=0.41)
    aligned_box = replace(LabeledPanel.image_band, left=0.49, width=0.48)


def draw_single_unit_dxf_asset(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    bounds = Bounds.combine((design.single_top, design.single_bottom))
    pad_x = max(bounds.width * 0.06, 0.55)
    pad_y = max(bounds.height * 0.06, 0.55)
    setup_raw_dxf_axis(ax, bounds, pad_x, pad_y)
    draw_dxf_layer_raw(ax, design.single_bottom, COLORS["bottom"], 0.14, 0.60)
    draw_dxf_layer_raw(ax, design.single_top, COLORS["top"], 1.25, 0.94)


def draw_wafer_mask_dxf_asset(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    bounds = Bounds.combine((design.wafer_top, design.wafer_bottom))
    pad_x = max(bounds.width * 0.035, 0.55)
    pad_y = max(bounds.height * 0.035, 0.55)
    setup_raw_dxf_axis(ax, bounds, pad_x, pad_y)
    draw_dxf_layer_raw(ax, design.wafer_bottom, COLORS["bottom"], 0.18, 0.58)
    draw_dxf_layer_raw(ax, design.wafer_top, COLORS["top"], 0.36, 0.92)


def draw_plate_layout_dxf_asset(ax: plt.Axes, design: GeneralizabilityDesign) -> None:
    bounds = Bounds.combine((design.multi_top, design.multi_bottom))
    pad_x = max(bounds.width * 0.025, 0.55)
    pad_y = max(bounds.height * 0.025, 0.55)
    setup_raw_dxf_axis(ax, bounds, pad_x, pad_y)
    draw_dxf_layer_raw(ax, design.multi_bottom, COLORS["bottom"], 0.18, 0.58)
    draw_dxf_layer_raw(ax, design.multi_top, COLORS["top"], 0.36, 0.92)


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
        ("B", "dxf_outputs", designs[1], DxfPanel()),
        ("C", "dxf_outputs", designs[2], DxfPanel()),
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


def build_figure() -> plt.Figure:
    myelination, axon_guidance, three_compartment = make_designs()
    layout = (
        ("A", myelination),
        ("B", axon_guidance),
        ("C", three_compartment),
    )
    row_count = len(layout)
    row_gap = BASE_ROW_GAP * ROW_GAP_SCALE * ROW_SPACING_INCREASE
    fig = plt.figure(figsize=(5.6, 6.2))
    fig.patch.set_facecolor("white")
    grid = fig.add_gridspec(
        row_count,
        1,
        height_ratios=(1.0,) * row_count,
        left=0.03,
        right=0.97,
        bottom=0.02,
        top=0.905,
        hspace=row_gap,
    )
    row_axes: list[plt.Axes] = []
    for row, (dxf_label, design) in enumerate(layout):
        dxf_ax = fig.add_subplot(grid[row, 0])
        dxf_ax.set_facecolor("none")
        LabeledDxfPanel(dxf_label)(dxf_ax, design)
        row_axes.append(dxf_ax)

    first_ax = row_axes[0]
    pos = first_ax.get_position()
    header_bottom = pos.y1 + HEADER_PADDING_INCHES / fig.get_figheight()
    header_top = 0.985
    header_y = (header_bottom + header_top) / 2
    header_positions = (
        pos.x0 + LabeledDxfPanel.single_box.center_x * pos.width,
        pos.x0 + LabeledDxfPanel.aligned_box.center_x * pos.width,
    )
    for x, title in zip(header_positions, DxfPanel.COLUMN_TITLES, strict=True):
        fig.text(x, header_y, title, ha="center", va="center",
                 fontsize=9.5, fontweight="bold", color=COLORS["ink"])

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
