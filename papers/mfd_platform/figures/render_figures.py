#!/usr/bin/env python3
"""Publish declared figure pairs without resurrecting historical ODPs."""
from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FINAL_DROP = ROOT / "final_drop"
RENDERED = ROOT / "rendered"
RENDERED_DOCX = ROOT / "rendered_docx"


@dataclass(frozen=True)
class FigureRenderSpec:
    """A retained document figure already owns its published PDF/PNG pair."""
    rendered_name: str

    @property
    def published_pdf(self) -> Path:
        return RENDERED / self.rendered_name

    @property
    def published_png(self) -> Path:
        return RENDERED_DOCX / Path(self.rendered_name).with_suffix(".png").name

    @property
    def source_pdf(self) -> Path:
        return self.published_pdf

    @property
    def source_png(self) -> Path:
        return self.published_png

    def generate_source(self) -> None:
        """Retained figures have no executable authoring step."""

    def write_outputs(self) -> None:
        """The retained pair is already published."""

    def publish(self) -> None:
        """Validate both formats before writing either."""
        for source in (self.source_pdf, self.source_png):
            if not source.is_file():
                raise FileNotFoundError(f"Missing authored figure output: {source}")
        self.write_outputs()


@dataclass(frozen=True, kw_only=True)
class GeneratedFigure(FigureRenderSpec):
    folder_name: str
    script: Path
    source_stem: str = "draft_figure"

    @property
    def source_base(self) -> Path:
        return FINAL_DROP / self.folder_name / self.source_stem

    @property
    def source_pdf(self) -> Path:
        return self.source_base.with_suffix(".pdf")

    @property
    def source_png(self) -> Path:
        return self.source_base.with_suffix(".png")

    def generate_source(self) -> None:
        subprocess.run([sys.executable, str(self.script)], check=True)

    def write_outputs(self) -> None:
        RENDERED.mkdir(parents=True, exist_ok=True)
        RENDERED_DOCX.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.source_pdf, self.published_pdf)
        shutil.copy2(self.source_png, self.published_png)


# Authored manuscript order, not type discovery. Producers belong to their figures.
FIGURE_SPECS = (
    GeneratedFigure(
        "openmfd_design.pdf", folder_name="Fig1_openmfd_design",
        script=ROOT / "generate_openmfd_design_figure.py",
    ),
    GeneratedFigure(
        "insert_bonding.pdf", folder_name="Fig2_insert_bonding",
        script=ROOT / "generate_bonding_fixture_figure.py",
    ),
    GeneratedFigure(
        "mold_casts_package.pdf", folder_name="Fig4_mold_casts_package",
        source_stem="assembly_protocol_schematic",
        script=ROOT / "generate_device_assembly_protocol.py",
    ),
    GeneratedFigure(
        "validation.pdf", folder_name="Fig5_plate_layout_validation",
        script=ROOT / "generate_validation_figure.py",
    ),
    GeneratedFigure(
        "generalizability.pdf", folder_name="Fig6_generalizability",
        script=ROOT / "generate_generalizability_figure.py",
    ),
    FigureRenderSpec("supp_fig_s1_no_lp360.pdf"),
    FigureRenderSpec("supp_fig_s2_delamination.pdf"),
)


def main() -> int:
    for spec in FIGURE_SPECS:
        spec.generate_source()
    for spec in FIGURE_SPECS:
        spec.publish()
    print(f"Rendered figures written to {RENDERED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
