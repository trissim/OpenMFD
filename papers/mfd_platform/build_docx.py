#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIGURES_RENDERED = ROOT / "figures" / "rendered"
DOCX_FIGURES = ROOT / "figures" / "rendered_docx"
BUILD_DIR = ROOT / "build"
SOURCE_MD = ROOT / "paper.md"
TMP_MD = BUILD_DIR / "paper_for_docx.md"
OUTPUT_DOCX = BUILD_DIR / "paper_review.docx"
PAPER_RENDERED_PREFIX = Path("figures") / "rendered"
DOCX_RENDERED_PREFIX = Path("..") / "figures" / "rendered_docx"
README_NAME = "README.md"
WORD_DOCUMENT_XML = "word/document.xml"
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
TABLE_FONT_SIZE_HALF_POINTS = "20"
SUPPLEMENTARY_DIR = ROOT / "supplementary"
SUPPLEMENTARY_FILES = (
    SUPPLEMENTARY_DIR / "Supplementary_Table_S1_pin_z_variability.md",
    SUPPLEMENTARY_DIR / "Supplementary_Note_S1_LP360_filter.md",
    SUPPLEMENTARY_DIR / "Supplementary_Note_S2_base_layer_adhesion.md",
    SUPPLEMENTARY_DIR / "Protocol_S1_device_assembly_and_axotomy.md",
)
SUPPLEMENTARY_MEDIA_PREFIX = "media/"
DOCX_SUPPLEMENTARY_MEDIA_PREFIX = "../supplementary/media/"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, check=True, cwd=cwd)


def render_figures() -> None:
    run([sys.executable, str(ROOT / "figures" / "render_figures.py")], cwd=ROOT)


def pdf_to_png(source: Path, destination: Path) -> None:
    need_render = not destination.exists() or source.stat().st_mtime > destination.stat().st_mtime
    if not need_render:
        return

    run(
        [
            "pdftoppm",
            "-png",
            "-singlefile",
            str(source),
            str(destination.with_suffix("")),
        ]
    )


def sync_docx_figures() -> None:
    DOCX_FIGURES.mkdir(parents=True, exist_ok=True)

    expected_outputs: set[str] = set()

    for path in FIGURES_RENDERED.iterdir():
        if path.name == README_NAME:
            continue
        if path.suffix.lower() == ".pdf":
            expected_outputs.add(f"{path.stem}.png")
        else:
            expected_outputs.add(path.name)

    for path in DOCX_FIGURES.iterdir():
        if path.name not in expected_outputs:
            path.unlink()

    for path in FIGURES_RENDERED.iterdir():
        if path.name == README_NAME:
            continue
        if path.suffix.lower() == ".pdf":
            pdf_to_png(path, DOCX_FIGURES / f"{path.stem}.png")
        else:
            shutil.copy2(path, DOCX_FIGURES / path.name)


def build_docx_reference_map() -> dict[str, str]:
    references: dict[str, str] = {}

    for path in FIGURES_RENDERED.iterdir():
        if path.name == README_NAME:
            continue

        source_ref = (PAPER_RENDERED_PREFIX / path.name).as_posix()
        if path.suffix.lower() == ".pdf":
            target_name = f"{path.stem}.png"
        else:
            target_name = path.name

        destination_ref = (DOCX_RENDERED_PREFIX / target_name).as_posix()
        references[source_ref] = destination_ref
        references[f"../{source_ref}"] = destination_ref

    return references


def build_temp_markdown() -> None:
    sections = [SOURCE_MD.read_text()]

    supplementary_sections = [
        file_path.read_text() for file_path in SUPPLEMENTARY_FILES if file_path.exists()
    ]
    if supplementary_sections:
        sections.append("## Supplementary Information")
        sections.extend(supplementary_sections)

    text = "\n\n".join(sections)

    reference_map = build_docx_reference_map()
    for source_ref, destination_ref in sorted(
        reference_map.items(), key=lambda item: len(item[0]), reverse=True
    ):
        text = text.replace(source_ref, destination_ref)

    text = text.replace(
        f"({SUPPLEMENTARY_MEDIA_PREFIX}",
        f"({DOCX_SUPPLEMENTARY_MEDIA_PREFIX}",
    )
    text = text.replace(
        f'src="{SUPPLEMENTARY_MEDIA_PREFIX}',
        f'src="{DOCX_SUPPLEMENTARY_MEDIA_PREFIX}',
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    TMP_MD.write_text(text)


def build_docx() -> None:
    run(["pandoc", str(TMP_MD.name), "-o", str(OUTPUT_DOCX.name)], cwd=BUILD_DIR)


def shrink_table_font_size() -> None:
    namespace = {"w": WORD_NAMESPACE}
    ET.register_namespace("w", WORD_NAMESPACE)

    with zipfile.ZipFile(OUTPUT_DOCX, "r") as source_zip:
        document_xml = source_zip.read(WORD_DOCUMENT_XML)

        root = ET.fromstring(document_xml)
        for run in root.findall(".//w:tbl//w:r", namespace):
            properties = run.find("w:rPr", namespace)
            if properties is None:
                properties = ET.Element(f"{{{WORD_NAMESPACE}}}rPr")
                run.insert(0, properties)

            for tag_name in ("sz", "szCs"):
                size = properties.find(f"w:{tag_name}", namespace)
                if size is None:
                    size = ET.SubElement(properties, f"{{{WORD_NAMESPACE}}}{tag_name}")
                size.set(f"{{{WORD_NAMESPACE}}}val", TABLE_FONT_SIZE_HALF_POINTS)

        updated_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

        temp_docx = OUTPUT_DOCX.with_suffix(".tmp.docx")
        with zipfile.ZipFile(temp_docx, "w") as dest_zip:
            for entry in source_zip.infolist():
                data = (
                    updated_xml
                    if entry.filename == WORD_DOCUMENT_XML
                    else source_zip.read(entry.filename)
                )
                dest_zip.writestr(entry, data)

    temp_docx.replace(OUTPUT_DOCX)


def main() -> int:
    render_figures()
    sync_docx_figures()
    build_temp_markdown()
    build_docx()
    shrink_table_font_size()
    print(f"DOCX written to {OUTPUT_DOCX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
