#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import ezdxf
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


@dataclass(frozen=True)
class PanelSpec:
    key: str
    title: str
    tail_tokens: tuple[str, ...]


PANEL_SPECS = {
    "aligned": PanelSpec("aligned", "Full aligned layout", ("aligned",)),
    "single_aligned": PanelSpec(
        "single_aligned",
        "Single-device aligned layout",
        ("single", "aligned"),
    ),
    "top": PanelSpec("top", "Top layout", ("top",)),
    "single_top": PanelSpec("single_top", "Single-device top detail", ("single", "top")),
    "bottom": PanelSpec("bottom", "Bottom layout", ("bottom",)),
    "single_bottom": PanelSpec(
        "single_bottom",
        "Single-device bottom detail",
        ("single", "bottom"),
    ),
}

DEFAULT_PANELS = (PANEL_SPECS["aligned"], PANEL_SPECS["single_top"])
DRAWING_CONFIG = Configuration.defaults().with_changes(
    color_policy=ColorPolicy.MONOCHROME,
    custom_fg_color="#1a1a1a",
    background_policy=BackgroundPolicy.CUSTOM,
    custom_bg_color="#ffffff",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a reusable side-by-side comparison figure from open_chamber DXF outputs.",
    )
    parser.add_argument("left", type=Path, help="Left design folder")
    parser.add_argument("right", type=Path, help="Right design folder")
    parser.add_argument("output", type=Path, help="Output PNG path")
    parser.add_argument("--left-label", default=None, help="Override label for the left design")
    parser.add_argument("--right-label", default=None, help="Override label for the right design")
    parser.add_argument(
        "--title",
        default="Open chamber design comparison",
        help="Figure title",
    )
    parser.add_argument(
        "--panel",
        choices=sorted(PANEL_SPECS),
        action="append",
        dest="panel_keys",
        help="Panel types to include; default is aligned + single_top",
    )
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        help="Optional note line shown below the figure",
    )
    return parser.parse_args()


def resolve_panel_path(folder: Path, panel: PanelSpec) -> Path:
    matches = []
    for candidate in sorted(folder.glob("*.dxf")):
        tokens = tuple(candidate.stem.split("_"))
        if tokens[-len(panel.tail_tokens) :] == panel.tail_tokens:
            if not panel.key.startswith("single_") and len(tokens) > len(panel.tail_tokens):
                if tokens[-len(panel.tail_tokens) - 1] == "single":
                    continue
            matches.append(candidate)
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one DXF ending in {panel.tail_tokens} in {folder}, found {len(matches)}"
        )
    return matches[0]


def render_dxf(ax: plt.Axes, path: Path) -> None:
    doc = ezdxf.readfile(path)
    ctx = RenderContext(doc)
    backend = MatplotlibBackend(ax)
    Frontend(ctx, backend, config=DRAWING_CONFIG).draw_layout(doc.modelspace(), finalize=True)
    ax.set_aspect("equal")
    ax.autoscale_view()
    ax.axis("off")


def build_comparison_figure(
    left_folder: Path,
    right_folder: Path,
    output_path: Path,
    title: str,
    left_label: str,
    right_label: str,
    panels: tuple[PanelSpec, ...],
    notes: list[str],
) -> None:
    note_lines = len(notes)
    footer_height = 0.6 if note_lines else 0.2
    fig_height = 4.3 * len(panels) + footer_height

    fig, axes = plt.subplots(
        nrows=len(panels),
        ncols=2,
        figsize=(12, fig_height),
        dpi=220,
        squeeze=False,
    )
    fig.patch.set_facecolor("white")
    fig.suptitle(title, fontsize=16, fontweight="bold", y=0.975)

    for x_pos, label in ((0.31, left_label), (0.74, right_label)):
        fig.text(x_pos, 0.915, label, fontsize=13, fontweight="bold", ha="center")

    for row, panel in enumerate(panels):
        left_path = resolve_panel_path(left_folder, panel)
        right_path = resolve_panel_path(right_folder, panel)
        render_dxf(axes[row][0], left_path)
        render_dxf(axes[row][1], right_path)
        fig.text(
            0.015,
            0.86 - row * (0.82 / max(len(panels), 1)),
            panel.title,
            fontsize=12,
            fontweight="bold",
            va="center",
            ha="left",
        )

    if notes:
        note_text = "\n".join(f"- {note}" for note in notes)
        fig.text(
            0.06,
            0.025,
            note_text,
            fontsize=10,
            va="bottom",
            ha="left",
        )

    plt.subplots_adjust(
        left=0.09, right=0.98, top=0.84, bottom=0.08 if notes else 0.04, hspace=0.18
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight", facecolor="white")
    fig.savefig(output_path.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> int:
    args = parse_args()
    panels = (
        tuple(PANEL_SPECS[key] for key in args.panel_keys) if args.panel_keys else DEFAULT_PANELS
    )
    build_comparison_figure(
        left_folder=args.left,
        right_folder=args.right,
        output_path=args.output,
        title=args.title,
        left_label=args.left_label or args.left.name,
        right_label=args.right_label or args.right.name,
        panels=panels,
        notes=args.note,
    )
    print(f"Wrote {args.output}")
    print(f"Wrote {args.output.with_suffix('.pdf')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
