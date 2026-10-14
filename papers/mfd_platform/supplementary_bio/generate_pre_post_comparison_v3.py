#!/usr/bin/env python3
"""Generate paired PRE-cell-body and POST-axon comparison figures.

Each well present in both analysis directories produces one TIFF containing:

* PRE Alexa Fluor 647/CTB cell-body image (channel 2), optionally with cell
  segmentation ROI outlines.
* POST axon image, optionally with skeleton ROI outlines.

The optional axon-compartment inset can be loaded directly from a prepared crop
directory or extracted from a full stitched image. The inset label is supplied
by the caller so the acquisition time point is explicit.
"""

from __future__ import annotations

import argparse
import gc
import json
import logging
import re
import sys
import zipfile
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np
from matplotlib.collections import LineCollection
from roifile import ROI_TYPE, ImagejRoi
from skimage import io, morphology, transform
from skimage.exposure import rescale_intensity

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

matplotlib.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 11,
        "axes.titlesize": 11,
        "figure.titlesize": 11,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

# Axon-compartment crop coordinates from cy5_axon_cell_body_crop_analysis.py.
AXON_CROP_START_X = 6800
AXON_CROP_START_Y = 632
AXON_CROP_WIDTH = 992
AXON_CROP_HEIGHT = 4294


@dataclass(frozen=True)
class RoiPath:
    """One ImageJ ROI path in the coordinate order expected by Matplotlib."""

    coordinates: np.ndarray
    closed: bool


def load_metadata(plate_dir: Path) -> dict:
    metadata_path = plate_dir / "openhcs_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")
    with metadata_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def convert_standard_to_opera_phenix_well_id(well_id: str) -> str:
    match = re.fullmatch(r"([A-Z])(\d+)", well_id.upper())
    if not match:
        return well_id.upper()
    row_num = ord(match.group(1)) - ord("A") + 1
    return f"R{row_num:02d}C{int(match.group(2)):02d}"


def normalize_well_id(well_id: str) -> str:
    if re.fullmatch(r"R\d+C\d+", well_id.upper()):
        row, col = re.fullmatch(r"R(\d+)C(\d+)", well_id.upper()).groups()
        return f"R{int(row):02d}C{int(col):02d}"
    return convert_standard_to_opera_phenix_well_id(well_id)


def get_used_wells_from_config(
    config_path: Path, results_csv_path: Path, plate_name: str
) -> set[str]:
    from openhcs.formats.experimental_analysis import load_plate_groups, read_plate_layout

    _, layout, _, ctrl_positions, excluded_positions, _ = read_plate_layout(config_path)
    plate_groups = load_plate_groups(config_path)

    plate_id = None
    current_plate_name = None
    with results_csv_path.open(encoding="utf-8") as handle:
        for line in handle:
            parts = line.rstrip("\n").split(",")
            if len(parts) < 2:
                continue
            if parts[0] == "Plate Name":
                current_plate_name = parts[1]
            elif parts[0] == "Plate ID" and current_plate_name == plate_name:
                plate_id = parts[1]
                break

    if plate_id is None:
        logger.warning("Could not find plate ID for %s", plate_name)
        return set()

    replicate = None
    group_id_for_plate = None
    for candidate_replicate, groups in plate_groups.items():
        for group_id, group_plate_id in groups.items():
            if str(group_plate_id) == str(plate_id):
                replicate = candidate_replicate
                group_id_for_plate = int(group_id)
                break
        if replicate is not None:
            break

    if replicate is None or group_id_for_plate is None:
        logger.warning("Could not find replicate for plate ID %s", plate_id)
        return set()

    used_wells: set[str] = set()
    for doses in layout.get(replicate, {}).values():
        for well_plate_tuples in doses.values():
            for well, plate_group in well_plate_tuples:
                if int(plate_group) == group_id_for_plate:
                    used_wells.add(convert_standard_to_opera_phenix_well_id(well))

    if ctrl_positions and replicate in ctrl_positions:
        for well, plate_group in ctrl_positions[replicate]:
            if int(plate_group) == group_id_for_plate:
                used_wells.add(convert_standard_to_opera_phenix_well_id(well))

    if excluded_positions and replicate in excluded_positions:
        for well, plate_group in excluded_positions[replicate]:
            if int(plate_group) == group_id_for_plate:
                used_wells.discard(convert_standard_to_opera_phenix_well_id(well))

    return used_wells


def generate_well_ids(plate_dir: Path, metadata: dict) -> list[str]:
    """Return metadata wells plus wells recoverable from image filenames.

    Some historical OpenHCS metadata files contain only the first processed
    well even though the analysis directory contains the complete plate.
    """
    wells: set[str] = set()
    for subdir in metadata.get("subdirectories", {}).values():
        wells.update(normalize_well_id(well) for well in subdir.get("wells", {}))

    for image_path in (plate_dir / "images").glob("*.tif*"):
        match = re.search(r"r(\d+)c(\d+)", image_path.name, flags=re.IGNORECASE)
        if match:
            wells.add(f"R{int(match.group(1)):02d}C{int(match.group(2)):02d}")
    return sorted(wells)


def first_existing(candidates: list[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def pre_image_path(pre_dir: Path, well_id: str) -> Path:
    return pre_dir / "images" / f"{well_id.lower()}f001p001-ch2sk1fk1fl1.tiff"


def pre_roi_path(pre_dir: Path, well_id: str, roi_step: int) -> Path:
    return first_existing(
        [
            pre_dir
            / "images_results"
            / f"{well_id.lower()}f001p001-ch2sk1fk1fl1_segmentation_masks_step{roi_step}_rois.roi.zip",
            pre_dir
            / "images_results"
            / f"{well_id}_channel-2_z_index-1_timepoint-1_segmentation_masks_step{roi_step}_rois.roi.zip",
        ]
    )


def post_image_path(post_dir: Path, well_id: str, channel: int, post_subdir: str) -> Path:
    return post_dir / post_subdir / f"{well_id.lower()}f001p001-ch{channel}sk1fk1fl1.tiff"


def post_roi_path(
    post_dir: Path,
    well_id: str,
    channel: int,
    roi_step: int,
    post_subdir: str,
) -> Path:
    return first_existing(
        [
            post_dir
            / f"{post_subdir}_results"
            / (
                f"{well_id.lower()}f001p001-ch{channel}sk1fk1fl1_"
                f"skeleton_rois_step{roi_step}_rois.roi.zip"
            ),
            post_dir
            / f"{post_subdir}_results"
            / (
                f"{well_id}_channel-{channel}_z_index-1_timepoint-1_"
                f"skeleton_rois_step{roi_step}_rois.roi.zip"
            ),
        ]
    )


def pre_stitched_axon_path(pre_stitched_dir: Path, well_id: str) -> Path:
    return pre_stitched_dir / "images" / f"{well_id.lower()}f001p001-ch2sk1fk1fl1.tiff"


def pre_axon_image_path(pre_axon_dir: Path, well_id: str) -> Path:
    return pre_axon_dir / "images" / f"{well_id.lower()}f001p001-ch2sk1fk1fl1.tiff"


def convert_to_uint8(image: np.ndarray) -> np.ndarray:
    return rescale_intensity(image, out_range=(0, 255)).astype(np.uint8)


def convert_to_uint8_percentile(image: np.ndarray) -> np.ndarray:
    p2, p98 = np.percentile(image, (2, 98))
    if p98 <= p2:
        p2, p98 = image.min(), image.max()
    return rescale_intensity(image, in_range=(p2, p98), out_range=(0, 255)).astype(np.uint8)


def prepare_pre_display_image(
    image: np.ndarray,
    background_radius: int = 30,
    low_percentile: float = 0.1,
    high_percentile: float = 99.9,
    downsample_factor: int = 4,
) -> np.ndarray:
    """Suppress uneven PRE-image background and return an 8-bit display image.

    This is a visualization-only transform. It follows the OpenHCS CTB
    preprocessing pattern: a white top-hat background subtraction followed by
    robust percentile normalization. Quantitative measurements continue to use
    the original analysis outputs.
    """
    array = np.asarray(image, dtype=np.float32)
    if array.ndim != 2:
        raise ValueError(f"Expected a 2D PRE image; received shape {array.shape}")
    if background_radius > 0:
        factor = max(1, int(downsample_factor))
        reduced_shape = tuple(max(1, size // factor) for size in array.shape)
        reduced = transform.resize(
            array,
            reduced_shape,
            anti_aliasing=True,
            preserve_range=True,
        )
        footprint = morphology.disk(max(1, int(background_radius) // factor))
        background_small = reduced - morphology.white_tophat(reduced, footprint)
        background = transform.resize(
            background_small,
            array.shape,
            order=1,
            preserve_range=True,
        )
        array = np.maximum(array - background, 0)
    low, high = np.percentile(array, (low_percentile, high_percentile))
    if not np.isfinite(low) or not np.isfinite(high) or high <= low:
        low, high = float(array.min()), float(array.max())
    if high <= low:
        return np.zeros(array.shape, dtype=np.uint8)
    return rescale_intensity(array, in_range=(low, high), out_range=(0, 255)).astype(np.uint8)


def safe_load_rois(roi_path: Path) -> list:
    if not roi_path.exists():
        logger.warning("ROI file not found: %s", roi_path)
        return []
    try:
        rois = []
        with zipfile.ZipFile(roi_path) as archive:
            for filename in archive.namelist():
                if not filename.endswith(".roi"):
                    continue
                imagej_roi = ImagejRoi.frombytes(archive.read(filename))
                coordinates = imagej_roi.coordinates()
                if coordinates is None or len(coordinates) == 0:
                    continue
                rois.append(
                    RoiPath(
                        coordinates=coordinates,
                        closed=imagej_roi.roitype != ROI_TYPE.POLYLINE,
                    )
                )
        if not rois:
            raise ValueError("archive contains no readable ROI members")
        logger.info("Loaded %d ImageJ ROIs from %s", len(rois), roi_path)
        return rois
    except Exception as exc:
        logger.error("Failed to load ROIs from %s: %s", roi_path, exc)
        return []


def crop_axon_compartment(full_image: np.ndarray) -> np.ndarray:
    y1 = AXON_CROP_START_Y
    y2 = y1 + AXON_CROP_HEIGHT
    x1 = AXON_CROP_START_X
    x2 = x1 + AXON_CROP_WIDTH
    return full_image[y1:y2, x1:x2].copy()


def draw_polygon_rois(axis, rois: list) -> None:
    segments = []
    for roi in rois:
        coordinates_xy = roi.coordinates
        if roi.closed and len(coordinates_xy) > 2:
            coordinates_xy = np.vstack((coordinates_xy, coordinates_xy[0]))
        segments.append(coordinates_xy)
    if segments:
        axis.add_collection(
            LineCollection(
                segments,
                colors="#ffff00",
                linewidths=0.7,
                alpha=0.8,
            )
        )


def draw_scale_bar(
    axis,
    image_shape: tuple[int, ...],
    pixel_size_um: float,
    length_um: float,
) -> None:
    """Draw a calibrated microscopy scale bar in image coordinates."""
    height, width = image_shape[:2]
    length_px = length_um / pixel_size_um
    x0 = width * 0.07
    x1 = x0 + length_px
    y = height * 0.93
    axis.plot([x0, x1], [y, y], color="black", linewidth=6, solid_capstyle="butt")
    axis.plot([x0, x1], [y, y], color="white", linewidth=3.5, solid_capstyle="butt")
    label = axis.text(
        (x0 + x1) / 2,
        y - height * 0.025,
        f"{length_um:g} µm",
        color="white",
        fontsize=18,
        ha="center",
        va="bottom",
    )
    label.set_path_effects([path_effects.withStroke(linewidth=2.5, foreground="black")])


def create_comparison_figure(
    pre_img: Path,
    pre_rois: list,
    post_img: Path,
    post_rois: list,
    pre_axon_crop: np.ndarray | None,
    well_id: str,
    output_path: Path,
    no_overlays: bool = False,
    inset_label: str = "PRE",
    pre_title: str = "PRE - Cell body",
    post_title: str = "POST - Regenerating axons",
    figure_title: str | None = None,
    pre_background_radius: int = 30,
    pre_low_percentile: float = 0.1,
    pre_high_percentile: float = 99.9,
    scale_bar_pixel_size_um: float | None = None,
    scale_bar_length_um: float = 500.0,
) -> None:
    image_pre = prepare_pre_display_image(
        io.imread(pre_img),
        background_radius=pre_background_radius,
        low_percentile=pre_low_percentile,
        high_percentile=pre_high_percentile,
    )
    image_post = convert_to_uint8_percentile(io.imread(post_img))

    pre_h, pre_w = image_pre.shape[:2]
    post_h, post_w = image_post.shape[:2]
    pre_aspect = pre_w / pre_h
    post_aspect = post_w / post_h

    axes_h = 0.84
    pre_ax_w = axes_h * pre_aspect
    post_ax_w = axes_h * post_aspect
    gap = 0.008
    total = pre_ax_w + post_ax_w + gap
    left_pre = (1.0 - total) / 2
    left_post = left_pre + pre_ax_w + gap

    fig_h = 8.0
    fig_w = fig_h * total / axes_h
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=600, facecolor="white")
    ax_pre = fig.add_axes([left_pre, 0.05, pre_ax_w, axes_h])
    ax_post = fig.add_axes([left_post, 0.05, post_ax_w, axes_h])

    ax_pre.imshow(image_pre, cmap="gray", interpolation="nearest")
    ax_pre.axis("off")
    if not no_overlays:
        draw_polygon_rois(ax_pre, pre_rois)
    if scale_bar_pixel_size_um is not None:
        draw_scale_bar(ax_pre, image_pre.shape, scale_bar_pixel_size_um, scale_bar_length_um)
    ax_pre.set_title(pre_title, fontname="Arial", fontsize=11, pad=6)

    ax_post.imshow(image_post, cmap="gray", interpolation="nearest")
    ax_post.axis("off")
    if not no_overlays:
        draw_polygon_rois(ax_post, post_rois)
    if scale_bar_pixel_size_um is not None:
        draw_scale_bar(ax_post, image_post.shape, scale_bar_pixel_size_um, scale_bar_length_um)
    ax_post.set_title(post_title, fontname="Arial", fontsize=11, pad=6)

    if pre_axon_crop is not None:
        inset_uint8 = convert_to_uint8_percentile(pre_axon_crop)
        inset_target_w = int(post_w * 0.30)
        inset_target_h = int(inset_target_w * inset_uint8.shape[0] / inset_uint8.shape[1])
        margin_y = 0.03
        margin_x = margin_y * fig_h / fig_w
        inset_w_norm = inset_target_w / post_w * post_ax_w
        inset_h_norm = inset_target_h / post_h * axes_h
        inset_left = left_post + post_ax_w - inset_w_norm - margin_x
        inset_bottom = 0.05 + axes_h - inset_h_norm - margin_y

        ax_inset = fig.add_axes(
            [inset_left, inset_bottom, inset_w_norm, inset_h_norm],
            facecolor="white",
        )
        ax_inset.imshow(inset_uint8, cmap="gray", interpolation="bicubic")
        ax_inset.axis("off")
        for spine in ax_inset.spines.values():
            spine.set_visible(True)
            spine.set_color("white")
            spine.set_linewidth(2)
        ax_inset.set_title(
            inset_label,
            fontname="Arial",
            fontsize=11,
            color="white",
            pad=2,
            loc="left",
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "black", "alpha": 0.7},
        )

    fig.suptitle(well_id if figure_title is None else figure_title,
                 fontname="Arial", fontsize=11, y=0.975)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        bbox_inches="tight",
        pad_inches=0.03,
        dpi=600,
        format="tiff",
        pil_kwargs={"compression": "tiff_lzw"},
    )
    plt.close(fig)
    del image_pre, image_post
    gc.collect()


def process_well(args) -> tuple[bool, str, str | None]:
    (
        well_id,
        pre_dir,
        post_dir,
        pre_stitched_dir,
        pre_axon_dir,
        output_dir,
        pre_roi_step,
        post_channel,
        post_roi_step,
        post_subdir,
        no_overlays,
        skip_existing,
        inset_label,
        pre_background_radius,
        pre_low_percentile,
        pre_high_percentile,
    ) = args

    output_path = output_dir / f"{well_id}_pre_post_comparison.tiff"
    if skip_existing and output_path.exists():
        return True, well_id, "skipped (exists)"

    try:
        p_img = pre_image_path(pre_dir, well_id)
        p_roi = pre_roi_path(pre_dir, well_id, pre_roi_step)
        t_img = post_image_path(post_dir, well_id, post_channel, post_subdir)
        t_roi = post_roi_path(post_dir, well_id, post_channel, post_roi_step, post_subdir)

        missing = []
        if not p_img.exists():
            missing.append(f"PRE image: {p_img.name}")
        if not t_img.exists():
            missing.append(f"POST image: {t_img.name}")
        if missing:
            return False, well_id, f"Missing files: {', '.join(missing)}"

        pre_rois = safe_load_rois(p_roi) if not no_overlays else []
        post_rois = safe_load_rois(t_roi) if not no_overlays else []

        pre_axon_crop = None
        if pre_axon_dir:
            axon_path = pre_axon_image_path(pre_axon_dir, well_id)
            if axon_path.exists():
                pre_axon_crop = io.imread(axon_path)
            else:
                logger.warning("Axon-compartment inset not found: %s", axon_path)
        elif pre_stitched_dir:
            stitched_path = pre_stitched_axon_path(pre_stitched_dir, well_id)
            if stitched_path.exists():
                stitched_img = io.imread(stitched_path)
                pre_axon_crop = crop_axon_compartment(stitched_img)
                del stitched_img
            else:
                logger.warning("PRE stitched image not found: %s", stitched_path)

        create_comparison_figure(
            p_img,
            pre_rois,
            t_img,
            post_rois,
            pre_axon_crop,
            well_id,
            output_path,
            no_overlays=no_overlays,
            inset_label=inset_label,
            pre_background_radius=pre_background_radius,
            pre_low_percentile=pre_low_percentile,
            pre_high_percentile=pre_high_percentile,
        )
        return True, well_id, None
    except Exception as exc:
        return False, well_id, str(exc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate side-by-side PRE versus POST comparison figures."
    )
    parser.add_argument("--pre-dir", type=Path, required=True)
    parser.add_argument("--post-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    inset_group = parser.add_mutually_exclusive_group()
    inset_group.add_argument(
        "--pre-stitched-dir",
        type=Path,
        help="Full stitched PRE images from which the fixed axon crop is extracted.",
    )
    inset_group.add_argument(
        "--pre-axon-dir",
        type=Path,
        help="Prepared axon-compartment crops with an images/ subdirectory.",
    )
    parser.add_argument("--inset-label", default="PRE")
    parser.add_argument("--pre-background-radius", type=int, default=30)
    parser.add_argument("--pre-low-percentile", type=float, default=0.1)
    parser.add_argument("--pre-high-percentile", type=float, default=99.9)
    parser.add_argument("--pre-roi-step", type=int, default=1)
    parser.add_argument("--post-channel", type=int, default=5)
    parser.add_argument("--post-roi-step", type=int, default=5)
    parser.add_argument("--post-subdir", default="axons")
    parser.add_argument("--no-overlays", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--results", type=Path)
    parser.add_argument(
        "--wells",
        nargs="+",
        help="Optional well IDs (for example R02C03 A3) to render.",
    )
    parser.add_argument("--workers", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    for label, path in (("PRE dir", args.pre_dir), ("POST dir", args.post_dir)):
        if not path.is_dir():
            logger.error("%s not found or not a directory: %s", label, path)
            sys.exit(1)
    if args.pre_stitched_dir and not args.pre_stitched_dir.is_dir():
        logger.error("PRE stitched dir not found: %s", args.pre_stitched_dir)
        sys.exit(1)
    if args.pre_axon_dir and not args.pre_axon_dir.is_dir():
        logger.error("PRE axon crop dir not found: %s", args.pre_axon_dir)
        sys.exit(1)
    if bool(args.config) != bool(args.results):
        logger.error("--config and --results must be supplied together")
        sys.exit(1)

    pre_wells = set(generate_well_ids(args.pre_dir, load_metadata(args.pre_dir)))
    post_wells = set(generate_well_ids(args.post_dir, load_metadata(args.post_dir)))
    common_wells = sorted(pre_wells & post_wells)
    logger.info(
        "PRE wells: %d | POST wells: %d | Common: %d",
        len(pre_wells),
        len(post_wells),
        len(common_wells),
    )

    if args.wells:
        requested = {normalize_well_id(well) for well in args.wells}
        common_wells = [well for well in common_wells if well in requested]
        missing_requested = sorted(requested - set(common_wells))
        if missing_requested:
            logger.warning("Requested wells not common to both datasets: %s", missing_requested)

    if args.config and args.results:
        used_wells = get_used_wells_from_config(args.config, args.results, args.pre_dir.name)
        if used_wells:
            before = len(common_wells)
            common_wells = [well for well in common_wells if well in used_wells]
            logger.info("Config filter: %d -> %d wells", before, len(common_wells))

    if not common_wells:
        logger.error("No matching wells found between PRE and POST directories")
        sys.exit(1)

    worker_args = [
        (
            well,
            args.pre_dir,
            args.post_dir,
            args.pre_stitched_dir,
            args.pre_axon_dir,
            args.output_dir,
            args.pre_roi_step,
            args.post_channel,
            args.post_roi_step,
            args.post_subdir,
            args.no_overlays,
            args.skip_existing,
            args.inset_label,
            args.pre_background_radius,
            args.pre_low_percentile,
            args.pre_high_percentile,
        )
        for well in common_wells
    ]
    num_workers = args.workers or min(4, max(1, cpu_count() // 4))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Processing %d wells with %d workers", len(common_wells), num_workers)

    with Pool(num_workers) as pool:
        results = pool.map(process_well, worker_args)

    succeeded = sum(1 for ok, _, _ in results if ok)
    failed = [(well, error) for ok, well, error in results if not ok]
    for well, error in failed:
        logger.error("FAILED %s: %s", well, error)
    logger.info(
        "Done. %d/%d figures saved to %s",
        succeeded,
        len(common_wells),
        args.output_dir,
    )
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
