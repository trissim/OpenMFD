#!/usr/bin/env python3

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpecFromSubplotSpec
from PIL import Image


FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig5_plate_layout_validation"
FLUORESCENCE_PDF = OUTPUT_DIR / "fluorescence_microscopy.pdf"
FLUORESCENCE_ODP = OUTPUT_DIR / "fluorescence_microscopy.odp"
DYE_DAY0 = OUTPUT_DIR / "dye_gradient_day0.png"
DYE_DAY3 = OUTPUT_DIR / "dye_gradient_day3.png"
CTB_COUNT_PLOT = OUTPUT_DIR / "plate_bar_var_Cell_Before.png"

INK = "#1d2633"
MUTED = "#687583"
PANEL_BOX = {"boxstyle": "round,pad=0.25", "facecolor": INK, "edgecolor": INK}


def crop_fraction(
    image: Image.Image,
    bounds: tuple[float, float, float, float],
) -> Image.Image:
    left, top, right, bottom = bounds
    return image.crop(
        (
            round(image.width * left),
            round(image.height * top),
            round(image.width * right),
            round(image.height * bottom),
        )
    )


def load_authored_ctb_row() -> Image.Image:
    # Reuse the exact three-image CTB row authored in the ODP: one overview at
    # left and two stacked crops at right.
    with TemporaryDirectory(prefix="openmfd-fluorescence-") as temporary_dir:
        output_stem = Path(temporary_dir) / "fluorescence"
        subprocess.run(
            [
                "pdftoppm",
                "-f",
                "1",
                "-l",
                "1",
                "-png",
                "-singlefile",
                "-r",
                "300",
                str(FLUORESCENCE_PDF),
                str(output_stem),
            ],
            check=True,
        )
        with Image.open(output_stem.with_suffix(".png")) as image:
            slide = image.convert("RGB")
            ct_b = crop_fraction(slide, (0.302, 0.355, 0.845, 0.681))

    # The ODP overlays a white channel label on the overview. Replace that
    # panel with its underlying source raster while retaining the authored
    # sizing and the two detail crops on the right.
    with ZipFile(FLUORESCENCE_ODP) as odp:
        overview_bytes = odp.read(
            "Pictures/1000000000001D8E00000E6C3664813B.png"
        )
    with Image.open(BytesIO(overview_bytes)) as image:
        overview = image.convert("RGB")
    overview_width = round(ct_b.width * 10.199 / 14.797)
    overview = overview.resize(
        (overview_width, ct_b.height),
        Image.Resampling.LANCZOS,
    )
    ct_b.paste(overview, (0, 0))
    return ct_b


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
    ct_b_group = load_authored_ctb_row()

    with Image.open(DYE_DAY0) as image:
        dye_day0 = image.convert("RGB")
    with Image.open(DYE_DAY3) as image:
        dye_day3 = image.convert("RGB")
    with Image.open(CTB_COUNT_PLOT) as image:
        # Remove the exploratory ICC and pairwise annotations while preserving
        # the original plate means, error bars, ticks, and plate labels.
        ct_b_counts = image.convert("RGB").crop((70, 390, image.width - 10, image.height - 5))

    fig = plt.figure(figsize=(10.0, 15.0), facecolor="white")
    outer = fig.add_gridspec(
        3,
        1,
        height_ratios=(1.25, 0.87, 1.15),
        left=0.035,
        right=0.99,
        bottom=0.055,
        top=0.895,
        hspace=0.24,
    )

    fig.suptitle(
        "Plate-format devices maintain directional bias\n"
        "and support distal CTB uptake",
        fontsize=23,
        color=INK,
        fontweight="bold",
        y=0.975,
    )

    dye_grid = GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[0], hspace=0.18)
    ax_day0 = fig.add_subplot(dye_grid[0, 0])
    ax_day3 = fig.add_subplot(dye_grid[1, 0])
    show_image(ax_day0, dye_day0, "Hour 0")
    show_image(ax_day3, dye_day3, "Hour 72")
    panel_label(ax_day0, "A")

    validation_grid = GridSpecFromSubplotSpec(1, 1, subplot_spec=outer[1])
    ax_ct_b = fig.add_subplot(validation_grid[0, 0])
    show_image(ax_ct_b, ct_b_group, "CTB-647 endpoint (DIV11)")
    panel_label(ax_ct_b, "B")

    ax_counts = fig.add_subplot(outer[2])
    show_image(ax_counts, ct_b_counts, "Mean CTB-positive soma count per analyzed device")
    panel_label(ax_counts, "C")
    ax_counts.text(
        0.5,
        -0.055,
        "Bars: plate mean; error bars: SD across analyzed interior devices\n"
        "One E18 donor preparation; three technical plate replicates; 69 devices analyzed",
        transform=ax_counts.transAxes,
        ha="center",
        va="top",
        fontsize=11.5,
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
