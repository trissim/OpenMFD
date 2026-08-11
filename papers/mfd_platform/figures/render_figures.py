#!/usr/bin/env python3

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
README_NAME = "README.md"
LIBREOFFICE_CMD = "libreoffice"
DRAFT_FIGURE_STEM = "draft_figure"
PREFERRED_SOURCE_STEMS = (DRAFT_FIGURE_STEM,)
GENERATED_SOURCE_SCRIPTS = (
    ROOT / "generate_openmfd_design_figure.py",
    ROOT / "generate_bonding_fixture_figure.py",
    ROOT / "generate_device_assembly_protocol.py",
    ROOT / "generate_validation_figure.py",
    ROOT / "generate_generalizability_figure.py",
)


@dataclass(frozen=True)
class FigureRenderSpec:
    folder_name: str
    rendered_name: str
    source_stem: str = DRAFT_FIGURE_STEM


FIGURE_SPECS = (
    FigureRenderSpec("Fig1_openmfd_design", "openmfd_design.pdf"),
    FigureRenderSpec("Fig2_insert_bonding", "insert_bonding.pdf"),
    FigureRenderSpec(
        "Fig4_mold_casts_package",
        "mold_casts_package.pdf",
        "assembly_protocol_schematic",
    ),
    FigureRenderSpec("Fig5_plate_layout_validation", "validation.pdf"),
    FigureRenderSpec("Fig6_generalizability", "generalizability.pdf"),
    FigureRenderSpec("Supp_FigS1_noLP360", "supp_fig_s1_no_lp360.pdf"),
    FigureRenderSpec("Supp_FigS2_delamination", "supp_fig_s2_delamination.pdf"),
)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def source_stems(spec: FigureRenderSpec) -> tuple[str, ...]:
    return (spec.source_stem,)


def resolve_source_base(spec: FigureRenderSpec) -> Path:
    folder = FINAL_DROP / spec.folder_name

    for stem in source_stems(spec):
        base = folder / stem
        if base.with_suffix(".pdf").exists() or base.with_suffix(".odp").exists():
            return base

    stems = ", ".join(source_stems(spec))
    raise FileNotFoundError(f"No figure source found in {folder} for stems: {stems}")


def export_odp_to_pdf(source_odp: Path, destination_pdf: Path) -> None:
    run(
        [
            LIBREOFFICE_CMD,
            "--headless",
            "--convert-to",
            "pdf",
            str(source_odp),
            "--outdir",
            str(source_odp.parent),
        ]
    )

    if not destination_pdf.exists():
        raise FileNotFoundError(f"Expected exported PDF not found for {source_odp}")


def ensure_source_pdf(source_base: Path) -> Path:
    source_pdf = source_base.with_suffix(".pdf")
    source_odp = source_base.with_suffix(".odp")

    if source_odp.exists():
        need_export = (
            not source_pdf.exists() or source_odp.stat().st_mtime > source_pdf.stat().st_mtime
        )
        if need_export:
            export_odp_to_pdf(source_odp, source_pdf)

    if not source_pdf.exists():
        raise FileNotFoundError(f"No PDF source available for {source_base}")

    return source_pdf


def clean_rendered_directory(expected_files: set[str]) -> None:
    RENDERED.mkdir(parents=True, exist_ok=True)

    for path in RENDERED.iterdir():
        if path.name == README_NAME:
            continue
        if path.name not in expected_files:
            path.unlink()


def generate_scripted_sources() -> None:
    for script in GENERATED_SOURCE_SCRIPTS:
        run([sys.executable, str(script)])


def render_figure(spec: FigureRenderSpec) -> None:
    source_base = resolve_source_base(spec)
    source_pdf = ensure_source_pdf(source_base)
    shutil.copy2(source_pdf, RENDERED / spec.rendered_name)

    source_png = source_base.with_suffix(".png")
    if source_png.exists():
        RENDERED_DOCX.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_png, RENDERED_DOCX / Path(spec.rendered_name).with_suffix(".png").name)


def main() -> int:
    generate_scripted_sources()

    expected_files = {spec.rendered_name for spec in FIGURE_SPECS}
    clean_rendered_directory(expected_files)

    for spec in FIGURE_SPECS:
        render_figure(spec)

    print(f"Rendered figures written to {RENDERED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
