#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
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
CAPTION_FONT_SIZE_PT = 11
SUPPLEMENTARY_DIR = ROOT / "supplementary"
SUPPLEMENTARY_FILES = (
    SUPPLEMENTARY_DIR / "Supplementary_Table_S1_pin_z_variability.md",
    SUPPLEMENTARY_DIR / "Supplementary_Table_S2_fabrication_strategies.md",
    SUPPLEMENTARY_DIR / "Supplementary_Table_S3_design_limits.md",
    SUPPLEMENTARY_DIR / "Supplementary_Table_S4_resin_insert_printing_settings.md",
    SUPPLEMENTARY_DIR / "Supplementary_Table_S5_process_qc.md",
    SUPPLEMENTARY_DIR / "Supplementary_Table_S6_FDM_frame_printing_settings.md",
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


def move_main_figures_after_text(root: ET.Element) -> None:
    """Keep review prose continuous without shrinking full-page figures."""
    body = root.find(word_tag("body"))
    if body is None:
        return
    blocks = list(body)
    boundary = next((block for block in blocks
                     if "".join(node.text or "" for node in block.iter(word_tag("t")))
                     == "Supplementary Information"), None)
    if boundary is None:
        boundary = body.find(word_tag("sectPr"))
    limit = blocks.index(boundary) if boundary is not None else len(blocks)
    figures = []
    for figure, caption in zip(blocks[:limit], blocks[1:limit]):
        style = caption.find(f"{word_tag('pPr')}/{word_tag('pStyle')}")
        if (figure.find(f".//{word_tag('drawing')}") is not None
                and style is not None and style.get(word_tag("val")) == "ImageCaption"):
            figures.extend((figure, caption))
    for block in figures:
        body.remove(block)
    index = list(body).index(boundary) if boundary is not None else len(body)
    for offset, block in enumerate(figures):
        body.insert(index + offset, block)


def fit_docx_figures(root: ET.Element) -> None:
    namespaces = {
        "w": WORD_NAMESPACE,
        "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    }
    section = root.find(".//w:sectPr", namespaces)
    if section is None:
        raise ValueError("Document has no page setup")
    # Make the page budget explicit instead of relying on the Word/Writer default.
    for name, defaults in (
        ("pgSz", {"w": "12240", "h": "15840"}),
        ("pgMar", {"top": "1440", "bottom": "1440", "left": "1440", "right": "1440"}),
    ):
        element = section.find(word_tag(name))
        if element is None:
            element = ET.SubElement(section, word_tag(name))
        for key, value in defaults.items():
            if element.get(word_tag(key)) is None:
                element.set(word_tag(key), value)
    size = section.find(word_tag("pgSz"))
    margins = section.find(word_tag("pgMar"))
    width_pt = (int(size.get(word_tag("w"))) - int(margins.get(word_tag("left")))
                - int(margins.get(word_tag("right")))) / 20
    height_pt = (int(size.get(word_tag("h"))) - int(margins.get(word_tag("top")))
                 - int(margins.get(word_tag("bottom")))) / 20
    body = root.find("w:body", namespaces)
    paragraphs = list(body)
    for figure, caption in zip(paragraphs, paragraphs[1:]):
        inline = figure.find(".//wp:inline", namespaces)
        style = caption.find("w:pPr/w:pStyle", namespaces)
        if inline is None or style is None or style.get(word_tag("val")) != "ImageCaption":
            continue
        for paragraph, flags in ((figure, ("keepNext", "keepLines")),
                                 (caption, ("keepLines",))):
            properties = paragraph.find(word_tag("pPr"))
            if properties is None:
                properties = ET.Element(word_tag("pPr"))
                paragraph.insert(0, properties)
            for flag in flags:
                element = properties.find(word_tag(flag))
                if element is None:
                    element = ET.SubElement(properties, word_tag(flag))
                element.set(word_tag("val"), "1")
        properties = figure.find(word_tag("pPr"))
        alignment = properties.find(word_tag("jc"))
        if alignment is None:
            alignment = ET.SubElement(properties, word_tag("jc"))
        alignment.set(word_tag("val"), "center")
        for run in caption.findall(".//w:r", namespaces):
            properties = run.find(word_tag("rPr"))
            if properties is None:
                properties = ET.Element(word_tag("rPr"))
                run.insert(0, properties)
            for name in ("sz", "szCs"):
                size = properties.find(word_tag(name))
                if size is None:
                    size = ET.SubElement(properties, word_tag(name))
                size.set(word_tag("val"), str(2 * CAPTION_FONT_SIZE_PT))
        # Reserve caption space using the same font size applied above.
        text = "".join(node.text or "" for node in caption.findall(".//w:t", namespaces))
        lines = math.ceil(len(text) / max(1, int(width_pt / (CAPTION_FONT_SIZE_PT * 0.55))))
        max_height_pt = height_pt - (lines * CAPTION_FONT_SIZE_PT * 1.25 + 30)
        if max_height_pt <= 0:
            raise ValueError("Figure caption is too long to share a page with its image")
        extent = inline.find("wp:extent", namespaces)
        width, height = int(extent.get("cx")), int(extent.get("cy"))
        scale = min(1.0, max_height_pt * 12700 / height, width_pt * 12700 / width)
        for element in [extent, *inline.findall(".//a:xfrm/a:ext", namespaces)]:
            element.set("cx", str(round(width * scale)))
            element.set("cy", str(round(height * scale)))


def style_docx_document() -> None:
    namespace = {"w": WORD_NAMESPACE}
    ET.register_namespace("w", WORD_NAMESPACE)

    with zipfile.ZipFile(OUTPUT_DOCX, "r") as source_zip:
        document_xml = source_zip.read(WORD_DOCUMENT_XML)

        root = ET.fromstring(document_xml)
        move_main_figures_after_text(root)
        fit_docx_figures(root)

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
    parser = argparse.ArgumentParser(description="Build the manuscript and supplementary DOCX/PDF.")
    parser.add_argument(
        "--skip-figures", action="store_true",
        help="Reuse existing rendered figures for text-only revisions.",
    )
    args = parser.parse_args()
    if not args.skip_figures:
        render_figures()
    sync_docx_figures()
    build_temp_markdown()
    build_docx()
    style_docx_document()
    build_pdf()
    print(f"DOCX written to {OUTPUT_DOCX}")
    print(f"PDF written to {OUTPUT_PDF}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
