"""Alignment mark generation for layer registration.

This module provides functions for creating alignment marks used in
multi-layer photolithography for precise layer-to-layer alignment.
"""

from enum import Enum
from typing import Callable, List, Optional, Tuple

import solid
from solid.utils import difference, union


class AlignmentMarkMode(str, Enum):
    """Closed set of array alignment-mark behaviors."""

    FULL = "full"
    HOLLOW = "hollow"
    PARTIAL = "partial"
    NONE = "none"

    @classmethod
    def from_value(cls, value: object) -> "AlignmentMarkMode":
        if value is None:
            return cls.NONE
        if isinstance(value, cls):
            return value
        modes = {mode.value: mode for mode in cls}
        if value in modes:
            return modes[value]
        raise ValueError(
            f"Unsupported alignment_mode {value!r}. Expected one of: "
            f"{', '.join(mode.value for mode in cls)}"
        )


class AlignmentPatternType(str, Enum):
    """Closed set of standalone alignment-pattern families."""

    CROSSHAIR = "crosshair"
    TARGET = "target"
    CORNER = "corner"
    VERNIER = "vernier"

    @classmethod
    def from_value(cls, value: object) -> "AlignmentPatternType":
        if isinstance(value, cls):
            return value
        patterns = {pattern.value: pattern for pattern in cls}
        if value in patterns:
            return patterns[value]
        raise ValueError(
            f"Unsupported pattern_type {value!r}. Expected one of: "
            f"{', '.join(pattern.value for pattern in cls)}"
        )


def create_single_L_mark(
    corner_length: float, thickness_divisor: float = 3.0
) -> solid.OpenSCADObject:
    """Create single L-shaped alignment mark.

    Creates an L-shaped mark used for alignment. The mark consists
    of two perpendicular rectangles forming an L-shape.

    Parameters
    ----------
    corner_length : float
        Length of L-mark arms.
    thickness_divisor : float, default=3.0
        Divisor for mark thickness (corner_length / thickness_divisor).

    Returns
    -------
    solid.OpenSCADObject
        L-shaped mark.

    Examples
    --------
    >>> mark = create_single_L_mark(corner_length=2.0, thickness_divisor=3.0)
    """
    thickness = corner_length / thickness_divisor

    # Create horizontal arm
    horizontal = solid.square([corner_length, thickness], center=False)

    # Create vertical arm
    vertical = solid.square([thickness, corner_length], center=False)

    # Combine to form L-shape
    return union()(horizontal, vertical)


def create_full_alignment_mark(
    corner_length: float, thickness_divisor: float = 8.0
) -> solid.OpenSCADObject:
    """Create full alignment mark (two L-shapes forming a crosshair).

    Creates a crosshair-like mark by combining two L-shapes rotated 180° apart.
    This matches the legacy behavior where two L-shapes overlap at their corners
    to form a + shape for precise alignment.

    Parameters
    ----------
    corner_length : float
        Length of corner mark arms.
    thickness_divisor : float, default=8.0
        Divisor for mark thickness (corner_length / thickness_divisor).

    Returns
    -------
    solid.OpenSCADObject
        Full alignment mark (crosshair from two L-shapes).

    Examples
    --------
    >>> mark = create_full_alignment_mark(corner_length=2.0, thickness_divisor=8.0)
    """
    thickness = corner_length / thickness_divisor

    # Create base L-shape
    corner = create_single_L_mark(corner_length, thickness_divisor)

    # Top-right L (rotated 180°)
    tr = solid.rotate(180)(corner)
    tr = solid.translate([thickness / 2, thickness / 2, 0])(tr)

    # Bottom-left L (rotated 0°)
    bl = solid.rotate(0)(corner)
    bl = solid.translate([-thickness / 2, -thickness / 2, 0])(bl)

    # Combine to form crosshair
    return union()(tr, bl)


def create_alignment_marks(
    array: solid.OpenSCADObject,
    dims: List[float],
    grid_size: List[int],
    alignment_mode: Optional[str] = "full",
    units_from_center: Optional[Tuple[float, float]] = None,
    corner_length: Optional[float] = None,
) -> solid.OpenSCADObject:
    """Add alignment marks to device array.

    Adds alignment marks (crosshairs formed by two L-shapes) at specified positions.
    These marks are used for layer-to-layer alignment in multi-layer photolithography.

    Alignment modes:
    - "full": Solid crosshair marks (two L-shapes forming +) for bottom layer
    - "hollow": Hollow crosshair marks (for top layer alignment to bottom)
    - "partial": Marks only at specified corners
    - None: No alignment marks

    Parameters
    ----------
    array : solid.OpenSCADObject
        Device array to add marks to.
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
    alignment_mode : str, default="full"
        Alignment mode ("full", "hollow", "partial").
    units_from_center : tuple of (float, float), optional
        Distance from center for alignment marks (in units).
        If None, marks are placed at array corners.
    corner_length : float, optional
        Length of corner marks. If None, computed from dims.

    Returns
    -------
    solid.OpenSCADObject
        Array with alignment marks added.

    Examples
    --------
    >>> # Add full alignment marks (solid crosshairs)
    >>> array_with_marks = create_alignment_marks(
    ...     array, dims=[9.0, 9.0, 0], grid_size=[6, 8],
    ...     alignment_mode="full", units_from_center=(3, 4)
    ... )

    >>> # Add hollow alignment marks (for top layer)
    >>> array_with_marks = create_alignment_marks(
    ...     array, dims=[9.0, 9.0, 0], grid_size=[6, 8],
    ...     alignment_mode="hollow", units_from_center=(3, 4)
    ... )
    """
    mark_mode = AlignmentMarkMode.from_value(alignment_mode)
    if mark_mode is AlignmentMarkMode.NONE:
        return array

    # Compute corner length if not provided
    if corner_length is None:
        corner_length = (dims[0] + dims[1]) / 2 / 8

    # Compute array dimensions
    width = grid_size[0] * dims[0]
    length = grid_size[1] * dims[1]

    # Determine mark positions
    center_x, center_y = width / 2, length / 2

    if units_from_center is not None:
        # Position marks at specified distance from center
        # Legacy behavior: marks at 4 cardinal positions (right, top, left, bottom)
        x_offset = units_from_center[0] * dims[0]
        y_offset = units_from_center[1] * dims[1]

        # Four positions: right, top, left, bottom (NOT corners!)
        positions = [
            (center_x + x_offset, center_y),  # Right
            (center_x, center_y + y_offset),  # Top
            (center_x - x_offset, center_y),  # Left
            (center_x, center_y - y_offset),  # Bottom
        ]
    else:
        # Position marks at array corners
        positions = [
            (0, 0),  # Bottom-left
            (width, 0),  # Bottom-right
            (0, length),  # Top-left
            (width, length),  # Top-right
        ]

    # Create marks at all four positions
    # IMPORTANT: Legacy behavior - ALWAYS use union() to add marks to array!
    # The "hollow" effect comes from the mark SHAPE (ring), not from subtraction.
    # When the wafer mask subtracts the array, hollow marks create registration holes.
    marks = []
    for x, y in positions:
        if mark_mode is AlignmentMarkMode.HOLLOW:
            inner = create_full_alignment_mark(corner_length, thickness_divisor=8.0)
            outer = create_full_alignment_mark(corner_length, thickness_divisor=4.0)
            mark = difference()(outer, inner)
        else:
            mark = create_full_alignment_mark(corner_length, thickness_divisor=8.0)

        mark = solid.translate([x, y])(mark)
        marks.append(mark)

    # Combine all marks
    all_marks = union()(*marks)

    # ALWAYS use union() to add marks to array (legacy behavior)
    # The wafer mask's difference() operation will handle the subtraction
    return union()(array, all_marks)


def create_crosshair_mark(size: float, thickness: float) -> solid.OpenSCADObject:
    """Create crosshair alignment mark.

    Creates a crosshair (+) mark for fine alignment.

    Parameters
    ----------
    size : float
        Size of crosshair (length of arms).
    thickness : float
        Thickness of crosshair lines.

    Returns
    -------
    solid.OpenSCADObject
        Crosshair mark.

    Examples
    --------
    >>> crosshair = create_crosshair_mark(size=5.0, thickness=0.1)
    """
    # Create horizontal line
    horizontal = solid.square([size, thickness], center=True)

    # Create vertical line
    vertical = solid.square([thickness, size], center=True)

    # Combine to form crosshair
    return union()(horizontal, vertical)


def create_vernier_scale(
    length: float, num_marks: int, mark_thickness: float, mark_height: float
) -> solid.OpenSCADObject:
    """Create vernier scale for precise alignment measurement.

    Creates a vernier scale with multiple marks for measuring alignment
    precision.

    Parameters
    ----------
    length : float
        Total length of vernier scale.
    num_marks : int
        Number of marks on scale.
    mark_thickness : float
        Thickness of each mark.
    mark_height : float
        Height of each mark.

    Returns
    -------
    solid.OpenSCADObject
        Vernier scale.

    Examples
    --------
    >>> scale = create_vernier_scale(
    ...     length=10.0, num_marks=10, mark_thickness=0.05, mark_height=1.0
    ... )
    """
    marks = []
    spacing = length / (num_marks - 1)

    for i in range(num_marks):
        mark = solid.square([mark_thickness, mark_height], center=False)
        mark = solid.translate([i * spacing, 0])(mark)
        marks.append(mark)

    return union()(*marks)


def create_alignment_target(
    outer_diameter: float, inner_diameter: float, num_rings: int = 3
) -> solid.OpenSCADObject:
    """Create concentric ring alignment target.

    Creates a target pattern with concentric rings for coarse alignment.

    Parameters
    ----------
    outer_diameter : float
        Outer diameter of target.
    inner_diameter : float
        Inner diameter of target.
    num_rings : int, default=3
        Number of concentric rings.

    Returns
    -------
    solid.OpenSCADObject
        Alignment target.

    Examples
    --------
    >>> target = create_alignment_target(
    ...     outer_diameter=10.0, inner_diameter=2.0, num_rings=3
    ... )
    """
    rings = []

    # Calculate ring spacing
    radius_step = (outer_diameter - inner_diameter) / (2 * num_rings)

    for i in range(num_rings):
        outer_r = outer_diameter / 2 - i * 2 * radius_step
        inner_r = outer_r - radius_step

        outer_circle = solid.circle(r=outer_r)
        inner_circle = solid.circle(r=inner_r)

        ring = difference()(outer_circle, inner_circle)
        rings.append(ring)

    return union()(*rings)


def create_custom_alignment_pattern(pattern_type: str, size: float) -> solid.OpenSCADObject:
    """Create custom alignment pattern.

    Creates various alignment patterns for different purposes.

    Parameters
    ----------
    pattern_type : str
        Type of pattern: "crosshair", "target", "corner", "vernier".
    size : float
        Size of pattern.

    Returns
    -------
    solid.OpenSCADObject
        Alignment pattern.

    Examples
    --------
    >>> pattern = create_custom_alignment_pattern("crosshair", size=5.0)
    """
    pattern_kind = AlignmentPatternType.from_value(pattern_type)
    builders: dict[AlignmentPatternType, Callable[[float], solid.OpenSCADObject]] = {
        AlignmentPatternType.CROSSHAIR: lambda pattern_size: create_crosshair_mark(
            pattern_size, thickness=pattern_size / 20
        ),
        AlignmentPatternType.TARGET: lambda pattern_size: create_alignment_target(
            pattern_size, pattern_size / 5, num_rings=3
        ),
        AlignmentPatternType.CORNER: lambda pattern_size: create_single_L_mark(
            pattern_size, thickness_divisor=3.0
        ),
        AlignmentPatternType.VERNIER: lambda pattern_size: create_vernier_scale(
            pattern_size,
            num_marks=10,
            mark_thickness=pattern_size / 100,
            mark_height=pattern_size / 5,
        ),
    }
    return builders[pattern_kind](size)
