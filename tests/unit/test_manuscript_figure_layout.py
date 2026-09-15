import importlib
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest


@pytest.fixture
def builder(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "papers/mfd_platform"))
    return importlib.import_module("build_docx")


def document(builder, height, caption_style="ImageCaption"):
    return ET.fromstring(f'''<w:document xmlns:w="{builder.WORD_NAMESPACE}"
        xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
        xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
      <w:body><w:p><w:r><w:drawing><wp:inline>
        <wp:extent cx="5334000" cy="{height}"/>
        <a:xfrm><a:ext cx="5334000" cy="{height}"/></a:xfrm>
      </wp:inline></w:drawing></w:r></w:p>
      <w:p><w:pPr><w:pStyle w:val="{caption_style}"/></w:pPr>
        <w:r><w:t>{"Caption text. " * 80}</w:t></w:r></w:p>
      <w:sectPr/></w:body></w:document>''')


@pytest.mark.unit
@pytest.mark.parametrize("height", [2000000, 8001000])
def test_captioned_figure_fits_preserves_aspect_and_stays_with_caption(builder, height):
    root = document(builder, height)
    builder.fit_docx_figures(root)
    extent, drawing_extent = [node for node in root.iter() if node.tag.endswith(("}extent", "}ext"))]
    assert extent.attrib == drawing_extent.attrib
    assert int(extent.get("cx")) / int(extent.get("cy")) == pytest.approx(5334000 / height)
    if height == 2000000:
        assert int(extent.get("cy")) == height
    else:
        assert int(extent.get("cy")) < height
    paragraphs = list(root.find(builder.word_tag("body")))[:2]
    assert paragraphs[0].find(".//" + builder.word_tag("keepNext")) is not None
    assert paragraphs[0].find(".//" + builder.word_tag("jc")).get(builder.word_tag("val")) == "center"
    assert all(p.find(".//" + builder.word_tag("keepLines")) is not None for p in paragraphs)
    assert paragraphs[1].find(".//" + builder.word_tag("sz")).get(builder.word_tag("val")) == "22"
    before = ET.tostring(root)
    builder.fit_docx_figures(root)
    assert ET.tostring(root) == before


@pytest.mark.unit
def test_unrelated_image_is_not_resized(builder):
    root = document(builder, 8001000, "Normal")
    builder.fit_docx_figures(root)
    extent = next(node for node in root.iter() if node.tag.endswith("}extent"))
    assert extent.get("cy") == "8001000"
    assert root.find(".//" + builder.word_tag("keepNext")) is None


@pytest.mark.unit
def test_main_figures_do_not_interrupt_prose_or_move_supplementary_figures(builder):
    root = document(builder, 2000000)
    body = root.find(builder.word_tag("body"))
    figure, caption, section = list(body)
    def paragraph(text):
        p = ET.Element(builder.word_tag('p'))
        r = ET.SubElement(p, builder.word_tag('r'))
        ET.SubElement(r, builder.word_tag('t')).text = text
        return p
    opening, following = paragraph('Results'), paragraph('Following results text')
    references = paragraph('References')
    supplement = paragraph('Supplementary Information')
    supplementary_figure = ET.fromstring(ET.tostring(figure))
    supplementary_caption = ET.fromstring(ET.tostring(caption))
    body[:] = [opening, figure, caption, following, references, supplement,
               supplementary_figure, supplementary_caption, section]
    builder.move_main_figures_after_text(root)
    assert list(body) == [opening, following, references, figure, caption, supplement,
                          supplementary_figure, supplementary_caption, section]
    before = ET.tostring(root)
    builder.move_main_figures_after_text(root)
    assert ET.tostring(root) == before
