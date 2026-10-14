#!/usr/bin/env python3
"""Build the control-reproducibility axotomy supplementary figure and PPTX."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median, stdev

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.ticker import FuncFormatter
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from axotomy_plate_mosaic import save_plate_mosaic

ROOT = Path(__file__).resolve().parents[3]
BIO_DIR = Path(__file__).resolve().parent
FIGURE_CODE_DIR = ROOT / "papers/mfd_platform/figures"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(FIGURE_CODE_DIR))

PLATES = ("p1", "p2", "p3")
PLATE_COLORS = {"p1": "#0072B2", "p2": "#E69F00", "p3": "#009E73"}
INK = "#17212B"
MUTED = "#5D6975"
GRID = "#D7DEE6"
EXCLUDED = "#C62828"
FONT_FAMILY = "Arial"
FONT_REGULAR = Path(font_manager.findfont(font_manager.FontProperties(family=FONT_FAMILY)))
FONT_BOLD = Path(
    font_manager.findfont(font_manager.FontProperties(family=FONT_FAMILY, weight="bold"))
)

matplotlib.rcParams.update(
    {
        "font.family": FONT_FAMILY,
        "font.size": 13.2,
        "axes.titlesize": 13.2,
        "axes.labelsize": 13.2,
        "xtick.labelsize": 13.2,
        "ytick.labelsize": 13.2,
        "legend.fontsize": 13.2,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

CANVAS_WIDTH = 5400
CANVAS_HEIGHT = 4510
PANEL_BOXES = {
    "A": (100, 60, 1450, 1370),
    "B": (1600, 60, 1800, 620),
    "C": (3450, 60, 1850, 620),
    "D": (1600, 740, 1800, 620),
    "E": (3450, 740, 1850, 620),
    "F": (100, 1430, 5200, 1880),
    "G": (100, 3340, 5200, 1130),
}
FINAL_DPI = 300
FONT_PT = 13.2
FONT_PX = round(FONT_PT * FINAL_DPI / 72)
GRAPH_FONT_PT = 14.5
GRAPH_FONT_PX = round(GRAPH_FONT_PT * FINAL_DPI / 72)
# Opera Phenix Index.xml ImageResolutionX/Y for every PRE and POST acquisition.
AXON_PIXEL_SIZE_UM = 1.1867525298988041
# The first two drug-assay acquisitions contain the cleaner immediate
# post-axotomy CTβ inset. Treatment had not yet occurred at this imaging stage,
# so examples can be drawn across later-treatment groups. Interleave plates to
# keep the 5 x 5 display balanced while excluding reviewed image outliers.
_AXOTOMY_CHECKS_BY_PLATE = tuple(
    tuple(
        source
        for source in sorted((BIO_DIR / plate / "overlay").glob(f"{plate}_*_overlay.tiff"))
        if "outlier" not in source.name
    )
    for plate in ("p1", "p2")
)
AXOTOMY_CHECK_SOURCES = tuple(
    sources[index]
    for index in range(max(map(len, _AXOTOMY_CHECKS_BY_PLATE)))
    for sources in _AXOTOMY_CHECKS_BY_PLATE
    if index < len(sources)
)[:18]
AXOTOMY_CHECK_KEYS = tuple(source.stem.removesuffix("_overlay") for source in AXOTOMY_CHECK_SOURCES)


@dataclass(frozen=True)
class Record:
    plate: str
    well: str
    row: int
    column: int
    pre_cell_count: float
    dapi_count: float
    total_axon_count: float
    pre_outlier: bool
    outlier_reason: str

    @property
    def key(self) -> str:
        return f"{self.plate}_{self.well}"

    @property
    def axon_per_pre(self) -> float:
        return self.total_axon_length_um / self.pre_cell_count

    @property
    def total_axon_length_um(self) -> float:
        return self.total_axon_count * AXON_PIXEL_SIZE_UM


@dataclass(frozen=True)
class MetricSpec:
    panel: str
    title: str
    ylabel: str
    value: str
    exclude_pre_artifacts: bool = False


METRICS = (
    MetricSpec(
        "B",
        "CTβ-positive cells",
        "CTβ-positive cells\n(count)",
        "pre_cell_count",
        True,
    ),
    MetricSpec(
        "C",
        "Regenerating axon length",
        "Axon skeleton length\n(µm)",
        "total_axon_length_um",
    ),
    MetricSpec(
        "D",
        "Cellular loading control",
        "Hoechst-positive nuclei\n(count)",
        "dapi_count",
    ),
    MetricSpec(
        "E",
        "Axon length per CTβ-positive cell",
        "Axon skeleton length /\nCTβ-positive cell (µm/cell)",
        "axon_per_pre",
        True,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--asset-root",
        type=Path,
        required=True,
        help="Portable output from generate_control_reproducibility_assets.py.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=BIO_DIR / "figure_output_control",
    )
    return parser.parse_args()


def read_records(data_csv: Path) -> list[Record]:
    records = []
    with data_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            records.append(
                Record(
                    plate=row["plate"],
                    well=row["well"],
                    row=int(row["row"].removeprefix("R")),
                    column=int(row["col"]),
                    pre_cell_count=float(row["pre_cell_count"]),
                    dapi_count=float(row["dapi_count"]),
                    total_axon_count=float(row["total_axon_count"]),
                    pre_outlier=row["pre_outlier"].strip().lower() == "true",
                    outlier_reason=row.get("outlier_reason", "").strip(),
                )
            )
    return records


def image_path(asset_root: Path, record: Record, overlay: bool) -> Path:
    variant = "overlay" if overlay else "no_overlay"
    return asset_root / record.plate / variant / f"{record.well}_pre_post_comparison.tiff"


def validate_inputs(asset_root: Path, records: list[Record]) -> None:
    if len(records) != 72:
        raise ValueError(f"Expected 72 control records; found {len(records)}")
    if len({record.key for record in records}) != 72:
        raise ValueError("Duplicate plate/well keys in control data")
    if {record.plate for record in records} != set(PLATES):
        raise ValueError("Control data must contain p1, p2, and p3")
    expected = {(row, column) for row in range(2, 8) for column in range(2, 6)}
    for plate in PLATES:
        plate_records = [record for record in records if record.plate == plate]
        if len(plate_records) != 24:
            raise ValueError(f"Expected 24 records for {plate}; found {len(plate_records)}")
        if {(record.row, record.column) for record in plate_records} != expected:
            raise ValueError(f"Unexpected well coordinates for {plate}")
    missing = [
        str(image_path(asset_root, record, overlay))
        for record in records
        for overlay in (True, False)
        if not image_path(asset_root, record, overlay).exists()
    ]
    if missing:
        raise FileNotFoundError(f"Missing {len(missing)} comparison TIFFs; first: {missing[0]}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def pil_font(size: int = FONT_PX, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def save_panel_a(path: Path) -> None:
    from generate_openmfd_design_figure import (
        COLORS as OPENMFD_COLORS, FRAME_STL, Bounds, DxfSources, StlMesh,
        add_bounds_background, draw_dxf_layer_raw, setup_raw_dxf_axis,
    )
    from openmfd.devices.presets import TwoCompartmentDeviceConfig
    from generate_device_assembly_protocol import (
        draw_scene_blender,
        single_device_cavity_render_parts,
    )

    width, height = PANEL_BOXES["A"][2:]
    config = TwoCompartmentDeviceConfig()
    dxf = DxfSources.from_generated_design()
    frame = StlMesh.from_file(FRAME_STL)
    frame_vertices = frame.triangles.reshape((-1, 3))
    plate_width = float(np.ptp(frame_vertices[:, 0]))
    plate_height = float(np.ptp(frame_vertices[:, 1]))
    array_width = config.grid_size[0] * config.casing_x
    array_height = config.grid_size[1] * config.casing_y
    array_left = (plate_width - array_width) / 2
    array_bottom = (plate_height - array_height) / 2

    fig = plt.figure(
        figsize=(width / FINAL_DPI, height / FINAL_DPI),
        dpi=FINAL_DPI,
        facecolor="white",
    )
    fig.suptitle("OpenMFD plate and assay device", fontsize=FONT_PT, y=0.985)
    plate_ax = fig.add_axes((0.07, 0.53, 0.86, 0.35))
    plate_ax.set_xlim(-2, plate_width + 2)
    plate_ax.set_ylim(-5, plate_height + 2)
    plate_ax.set_aspect("equal")
    plate_ax.axis("off")
    plate_ax.add_patch(
        FancyBboxPatch(
            (0, 0),
            plate_width,
            plate_height,
            boxstyle="round,pad=0,rounding_size=4",
            facecolor="#F4F7FA",
            edgecolor=INK,
            linewidth=1.0,
        )
    )
    interior_left = array_left + config.casing_x
    interior_bottom = array_bottom + config.casing_y
    plate_ax.add_patch(
        Rectangle(
            (interior_left, interior_bottom),
            4 * config.casing_x,
            6 * config.casing_y,
            facecolor="#FFF1B8",
            edgecolor="#B97B00",
            linewidth=0.8,
            alpha=0.65,
            zorder=1,
        )
    )
    top_segments = []
    bottom_segments = []
    for x_index in range(config.grid_size[0]):
        for y_index in range(config.grid_size[1]):
            dx = array_left + x_index * config.casing_x
            dy = array_bottom + y_index * config.casing_y
            top_segments.extend(
                [
                    ((a[0] + dx, a[1] + dy), (b[0] + dx, b[1] + dy))
                    for a, b in dxf.single_top.segments
                ]
            )
            bottom_segments.extend(
                [
                    ((a[0] + dx, a[1] + dy), (b[0] + dx, b[1] + dy))
                    for a, b in dxf.single_bottom.segments
                ]
            )
    plate_ax.add_collection(
        LineCollection(
            bottom_segments,
            colors=OPENMFD_COLORS["bottom"],
            linewidths=0.20,
            alpha=0.70,
            zorder=2,
        )
    )
    plate_ax.add_collection(
        LineCollection(
            top_segments,
            colors=OPENMFD_COLORS["top"],
            linewidths=0.36,
            alpha=0.96,
            zorder=3,
        )
    )
    plate_ax.text(
        plate_width / 2,
        -2.0,
        "48 devices / 96 wells",
        ha="center",
        va="top",
        fontsize=FONT_PT,
    )
    plate_ax.text(
        interior_left + 2 * config.casing_x,
        interior_bottom + 3 * config.casing_y,
        "24-device imaging region",
        ha="center",
        va="center",
        fontsize=FONT_PT,
        color="#815E00",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.84, "pad": 1.2},
        zorder=4,
    )

    zoom_ax = fig.add_axes((0.05, 0.10, 0.43, 0.27))
    zoom_bounds = Bounds.combine((dxf.single_top, dxf.single_bottom))
    setup_raw_dxf_axis(zoom_ax, zoom_bounds, 0.7, 0.7)
    add_bounds_background(zoom_ax, zoom_bounds, 0.7, 0.7)
    draw_dxf_layer_raw(zoom_ax, dxf.single_bottom, OPENMFD_COLORS["bottom"], 0.45, 0.72)
    draw_dxf_layer_raw(zoom_ax, dxf.single_top, OPENMFD_COLORS["top"], 1.1, 1.0)
    zoom_ax.text(4.5, 1.85, "Soma", ha="center", va="top", fontsize=FONT_PT, clip_on=False)
    zoom_ax.text(13.5, 1.85, "Axon", ha="center", va="top", fontsize=FONT_PT, clip_on=False)
    zoom_ax.text(9.0, 8.0, "2D device layout", ha="center", va="bottom", fontsize=FONT_PT)
    zoom_ax.plot(
        [0.36, 0.64],
        [-0.15, -0.15],
        color=INK,
        linewidth=2.2,
        solid_capstyle="butt",
        transform=zoom_ax.transAxes,
        clip_on=False,
    )
    zoom_ax.text(
        0.50,
        -0.18,
        "5 mm",
        ha="center",
        va="top",
        fontsize=FONT_PT,
        transform=zoom_ax.transAxes,
        clip_on=False,
    )

    render_cache = path.parent.parent / "assets/single_device_pdms_interior.png"
    render_cache.parent.mkdir(parents=True, exist_ok=True)
    if not render_cache.exists():
        render_figure = plt.figure(figsize=(6.0, 4.0), dpi=300, facecolor="white")
        render_axis = render_figure.add_axes((0, 0, 1, 1))
        render_axis.set_xlim(0, 1)
        render_axis.set_ylim(0, 1)
        render_axis.axis("off")
        draw_scene_blender(
            render_axis,
            single_device_cavity_render_parts(upside_down=False),
            (0.02, 0.02, 0.96, 0.96),
            azimuth=-38.0,
            elevation=10.0,
            z_scale=1.7,
            framing_margin=1.02,
        )
        render_figure.savefig(render_cache, dpi=300, facecolor="white")
        plt.close(render_figure)
    render_ax = fig.add_axes((0.50, 0.025, 0.49, 0.39))
    with Image.open(render_cache) as rendered_device:
        render_ax.imshow(rendered_device.convert("RGB"), interpolation="lanczos")
    render_ax.axis("off")
    render_ax.set_title("PDMS Device 3D Render", fontsize=FONT_PT, pad=3)
    fig.savefig(path, dpi=FINAL_DPI, facecolor="white")
    fig.savefig(path.with_suffix(".svg"), facecolor="white")
    plt.close(fig)


def crop_comparison_content(source: Image.Image) -> Image.Image:
    # Remove only the well-ID heading; retain image titles and the complete crops.
    top = round(source.height * 0.05)
    return source.crop((0, top, source.width, source.height))


def image_thumbnail(
    path: Path,
    size: tuple[int, int],
    crop_header: bool = True,
    background: str = "white",
) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGB")
        if crop_header:
            image = crop_comparison_content(image)
        image = ImageOps.contain(image, size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def suppress_rendered_pre_background(image: Image.Image, black_point: int = 28) -> Image.Image:
    """Darken residual grayscale background in the PRE half of overview exports."""
    array = np.asarray(image.convert("RGB")).copy()
    pre = array[:, : array.shape[1] // 2]
    grayscale = np.ptp(pre.astype(np.int16), axis=2) <= 3
    values = pre[..., 0].astype(np.float32)
    remapped = np.clip((values - black_point) * 255 / (255 - black_point), 0, 255).astype(np.uint8)
    pre[grayscale] = np.repeat(remapped[..., None], 3, axis=2)[grayscale]
    return Image.fromarray(array, mode="RGB")


def microscopy_content_crop(image: Image.Image) -> Image.Image:
    """Crop the dominant dark microscopy field from a microscopy panel."""
    array = np.asarray(image.convert("RGB"))
    dark = array.mean(axis=2) < 210
    rows = np.flatnonzero(dark.mean(axis=1) > 0.25)
    columns = np.flatnonzero(dark.mean(axis=0) > 0.25)
    if not len(rows) or not len(columns):
        return image.copy()
    return image.crop((int(columns[0]), int(rows[0]), int(columns[-1] + 1), int(rows[-1] + 1)))


def render_clean_mosaic_tiles(
    asset_root: Path,
    records: list[Record],
    output_dir: Path,
) -> dict[str, Path]:
    """Build compact mosaics from CTβ-positive-cell and regeneration overlays."""
    from generate_pre_post_comparison_v3 import (
        convert_to_uint8_percentile,
        post_image_path,
        post_roi_path,
        pre_image_path,
        pre_roi_path,
        prepare_pre_display_image,
        safe_load_rois,
    )
    from skimage import io

    manifest = json.loads((asset_root / "asset_manifest.json").read_text(encoding="utf-8"))
    dataset_root = Path(manifest["dataset_root"])
    tile_paths = {}
    tile_size = (500, 408)
    half_width = (tile_size[0] - 6) // 2

    for record in records:
        output_path = output_dir / record.plate / f"{record.well}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tile_paths[record.key] = output_path
        if output_path.exists():
            continue

        plate_config = manifest["plates"][record.plate]
        pre_dir = dataset_root / plate_config["pre"]
        post_dir = dataset_root / plate_config["post"]
        post_image = post_image_path(
            post_dir,
            record.well,
            int(manifest["post_axon_channel"]),
            "images",
        )
        if not post_image.exists() and plate_config.get("post_fallback"):
            post_dir = dataset_root / plate_config["post_fallback"]
            post_image = post_image_path(
                post_dir,
                record.well,
                int(manifest["post_axon_channel"]),
                "images",
            )
        pre_array = prepare_pre_display_image(io.imread(pre_image_path(pre_dir, record.well)))
        pre_source = Image.fromarray(pre_array, mode="L").convert("RGB")
        scale = min(half_width / pre_source.width, tile_size[1] / pre_source.height)
        pre_width = max(1, round(pre_source.width * scale))
        pre_height = max(1, round(pre_source.height * scale))
        pre_panel = pre_source.resize((pre_width, pre_height), Image.Resampling.LANCZOS)
        pre_canvas = Image.new("RGB", (half_width, tile_size[1]), "black")
        offset_x = (half_width - pre_width) // 2
        offset_y = (tile_size[1] - pre_height) // 2
        pre_canvas.paste(pre_panel, (offset_x, offset_y))
        roi_draw = ImageDraw.Draw(pre_canvas)
        for roi in safe_load_rois(
            pre_roi_path(pre_dir, record.well, int(manifest["pre_roi_step"]))
        ):
            points = [
                (offset_x + float(x) * scale, offset_y + float(y) * scale)
                for x, y in roi.coordinates
            ]
            if roi.closed and len(points) > 2:
                points.append(points[0])
            if len(points) > 1:
                roi_draw.line(points, fill="#FFFF00", width=2)

        post_array = convert_to_uint8_percentile(io.imread(post_image))
        post_source = Image.fromarray(post_array, mode="L").convert("RGB")
        post_scale = min(half_width / post_source.width, tile_size[1] / post_source.height)
        post_width = max(1, round(post_source.width * post_scale))
        post_height = max(1, round(post_source.height * post_scale))
        post_panel = post_source.resize(
            (post_width, post_height),
            Image.Resampling.LANCZOS,
        )
        post_canvas = Image.new("RGB", (half_width, tile_size[1]), "black")
        post_offset_x = (half_width - post_width) // 2
        post_offset_y = (tile_size[1] - post_height) // 2
        post_canvas.paste(post_panel, (post_offset_x, post_offset_y))
        post_draw = ImageDraw.Draw(post_canvas)
        for roi in safe_load_rois(
            post_roi_path(
                post_dir,
                record.well,
                int(manifest["post_axon_channel"]),
                int(manifest["post_roi_step"]),
                "images",
            )
        ):
            points = [
                (
                    post_offset_x + float(x) * post_scale,
                    post_offset_y + float(y) * post_scale,
                )
                for x, y in roi.coordinates
            ]
            if roi.closed and len(points) > 2:
                points.append(points[0])
            if len(points) > 1:
                post_draw.line(points, fill="#FFFF00", width=2)

        tile = Image.new("RGB", tile_size, "white")
        tile.paste(pre_canvas, (0, 0))
        tile.paste(post_canvas, (half_width + 6, 0))
        tile.save(output_path, dpi=(FINAL_DPI, FINAL_DPI), compress_level=4)
    return tile_paths


def save_mosaic_panel(asset_root: Path, records: list[Record], path: Path) -> None:
    assets_dir = path.parent.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    mosaic_path = assets_dir / "panel_B_three_plate_mosaic.png"
    clean_tiles = render_clean_mosaic_tiles(
        asset_root,
        records,
        assets_dir / "mosaic_clean_pre_regeneration_v3",
    )
    save_plate_mosaic(
        records,
        mosaic_path,
        plates=PLATES,
        image_path_for_record=lambda record: clean_tiles[record.key],
        is_excluded=lambda record: record.pre_outlier,
        plate_colors=PLATE_COLORS,
        legend_plates=(),
        title="DMSO-only experiment: three plate mosaics",
        font_regular=FONT_REGULAR,
        font_bold=FONT_BOLD,
        excluded_label="red outline: excluded",
        label_font_px=FONT_PX,
    )
    width, height = PANEL_BOXES["F"][2:]
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    cut_box_width = 1400
    gap = 24
    with Image.open(mosaic_path) as mosaic_source:
        mosaic_source_width = mosaic_source.width
    mosaic = contain_image(mosaic_path, (width - cut_box_width - gap, height))
    mosaic_top = (height - mosaic.height) // 2
    check_gap = 5
    check_columns = 9
    check_rows = 2
    check_width = (cut_box_width - (check_columns + 1) * check_gap) // check_columns
    # Match the CTβ grid to the actual six-row plate-image region, excluding
    # the mosaic title and legend margins from the alignment calculation.
    mosaic_source_top = 5 * FONT_PX
    mosaic_source_plate_height = 6 * 204
    mosaic_scale = mosaic.width / mosaic_source_width
    check_total_height = round(mosaic_source_plate_height * mosaic_scale)
    check_height = (check_total_height - check_gap) // check_rows
    check_top = mosaic_top + round(mosaic_source_top * mosaic_scale)
    draw.text(
        (cut_box_width / 2, check_top - 135),
        "Post-axotomy CTβ",
        font=pil_font(bold=True),
        fill=INK,
        anchor="ma",
    )
    draw.text(
        (cut_box_width / 2, check_top - 75),
        "Immediate cut verification",
        font=pil_font(),
        fill=MUTED,
        anchor="ma",
    )
    missing = [source for source in AXOTOMY_CHECK_SOURCES if not source.exists()]
    if missing:
        raise FileNotFoundError(f"Missing drug DMSO axotomy overlay: {missing[0]}")
    for index, source in enumerate(AXOTOMY_CHECK_SOURCES):
        column = index % check_columns
        row = index // check_columns
        x = check_gap + column * (check_width + check_gap)
        y = check_top + row * (check_height + check_gap)
        with Image.open(source) as source_image:
            # Keep only the cleaner immediate post-axotomy CTβ inset. The
            # regeneration panel surrounding it does not belong in this row.
            width_source, height_source = source_image.size
            axotomy = source_image.convert("RGB").crop(
                (
                    round(width_source * 0.885),
                    round(height_source * 0.15),
                    round(width_source * 0.985),
                    round(height_source * 0.78),
                )
            )
        check = ImageOps.contain(
            axotomy,
            (round(check_width * 0.98), round(check_height * 0.98)),
            Image.Resampling.LANCZOS,
        )
        paste_x = x + (check_width - check.width) // 2
        paste_y = y + (check_height - check.height) // 2
        canvas.paste(check, (paste_x, paste_y))
        draw.rectangle(
            (paste_x, paste_y, paste_x + check.width - 1, paste_y + check.height - 1),
            outline="#7A8793",
            width=2,
        )
    canvas.paste(
        mosaic,
        (cut_box_width + gap, mosaic_top),
    )
    canvas.save(path, dpi=(FINAL_DPI, FINAL_DPI), compress_level=5)


def representative_records(records: list[Record]) -> list[Record]:
    """Choose a non-excluded device nearest each plate's four metric medians."""
    selected = []
    names = tuple(spec.value for spec in METRICS)
    for plate in PLATES:
        candidates = sorted(
            (record for record in records if record.plate == plate and not record.pre_outlier),
            key=lambda record: record.well,
        )
        if not candidates:
            raise ValueError(f"No non-excluded representative for {plate}")
        centers = {name: median(metric_value(r, name) for r in candidates) for name in names}
        scales = {
            name: median(abs(metric_value(r, name) - centers[name]) for r in candidates) or 1.0
            for name in names
        }
        selected.append(min(candidates, key=lambda r: sum(
            ((metric_value(r, name) - centers[name]) / scales[name]) ** 2 for name in names
        )))
    return selected


def render_representative_assets(
    asset_root: Path,
    selected: list[Record],
    output_dir: Path,
) -> dict[tuple[str, bool], Path]:
    """Regenerate selected comparisons from source data without embedded insets."""
    from generate_pre_post_comparison_v3 import (
        create_comparison_figure,
        post_image_path,
        post_roi_path,
        pre_image_path,
        pre_roi_path,
        safe_load_rois,
    )

    manifest = json.loads((asset_root / "asset_manifest.json").read_text(encoding="utf-8"))
    dataset_root = Path(manifest["dataset_root"])
    rendered = {}
    for record in selected:
        plate_config = manifest["plates"][record.plate]
        pre_dir = dataset_root / plate_config["pre"]
        post_dir = dataset_root / plate_config["post"]
        for overlay in (False, True):
            variant = "overlay" if overlay else "no_overlay"
            output_path = output_dir / record.plate / variant / f"{record.well}_pre_post_comparison.tiff"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            pre_rois = safe_load_rois(
                pre_roi_path(pre_dir, record.well, int(manifest["pre_roi_step"]))
            ) if overlay else []
            post_rois = safe_load_rois(
                post_roi_path(
                    post_dir,
                    record.well,
                    int(manifest["post_axon_channel"]),
                    int(manifest["post_roi_step"]),
                    "images",
                )
            ) if overlay else []
            create_comparison_figure(
                pre_image_path(pre_dir, record.well),
                pre_rois,
                post_image_path(
                    post_dir,
                    record.well,
                    int(manifest["post_axon_channel"]),
                    "images",
                ),
                post_rois,
                None,
                record.well,
                output_path,
                no_overlays=not overlay,
                figure_title="",
                scale_bar_pixel_size_um=AXON_PIXEL_SIZE_UM,
                scale_bar_length_um=500.0,
            )
            rendered[(record.key, overlay)] = output_path
    return rendered


def save_panel_g(asset_root: Path, records: list[Record], path: Path) -> list[Record]:
    selected = representative_records(records)
    representative_paths = render_representative_assets(
        asset_root,
        selected,
        path.parent.parent / "assets/representatives_no_inset",
    )
    width, height = PANEL_BOXES["G"][2:]
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    mosaic_path = path.parent.parent / "assets/panel_B_three_plate_mosaic.png"
    with Image.open(mosaic_path) as mosaic_source:
        mosaic_scale = min(
            (PANEL_BOXES["F"][2] - 1400 - 24) / mosaic_source.width,
            PANEL_BOXES["F"][3] / mosaic_source.height,
        )
    plate_title_font = pil_font(size=round(FONT_PX * mosaic_scale), bold=True)
    draw.text((width / 2, 0), "Representative DMSO devices: CTβ-positive cells and regenerating axons",
              font=pil_font(bold=True), fill=INK, anchor="ma")
    group_gap, pair_gap, top = 70, 24, 165
    group_width = (width - 2 * group_gap) // 3
    tile_width = (group_width - pair_gap) // 2
    for index, record in enumerate(selected):
        x = index * (group_width + group_gap)
        draw.text((x + group_width / 2, 58), f"Plate {record.plate[1:]}",
                  font=plate_title_font, fill=INK, anchor="ma")
        for variant_index, overlay in enumerate((False, True)):
            tile_x = x + variant_index * (tile_width + pair_gap)
            draw.text((tile_x + tile_width / 2, 112), "Traced" if overlay else "Untraced",
                      font=pil_font(), fill=INK, anchor="ma")
            tile = image_thumbnail(representative_paths[(record.key, overlay)],
                                   (tile_width, height - top))
            canvas.paste(tile, (tile_x, top))
    canvas.save(path, dpi=(FINAL_DPI, FINAL_DPI), compress_level=5)
    return selected


def metric_value(record: Record, name: str) -> float:
    return float(getattr(record, name))


def save_metric_panel(
    records: list[Record],
    spec: MetricSpec,
    path: Path,
    size: tuple[int, int] | None = None,
) -> None:
    width, height = size or PANEL_BOXES[spec.panel][2:]
    compact = width < 2000
    figure, axis = plt.subplots(
        figsize=(width / FINAL_DPI, height / FINAL_DPI),
        dpi=FINAL_DPI,
        facecolor="white",
    )
    x_values = np.arange(len(PLATES), dtype=float)
    means = []
    deviations = []
    counts = []
    for plate in PLATES:
        retained = [
            record
            for record in records
            if record.plate == plate and (not spec.exclude_pre_artifacts or not record.pre_outlier)
        ]
        values = [metric_value(record, spec.value) for record in retained]
        means.append(mean(values))
        deviations.append(stdev(values))
        counts.append(len(values))

    axis.bar(
        x_values,
        means,
        width=0.62,
        color=[PLATE_COLORS[plate] for plate in PLATES],
        alpha=0.33,
        edgecolor=INK,
        linewidth=1.0,
        zorder=1,
    )
    lower = np.minimum(np.asarray(means), np.asarray(deviations))
    axis.errorbar(
        x_values,
        means,
        yerr=np.vstack((lower, deviations)),
        fmt="none",
        ecolor=INK,
        elinewidth=1.1,
        capsize=4,
        capthick=1.1,
        zorder=2,
    )
    for plate_index, plate in enumerate(PLATES):
        plate_records = [record for record in records if record.plate == plate]
        retained = [
            record
            for record in plate_records
            if not spec.exclude_pre_artifacts or not record.pre_outlier
        ]
        jitter = [(((record.row * 7 + record.column * 11) % 13) - 6) * 0.018 for record in retained]
        axis.scatter(
            np.asarray(jitter) + plate_index,
            [metric_value(record, spec.value) for record in retained],
            s=24,
            color=PLATE_COLORS[plate],
            edgecolors="white",
            linewidths=0.45,
            alpha=0.9,
            zorder=3,
        )
        if spec.exclude_pre_artifacts:
            excluded = [record for record in plate_records if record.pre_outlier]
            axis.scatter(
                [plate_index] * len(excluded),
                [metric_value(record, spec.value) for record in excluded],
                marker="x",
                s=42,
                color=EXCLUDED,
                linewidths=1.2,
                zorder=4,
            )

    title = spec.title
    if compact and spec.panel == "E":
        title = "Axon length / CTβ-positive cell"
    axis.set_title(title, fontsize=GRAPH_FONT_PT, pad=6 if compact else 11)
    axis.set_ylabel(spec.ylabel, fontsize=11.5 if compact else GRAPH_FONT_PT, labelpad=5 if compact else 4)
    axis.set_xticks(x_values)
    axis.set_xticklabels([f"Plate {plate[1:]}\nn={count}" for plate, count in zip(PLATES, counts)])
    axis.set_xlim(-0.6, 2.6)
    axis.set_ylim(bottom=0)
    axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    axis.grid(axis="y", color=GRID, linewidth=0.75, alpha=0.9, zorder=0)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#7A8793")
    axis.tick_params(colors=INK)
    note = "Mean +/- SD; points: devices"
    if spec.exclude_pre_artifacts:
        note += "\nRed x: excluded" if compact else "; red x: excluded"
    if compact:
        axis.tick_params(axis="both", labelsize=12, pad=2)
        figure.subplots_adjust(left=0.27, right=0.98, bottom=0.24, top=0.82)
    else:
        figure.text(
            0.99,
            0.01,
            note,
            ha="right",
            va="bottom",
            fontsize=FONT_PT,
            color=MUTED,
        )
        figure.tight_layout(rect=(0.04, 0.08, 0.99, 0.98))
    figure.savefig(path, dpi=FINAL_DPI, facecolor="white")
    figure.savefig(path.with_suffix(".svg"), facecolor="white")
    plt.close(figure)


def contain_image(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.contain(source.convert("RGB"), size, Image.Resampling.LANCZOS)


def compose_figure(panel_paths: dict[str, Path], output_path: Path) -> None:
    canvas = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
    draw = ImageDraw.Draw(canvas)
    for label, box in PANEL_BOXES.items():
        x, y, width, height = box
        panel = contain_image(panel_paths[label], (width, height))
        paste_x = x + (width - panel.width) // 2
        paste_y = y + (height - panel.height) // 2
        canvas.paste(panel, (paste_x, paste_y))
        draw.text(
            (x - 28, y + 2),
            label,
            font=pil_font(bold=True),
            fill=INK,
            anchor="ra",
        )
    draw.text(
        (3450, 1400),
        "Bars: mean +/- SD; points: devices; red x: excluded where shown",
        font=pil_font(size=GRAPH_FONT_PX),
        fill=MUTED,
        anchor="mm",
    )
    canvas.save(output_path, dpi=(FINAL_DPI, FINAL_DPI), compress_level=4)
    canvas.save(output_path.with_suffix(".pdf"), resolution=FINAL_DPI)


def add_picture_contained(
    slide,
    path: Path,
    box: tuple[int, int, int, int],
    slide_width: float,
) -> None:
    x_px, y_px, width_px, height_px = box
    x = x_px / CANVAS_WIDTH * slide_width
    y = y_px / CANVAS_WIDTH * slide_width
    width = width_px / CANVAS_WIDTH * slide_width
    height = height_px / CANVAS_WIDTH * slide_width
    with Image.open(path) as image:
        image_aspect = image.width / image.height
    box_aspect = width / height
    if image_aspect > box_aspect:
        picture_width = width
        picture_height = width / image_aspect
        picture_x = x
        picture_y = y + (height - picture_height) / 2
    else:
        picture_height = height
        picture_width = height * image_aspect
        picture_x = x + (width - picture_width) / 2
        picture_y = y
    picture = slide.shapes.add_picture(
        str(path),
        Inches(picture_x),
        Inches(picture_y),
        width=Inches(picture_width),
        height=Inches(picture_height),
    )
    picture.name = f"Panel {path.stem.removeprefix('panel_')} - {path.name}"


def build_powerpoint(panel_paths: dict[str, Path], output_path: Path) -> None:
    presentation = Presentation()
    slide_width = CANVAS_WIDTH / FINAL_DPI
    slide_height = slide_width * CANVAS_HEIGHT / CANVAS_WIDTH
    presentation.slide_width = Inches(slide_width)
    presentation.slide_height = Inches(slide_height)
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = RGBColor(255, 255, 255)

    for label, box in PANEL_BOXES.items():
        add_picture_contained(slide, panel_paths[label], box, slide_width)
        x, y, _, _ = box
        label_box = slide.shapes.add_textbox(
            Inches((x - 100) / CANVAS_WIDTH * slide_width),
            Inches((y + 2) / CANVAS_WIDTH * slide_width),
            Inches(0.20),
            Inches(0.22),
        )
        label_box.name = f"Panel label {label}"
        frame = label_box.text_frame
        frame.clear()
        frame.margin_left = 0
        frame.margin_right = 0
        frame.margin_top = 0
        frame.margin_bottom = 0
        paragraph = frame.paragraphs[0]
        paragraph.alignment = PP_ALIGN.RIGHT
        run = paragraph.add_run()
        run.text = label
        run.font.name = FONT_FAMILY
        run.font.size = Pt(FONT_PT)
        run.font.bold = True
        run.font.color.rgb = RGBColor(23, 33, 43)
    presentation.save(output_path)


def write_manifest(
    data_csv: Path,
    records: list[Record],
    panel_paths: dict[str, Path],
    output_dir: Path,
    selected: list[Record],
) -> None:
    manifest = {
        "figure_scope": "all-DMSO/no-drug inter-plate control reproducibility",
        "authoritative_data": str(data_csv),
        "data_sha256": sha256(data_csv),
        "records_total": len(records),
        "plates": {plate: sum(record.plate == plate for record in records) for plate in PLATES},
        "pre_artifacts_flagged": [record.key for record in records if record.pre_outlier],
        "pre_artifact_policy": (
            "Flagged cell-counting artifacts are excluded only from CTβ-positive-cell "
            "and axon-length-per-cell summary bars; red x markers retain them in those panels."
        ),
        "ctb_measurement": "CTβ-647-positive cells, channel 2",
        "axon_measurement": (
            "Total skeleton length converted from pixels using the Opera Phenix "
            f"acquisition calibration ({AXON_PIXEL_SIZE_UM:.10f} µm/pixel)"
        ),
        "microscopy_scale_bar": (
            "500 µm = "
            f"{500.0 / AXON_PIXEL_SIZE_UM:.3f} source-image pixels; calibration "
            "verified against acquisition metadata, full-resolution stitching, and the 300 µm CAD channel length"
        ),
        "font": "Arial; base 13.2 pt and graph text up to 14.5 pt",
        "representative_devices": {record.plate: record.key for record in selected},
        "representative_rule": "Per-plate minimum squared distance to four metric medians, scaled by median absolute deviations; excluded wells ineligible; well-ID tie break",
        "representative_views": "Same device untraced and traced; embedded cut-check insets removed; well IDs omitted from panel G",
        "pre_display_processing": "White top-hat background subtraction (30 px radius, 4x reduced estimate) followed by 0.1-99.9 percentile normalization in panel B mosaics and panel G; display only",
        "mosaic_views": "CTβ-positive-cell overlay and regenerating-axon overlay for each DMSO-only control device; no axotomy inset",
        "axotomy_check_devices": list(AXOTOMY_CHECK_KEYS),
        "axotomy_check_sources": [str(path.relative_to(BIO_DIR)) for path in AXOTOMY_CHECK_SOURCES],
        "axotomy_check_view": "Immediate post-axotomy CTβ inset only from improved pre-treatment acquisitions; regeneration panel excluded",
        "replication": "Three technical replicate plates from one animal; not three independent biological replicates",
        "metric_summary_counts": {
            spec.panel: {plate: sum(r.plate == plate and (not spec.exclude_pre_artifacts or not r.pre_outlier)
                                   for r in records) for plate in PLATES}
            for spec in METRICS
        },
        "panels": {label: str(path) for label, path in panel_paths.items()},
    }
    (output_dir / "figure_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    panels_dir = output_dir / "panels"
    output_dir.mkdir(parents=True, exist_ok=True)
    panels_dir.mkdir(parents=True, exist_ok=True)
    for stale_path in panels_dir.glob("panel_*.*"):
        if stale_path.stem.removeprefix("panel_") not in PANEL_BOXES:
            stale_path.unlink()
    for raster_only_panel in ("F", "G"):
        stale_svg = panels_dir / f"panel_{raster_only_panel}.svg"
        if stale_svg.exists():
            stale_svg.unlink()
    data_csv = args.asset_root / "data.csv"
    records = read_records(data_csv)
    validate_inputs(args.asset_root, records)

    panel_paths = {label: panels_dir / f"panel_{label}.png" for label in PANEL_BOXES}
    save_panel_a(panel_paths["A"])
    save_mosaic_panel(args.asset_root, records, panel_paths["F"])
    for spec in METRICS:
        save_metric_panel(records, spec, panel_paths[spec.panel])
    selected = save_panel_g(args.asset_root, records, panel_paths["G"])

    figure_path = output_dir / "axotomy_control_reproducibility_figure.png"
    compose_figure(panel_paths, figure_path)
    build_powerpoint(
        panel_paths,
        output_dir / "axotomy_control_reproducibility_figure_editable.pptx",
    )
    write_manifest(data_csv, records, panel_paths, output_dir, selected)
    print(f"Wrote {figure_path}")
    print(f"Wrote {figure_path.with_suffix('.pdf')}")
    print(f"Wrote {output_dir / 'axotomy_control_reproducibility_figure_editable.pptx'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
