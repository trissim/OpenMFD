"""Shared plate-coordinate mosaic renderer for axotomy figures."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


INK = "#17212B"
MUTED = "#5D6975"
GRID = "#D7DEE6"
EXCLUDED = "#D62828"


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def _thumbnail(
    path: Path,
    size: tuple[int, int],
    transform: Callable[[Image.Image], Image.Image] | None = None,
) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGB")
        if transform is not None:
            image = transform(image)
        image.thumbnail(size, Image.Resampling.LANCZOS, reducing_gap=3.0)
    canvas = Image.new("RGB", size, "white")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def save_plate_mosaic(
    records: Sequence[Any],
    path: Path,
    *,
    plates: tuple[str, ...],
    image_path_for_record: Callable[[Any], Path],
    is_excluded: Callable[[Any], bool],
    plate_colors: Mapping[str, str],
    legend_plates: tuple[str, ...],
    title: str,
    font_regular: Path,
    font_bold: Path,
    legend_panel_range: str = "C-F",
    dpi: int = 300,
    excluded_label: str = "red outline: excluded device",
    subtitle: str = "Rows R02-R07; device columns C02-C05",
    label_font_px: int | None = None,
    thumbnail_transform: Callable[[Image.Image], Image.Image] | None = None,
) -> None:
    """Render one or more 6 x 4 plate mosaics with shared geometry."""
    if not plates:
        raise ValueError("At least one plate is required")

    tile_width, tile_height = 250, 204
    plate_width = 4 * tile_width
    plate_height = 6 * tile_height
    left_label = 45 if label_font_px is None else 3 * label_font_px
    plate_gap = 65 if label_font_px is None else 3 * label_font_px
    top = 145 if label_font_px is None else 5 * label_font_px
    bottom = 95 if label_font_px is None else 3 * label_font_px
    content_width = len(plates) * plate_width + (len(plates) - 1) * plate_gap
    canvas_width = max(1890, 2 * left_label + content_width)
    plate_start = (canvas_width - content_width) // 2
    canvas_height = top + plate_height + bottom
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)

    draw.text(
        (canvas_width / 2, 5),
        title,
        font=_font(font_bold, label_font_px or 34),
        fill=INK,
        anchor="ma",
    )
    draw.text(
        (canvas_width / 2, 51 if label_font_px is None else label_font_px + 17),
        subtitle,
        font=_font(font_regular, label_font_px or 22),
        fill=MUTED,
        anchor="ma",
    )

    for plate_index, plate in enumerate(plates):
        x0 = plate_start + plate_index * (plate_width + plate_gap)
        draw.rounded_rectangle(
            (x0 - 12, top - 4, x0 + plate_width + 12, top + plate_height + 12),
            radius=10,
            fill="#F4F7FA",
            outline="#AAB5BF",
            width=3,
        )
        draw.text(
            (x0 + plate_width / 2, top - (55 if label_font_px is None else 2.5 * label_font_px)),
            f"Plate {plate[1:]}",
            font=_font(font_bold, label_font_px or 27),
            fill=INK,
            anchor="ma",
        )
        for column in range(2, 6):
            draw.text(
                (x0 + (column - 1.5) * tile_width, top - 18),
                f"C{column:02d}",
                font=_font(font_regular, label_font_px or 15),
                fill=MUTED,
                anchor="ms",
            )
        for row in range(2, 8):
            draw.text(
                (x0 - 16, top + (row - 1.5) * tile_height),
                f"R{row:02d}",
                font=_font(font_regular, label_font_px or 15),
                fill=MUTED,
                anchor="rm",
            )
        plate_records = sorted(
            (record for record in records if record.plate == plate),
            key=lambda record: (record.row, record.column),
        )
        if len(plate_records) != 24:
            raise ValueError(f"Expected 24 records for {plate}; found {len(plate_records)}")
        for record in plate_records:
            x = x0 + (record.column - 2) * tile_width
            y = top + (record.row - 2) * tile_height
            tile = _thumbnail(
                image_path_for_record(record),
                (tile_width, tile_height),
                thumbnail_transform,
            )
            canvas.paste(tile, (x, y))
            excluded = is_excluded(record)
            draw.rectangle(
                (x, y, x + tile_width - 1, y + tile_height - 1),
                outline=EXCLUDED if excluded else "#111111",
                width=6 if excluded else 1,
            )

    legend_y = canvas_height - 46
    regular = _font(font_regular, label_font_px or 18)
    prefix = f"Point colors in {legend_panel_range}:" if legend_plates else ""
    prefix_width = draw.textbbox((0, 0), prefix, font=regular)[2]
    items = [(plate_colors[plate], f"Plate {plate[1:]}") for plate in legend_plates]
    items.append((EXCLUDED, excluded_label))
    item_widths = [24 + 10 + draw.textbbox((0, 0), label, font=regular)[2] for _, label in items]
    prefix_gap = 42 if prefix else 0
    total_width = prefix_width + prefix_gap + sum(item_widths) + 35 * (len(items) - 1)
    x = (canvas_width - total_width) / 2
    if prefix:
        draw.text((x, legend_y + 4), prefix, font=regular, fill=INK, anchor="lm")
        x += prefix_width + prefix_gap
    for (color, label), item_width in zip(items, item_widths, strict=True):
        draw.rounded_rectangle((x, legend_y - 8, x + 24, legend_y + 16), radius=4, fill=color)
        draw.text((x + 34, legend_y + 4), label, font=regular, fill=INK, anchor="lm")
        x += item_width + 35

    canvas.save(path, dpi=(dpi, dpi), compress_level=5)
