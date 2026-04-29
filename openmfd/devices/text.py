"""Text annotation for device labeling and documentation.

This module provides functions for adding text annotations to devices,
including cure temperatures, device names, and other metadata.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import solid
from solid.utils import union

from .wafer import compute_wafer_center


class DeviceLabelPosition(str, Enum):
    """Closed set of supported device-label positions."""

    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"

    @classmethod
    def from_value(cls, value: object) -> "DeviceLabelPosition":
        if isinstance(value, cls):
            return value
        positions = {position.value: position for position in cls}
        if value in positions:
            return positions[value]
        raise ValueError(
            f"Unsupported position {value!r}. Expected one of: "
            f"{', '.join(position.value for position in cls)}"
        )


@dataclass(frozen=True)
class TextLayoutContext:
    """Nominal context for repeated text-placement parameters."""

    grid_size: List[int]
    dims: List[float]
    size: float = 2.0
    offset_y: float = 0.0
    alignment_offset: Optional[Tuple[float, float]] = None

    @classmethod
    def from_fields(
        cls,
        grid_size: List[int],
        dims: List[float],
        size: float = 2.0,
        offset_y: float = 0.0,
        alignment_offset: Optional[Tuple[float, float]] = None,
    ) -> "TextLayoutContext":
        return cls(
            grid_size=grid_size,
            dims=dims,
            size=size,
            offset_y=offset_y,
            alignment_offset=alignment_offset,
        )

    def with_offset(self, offset_y: float) -> "TextLayoutContext":
        return TextLayoutContext(
            grid_size=self.grid_size,
            dims=self.dims,
            size=self.size,
            offset_y=offset_y,
            alignment_offset=self.alignment_offset,
        )


def _position_text(
    text_obj: solid.OpenSCADObject,
    context: TextLayoutContext,
) -> solid.OpenSCADObject:
    cx, cy = compute_wafer_center(context.grid_size, context.dims)
    if context.alignment_offset is not None:
        text_obj = solid.translate([context.alignment_offset[0], context.alignment_offset[1]])(
            text_obj
        )
    text_obj = solid.translate([cx, cy])(text_obj)
    return solid.translate([0, context.offset_y])(text_obj)


def create_centered_text(
    text: str,
    context: TextLayoutContext,
    halign: str = "center",
    valign: str = "center",
) -> solid.OpenSCADObject:
    """Create text centered on wafer.

    Creates text annotation positioned at the wafer center with optional
    vertical offset. Uses the centralized wafer centering system.

    Parameters
    ----------
    text : str
        Text to render.
    context : TextLayoutContext
        Shared placement context containing grid size, unit dimensions,
        text size, vertical offset, and optional alignment offset.
    halign : str, default="center"
        Horizontal alignment ("left", "center", "right").
    valign : str, default="center"
        Vertical alignment ("top", "center", "bottom", "baseline").

    Returns
    -------
    solid.OpenSCADObject
        Centered text geometry.

    Examples
    --------
    >>> # Create cure temperature text
    >>> text = create_centered_text(
    ...     "Cure at 100°C",
    ...     TextLayoutContext.from_fields([6, 8], [9.0, 9.0, 0], size=2.0, offset_y=-40)
    ... )
    """
    text_obj = solid.text(text, halign=halign, valign=valign, size=context.size)
    return _position_text(text_obj, context)


def create_multiline_text(
    lines: List[str],
    context: TextLayoutContext,
    line_spacing: Optional[float] = None,
) -> solid.OpenSCADObject:
    """Create multiple lines of centered text.

    Creates multiple lines of text, each centered and vertically spaced.

    Parameters
    ----------
    lines : list of str
        Lines of text to render.
    context : TextLayoutContext
        Shared placement context containing grid size, unit dimensions,
        text size, vertical offset, and optional alignment offset.
    line_spacing : float, optional
        Spacing between lines. If None, uses context.dims[1] / 2.

    Returns
    -------
    solid.OpenSCADObject
        Multiline text geometry.

    Examples
    --------
    >>> # Create multi-line instructions
    >>> text = create_multiline_text(
    ...     ["Cure at 100°C", "Use 60mL Sylgard 184 in 1:10 ratio"],
    ...     TextLayoutContext.from_fields([6, 8], [9.0, 9.0, 0], size=2.0, offset_y=-40)
    ... )
    """
    if line_spacing is None:
        line_spacing = context.dims[1] / 2

    text_objects = []

    for i, line in enumerate(lines):
        # Calculate vertical offset for this line
        line_offset = context.offset_y - i * line_spacing

        text_context = context.with_offset(line_offset)
        text_obj = _position_text(
            solid.text(line, halign="center", valign="center", size=context.size),
            text_context,
        )
        text_objects.append(text_obj)

    return union()(*text_objects)


def create_cure_temperature_text(
    cure_temp: int,
    context: TextLayoutContext,
    include_instructions: bool = True,
) -> solid.OpenSCADObject:
    """Create cure temperature annotation text.

    Creates standardized text for PDMS curing temperature with optional
    mixing instructions.

    Parameters
    ----------
    cure_temp : int
        Cure temperature in Celsius.
    context : TextLayoutContext
        Shared placement context for the text block.
    include_instructions : bool, default=True
        Whether to include mixing instructions.

    Returns
    -------
    solid.OpenSCADObject
        Cure temperature text.

    Examples
    --------
    >>> # Create cure text for 100°C
    >>> text = create_cure_temperature_text(
    ...     cure_temp=100,
    ...     context=TextLayoutContext.from_fields([6, 8], [9.0, 9.0, 0])
    ... )
    """
    # Create cure temperature text
    cure_text = f"Cure at {cure_temp}°C"

    # Calculate offset to position below array
    offset_y = -(context.grid_size[1] + 3) * context.dims[1] / 2
    positioned_context = context.with_offset(offset_y)

    if include_instructions:
        lines = [cure_text, "Use 60mL of Sylgard 184 in 1:10 ratio"]
        return create_multiline_text(
            lines,
            positioned_context,
            line_spacing=context.dims[1] / 2,
        )

    return create_centered_text(cure_text, positioned_context)


def create_device_label(
    device_name: str,
    version: str,
    context: TextLayoutContext,
    position: str = "top",
) -> solid.OpenSCADObject:
    """Create device name and version label.

    Creates a label with device name and version number.

    Parameters
    ----------
    device_name : str
        Device name.
    version : str
        Version string (e.g., "v27").
    context : TextLayoutContext
        Shared placement context for the label.
    position : str, default="top"
        Position of label ("top", "bottom", "left", "right").

    Returns
    -------
    solid.OpenSCADObject
        Device label text.

    Examples
    --------
    >>> label = create_device_label(
    ...     "2_compartment_96_well",
    ...     "v27",
    ...     TextLayoutContext.from_fields([6, 8], [9.0, 9.0, 0], size=1.5)
    ... )
    """
    label_text = f"{device_name} {version}"

    position_kind = DeviceLabelPosition.from_value(position)
    offset_by_position = {
        DeviceLabelPosition.TOP: (context.grid_size[1] + 2) * context.dims[1] / 2,
        DeviceLabelPosition.BOTTOM: -(context.grid_size[1] + 2) * context.dims[1] / 2,
        DeviceLabelPosition.LEFT: 0,
        DeviceLabelPosition.RIGHT: 0,
    }
    offset_y = offset_by_position[position_kind]

    return create_centered_text(label_text, context.with_offset(offset_y))


def create_date_stamp(
    date_str: str,
    context: TextLayoutContext,
) -> solid.OpenSCADObject:
    """Create date stamp annotation.

    Creates a date stamp for tracking fabrication date.

    Parameters
    ----------
    date_str : str
        Date string (e.g., "2024-10-21").
    context : TextLayoutContext
        Shared placement context for the stamp.

    Returns
    -------
    solid.OpenSCADObject
        Date stamp text.

    Examples
    --------
    >>> stamp = create_date_stamp(
    ...     "2024-10-21",
    ...     TextLayoutContext.from_fields([6, 8], [9.0, 9.0, 0], size=1.0)
    ... )
    """
    # Position at bottom corner
    offset_y = -(context.grid_size[1] + 1) * context.dims[1] / 2

    return create_centered_text(date_str, context.with_offset(offset_y))
