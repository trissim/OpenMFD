#!/usr/bin/env python3
"""Render validation figures from retained, typed measurements.

This renderer does not import or reinterpret external analyses. Scientific
sources and their original import verification remain in supplementary/validation.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from statistics import mean, stdev
from typing import ClassVar, Self, cast, get_type_hints

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from metaclass_registry import AutoRegisterMeta
import numpy as np
from PIL import Image

logging.getLogger("fontTools").setLevel(logging.WARNING)
FIGURE_DIR = Path(__file__).resolve().parent
ROOT = FIGURE_DIR.parent
OUTPUT_DIR = FIGURE_DIR / "final_drop/Fig5_plate_layout_validation"
DATA_DIR = ROOT / "supplementary/validation"
COLORS = ("#0072B2", "#D17800", "#00856A")
PANEL_LABEL_GAP_INCHES = 0.08
TRACER_SCALE_MARGIN_PX = 420
FIGURE_SIZE = (7.0, 5.8)
FIGURE_LEFT = 0.045
FIGURE_RIGHT = 0.99
FIGURE_TOP = 0.97
FIGURE_BOTTOM = 0.08
FIGURE_ROW_GAP = 0.06
COUNT_PANEL_FRACTION = 0.27
IMAGE_PANEL_FRACTION = (1.0 - COUNT_PANEL_FRACTION) / 2.0
WireObject = Mapping[str, object]


class PlateId(str):
    def __new__(cls, wire: str) -> Self:
        match = re.fullmatch(r"[pP]([1-9][0-9]*)", wire)
        if match is None:
            raise ValueError(f"Invalid plate identity: {wire!r}")
        return super().__new__(cls, f"p{int(match[1])}")

    @property
    def label(self) -> str:
        return f"Plate {self[1:]}"


class DeviceId(str):
    def __new__(cls, wire: str) -> Self:
        value = wire.upper()
        if re.fullmatch(r"R[0-9]{2}C[0-9]{2}", value) is None:
            raise ValueError(f"Invalid device identity: {wire!r}")
        return super().__new__(cls, value)


class CsvRecord:
    """Decode fields once, deriving names and conversions from the dataclass."""
    @classmethod
    def record_type(cls, row: Mapping[str, str]) -> type[Self]:
        return cls

    @classmethod
    def read(cls, path: Path) -> tuple[Self, ...]:
        result: list[Self] = []
        with path.open(newline="") as stream:
            for row in csv.DictReader(stream):
                record = cls.record_type(row)
                annotations = get_type_hints(record)
                result.append(record(**{
                    field.name: annotations[field.name](row[field.name])
                    for field in fields(record)
                }))
        return tuple(result)


@dataclass(frozen=True)
class CtbCount(CsvRecord, metaclass=AutoRegisterMeta):
    """A saved count and its recorded inclusion state, not a new QC decision."""
    plate: PlateId
    device: DeviceId
    ctb_positive_cells: float
    exclusion_reason: str

    __registry__: ClassVar[dict[str, type[CtbCount]]] = {}
    __registry_key__: ClassVar[str] = "included_wire"
    __skip_if_no_key__: ClassVar[bool] = True
    included_wire: ClassVar[str]
    marker: ClassVar[str] = "x"

    @classmethod
    def record_type(cls, row: Mapping[str, str]) -> type[Self]:
        return cast(type[Self], cls.__registry__[row["included"]])

    @property
    def summary_values(self) -> tuple[float, ...]:
        return ()

    def point_color(self, plate_color: str) -> str:
        return "#BB2828"

    def draw(self, ax: Axes, x: float, plate_color: str) -> None:
        ax.scatter(x, self.ctb_positive_cells, s=20, marker=self.marker,
                   color=self.point_color(plate_color), linewidths=1, alpha=.85, zorder=3)


class IncludedCtbCount(CtbCount):
    included_wire = "True"
    marker = "o"

    @property
    def summary_values(self) -> tuple[float, ...]:
        return (self.ctb_positive_cells,)

    def point_color(self, plate_color: str) -> str:
        return plate_color


class ExcludedCtbCount(CtbCount):
    """Excluded by the retained flag; the reason's validity is not inferred."""
    included_wire = "False"


@dataclass(frozen=True)
class CountSummary:
    plate: PlateId
    n: int
    mean: float
    sd: float


@dataclass(frozen=True)
class PlateCounts:
    plate: PlateId
    devices: tuple[CtbCount, ...]

    @property
    def summary(self) -> CountSummary:
        values = tuple(value for device in self.devices for value in device.summary_values)
        return CountSummary(self.plate, len(values), mean(values), stdev(values))

    @property
    def label(self) -> str:
        return f"{self.plate.label}\nn = {self.summary.n}"

    def draw(self, ax: Axes, index: int, color: str) -> None:
        summary = self.summary
        ax.bar(index, summary.mean, width=.66, color=color, alpha=.2, zorder=1)
        for j, device in enumerate(sorted(self.devices, key=lambda d: d.device)):
            x = index + ((j * 7) % 24 - 11.5) / 60
            device.draw(ax, x, color)
        ax.errorbar(index, summary.mean, yerr=summary.sd, color="black",
                    fmt="_", markersize=11, capsize=4, linewidth=1.3, zorder=4)


@dataclass(frozen=True)
class CountDataset:
    plates: tuple[PlateCounts, ...]

    @classmethod
    def read(cls, path: Path) -> Self:
        rows = CtbCount.read(path)
        expected = {(PlateId(f"p{p}"), DeviceId(f"R{r:02d}C{c:02d}"))
                    for p in range(1, 4) for r in range(2, 8) for c in range(2, 6)}
        if len(rows) != len(expected) or {(r.plate, r.device) for r in rows} != expected:
            raise ValueError("Expected the 72 unique interior devices")
        return cls(tuple(PlateCounts(plate, tuple(r for r in rows if r.plate == plate))
                         for plate in sorted({r.plate for r in rows})))

    def draw(self, ax: Axes) -> None:
        for i, (plate, color) in enumerate(zip(self.plates, COLORS, strict=True)):
            plate.draw(ax, i, color)
        ax.set_xticks(range(len(self.plates)), [plate.label for plate in self.plates])


@dataclass(frozen=True)
class WidthMeasurement(CsvRecord):
    measurement_id: str
    plate: PlateId
    device: DeviceId
    x0_px: float
    y0_px: float
    x1_px: float
    y1_px: float
    width_px: float
    pixel_size_um: float
    width_um: float

    def draw(self, ax: Axes) -> None:
        ax.plot([self.x0_px, self.x0_px], [self.y0_px, self.y1_px], color="#FFE500",
                marker="|", markersize=7, linewidth=1.5)
        ax.text(self.x0_px+6, (self.y0_px+self.y1_px)/2,
                f"{self.measurement_id}: {self.width_um:.1f} µm", color="#FFE500",
                fontsize=8, va="center", bbox=dict(facecolor="black", alpha=.65, pad=1))


@dataclass(frozen=True)
class ImageShape:
    height: int
    width: int

    @classmethod
    def decode(cls, values: Sequence[int]) -> Self:
        height, width = values
        return cls(int(height), int(width))


@dataclass(frozen=True)
class CtbView:
    plate: PlateId
    device: DeviceId
    shape: ImageShape
    pixel_size_um: float
    display: Path
    outlines: tuple[tuple[Point, ...], ...]

    @classmethod
    def decode(cls, plate: str, wire: WireObject) -> Self:
        contours = cast(Sequence[Sequence[Sequence[float]]],
                        json.loads((DATA_DIR / str(wire["outlines"])).read_text()))
        return cls(PlateId(plate), DeviceId(str(wire["device"])),
                   ImageShape.decode(cast(Sequence[int], wire["source_shape_yx"])),
                   float(cast(float, wire["pixel_size_um"])), Path(str(wire["display"])),
                   tuple(tuple(Point.decode(point) for point in contour) for contour in contours))

    def draw(self, image_ax: Axes, outline_ax: Axes) -> None:
        with Image.open(DATA_DIR / self.display) as image:
            pixels = np.asarray(image)
        for ax in (image_ax, outline_ax):
            ax.imshow(pixels, cmap="gray_r", vmin=0, vmax=64,
                      extent=(-.5, self.shape.width-.5, self.shape.height-.5, -.5),
                      interpolation="nearest")
            ax.set_xlim(-.5, self.shape.width-.5)
            ax.set_ylim(self.shape.height-.5, -.5)
            ax.set_axis_off()
            x, y = self.shape.width * .08, self.shape.height * .94
            ax.plot([x, x + 500 / self.pixel_size_um], [y, y], color="black", linewidth=2)
            ax.text(x, y - self.shape.height * .025, "500 µm", color="black", fontsize=7)
        outline_ax.add_collection(LineCollection(
            tuple(tuple((point.x, point.y) for point in contour) for contour in self.outlines),
            colors="#D17800", linewidths=.4), autolim=False)
        image_ax.set_title("CTB", fontsize=8, pad=3)
        outline_ax.set_title("Outlines", fontsize=8, pad=3)
        left = image_ax.get_position()
        right = outline_ax.get_position()
        image_ax.figure.text((left.x0 + right.x1) / 2, left.y1 + .025,
                             f"{self.plate.label} / {self.device}", ha="center", fontsize=8)


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    @classmethod
    def decode(cls, values: Sequence[float]) -> Self:
        x, y = values
        return cls(float(x), float(y))


@dataclass(frozen=True)
class TracerFrame:
    day: int
    first_centre: Point
    second_centre: Point

    @classmethod
    def decode(cls, day: int, values: Sequence[Sequence[float]]) -> Self:
        first, second = values
        return cls(day, Point.decode(first), Point.decode(second))


@dataclass(frozen=True)
class TracerScale:
    spacing_um: float
    frames: tuple[TracerFrame, ...]

    @classmethod
    def decode(cls, wire: WireObject) -> Self:
        return cls(float(cast(float, wire["spacing_um"])), (
            TracerFrame.decode(0, cast(Sequence[Sequence[float]], wire["day0_centres_xy"])),
            TracerFrame.decode(3, cast(Sequence[Sequence[float]], wire["day3_centres_xy"])),
        ))

    def draw(self, ax: Axes, frame: TracerFrame) -> None:
        with Image.open(OUTPUT_DIR / f"dye_gradient_day{frame.day}.png") as source:
            image = source.convert("RGB")
            ax.imshow(image)
        ax.set_axis_off()
        ax.set_ylim(image.height + TRACER_SCALE_MARGIN_PX, -.5)
        ax.set_title(f"Hour {frame.day * 24}", fontsize=10, loc="left", pad=3)
        span = np.linalg.norm(np.asarray((frame.second_centre.x-frame.first_centre.x,
                                         frame.second_centre.y-frame.first_centre.y)))
        # Montage gutters are not physical distances; use one device's well pair.
        bar = 5000 * span / self.spacing_um
        ax.plot([100, 100 + bar], [image.height + 190, image.height + 190], color="black", linewidth=2)
        ax.text(600, image.height + 190, "~5 mm", color="black", fontsize=8, va="center")


@dataclass(frozen=True)
class WidthCrop:
    plate: PlateId
    y0: int
    y1: int
    x0: int
    x1: int

    @classmethod
    def decode(cls, plate: str, wire: WireObject) -> Self:
        ys, xs = cast(Sequence[Sequence[int]], wire["slices_yx"])
        y0, y1 = ys
        x0, x1 = xs
        return cls(PlateId(plate), int(y0), int(y1), int(x0), int(x1))

    def draw(self, ax: Axes, measurements: tuple[WidthMeasurement, ...]) -> None:
        pixels = np.load(DATA_DIR / f"{self.plate.upper()}_width_crop.npy", allow_pickle=False)
        ax.imshow(pixels, cmap="gray", extent=(self.x0-.5, self.x1-.5, self.y1-.5, self.y0-.5),
                  interpolation="nearest")
        selected = tuple(row for row in measurements if row.plate == self.plate)
        for row in selected:
            row.draw(ax)
        first = selected[0]
        x = first.x0_px
        ax.set_xlim(x-25, x+100)
        ax.set_ylim(290, 155)
        ax.set_title(f"{self.plate.upper()} / {first.device}", fontsize=10)
        ax.set_axis_off()
        bar = 20 / first.pixel_size_um
        ax.plot([x-17, x-17+bar], [282, 282], color="white", linewidth=2)
        ax.text(x-17, 276, "20 µm", color="white", fontsize=8)


@dataclass(frozen=True)
class ValidationSources:
    views: tuple[CtbView, ...]
    tracer: TracerScale
    width_crops: tuple[WidthCrop, ...]

    @classmethod
    def read(cls, path: Path) -> Self:
        wire = cast(WireObject, json.loads(path.read_text()))
        views = cast(Mapping[str, WireObject], wire["representatives"])
        crops = cast(Mapping[str, WireObject], wire["width_crops"])
        return cls(tuple(CtbView.decode(plate, view) for plate, view in views.items()),
                   TracerScale.decode(cast(WireObject, wire["tracer_scale"])),
                   tuple(WidthCrop.decode(plate, crop) for plate, crop in crops.items()))

    def render_widths(self, measurements: tuple[WidthMeasurement, ...]) -> None:
        fig, axes = plt.subplots(1, len(self.width_crops), figsize=(7, 2.65))
        for ax, crop in zip(axes, self.width_crops, strict=True):
            crop.draw(ax, measurements)
        fig.subplots_adjust(left=.01, right=.99, top=.88, bottom=.02, wspace=.08)
        fig.savefig(OUTPUT_DIR / "channel_widths.png", dpi=300)
        fig.savefig(OUTPUT_DIR / "channel_widths.pdf", dpi=300)
        plt.close(fig)


def label_panel(fig: plt.Figure, ax: Axes, label: str, *, above: bool = False) -> None:
    """Place a panel label beside its axes without colliding with tick labels."""
    bounds = ax.get_position()
    if above:
        x = bounds.x0
        y = bounds.y1 + PANEL_LABEL_GAP_INCHES / fig.get_figheight()
        horizontal_alignment, vertical_alignment = "left", "bottom"
    else:
        x = bounds.x0 - PANEL_LABEL_GAP_INCHES / fig.get_figwidth()
        y = bounds.y1
        horizontal_alignment, vertical_alignment = "right", "top"
    fig.text(
        x,
        y,
        label,
        weight="bold",
        fontsize=13,
        ha=horizontal_alignment,
        va=vertical_alignment,
    )


def figure_row_heights(tracer: TracerScale) -> tuple[float, float, float]:
    """Size tracer rows from their pixels so their image fills the text width."""
    with Image.open(OUTPUT_DIR / f"dye_gradient_day{tracer.frames[0].day}.png") as image:
        tracer_aspect = image.width / (image.height + TRACER_SCALE_MARGIN_PX)
    panel_width_inches = FIGURE_SIZE[0] * (FIGURE_RIGHT - FIGURE_LEFT)
    tracer_height_inches = panel_width_inches / tracer_aspect
    available_height_inches = FIGURE_SIZE[1] * (FIGURE_TOP - FIGURE_BOTTOM)
    axes_height_inches = available_height_inches / (1 + 2 * FIGURE_ROW_GAP / 3)
    lower_height_inches = axes_height_inches - 2 * tracer_height_inches
    if lower_height_inches <= 0:
        raise ValueError("Figure height cannot hold width-filling tracer panels")
    return tracer_height_inches, tracer_height_inches, lower_height_inches


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    counts = CountDataset.read(DATA_DIR / "ctb_device_counts.csv")
    metadata = ValidationSources.read(DATA_DIR / "sources.json")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "pdf.fonttype": 42})
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor="white")
    grid = fig.add_gridspec(
        3,
        3,
        height_ratios=figure_row_heights(metadata.tracer),
        width_ratios=(IMAGE_PANEL_FRACTION, IMAGE_PANEL_FRACTION, COUNT_PANEL_FRACTION),
        left=FIGURE_LEFT,
        right=FIGURE_RIGHT,
        top=FIGURE_TOP,
        bottom=FIGURE_BOTTOM,
        hspace=FIGURE_ROW_GAP,
        wspace=.14,
    )
    for i, frame in enumerate(metadata.tracer.frames):
        ax = fig.add_subplot(grid[i, :])
        metadata.tracer.draw(ax, frame)
        if i == 0:
            label_panel(fig, ax, "A")

    # One large image pair shows the saved segmentation clearly; the count panel
    # beside it carries all three plates and every retained device observation.
    view = min(metadata.views, key=lambda candidate: candidate.plate)
    pair = grid[2, :2].subgridspec(1, 2, wspace=.02)
    image_ax = fig.add_subplot(pair[0, 0])
    outline_ax = fig.add_subplot(pair[0, 1])
    view.draw(image_ax, outline_ax)
    label_panel(fig, image_ax, "B")

    ax = fig.add_subplot(grid[2, 2])
    counts.draw(ax)
    ax.set_ylabel("CTB-positive cells", fontsize=9)
    ax.tick_params(axis="x", labelsize=8.5)
    ax.set_xlim(-.5, 2.5)
    ax.set_ylim(bottom=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#E6E6E6", linewidth=.6)
    label_panel(fig, ax, "C", above=True)
    fig.savefig(OUTPUT_DIR / "draft_figure.pdf", dpi=300)
    fig.savefig(OUTPUT_DIR / "draft_figure.png", dpi=300)
    plt.close(fig)
    print(json.dumps([asdict(plate.summary) for plate in counts.plates], indent=2))


if __name__ == "__main__":
    main()
