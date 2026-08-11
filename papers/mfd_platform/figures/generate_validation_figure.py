#!/usr/bin/env python3

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpecFromSubplotSpec
from PIL import Image


FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig5_plate_layout_validation"
FLUORESCENCE_ODP = OUTPUT_DIR / "fluorescence_microscopy.odp"
DYE_DAY0 = OUTPUT_DIR / "dye_gradient_day0.png"
DYE_DAY3 = OUTPUT_DIR / "dye_gradient_day3.png"
CTB_COUNT_PLOT = OUTPUT_DIR / "plate_bar_var_Cell_Before.png"

INK = "#1d2633"
MUTED = "#687583"
PANEL_BOX = {"boxstyle": "round,pad=0.25", "facecolor": INK, "edgecolor": INK}


def load_odp_images() -> list[Image.Image]:
    images: list[Image.Image] = []
    with ZipFile(FLUORESCENCE_ODP) as archive:
        for name in archive.namelist():
            if not name.startswith("Pictures/"):
                continue
            with Image.open(BytesIO(archive.read(name))) as image:
                images.append(image.convert("RGB"))
    return images


def select_ctb_images(images: list[Image.Image]) -> tuple[Image.Image, Image.Image]:
    # The CTB overview is the widest large grayscale mosaic; the representative
    # field is the remaining large near-square grayscale image.
    overview = max(images, key=lambda image: image.width)
    representative = max(
        (image for image in images if image is not overview and image.width > 4000),
        key=lambda image: image.width * image.height,
    )
    return overview, representative


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.01,
        1.04,
        label,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color="white",
        fontsize=17,
        fontweight="bold",
        bbox=PANEL_BOX,
    )


def show_image(ax: plt.Axes, image: Image.Image, title: str | None = None) -> None:
    ax.imshow(image)
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=15, color=INK, fontweight="bold", pad=8)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ct_b_overview, ct_b_field = select_ctb_images(load_odp_images())

    with Image.open(DYE_DAY0) as image:
        dye_day0 = image.convert("RGB")
    with Image.open(DYE_DAY3) as image:
        dye_day3 = image.convert("RGB")
    with Image.open(CTB_COUNT_PLOT) as image:
        # Remove the exploratory ICC and pairwise annotations while preserving
        # the original plate means, error bars, ticks, and plate labels.
        ct_b_counts = image.convert("RGB").crop((70, 390, image.width - 10, image.height - 5))

    fig = plt.figure(figsize=(15, 13), facecolor="white")
    outer = fig.add_gridspec(
        3,
        1,
        height_ratios=(0.78, 1.08, 1.25),
        left=0.055,
        right=0.98,
        bottom=0.055,
        top=0.925,
        hspace=0.29,
    )

    fig.suptitle(
        "Plate-format devices maintain directional bias and support distal CTB uptake",
        fontsize=23,
        color=INK,
        fontweight="bold",
        y=0.975,
    )

    dye_grid = GridSpecFromSubplotSpec(1, 2, subplot_spec=outer[0], wspace=0.035)
    ax_day0 = fig.add_subplot(dye_grid[0, 0])
    ax_day3 = fig.add_subplot(dye_grid[0, 1])
    show_image(ax_day0, dye_day0, "Hour 0")
    show_image(ax_day3, dye_day3, "Hour 72")
    panel_label(ax_day0, "A")

    ct_b_grid = GridSpecFromSubplotSpec(
        1,
        2,
        subplot_spec=outer[1],
        width_ratios=(2.15, 1.0),
        wspace=0.035,
    )
    ax_ct_b_overview = fig.add_subplot(ct_b_grid[0, 0])
    ax_ct_b_field = fig.add_subplot(ct_b_grid[0, 1])
    show_image(ax_ct_b_overview, ct_b_overview, "CTB-647 endpoint overview")
    show_image(ax_ct_b_field, ct_b_field, "Representative CTB-positive soma field")
    panel_label(ax_ct_b_overview, "B")

    ax_counts = fig.add_subplot(outer[2])
    show_image(ax_counts, ct_b_counts, "CTB-positive soma counts across three plates")
    panel_label(ax_counts, "C")
    ax_counts.text(
        0.5,
        -0.055,
        "One E18 donor preparation; three technical plate replicates; 69 eligible interior device positions",
        transform=ax_counts.transAxes,
        ha="center",
        va="top",
        fontsize=12.5,
        color=MUTED,
    )
    ax_counts.text(
        -0.012,
        0.48,
        "CTB-positive soma count",
        transform=ax_counts.transAxes,
        ha="center",
        va="center",
        rotation=90,
        fontsize=13,
        color=INK,
    )

    output_pdf = OUTPUT_DIR / "draft_figure.pdf"
    output_png = OUTPUT_DIR / "draft_figure.png"
    fig.savefig(output_pdf, dpi=300, facecolor="white")
    fig.savefig(output_png, dpi=300, facecolor="white")
    plt.close(fig)

    print(f"Wrote {output_pdf}")
    print(f"Wrote {output_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
