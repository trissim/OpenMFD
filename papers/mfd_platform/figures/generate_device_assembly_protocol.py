#!/usr/bin/env python3

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig4_mold_casts_package"
OUTPUT_STEM = "assembly_protocol_schematic"
DPI = 600

COLORS = {
    "ink": "#1d2633",
    "muted": "#687583",
    "grid": "#d8dee8",
    "paper": "#f7f9fb",
    "wafer": "#343b49",
    "pdms": "#d9f0f7",
    "pdms_edge": "#75aec0",
    "suex": "#32a889",
    "insert": "#f2a33a",
    "glass": "#cfe8f6",
    "frame": "#273140",
    "glue": "#f3c44d",
    "sterile": "#f4e8f5",
    "accent": "#1d6fbc",
}


@dataclass(frozen=True)
class Step:
    number: int
    title: str
    detail: str


STEPS = (
    Step(1, "Hybrid mold ready", "Parylene-coated SU-8/SUEX wafer with bonded resin well inserts"),
    Step(2, "Cast PDMS", "Mix, pour, degas, and heat-cure PDMS on the reusable mold"),
    Step(3, "Demold and trim", "Release cast, cut to guide, chamfer corners, and tape-clean"),
    Step(
        4, "Bond to glass", "Plasma-treat PDMS and 110 x 74 mm glass, align, press, and heat-finish"
    ),
    Step(5, "Sterilize", "Dry autoclave the bonded PDMS-glass device in a pouch"),
    Step(
        6,
        "Frame, cure, clean",
        "Ethanol-sterilize HIPS frame; glue, seat, cure 3 days, then plasma-clean",
    ),
)


def setup_axis(ax: plt.Axes) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def add_text(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    *,
    size: float,
    color: str = COLORS["ink"],
    ha: str = "center",
    va: str = "center",
    weight: str | None = None,
    wrap: int | None = None,
    zorder: float = 10.0,
) -> None:
    if wrap is not None:
        text = textwrap.fill(text, wrap)
    ax.text(
        x,
        y,
        text,
        ha=ha,
        va=va,
        fontsize=size,
        color=color,
        fontweight=weight,
        linespacing=1.15,
        zorder=zorder,
    )


def rounded_box(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    facecolor: str = "white",
    edgecolor: str = COLORS["grid"],
    linewidth: float = 1.0,
    radius: float = 0.018,
    zorder: float = 1.0,
) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle=f"round,pad=0.010,rounding_size={radius}",
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=linewidth,
            zorder=zorder,
        )
    )


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = COLORS["muted"],
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=13,
            linewidth=1.4,
            color=color,
            shrinkA=3,
            shrinkB=3,
            zorder=4,
        )
    )


def add_wells(
    ax: plt.Axes, x: float, y: float, width: float, height: float, *, rows: int = 3, cols: int = 5
) -> None:
    gap_x = width / (cols * 2.25)
    gap_y = height / (rows * 2.15)
    well_w = (width - gap_x * (cols + 1)) / cols
    well_h = (height - gap_y * (rows + 1)) / rows
    for row in range(rows):
        for col in range(cols):
            wx = x + gap_x + col * (well_w + gap_x)
            wy = y + gap_y + row * (well_h + gap_y)
            rounded_box(
                ax,
                wx,
                wy,
                well_w,
                well_h,
                facecolor="#ffffff",
                edgecolor=COLORS["pdms_edge"],
                linewidth=0.8,
                radius=0.006,
                zorder=6,
            )


def icon_mold(ax: plt.Axes, x: float, y: float, scale: float) -> None:
    ax.add_patch(
        Circle(
            (x, y),
            0.045 * scale,
            facecolor=COLORS["wafer"],
            edgecolor="#141923",
            linewidth=1.0,
            zorder=5,
        )
    )
    ax.add_patch(
        Rectangle(
            (x - 0.053 * scale, y - 0.020 * scale),
            0.106 * scale,
            0.040 * scale,
            facecolor="#e6eaef",
            edgecolor="#b6beca",
            linewidth=0.8,
            zorder=6,
        )
    )
    for idx in range(4):
        ax.add_patch(
            Rectangle(
                (x - 0.036 * scale + idx * 0.024 * scale, y - 0.016 * scale),
                0.012 * scale,
                0.032 * scale,
                facecolor=COLORS["insert"],
                edgecolor="#bf7828",
                linewidth=0.7,
                zorder=7,
            )
        )
    for idx in range(5):
        ax.add_patch(
            Rectangle(
                (x - 0.044 * scale + idx * 0.022 * scale, y + 0.027 * scale),
                0.014 * scale,
                0.006 * scale,
                facecolor=COLORS["suex"],
                edgecolor="none",
                zorder=7,
            )
        )


def icon_cast(ax: plt.Axes, x: float, y: float, scale: float) -> None:
    ax.add_patch(
        Rectangle(
            (x - 0.057 * scale, y - 0.025 * scale),
            0.114 * scale,
            0.050 * scale,
            facecolor="#dfe3e9",
            edgecolor="#a9b2bf",
            linewidth=0.8,
            zorder=5,
        )
    )
    ax.add_patch(
        Rectangle(
            (x - 0.048 * scale, y - 0.015 * scale),
            0.096 * scale,
            0.030 * scale,
            facecolor=COLORS["pdms"],
            edgecolor=COLORS["pdms_edge"],
            linewidth=0.8,
            zorder=6,
        )
    )
    for idx in range(4):
        ax.add_patch(
            Rectangle(
                (x - 0.033 * scale + idx * 0.022 * scale, y - 0.011 * scale),
                0.010 * scale,
                0.022 * scale,
                facecolor="#ffffff",
                edgecolor=COLORS["pdms_edge"],
                linewidth=0.6,
                zorder=7,
            )
        )
    ax.add_patch(
        Rectangle(
            (x + 0.015 * scale, y + 0.040 * scale),
            0.065 * scale,
            0.012 * scale,
            angle=-24,
            facecolor="#f0f4f8",
            edgecolor="#95a2b1",
            linewidth=0.8,
            zorder=8,
        )
    )
    ax.add_patch(
        Polygon(
            [
                (x - 0.004 * scale, y + 0.023 * scale),
                (x + 0.010 * scale, y + 0.030 * scale),
                (x + 0.004 * scale, y + 0.012 * scale),
            ],
            closed=True,
            facecolor=COLORS["pdms"],
            edgecolor=COLORS["pdms_edge"],
            linewidth=0.7,
            zorder=9,
        )
    )


def icon_trim(ax: plt.Axes, x: float, y: float, scale: float) -> None:
    ax.add_patch(
        Rectangle(
            (x - 0.052 * scale, y - 0.034 * scale),
            0.104 * scale,
            0.068 * scale,
            facecolor=COLORS["pdms"],
            edgecolor=COLORS["pdms_edge"],
            linewidth=0.9,
            zorder=5,
        )
    )
    ax.add_patch(
        Rectangle(
            (x - 0.042 * scale, y - 0.025 * scale),
            0.084 * scale,
            0.050 * scale,
            facecolor="none",
            edgecolor=COLORS["muted"],
            linewidth=0.9,
            linestyle=(0, (3, 2)),
            zorder=6,
        )
    )
    add_wells(
        ax, x - 0.035 * scale, y - 0.020 * scale, 0.070 * scale, 0.040 * scale, rows=2, cols=4
    )
    ax.add_patch(
        Polygon(
            [
                (x + 0.028 * scale, y + 0.050 * scale),
                (x + 0.066 * scale, y + 0.018 * scale),
                (x + 0.054 * scale, y + 0.008 * scale),
                (x + 0.016 * scale, y + 0.040 * scale),
            ],
            closed=True,
            facecolor="#8a929d",
            edgecolor="#5e6672",
            linewidth=0.8,
            zorder=9,
        )
    )


def icon_bond(ax: plt.Axes, x: float, y: float, scale: float) -> None:
    ax.add_patch(
        Rectangle(
            (x - 0.060 * scale, y - 0.036 * scale),
            0.120 * scale,
            0.022 * scale,
            facecolor=COLORS["glass"],
            edgecolor="#8bb6d1",
            linewidth=0.8,
            zorder=5,
        )
    )
    ax.add_patch(
        Rectangle(
            (x - 0.048 * scale, y - 0.006 * scale),
            0.096 * scale,
            0.036 * scale,
            facecolor=COLORS["pdms"],
            edgecolor=COLORS["pdms_edge"],
            linewidth=0.9,
            zorder=6,
        )
    )
    add_wells(
        ax, x - 0.036 * scale, y + 0.000 * scale, 0.072 * scale, 0.024 * scale, rows=2, cols=4
    )
    for dx in (-0.032, 0.000, 0.032):
        ax.plot(
            [x + dx * scale, x + (dx + 0.008) * scale],
            [y + 0.048 * scale, y + 0.033 * scale],
            color=COLORS["accent"],
            linewidth=1.1,
            zorder=9,
        )
        ax.plot(
            [x + (dx + 0.008) * scale, x + (dx - 0.004) * scale],
            [y + 0.033 * scale, y + 0.035 * scale],
            color=COLORS["accent"],
            linewidth=1.1,
            zorder=9,
        )


def icon_sterilize(ax: plt.Axes, x: float, y: float, scale: float) -> None:
    rounded_box(
        ax,
        x - 0.052 * scale,
        y - 0.040 * scale,
        0.104 * scale,
        0.080 * scale,
        facecolor=COLORS["sterile"],
        edgecolor="#c5aacb",
        linewidth=0.9,
        radius=0.010,
        zorder=5,
    )
    ax.add_patch(
        Rectangle(
            (x - 0.040 * scale, y - 0.020 * scale),
            0.080 * scale,
            0.035 * scale,
            facecolor=COLORS["pdms"],
            edgecolor=COLORS["pdms_edge"],
            linewidth=0.8,
            zorder=6,
        )
    )
    add_wells(
        ax, x - 0.030 * scale, y - 0.015 * scale, 0.060 * scale, 0.024 * scale, rows=2, cols=4
    )
    for yy in (0.024, 0.032):
        ax.plot(
            [x - 0.035 * scale, x + 0.035 * scale],
            [y + yy * scale, y + yy * scale],
            color="#c5aacb",
            linewidth=0.7,
            zorder=7,
        )
    add_text(
        ax, x, y - 0.032 * scale, "121 C", size=5.7 * scale, color=COLORS["muted"], weight="bold"
    )


def icon_frame(ax: plt.Axes, x: float, y: float, scale: float) -> None:
    ax.add_patch(
        Rectangle(
            (x - 0.064 * scale, y - 0.040 * scale),
            0.128 * scale,
            0.080 * scale,
            facecolor=COLORS["frame"],
            edgecolor="#101722",
            linewidth=0.9,
            zorder=5,
        )
    )
    ax.add_patch(
        Rectangle(
            (x - 0.048 * scale, y - 0.026 * scale),
            0.096 * scale,
            0.052 * scale,
            facecolor="#ffffff",
            edgecolor="#101722",
            linewidth=0.7,
            zorder=6,
        )
    )
    ax.add_patch(
        Rectangle(
            (x - 0.040 * scale, y - 0.019 * scale),
            0.080 * scale,
            0.038 * scale,
            facecolor="#efd0d5",
            edgecolor="#bc8992",
            linewidth=0.8,
            zorder=7,
        )
    )
    add_wells(
        ax, x - 0.032 * scale, y - 0.014 * scale, 0.064 * scale, 0.028 * scale, rows=2, cols=4
    )
    for dx in (-0.052, 0.052):
        ax.add_patch(
            Rectangle(
                (x + dx * scale - 0.006 * scale, y - 0.026 * scale),
                0.012 * scale,
                0.052 * scale,
                facecolor=COLORS["glue"],
                edgecolor="#c28f22",
                linewidth=0.6,
                zorder=8,
            )
        )
    ax.add_patch(
        Circle(
            (x + 0.066 * scale, y + 0.043 * scale),
            0.016 * scale,
            facecolor="#fff7d6",
            edgecolor="#c28f22",
            linewidth=0.7,
            zorder=9,
        )
    )
    add_text(
        ax,
        x + 0.066 * scale,
        y + 0.043 * scale,
        "3d",
        size=4.7 * scale,
        color=COLORS["ink"],
        weight="bold",
    )


ICON_DRAWERS = (icon_mold, icon_cast, icon_trim, icon_bond, icon_sterilize, icon_frame)


def draw_step(ax: plt.Axes, step: Step, x: float, y: float, width: float, height: float) -> None:
    rounded_box(ax, x, y, width, height, facecolor="white", edgecolor=COLORS["grid"], linewidth=1.0)
    ax.add_patch(
        Circle(
            (x + 0.025, y + height - 0.030),
            0.017,
            facecolor=COLORS["accent"],
            edgecolor="none",
            zorder=7,
        )
    )
    add_text(
        ax,
        x + 0.025,
        y + height - 0.030,
        str(step.number),
        size=8.0,
        color="white",
        weight="bold",
        zorder=8,
    )
    ICON_DRAWERS[step.number - 1](ax, x + width / 2, y + height * 0.62, 1.0)
    add_text(ax, x + width / 2, y + height * 0.335, step.title, size=9.3, weight="bold", wrap=19)
    add_text(
        ax, x + width / 2, y + height * 0.145, step.detail, size=7.2, color=COLORS["muted"], wrap=28
    )


def draw_frame_branch(ax: plt.Axes) -> None:
    rounded_box(
        ax,
        0.730,
        0.740,
        0.195,
        0.105,
        facecolor=COLORS["paper"],
        edgecolor=COLORS["grid"],
        linewidth=1.0,
    )
    ax.add_patch(
        Rectangle(
            (0.747, 0.768),
            0.048,
            0.032,
            facecolor=COLORS["frame"],
            edgecolor="#101722",
            linewidth=0.8,
            zorder=5,
        )
    )
    ax.add_patch(
        Rectangle(
            (0.756, 0.776),
            0.030,
            0.016,
            facecolor="white",
            edgecolor="#101722",
            linewidth=0.6,
            zorder=6,
        )
    )
    add_text(ax, 0.826, 0.806, "HIPS frame", size=8.0, ha="left", weight="bold")
    add_text(
        ax,
        0.826,
        0.778,
        "printed and ethanol-sterilized",
        size=7.2,
        color=COLORS["muted"],
        ha="left",
    )
    add_arrow(ax, (0.827, 0.740), (0.895, 0.690), color=COLORS["accent"])


def draw_timeline() -> None:
    fig, ax = plt.subplots(figsize=(13.2, 4.8))
    setup_axis(ax)

    add_text(
        ax,
        0.040,
        0.945,
        "Post-mold device replication and assembly",
        size=15.0,
        ha="left",
        weight="bold",
    )
    add_text(
        ax,
        0.040,
        0.892,
        "From the parylene-coated hybrid mold to an assembly-ready framed PDMS device.",
        size=9.0,
        color=COLORS["muted"],
        ha="left",
    )

    ax.plot([0.040, 0.960], [0.863, 0.863], color=COLORS["grid"], linewidth=1.0)

    left = 0.035
    gap = 0.017
    width = (0.930 - gap * 5) / 6
    height = 0.500
    y = 0.165
    xs = [left + idx * (width + gap) for idx in range(6)]

    for step, x in zip(STEPS, xs, strict=True):
        draw_step(ax, step, x, y, width, height)

    for idx in range(5):
        add_arrow(
            ax,
            (xs[idx] + width + 0.004, y + height * 0.62),
            (xs[idx + 1] - 0.004, y + height * 0.62),
        )

    draw_frame_branch(ax)

    rounded_box(
        ax,
        0.040,
        0.045,
        0.445,
        0.060,
        facecolor=COLORS["paper"],
        edgecolor=COLORS["grid"],
        linewidth=0.8,
    )
    rounded_box(
        ax,
        0.515,
        0.045,
        0.445,
        0.060,
        facecolor=COLORS["paper"],
        edgecolor=COLORS["grid"],
        linewidth=0.8,
    )
    add_text(
        ax,
        0.058,
        0.075,
        "Upstream mold:",
        size=7.6,
        color=COLORS["muted"],
        ha="left",
        weight="bold",
    )
    add_text(
        ax,
        0.205,
        0.075,
        "SU-8/SUEX, insert bonding, parylene coating",
        size=7.6,
        color=COLORS["muted"],
        ha="left",
    )
    add_text(
        ax,
        0.533,
        0.075,
        "Repeated assembly:",
        size=7.6,
        color=COLORS["muted"],
        ha="left",
        weight="bold",
    )
    add_text(
        ax,
        0.700,
        0.075,
        "PDMS casting, glass bonding, frame, final plasma clean",
        size=7.6,
        color=COLORS["muted"],
        ha="left",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / f"{OUTPUT_STEM}.pdf", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(OUTPUT_DIR / f"{OUTPUT_STEM}.png", bbox_inches="tight", pad_inches=0.04, dpi=DPI)
    plt.close(fig)


def main() -> int:
    draw_timeline()
    print(f"Wrote {OUTPUT_DIR / f'{OUTPUT_STEM}.pdf'}")
    print(f"Wrote {OUTPUT_DIR / f'{OUTPUT_STEM}.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
