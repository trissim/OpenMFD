"""DMSO-only figure selection, exclusion, and layout regressions."""

import importlib
import sys
from pathlib import Path

import pytest
import numpy as np
from PIL import Image


@pytest.fixture(scope="module")
def figure():
    folder = Path(__file__).resolve().parents[2] / "papers/mfd_platform/supplementary_bio"
    sys.path.insert(0, str(folder))
    return importlib.import_module("generate_axotomy_control_supplementary_figure")


def test_three_plate_selection_preserves_reviewed_exclusions(figure):
    records = figure.read_records(figure.BIO_DIR / "control_reproducibility_data.csv")
    selected = figure.representative_records(records)
    assert len(records) == 72
    assert [r.plate for r in selected] == ["p1", "p2", "p3"]
    assert not any(r.pre_outlier for r in selected)
    assert selected == figure.representative_records(list(reversed(records)))
    assert {r.key for r in records if r.pre_outlier} == {
        "p1_R03C02", "p1_R06C02", "p2_R02C02", "p2_R05C03", "p2_R06C03"
    }
    assert [sum(r.plate == plate and not r.pre_outlier for r in records)
            for plate in figure.PLATES] == [22, 21, 24]
    for r in records:
        assert r.total_axon_length_um == r.total_axon_count * figure.AXON_PIXEL_SIZE_UM
        assert r.axon_per_pre == r.total_axon_length_um / r.pre_cell_count


def test_no_eligible_representative_fails(figure):
    with pytest.raises(ValueError, match="p1"):
        figure.representative_records([])


def test_panels_fit_without_overlap(figure):
    assert set(figure.PANEL_BOXES) == set("ABCDEFG")
    boxes = list(figure.PANEL_BOXES.values())
    for index, (x, y, w, h) in enumerate(boxes):
        assert 0 <= x < x + w <= figure.CANVAS_WIDTH
        assert 0 <= y < y + h <= figure.CANVAS_HEIGHT
        for xx, yy, ww, hh in boxes[index + 1:]:
            assert x + w <= xx or xx + ww <= x or y + h <= yy or yy + hh <= y


def test_panel_b_uses_multiple_unlabeled_axotomy_checks(figure):
    assert len(figure.AXOTOMY_CHECK_KEYS) == 18
    assert len(set(figure.AXOTOMY_CHECK_KEYS)) == 18
    assert len(figure.AXOTOMY_CHECK_SOURCES) == 18
    assert {path.parent.parent.name for path in figure.AXOTOMY_CHECK_SOURCES} == {"p1", "p2"}
    assert all("outlier" not in path.name for path in figure.AXOTOMY_CHECK_SOURCES)


def test_heading_crop_keeps_image_titles_and_image(figure):
    source = Image.new("RGB", (100, 1000), "white")
    source.paste("red", (0, 100, 100, 125))
    source.paste("blue", (0, 126, 100, 1000))
    cropped = figure.crop_comparison_content(source)
    assert cropped.size == (100, 950)
    assert cropped.getpixel((50, 50)) == (255, 0, 0)
    assert cropped.getpixel((50, 949)) == (0, 0, 255)


def test_thumbnail_letterboxing_is_white(figure, tmp_path):
    path = tmp_path / "comparison.png"
    Image.new("RGB", (100, 200), "gray").save(path)
    thumbnail = figure.image_thumbnail(path, (300, 200), crop_header=False)
    assert thumbnail.getpixel((0, 0)) == (255, 255, 255)
    assert thumbnail.getpixel((150, 100)) == (128, 128, 128)


def test_rendered_pre_background_suppression_preserves_colored_overlays(figure):
    source = Image.new("RGB", (20, 10), (40, 40, 40))
    source.putpixel((3, 3), (255, 255, 0))
    source.paste((40, 40, 40), (10, 0, 20, 10))
    processed = figure.suppress_rendered_pre_background(source)
    assert processed.getpixel((0, 0))[0] < 40
    assert processed.getpixel((3, 3)) == (255, 255, 0)
    assert processed.getpixel((15, 5)) == (40, 40, 40)


def test_pre_display_processing_removes_slow_background(figure):
    comparison = importlib.import_module("generate_pre_post_comparison_v3")
    yy, xx = np.mgrid[:96, :96]
    background = (20 + xx * 0.5 + yy * 0.25).astype(np.float32)
    image = background.copy()
    image[45:50, 45:50] += 200
    processed = comparison.prepare_pre_display_image(
        image,
        background_radius=20,
        downsample_factor=2,
    )
    assert processed.dtype == np.uint8
    assert processed.shape == image.shape
    assert processed[47, 47] > 200
    assert np.median(processed[:20, :20]) < 10
