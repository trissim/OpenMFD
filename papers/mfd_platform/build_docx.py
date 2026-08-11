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
TMP_DOCX_MD = BUILD_DIR / "paper_for_docx.md"
TMP_PDF_MD = BUILD_DIR / "paper_for_pdf.md"
OUTPUT_DOCX = BUILD_DIR / "paper_review.docx"
OUTPUT_PDF = BUILD_DIR / "paper_review.pdf"
PAPER_RENDERED_PREFIX = Path("figures") / "rendered"
DOCX_RENDERED_PREFIX = Path("..") / "figures" / "rendered_docx"
PDF_RENDERED_PREFIX = Path("..") / "figures" / "rendered"
README_NAME = "README.md"
WORD_DOCUMENT_XML = "word/document.xml"
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
TABLE_FONT_SIZE_HALF_POINTS = "20"
TABLE_BORDER_SIZE_EIGHTH_POINTS = "4"
TABLE_BORDER_COLOR = "808080"
SUPPLEMENTARY_DIR = ROOT / "supplementary"
SUPPLEMENTARY_FILES = (
    SUPPLEMENTARY_DIR / "Supplementary_Table_S1_pin_z_variability.md",
    SUPPLEMENTARY_DIR / "Supplementary_Table_S2_fabrication_strategies.md",
    SUPPLEMENTARY_DIR / "Supplementary_Table_S3_design_limits.md",
    SUPPLEMENTARY_DIR / "Supplementary_Table_S4_resin_insert_printing_settings.md",
    SUPPLEMENTARY_DIR / "Supplementary_Table_S5_process_qc.md",
    SUPPLEMENTARY_DIR / "Supplementary_Note_S1_LP360_filter.md",
    SUPPLEMENTARY_DIR / "Supplementary_Note_S2_base_layer_adhesion.md",
    SUPPLEMENTARY_DIR / "Supplementary_Protocol_S1_device_assembly_culture_and_CTB.md",
    SUPPLEMENTARY_DIR / "Supplementary_Protocol_S2_hybrid_mold_fabrication.md",
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


def build_figure_reference_map(
    rendered_prefix: Path,
    *,
    convert_pdf_to_png: bool,
) -> dict[str, str]:
    references: dict[str, str] = {}

    for path in FIGURES_RENDERED.iterdir():
        if path.name == README_NAME:
            continue

        source_ref = (PAPER_RENDERED_PREFIX / path.name).as_posix()
        if convert_pdf_to_png and path.suffix.lower() == ".pdf":
            target_name = f"{path.stem}.png"
        else:
            target_name = path.name

        destination_ref = (rendered_prefix / target_name).as_posix()
        references[source_ref] = destination_ref
        references[f"../{source_ref}"] = destination_ref

    return references


def build_source_text() -> str:
    sections = [SOURCE_MD.read_text()]

    supplementary_sections = [
        file_path.read_text() for file_path in SUPPLEMENTARY_FILES if file_path.exists()
    ]
    if supplementary_sections:
        sections.append("## Supplementary Information")
        sections.extend(supplementary_sections)

    return "\n\n".join(sections)


def rewrite_references(text: str, reference_map: dict[str, str]) -> str:
    placeholders: dict[str, str] = {}

    for index, (source_ref, destination_ref) in enumerate(sorted(
        reference_map.items(), key=lambda item: len(item[0]), reverse=True
    )):
        placeholder = f"__OPENMFD_REFERENCE_{index}__"
        text = text.replace(source_ref, placeholder)
        placeholders[placeholder] = destination_ref

    for placeholder, destination_ref in placeholders.items():
        text = text.replace(placeholder, destination_ref)

    text = text.replace(
        f"({SUPPLEMENTARY_MEDIA_PREFIX}",
        f"({DOCX_SUPPLEMENTARY_MEDIA_PREFIX}",
    )
    text = text.replace(
        f'src="{SUPPLEMENTARY_MEDIA_PREFIX}',
        f'src="{DOCX_SUPPLEMENTARY_MEDIA_PREFIX}',
    )

    return text


def build_temp_markdown() -> None:
    source_text = build_source_text()

    docx_text = rewrite_references(
        source_text,
        build_figure_reference_map(DOCX_RENDERED_PREFIX, convert_pdf_to_png=True),
    )
    pdf_text = rewrite_references(
        source_text,
        build_figure_reference_map(PDF_RENDERED_PREFIX, convert_pdf_to_png=False),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DOCX_MD.write_text(docx_text)
    TMP_PDF_MD.write_text(pdf_text)


def build_docx() -> None:
    run(["pandoc", str(TMP_DOCX_MD.name), "-o", str(OUTPUT_DOCX.name)], cwd=BUILD_DIR)


def build_pdf_from_docx() -> bool:
    converter = shutil.which("libreoffice") or shutil.which("soffice")
    if converter is None:
        return False

    if OUTPUT_PDF.exists():
        OUTPUT_PDF.unlink()

    run(
        [
            converter,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(BUILD_DIR),
            str(OUTPUT_DOCX),
        ],
        cwd=ROOT,
    )

    if not OUTPUT_PDF.exists():
        raise RuntimeError(f"LibreOffice did not create expected PDF: {OUTPUT_PDF}")

    return True


def build_pdf_with_pandoc() -> None:
    errors: list[str] = []

    for engine in ("lualatex", "xelatex", "pdflatex"):
        if shutil.which(engine) is None:
            continue

        try:
            run(
                [
                    "pandoc",
                    str(TMP_PDF_MD.name),
                    f"--pdf-engine={engine}",
                    "-V",
                    "geometry:margin=0.75in",
                    "-o",
                    str(OUTPUT_PDF.name),
                ],
                cwd=BUILD_DIR,
            )
            return
        except subprocess.CalledProcessError as exc:
            errors.append(f"{engine}: exit status {exc.returncode}")

    attempted = "; ".join(errors) if errors else "no supported PDF engine found"
    raise RuntimeError(f"Could not build PDF review copy ({attempted})")


def build_pdf() -> None:
    if build_pdf_from_docx():
        return

    build_pdf_with_pandoc()


def word_tag(tag_name: str) -> str:
    return f"{{{WORD_NAMESPACE}}}{tag_name}"


def style_docx_tables() -> None:
    namespace = {"w": WORD_NAMESPACE}
    ET.register_namespace("w", WORD_NAMESPACE)

    with zipfile.ZipFile(OUTPUT_DOCX, "r") as source_zip:
        document_xml = source_zip.read(WORD_DOCUMENT_XML)

        root = ET.fromstring(document_xml)

        for table in root.findall(".//w:tbl", namespace):
            properties = table.find("w:tblPr", namespace)
            if properties is None:
                properties = ET.Element(word_tag("tblPr"))
                table.insert(0, properties)

            borders = properties.find("w:tblBorders", namespace)
            if borders is None:
                borders = ET.SubElement(properties, word_tag("tblBorders"))

            for border_name in ("top", "left", "bottom", "right", "insideH", "insideV"):
                border = borders.find(f"w:{border_name}", namespace)
                if border is None:
                    border = ET.SubElement(borders, word_tag(border_name))
                border.set(word_tag("val"), "single")
                border.set(word_tag("sz"), TABLE_BORDER_SIZE_EIGHTH_POINTS)
                border.set(word_tag("space"), "0")
                border.set(word_tag("color"), TABLE_BORDER_COLOR)

            for row in table.findall("w:tr", namespace):
                row_properties = row.find("w:trPr", namespace)
                if row_properties is None:
                    row_properties = ET.Element(word_tag("trPr"))
                    row.insert(0, row_properties)
                if row_properties.find("w:cantSplit", namespace) is None:
                    ET.SubElement(row_properties, word_tag("cantSplit"))

        for run in root.findall(".//w:tbl//w:r", namespace):
            properties = run.find("w:rPr", namespace)
            if properties is None:
                properties = ET.Element(word_tag("rPr"))
                run.insert(0, properties)

            for tag_name in ("sz", "szCs"):
                size = properties.find(f"w:{tag_name}", namespace)
                if size is None:
                    size = ET.SubElement(properties, word_tag(tag_name))
                size.set(word_tag("val"), TABLE_FONT_SIZE_HALF_POINTS)

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
    style_docx_tables()
    build_pdf()
    print(f"DOCX written to {OUTPUT_DOCX}")
    print(f"PDF written to {OUTPUT_PDF}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
