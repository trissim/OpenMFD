#!/usr/bin/env python3
"""Build a September outgrowth figure with condition-verified stitched FITC fields.

The quantitative panels reuse the established MetaXpress dose-plot renderer.
Microscopy is display-only; provisional OpenHCS measurements are not plotted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image, ImageDraw
from skimage.restoration import rolling_ball
from skimage.transform import resize

import generate_combined_axotomy_supplementary_figure as assembly
import generate_september_axotomy_figure as september
from generate_axotomy_supplementary_figure import INK, MUTED, pil_font


BIO = Path(__file__).resolve().parent
DEFAULT_WORKBOOK = september.DEFAULT_ROOT / "neurite outgrowth/results.xlsx"
DEFAULT_STITCH_ROOT = Path("/run/media/ts/hdd/blind-neurite-analysis-20260923")
DEFAULT_RAW_ROOT = september.DEFAULT_ROOT / "neurite outgrowth"
DEFAULT_OUTPUT = BIO / "figure_output_september_outgrowth_20260924"
PIXEL_SIZE_UM = 1.3556  # Acquired TIFF spatial calibration; stitching preserves pixel scale.
FULL_MOSAIC_DISPLAY_PX = 1560
DISPLAY_RAW_LOW_PERCENTILE = 0.0
DISPLAY_RAW_HIGH_PERCENTILE = 99.9
ROLLING_BALL_RADIUS_PX = 192
ROLLING_BALL_DOWNSAMPLE = 8
ROLLING_BALL_SUBTRACTION_FRACTION = 0.70
DISPLAY_POST_HIGH_PERCENTILE = 99.9
DISPLAY_POST_LOW_PERCENTILE = 35.0
DISPLAY_POST_ASINH_SCALE = 0.0015
DISPLAY_POST_GAMMA = 0.80
DISPLAY_HIGHLIGHT_CEILING = 1.0
DAPI_LOW_PERCENTILE = 90.0
DAPI_HIGH_PERCENTILE = 99.9
DAPI_GAMMA = 0.55
DAPI_BLUE_CEILING = 230
PLOT_ORDER = {
    "24098": ("F04", "09-027", "06-049", "09-037", "08-115", "09-079"),
    "24099": ("DMSO", "Y27", "FC-A"),
}
CANVAS = (5400, 7750)
FIGURE_NOTE = (
    "Bars show averages; whiskers show standard deviation; dots show each well. "
    "The dotted line marks average DMSO. Doses are in µM."
)
BOXES = {
    **{letter: (150 + (i % 3) * 1750, 90 + (i // 3) * 1850, 1600, 1750)
       for i, letter in enumerate("ABCDEF")},
    **{letter: (150, 3730 + i * 980, 5100, 960)
       for i, letter in enumerate("GHIJ")},
}


@dataclass(frozen=True)
class StitchedExample:
    panel: str
    condition: str
    dose_um: int | None
    source_plate: str
    source_well: str
    coded_plate: str
    coded_well: str
    result_folder: str

    def channel_path(self, root: Path, channel: str = "w2") -> Path:
        if channel not in {"w1", "w2"}:
            raise ValueError(f"Unknown image channel: {channel}")
        return (
            root / self.result_folder / f"{self.coded_plate}_openhcs_openhcs"
            / "analysis_inputs" / f"{self.coded_well}_s001_{channel}_z001_t001.tif"
        )


# Mapping was verified by SHA-256 of original and neutrally coded FITC site-1
# pixel arrays. It is used only after completion of the blinded analysis.
EXAMPLES = (
    StitchedExample("A", "DMSO", None, "24099", "F02", "P001", "A46", "p001-a083-blind-full"),
    StitchedExample("B", "F04", 20, "24098", "C03", "P002", "A02", "p002-a083-blind-full"),
    StitchedExample("C", "06-049", 40, "24098", "D02", "P002", "A42", "p002-a083-blind-full"),
    StitchedExample("D", "08-115", 5, "24098", "F05", "P002", "A53", "p002-a083-blind-full"),
    StitchedExample("E", "Y27", 40, "24099", "C02", "P001", "A49", "p001-a083-blind-full"),
    StitchedExample("F", "FC-A", 40, "24099", "D02", "P001", "A59", "p001-a083-blind-full"),
)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def pooled_uint16_percentile(images: list[np.ndarray], percentile: float) -> float:
    """Find an exact percentile over unequal-sized stitched planes as one stack."""

    if not images or not 0 <= percentile <= 100:
        raise ValueError("Expected images and a percentile in [0, 100]")
    counts = np.zeros(65536, dtype=np.int64)
    for image in images:
        if image.ndim != 2 or image.dtype != np.uint16:
            raise ValueError("Expected lossless uint16 stitched FITC planes")
        counts += np.bincount(image.ravel(), minlength=len(counts))
    cumulative = np.cumsum(counts)
    rank = (int(cumulative[-1]) - 1) * percentile / 100
    left_rank = int(np.floor(rank))
    right_rank = int(np.ceil(rank))
    left = int(np.searchsorted(cumulative, left_rank + 1))
    right = int(np.searchsorted(cumulative, right_rank + 1))
    return left + (rank - left_rank) * (right - left)


def rolling_ball_corrected(image: np.ndarray, raw_low: float,
                           raw_high: float) -> np.ndarray:
    """Estimate slow background at reduced resolution; preserve native pixels."""

    normalized = np.clip(
        (image.astype(np.float32) - raw_low) / (raw_high - raw_low), 0, 1
    )
    small_shape = tuple(max(1, round(size / ROLLING_BALL_DOWNSAMPLE))
                        for size in image.shape)
    small = resize(normalized, small_shape, order=1, anti_aliasing=True,
                   preserve_range=True).astype(np.float32)
    radius = round(ROLLING_BALL_RADIUS_PX / ROLLING_BALL_DOWNSAMPLE)
    background_small = rolling_ball(small * 255, radius=radius, workers=4) / 255
    background = resize(background_small, image.shape, order=1,
                        anti_aliasing=False, preserve_range=True).astype(np.float32)
    return np.maximum(normalized - ROLLING_BALL_SUBTRACTION_FRACTION * background, 0)


def green_image(signal: np.ndarray) -> Image.Image:
    green = np.rint(255 * signal).astype(np.uint8)
    rgb = np.zeros((*signal.shape, 3), dtype=np.uint8)
    rgb[..., 1] = green
    return Image.fromarray(rgb, mode="RGB")


def dapi_stack(images: list[np.ndarray]) -> tuple[list[np.ndarray], dict]:
    """Use one complete-mosaic window for all six stitched DAPI channels."""

    low = pooled_uint16_percentile(images, DAPI_LOW_PERCENTILE)
    high = pooled_uint16_percentile(images, DAPI_HIGH_PERCENTILE)
    if high <= low:
        raise ValueError("Stitched DAPI stack has no usable display range")
    rendered = [np.rint(DAPI_BLUE_CEILING * np.power(np.clip(
        (image.astype(np.float32) - low) / (high - low), 0, 1
    ), DAPI_GAMMA)).astype(np.uint8) for image in images]
    return rendered, {
        "scope": "six complete stitched DAPI mosaics; one shared window",
        "percentiles": [DAPI_LOW_PERCENTILE, DAPI_HIGH_PERCENTILE],
        "window": [low, high],
        "gamma": DAPI_GAMMA,
        "blue_ceiling": DAPI_BLUE_CEILING,
    }


def overlay_dapi(fitc: Image.Image, dapi_blue: np.ndarray) -> Image.Image:
    rgb = np.array(fitc)
    if rgb.shape[:2] != dapi_blue.shape:
        raise ValueError("Stitched FITC and DAPI shapes differ")
    rgb[..., 2] = dapi_blue
    return Image.fromarray(rgb, mode="RGB")


def display_stack(images: list[np.ndarray]) -> tuple[list[Image.Image], dict]:
    """Apply two shared percentile fits around a large rolling-ball estimate."""

    raw_low = pooled_uint16_percentile(images, DISPLAY_RAW_LOW_PERCENTILE)
    raw_high = pooled_uint16_percentile(images, DISPLAY_RAW_HIGH_PERCENTILE)
    if raw_high <= raw_low:
        raise ValueError("Stitched FITC stack has no usable display range")
    corrected = [rolling_ball_corrected(image, raw_low, raw_high)
                 for image in images]
    post_low, post_high = np.percentile(
        np.concatenate([image.ravel() for image in corrected]),
        [DISPLAY_POST_LOW_PERCENTILE, DISPLAY_POST_HIGH_PERCENTILE],
    )
    post_low, post_high = float(post_low), float(post_high)
    if not np.isfinite(post_high) or post_high <= post_low:
        raise ValueError("Corrected FITC stack has no usable display range")
    denominator = np.arcsinh((post_high - post_low) / DISPLAY_POST_ASINH_SCALE)
    rendered = [
        green_image(DISPLAY_HIGHLIGHT_CEILING * np.power(np.clip(
            np.arcsinh(np.maximum(image - post_low, 0) / DISPLAY_POST_ASINH_SCALE)
            / denominator, 0, 1
        ), DISPLAY_POST_GAMMA))
        for image in corrected
    ]
    display = {
        "scope": "six complete stitched FITC mosaics; both windows shared",
        "raw_percentiles": [DISPLAY_RAW_LOW_PERCENTILE, DISPLAY_RAW_HIGH_PERCENTILE],
        "raw_window": [raw_low, raw_high],
        "background": "large rolling-ball estimate on 8x downsampled normalized mosaic",
        "rolling_ball_radius_native_px": ROLLING_BALL_RADIUS_PX,
        "rolling_ball_downsample": ROLLING_BALL_DOWNSAMPLE,
        "background_subtraction_fraction": ROLLING_BALL_SUBTRACTION_FRACTION,
        "post_low_percentile": DISPLAY_POST_LOW_PERCENTILE,
        "post_low_value": post_low,
        "post_high_percentile": DISPLAY_POST_HIGH_PERCENTILE,
        "post_high_value": post_high,
        "post_asinh_scale": DISPLAY_POST_ASINH_SCALE,
        "post_gamma": DISPLAY_POST_GAMMA,
        "highlight_ceiling_fraction": DISPLAY_HIGHLIGHT_CEILING,
    }
    return rendered, display


def original_site_path(example: StitchedExample, raw_root: Path,
                       channel: str = "w2") -> Path:
    folder = next(raw_root.glob(f"*Plate_{example.source_plate}/TimePoint_1"), None)
    if folder is None:
        raise FileNotFoundError(f"Raw plate {example.source_plate} under {raw_root}")
    matches = list(folder.glob(f"*_{example.source_well}_s1_{channel}.TIF"))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one original {channel} site-1 for {example}")
    return matches[0]


def verify_identity(example: StitchedExample, raw_root: Path,
                    coded_root: Path, outgrowth) -> dict:
    rows = outgrowth.loc[(outgrowth.plate == example.source_plate)
                         & (outgrowth.well == example.source_well)]
    if len(rows) != 1 or rows.iloc[0].condition != example.condition:
        raise ValueError(f"Workbook condition does not match {example}")
    if example.dose_um is not None and rows.iloc[0].nominal_dose_uM != example.dose_um:
        raise ValueError(f"Workbook dose does not match {example}")
    channel_records = {}
    for channel, name in (("w1", "dapi"), ("w2", "fitc")):
        source = original_site_path(example, raw_root, channel)
        coded = (coded_root / example.coded_plate /
                 f"{example.coded_well}_s001_{channel}_z001_t001.tif")
        with tifffile.TiffFile(source) as original_tiff:
            original_site = original_tiff.asarray()
            properties = {
                element.attrib["id"]: element.attrib.get("value")
                for element in ET.fromstring(original_tiff.pages[0].description).iter()
                if "id" in element.attrib
            }
        pixel_size_yx = [float(properties[f"spatial-calibration-{axis}"])
                         for axis in ("y", "x")]
        if original_site.shape != (1024, 1024) or pixel_size_yx != [PIXEL_SIZE_UM] * 2 \
                or properties["spatial-calibration-units"] != "um":
            raise ValueError(f"Unexpected source dimensions or calibration for {source}")
        if not coded.is_file() or not np.array_equal(original_site, tifffile.imread(coded)):
            raise ValueError(f"Original and coded {channel} site-1 pixels differ for {example}")
        channel_records[name] = {
            "original": {"path": str(source), "sha256": digest(source)},
            "coded": {"path": str(coded), "sha256": digest(coded)},
        }
    return {
        "source_plate": example.source_plate,
        "source_well": example.source_well,
        "condition": example.condition,
        "dose_um": example.dose_um,
        "coded_plate": example.coded_plate,
        "coded_well": example.coded_well,
        "original_site_1_fitc": channel_records["fitc"]["original"],
        "coded_site_1_fitc": channel_records["fitc"]["coded"],
        "original_site_1_dapi": channel_records["dapi"]["original"],
        "coded_site_1_dapi": channel_records["dapi"]["coded"],
        "identity_check": "original and coded site-1 FITC and DAPI pixels equal",
        "original_site_shape_yx": [1024, 1024],
        "source_pixel_size_um_yx": [PIXEL_SIZE_UM] * 2,
    }


def draw_scale_bar(draw: ImageDraw.ImageDraw, xy: tuple[int, int],
                   length_px: int, label: str) -> None:
    x, y = xy
    draw.line((x, y, x + length_px, y), fill="white", width=9)
    draw.text((x + length_px / 2, y - 18), label,
              font=pil_font(36, bold=True), fill="white", anchor="ms",
              stroke_width=3, stroke_fill="black")


def image_panel(example: StitchedExample, stitch_root: Path,
                target: Path, identity: dict, fitc: np.ndarray,
                dapi: np.ndarray, merged: Image.Image,
                display: dict, dapi_display: dict) -> dict:
    source = example.channel_path(stitch_root)
    dapi_source = example.channel_path(stitch_root, "w1")
    for path in (source, dapi_source):
        if not path.is_file():
            raise FileNotFoundError(path)
    if fitc.shape != dapi.shape:
        raise ValueError(f"Stitched FITC and DAPI shapes differ for {example}")
    width, height = BOXES[example.panel][2:]
    panel = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(panel)
    dose = "matched vehicle" if example.dose_um is None else f"{example.dose_um} µM"
    draw.text((width / 2, 8), f"{example.condition}  |  {dose}",
              font=pil_font(53, bold=True), fill=INK, anchor="ma")

    full_size = FULL_MOSAIC_DISPLAY_PX
    full_x, full_y = 20, 100
    full = merged.resize((full_size, full_size), Image.Resampling.LANCZOS)
    preview = np.asarray(full)
    green_levels = np.percentile(preview[..., 1], [25, 50, 75, 95])
    presentation_qc = {
        "scope": "final resampled mosaic, before scale bar and border",
        "green_percentiles_25_50_75_95": [float(value) for value in green_levels],
        "green_p95_minus_p50": float(green_levels[3] - green_levels[1]),
        "green_ceiling_fraction": float(np.mean(preview[..., 1] >= 254)),
        "blue_above_60_fraction": float(np.mean(preview[..., 2] > 60)),
        "interpretation": "presentation diagnostics, not neurite or nucleus validation",
    }
    panel.paste(full, (full_x, full_y))
    outline_color = september.COLORS[example.condition]
    draw.rectangle((full_x - 20, full_y - 20, full_x + full_size + 19,
                    full_y + full_size + 19), outline=outline_color, width=24)
    full_scale = full_size / merged.width
    bar_length_px = round((500 / PIXEL_SIZE_UM) * full_scale)
    draw_scale_bar(draw, (full_x + 65, full_y + full_size - 65),
                   bar_length_px, "500 µm")
    panel.save(target, dpi=(300, 300), compress_level=5)
    return {
        **identity,
        "stitched_fitc": {"path": str(source), "sha256": digest(source)},
        "stitched_dapi": {"path": str(dapi_source), "sha256": digest(dapi_source)},
        "stitched_shape_yx": list(fitc.shape),
        "display": display,
        "dapi_display": dapi_display,
        "presentation_qc": presentation_qc,
        "condition_outline_color": outline_color,
        "condition_outline_width_px": 24,
        "scale_bar": {
            "label_um": 500,
            "rendered_length_px": bar_length_px,
            "effective_length_um": bar_length_px / full_scale * PIXEL_SIZE_UM,
        },
        "panel_sha256": digest(target),
    }


def build(workbook: Path, stitch_root: Path, raw_root: Path,
          coded_root: Path, output: Path) -> None:
    if not workbook.is_file():
        raise FileNotFoundError(workbook)
    output.mkdir(parents=True, exist_ok=True)
    panels = output / "panels"
    panels.mkdir(exist_ok=True)
    sources = output / "sources"
    sources.mkdir(exist_ok=True)
    retained_workbook = sources / workbook.name
    if workbook != retained_workbook:
        shutil.copy2(workbook, retained_workbook)
    if digest(retained_workbook) != digest(workbook):
        raise ValueError("Retained workbook differs from the plotted source")
    paths = {label: panels / f"panel_{label}.png" for label in BOXES}
    outgrowth, descriptions = september.read_outgrowth(workbook)
    outgrowth.to_csv(output / "outgrowth_wells.csv", index=False)
    plotted = outgrowth.loc[
        outgrowth.apply(lambda row: row.condition in PLOT_ORDER[row.plate], axis=1)
    ]
    plotted.to_csv(output / "outgrowth_plotted_wells.csv", index=False)
    descriptions.to_csv(output / "workbook_plate_descriptions.csv", index=False)
    long = outgrowth.melt(
        id_vars=[column for column in outgrowth.columns
                  if column not in {spec[0] for spec in september.OUTGROWTH_SPECS}],
        value_vars=[spec[0] for spec in september.OUTGROWTH_SPECS],
        var_name="metric", value_name="value",
    )
    summary = long.groupby(
        ["plate", "condition", "nominal_dose_uM", "metric"]
    ).value.agg(["count", "mean", "std"]).reset_index()
    summary.to_csv(output / "outgrowth_summary.csv", index=False)
    identities = [verify_identity(example, raw_root, coded_root, outgrowth)
                  for example in EXAMPLES]
    fitc_images = [tifffile.imread(example.channel_path(stitch_root))
                   for example in EXAMPLES]
    dapi_images = [tifffile.imread(example.channel_path(stitch_root, "w1"))
                   for example in EXAMPLES]
    rendered_fitc, display = display_stack(fitc_images)
    rendered_dapi, dapi_display = dapi_stack(dapi_images)
    rendered_images = [overlay_dapi(fitc, dapi) for fitc, dapi in
                       zip(rendered_fitc, rendered_dapi, strict=True)]
    image_records = [
        image_panel(example, stitch_root, paths[example.panel], identity,
                    fitc, dapi, rendered, display, dapi_display)
        for example, identity, fitc, dapi, rendered in zip(
            EXAMPLES, identities, fitc_images, dapi_images, rendered_images, strict=True
        )
    ]
    for label, spec in zip("GHIJ", september.OUTGROWTH_SPECS, strict=True):
        september.dose_panel(outgrowth, spec, paths[label], BOXES[label][2:],
                             order=PLOT_ORDER,
                             font_scale=1.35,
                             show_note=False)
    stem = output / "September_outgrowth_stitched"
    assembly.compose_figure(paths, stem.with_suffix(".png"),
                            panel_boxes=BOXES, canvas_size=CANVAS,
                            footer_text=FIGURE_NOTE)
    powerpoint = output / f"{stem.name}_editable.pptx"
    assembly.build_powerpoint(paths, powerpoint,
                              panel_boxes=BOXES, canvas_size=CANVAS,
                              footer_text=FIGURE_NOTE)
    legend = (
        "# September neurite outgrowth: stitched fields and MetaXpress exports\n\n"
        "(A–F) Representative nine-site stitched FITC/DAPI fields, outlined "
        "in the matching graph colors: DMSO matched "
        "vehicle, F04 20 µM, 06-049 40 µM, 08-115 5 µM, Y27 40 µM, and "
        "FC-A 40 µM, respectively. Original treatment wells were matched to "
        "the completed coded stitches by exact site-1 FITC and DAPI pixel equality. "
        "Scale bars are 500 µm using the acquisition calibration of "
        "1.3556 µm/pixel. Green FITC and blue DAPI pseudocolor are display-only. "
        "One raw 0th–99.9th FITC percentile window was fitted across all six "
        "complete mosaics. A "
        "192-pixel-radius rolling-ball background estimate was computed at "
        "one-eighth resolution for each mosaic and subtracted at 70%. A shared "
        "35th–99.9th-percentile asinh/gamma display stretch was then applied "
        "across the six mosaics, preserving full highlight headroom. DAPI used "
        "a separate shared 90th–99.9th-percentile window across its six mosaics. "
        "No source site was normalized independently. Intensities share the "
        "same display transform, but the panels were not chosen as statistical "
        "representatives.\n\n"
        "(G–J) MetaXpress-exported mean outgrowth per cell, exported median "
        "process length, mean branches per cell, and exported cell-count "
        "summary for both September plates, excluding EpoB and EpoB+FC-A. "
        "Drug concentrations are labeled by the amount added: 40, 20, 10, "
        "and 5 µM. Bars show mean ± sample SD; "
        "points are individual well "
        "summaries; the dotted line is the pooled DMSO mean for the same "
        "metric. DMSO positions represent matched dilutions, not a molar "
        "DMSO concentration. Exported length units and aggregation were "
        "not declared in the source workbook. No axotomy data, OpenHCS "
        "segmentation-derived measurement, inferential test, or biological "
        "replicate claim is included.\n"
    )
    legend_path = output / "FIGURE_LEGEND.md"
    legend_path.write_text(legend)
    manifest = {
        "workbook": {"path": str(workbook), "sha256": digest(workbook),
                     "retained_copy": str(retained_workbook.relative_to(output))},
        "quantitative_source": "MetaXpress results.xlsx exported well summaries only",
        "outgrowth_fields": {spec[0]: spec[3]
                             for spec in september.OUTGROWTH_SPECS},
        "doses_left_to_right_uM": list(september.DOSES),
        "plotted_doses_uM": [dose for dose in september.DOSES if dose != 0],
        "image_source": "lossless pre-segmentation OpenHCS stitched FITC and DAPI channels",
        "image_selection": "six illustrative completed stitches, condition-verified against original acquisition pixels",
        "plotted_conditions": PLOT_ORDER,
        "excluded_conditions": ["EpoB", "EpoB+FC-A"],
        "images": image_records,
        "panels": {label: list(box) for label, box in BOXES.items()},
        "figure_note": FIGURE_NOTE,
        "panel_sha256": {label: digest(path) for label, path in paths.items()},
        "figure_files": {
            path.name: digest(path)
            for path in (stem.with_suffix(".png"), stem.with_suffix(".pdf"),
                         powerpoint, legend_path)
        },
        "canvas_pixels": list(CANVAS),
        "pixel_size_um": PIXEL_SIZE_UM,
        "warnings": [
            "Image identities were verified after completion of blinded analysis; no treatment key was used for segmentation tuning.",
            "The provisional OpenHCS neurite segmentation is not used for plotted values.",
            "All six FITC mosaics use shared display windows; background correction and contrast enhancement are display only.",
            "MetaXpress workbook does not declare its exported length units.",
            "DMSO dose labels indicate matched dilution positions, not DMSO molarity.",
            "No inferential statistics or biological-replicate claims are shown.",
        ],
    }
    (output / "figure_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {stem}.png/.pdf and editable PPTX", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--stitched-root", type=Path, default=DEFAULT_STITCH_ROOT)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--coded-root", type=Path, default=Path(
        "/run/media/ts/0BA20E780BA20E78/slas-neurite-coded-20260915"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.workbook.resolve(), args.stitched_root.resolve(),
          args.raw_root.resolve(), args.coded_root.resolve(),
          args.output_dir.resolve())


if __name__ == "__main__":
    main()
