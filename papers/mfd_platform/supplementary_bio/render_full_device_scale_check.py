"""Display a calibrated bar on the full native-resolution stitched device."""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from tifffile import memmap

from generate_pre_post_comparison_v3 import draw_scale_bar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    metadata = ET.parse(args.index)
    values = {float(e.text) * 1e6 for e in metadata.iter()
              if e.tag.rsplit("}", 1)[-1] in ("ImageResolutionX", "ImageResolutionY")}
    if len(values) != 1:
        raise ValueError(f"Expected one isotropic calibration: {values}")
    pixel_size = values.pop()
    original = memmap(args.image)
    if original.ndim != 2:
        raise ValueError(f"Expected a 2D stitched image: {original.shape}")
    low, high = np.percentile(original[::8, ::8], (1, 99.8))
    display = np.empty(original.shape, dtype=np.uint8)
    # Intensity conversion only; retain every source pixel and its coordinates.
    for start in range(0, original.shape[0], 256):
        block = np.asarray(original[start:start + 256], dtype=np.float32)
        display[start:start + 256] = (np.clip((block - low) / (high - low), 0, 1) * 255).astype(np.uint8)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    h, w = display.shape
    fig = plt.figure(figsize=(16, 16 * h / w), dpi=240, facecolor="black")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.imshow(display, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
    ax.axis("off")
    draw_scale_bar(ax, display.shape, pixel_size, 500)
    ax.set_xlim(-0.5, w - 0.5)
    ax.set_ylim(h - 0.5, -0.5)
    fig.savefig(args.output_dir / "full_stitched_device_500um.png", dpi=240, facecolor="black")
    plt.close(fig)

    # Known P1 R04C04 channel boundary positions, measured on the full image.
    x_left, x_right = 5924, 6177
    crop_box = (5700, 1700, 6400, 2450)
    x0, y0, x1, y1 = crop_box
    crop = display[y0:y1, x0:x1]
    fig, ax = plt.subplots(figsize=(7, 7.5), dpi=240, facecolor="black")
    ax.imshow(crop, cmap="gray", vmin=0, vmax=255,
              extent=(x0 - 0.5, x1 - 0.5, y1 - 0.5, y0 - 0.5), interpolation="nearest")
    for x in (x_left, x_right):
        ax.axvline(x, color="#00e5ff", linewidth=1, alpha=0.8)
    ax.annotate("", xy=(x_right, 1760), xytext=(x_left, 1760),
                arrowprops=dict(arrowstyle="<->", color="#00e5ff", lw=1.5))
    length = (x_right - x_left) * pixel_size
    ax.set_title(f"253 pixels = {length:.1f} µm\nDesigned channel length: 300 µm",
                 color="white", fontsize=18, pad=16)
    ax.axis("off")
    fig.savefig(args.output_dir / "channel_length_calibration_check.png", dpi=240,
                facecolor="black", bbox_inches="tight")
    plt.close(fig)
    print(f"Source: {w} x {h} px; {pixel_size:.10f} um/px")
    print(f"500 um bar: {500 / pixel_size:.6f} native pixels")
    print(f"Full field: {w * pixel_size / 1000:.3f} x {h * pixel_size / 1000:.3f} mm")


if __name__ == "__main__":
    main()
