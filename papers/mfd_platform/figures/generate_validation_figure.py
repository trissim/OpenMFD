#!/usr/bin/env python3
"""Render Figure 4 and the channel-width supplement from saved measurements."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
from pathlib import Path
from statistics import mean, stdev
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from PIL import Image
logging.getLogger("fontTools").setLevel(logging.WARNING)

FIGURE_DIR = Path(__file__).resolve().parent
ROOT = FIGURE_DIR.parent
OUTPUT_DIR = FIGURE_DIR / "final_drop/Fig5_plate_layout_validation"
DATA_DIR = ROOT / "supplementary/validation"
BIO_DIR = ROOT / "supplementary_bio"
SAVED_FIGURE = BIO_DIR / "figure_output_dmso_only_20260916"
WIDTH_DIR = ROOT / "build/channel_width_20261013"
COLORS = ("#0072B2", "#D17800", "#00856A")


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def import_saved_data():
    """Keep the baseline counts and display crops independent of the external disk."""
    sys.path.insert(0, str(BIO_DIR))
    from generate_pre_post_comparison_v3 import prepare_pre_display_image, pre_image_path
    import tifffile

    manifest = json.loads((SAVED_FIGURE / "figure_manifest.json").read_text())
    source = Path(manifest["authoritative_data"])
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest["data_sha256"]:
        raise ValueError("The saved DMSO data changed; reconcile before importing")
    assets = json.loads((source.parent / "asset_manifest.json").read_text())
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = [{"plate": row["plate"], "device": row["well"],
             "ctb_positive_cells": row["pre_cell_count"],
             "included": str(row["pre_outlier"].lower() != "true"),
             "exclusion_reason": row["outlier_reason"]}
            for row in read_csv(source)]
    analysis_dirs = {}
    for plate, config in assets["plates"].items():
        # The archived table uses the original analysis, not the later _final run.
        directory = Path(assets["dataset_root"]) / config["pre"].removesuffix("_final")
        analysis_dirs[plate] = directory
    for row in rows:
        details = analysis_dirs[row["plate"]] / "images_results" / (
            f"{row['device'].lower()}f001p001-ch2sk1fk1fl1_cell_counts_step2_details.csv")
        counts = read_csv(details)
        if len(counts) != 1 or float(counts[0]["cell_count"]) != float(row["ctb_positive_cells"]):
            raise ValueError(f"Saved count does not match original analysis: {details}")
    write_csv(DATA_DIR / "ctb_device_counts.csv", rows)
    metadata = {"count_source": str(source), "count_source_sha256": manifest["data_sha256"],
                "analysis_version": "OpenHCS 0.5.15", "ctb_channel": 2,
                "representatives": {}, "tracer_scale": {
                    "method": "Estimated from 9 mm well-centre spacing in the exported montage",
                    "day0_centres_xy": [[490, 260], [1130, 260]],
                    "day3_centres_xy": [[490, 260], [1130, 260]],
                    "spacing_um": 9000,
                }}
    for plate, key in manifest["representative_devices"].items():
        directory = Path(assets["dataset_root"]) / assets["plates"][plate]["pre"]
        well = key.split("_")[1]
        image_path = pre_image_path(directory, well)
        raw = tifffile.imread(image_path)
        display = prepare_pre_display_image(raw)
        acquisition = next(Path(assets["dataset_root"]).parent.glob(
            f"TS_MFD_PRE_{plate.upper()}_20260203__*/Images/Index.xml"))
        root = ET.parse(acquisition).getroot()
        scale_x = {float(n.text) * 1e6 for n in root.iter() if n.tag.endswith("}ImageResolutionX")}
        scale_y = {float(n.text) * 1e6 for n in root.iter() if n.tag.endswith("}ImageResolutionY")}
        if len(scale_x) != 1 or scale_x != scale_y:
            raise ValueError(f"Ambiguous acquisition scale: {acquisition}")
        image = Image.fromarray(display)
        image.thumbnail((900, 1500), Image.Resampling.LANCZOS)
        image.save(DATA_DIR / f"{key}_ctb.png")
        metadata["representatives"][plate] = {
            "device": well, "source": str(image_path), "acquisition_xml": str(acquisition),
            "source_shape_yx": list(raw.shape), "pixel_size_um": scale_x.pop(),
            "display": f"{key}_ctb.png",
            "display_processing": manifest["pre_display_processing"],
            "selection": manifest["representative_rule"],
        }
    metadata["count_analysis_directories"] = {p: str(d) for p, d in analysis_dirs.items()}
    metadata["count_verification"] = "All 72 counts match the original per-device count CSVs; later ROI exports are not the count source."

    widths = read_csv(WIDTH_DIR / "measurements.csv")
    write_csv(DATA_DIR / "channel_widths.csv", widths)
    for plate, sample in (("P1", 1), ("P2", 3), ("P3", 4)):
        data = json.loads((WIDTH_DIR / f"raw_sample_{sample:02d}.json").read_text())
        pixels = np.asarray(data["records"][0]["array_values"], dtype=np.uint16)
        np.save(DATA_DIR / f"{plate}_width_crop.npy", pixels, allow_pickle=False)
        metadata.setdefault("width_crops", {})[plate] = {"slices_yx": data["array_slices"]}
    (DATA_DIR / "sources.json").write_text(json.dumps(metadata, indent=2) + "\n")


def count_data():
    rows = read_csv(DATA_DIR / "ctb_device_counts.csv")
    expected = {(f"p{p}", f"R{r:02d}C{c:02d}") for p in range(1, 4)
                for r in range(2, 8) for c in range(2, 6)}
    if len(rows) != 72 or {(r["plate"], r["device"]) for r in rows} != expected:
        raise ValueError("Expected the 72 unique interior devices")
    if any(r["included"] not in ("True", "False") for r in rows):
        raise ValueError("Invalid inclusion flag")
    return rows


def import_saved_overlays():
    """Retain the segmentation outlines from the analysis supplying the counts."""
    from roifile import ImagejRoi, ROI_TYPE

    metadata_path = DATA_DIR / "sources.json"
    metadata = json.loads(metadata_path.read_text())
    for plate, source in metadata["representatives"].items():
        filename = f"{source['device'].lower()}f001p001-ch2sk1fk1fl1_segmentation_masks_step2_rois.roi.zip"
        archive_path = Path(metadata["count_analysis_directories"][plate]) / "images_results" / filename
        outlines = []
        with ZipFile(archive_path) as archive:
            for member in archive.namelist():
                if not member.endswith(".roi"):
                    continue
                roi = ImagejRoi.frombytes(archive.read(member))
                coordinates = roi.coordinates()
                if coordinates is None or len(coordinates) == 0:
                    raise ValueError(f"Empty segmentation outline: {archive_path} / {member}")
                if roi.roitype != ROI_TYPE.POLYLINE:
                    coordinates = np.vstack((coordinates, coordinates[0]))
                outlines.append(coordinates.tolist())
        if not outlines:
            raise ValueError(f"No segmentation outlines: {archive_path}")
        destination = f"{plate}_{source['device']}_outlines.json"
        (DATA_DIR / destination).write_text(json.dumps(outlines, separators=(",", ":")) + "\n")
        source["outlines"] = destination
        source["outline_source"] = str(archive_path)
        source["outline_source_sha256"] = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")


def count_summaries(rows):
    result = []
    for plate in ("p1", "p2", "p3"):
        values = [float(r["ctb_positive_cells"]) for r in rows
                  if r["plate"] == plate and r["included"] == "True"]
        result.append({"plate": plate, "n": len(values), "mean": mean(values), "sd": stdev(values)})
    return result


def scale_bar(ax, shape, pixel_size_um, length_um=500, color="white", fontsize=9):
    h, w = shape
    x, y = w * .08, h * .94
    ax.plot([x, x + length_um / pixel_size_um], [y, y], color=color, linewidth=2.5)
    ax.text(x, y - h * .025, f"{length_um:g} µm", color=color, fontsize=fontsize)


def render_widths(metadata):
    rows = read_csv(DATA_DIR / "channel_widths.csv")
    fig, axes = plt.subplots(1, 3, figsize=(7, 2.65))
    for ax, plate in zip(axes, ("P1", "P2", "P3")):
        pixels = np.load(DATA_DIR / f"{plate}_width_crop.npy", allow_pickle=False)
        (y0, y1), (x0, x1) = metadata["width_crops"][plate]["slices_yx"]
        ax.imshow(pixels, cmap="gray", extent=(x0-.5, x1-.5, y1-.5, y0-.5), interpolation="nearest")
        selected = [r for r in rows if r["plate"] == plate]
        for row in selected:
            x, ya, yb = (float(row[k]) for k in ("x0_px", "y0_px", "y1_px"))
            ax.plot([x, x], [ya, yb], color="#FFE500", marker="|", markersize=7, linewidth=1.5)
            ax.text(x+6, (ya+yb)/2, f"{row['measurement_id']}: {float(row['width_um']):.1f} µm",
                    color="#FFE500", fontsize=8, va="center", bbox=dict(facecolor="black", alpha=.65, pad=1))
        x = float(selected[0]["x0_px"])
        ax.set_xlim(x-25, x+100)
        ax.set_ylim(290, 155)
        ax.set_title(f"{plate} / R02C02", fontsize=10)
        ax.set_axis_off()
        bar = 20 / float(selected[0]["pixel_size_um"])
        ax.plot([x-17, x-17+bar], [282, 282], color="white", linewidth=2)
        ax.text(x-17, 276, "20 µm", color="white", fontsize=8)
    fig.subplots_adjust(left=.01, right=.99, top=.88, bottom=.02, wspace=.08)
    fig.savefig(OUTPUT_DIR / "channel_widths.png", dpi=300)
    fig.savefig(OUTPUT_DIR / "channel_widths.pdf", dpi=300)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-saved-data", action="store_true")
    parser.add_argument("--import-overlays", action="store_true")
    args = parser.parse_args()
    if args.import_saved_data:
        import_saved_data()
    if args.import_saved_data or args.import_overlays:
        import_saved_overlays()
    rows = count_data()
    metadata = json.loads((DATA_DIR / "sources.json").read_text())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(7, 7.6), facecolor="white")
    grid = fig.add_gridspec(4, 3, height_ratios=(1.5, 1.5, 1.9, 1.5),
                           left=.09, right=.98, top=.97, bottom=.07, hspace=.12, wspace=.12)
    for i, day in enumerate((0, 3)):
        ax = fig.add_subplot(grid[i, :])
        with Image.open(OUTPUT_DIR / f"dye_gradient_day{day}.png") as source:
            image = source.convert("RGB")
            ax.imshow(image)
        ax.set_axis_off()
        ax.set_ylim(image.height + 300, -.5)
        ax.set_title(f"Hour {day * 24}", fontsize=10, loc="left", pad=3)
        centres = metadata["tracer_scale"][f"day{day}_centres_xy"]
        span = np.linalg.norm(np.asarray(centres[1]) - centres[0])
        # Montage gutters are not physical distances; use one device's well pair.
        bar = 5000 * span / metadata["tracer_scale"]["spacing_um"]
        ax.plot([100, 100 + bar], [image.height + 190, image.height + 190], color="black", linewidth=2)
        ax.text(600, image.height + 190, "~5 mm", color="black", fontsize=8, va="center")
        if i == 0:
            fig.text(.02, ax.get_position().y1 + .01, "A", weight="bold", fontsize=13)
    for i, (plate, source) in enumerate(metadata["representatives"].items()):
        pair = grid[2, i].subgridspec(1, 2, wspace=.06)
        shape = source["source_shape_yx"]
        with Image.open(DATA_DIR / source["display"]) as image:
            pixels = np.asarray(image)
        outlines = json.loads((DATA_DIR / source["outlines"]).read_text())
        axes = [fig.add_subplot(pair[0, j]) for j in range(2)]
        for j, ax in enumerate(axes):
            # Use the same display window for each plate and its outline view.
            ax.imshow(pixels, cmap="gray_r", vmin=0, vmax=64,
                      extent=(0, shape[1], shape[0], 0), interpolation="nearest")
            if j:
                ax.add_collection(LineCollection(outlines, colors="#FFD400", linewidths=.35),
                                  autolim=False)
            ax.set_xlim(0, shape[1])
            ax.set_ylim(shape[0], 0)
            ax.set_axis_off()
            ax.set_title("CTβ" if j == 0 else "Outlines", fontsize=7, pad=3)
            scale_bar(ax, shape, source["pixel_size_um"], color="black", fontsize=6)
        left, right = (ax.get_position() for ax in axes)
        fig.text((left.x0 + right.x1) / 2, left.y1 + .025,
                 f"Plate {i+1} / {source['device']}", ha="center", fontsize=8)
        if i == 0:
            fig.text(.02, left.y1 + .025, "B", weight="bold", fontsize=13)
    ax = fig.add_subplot(grid[3, :])
    for i, (summary, color) in enumerate(zip(count_summaries(rows), COLORS)):
        ax.bar(i, summary["mean"], width=.66, color=color, alpha=.2, zorder=1)
        device_rows = sorted((r for r in rows if r["plate"] == summary["plate"]), key=lambda r: r["device"])
        for j, row in enumerate(device_rows):
            x = i + ((j * 7) % 24 - 11.5) / 60
            excluded = row["included"] == "False"
            ax.scatter(x, float(row["ctb_positive_cells"]), s=20,
                       marker="x" if excluded else "o", color="#BB2828" if excluded else color,
                       linewidths=1, alpha=.85, zorder=3)
        ax.errorbar(i, summary["mean"], yerr=summary["sd"], color="black",
                    fmt="_", markersize=11, capsize=4, linewidth=1.3, zorder=4)
    ax.set_xticks(range(3), [f"Plate {i+1}\nn = {s['n']}" for i, s in enumerate(count_summaries(rows))])
    ax.set_ylabel("CTβ-positive cells", fontsize=10)
    ax.set_xlim(-.5, 2.7)
    ax.set_ylim(bottom=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, color="#E6E6E6", linewidth=.6)
    fig.text(.02, ax.get_position().y1 + .01, "C", weight="bold", fontsize=13)
    ax.text(.99, .98, "Bars: mean; dots: devices; whiskers: SD\nRed crosses: excluded counting artifacts",
            transform=ax.transAxes, ha="right", va="top", fontsize=8)
    fig.savefig(OUTPUT_DIR / "draft_figure.pdf", dpi=300)
    fig.savefig(OUTPUT_DIR / "draft_figure.png", dpi=300)
    plt.close(fig)
    render_widths(metadata)
    print(json.dumps(count_summaries(rows), indent=2))


if __name__ == "__main__":
    main()
