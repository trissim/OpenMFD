"""Well patterns and configurations for microfluidic devices.

This module provides functions for creating wells in various patterns
(single, pairs, corners, grids) with configurable dimensions and positions.
"""

from dataclasses import dataclass
from typing import List, Literal, Optional
import solid
from solid.utils import union

from .types import Position2D, Dimensions
from .primitives import WellGeometryRequest
from .positioning import wells_pos_from_center_2, wells_pos_from_center_4


WellShape = Literal["circle", "square"]


@dataclass
class WellConfiguration:
    """Configuration for well geometry.

    Attributes
    ----------
    radius : float, optional
        Well radius (for circular wells).
    dimensions : tuple, optional
        Well dimensions (for square/rectangular wells).
    height : float, optional
        Well height (for 3D geometry). If None, creates 2D.
    shape : {'circle', 'square'}, default='circle'
        Well shape type.
    positions : list of (float, float), optional
        Custom well positions. If None, uses default positioning.
    segments : int, default=64
        Number of segments for circular wells.
    """

    radius: Optional[float] = None
    dimensions: Optional[Dimensions] = None
    height: Optional[float] = None
    shape: WellShape = "circle"
    positions: Optional[List[Position2D]] = None
    segments: int = 64

    def __post_init__(self):
        """Validate configuration."""
        if self.radius is None and self.dimensions is None:
            raise ValueError("Either radius or dimensions must be specified")
        if self.radius is not None and self.dimensions is not None:
            raise ValueError("Cannot specify both radius and dimensions")
        if self.radius is not None and self.radius <= 0:
            raise ValueError(f"radius must be positive, got {self.radius}")

    def get_dims(self) -> Dimensions:
        """Get dimensions for well creation."""
        if self.radius is not None:
            return self.radius
        assert self.dimensions is not None
        return self.dimensions


@dataclass(frozen=True)
class WellPatternContext:
    """Nominal context record for repeated well-pattern parameters."""

    dims: Dimensions
    positions: List[Position2D]
    height: Optional[float] = None
    dxf: bool = False
    segments: int = 64

    @classmethod
    def from_fields(
        cls,
        dims: Dimensions,
        positions: List[Position2D],
        height: Optional[float] = None,
        dxf: bool = False,
        segments: int = 64,
    ) -> "WellPatternContext":
        return cls(
            dims=dims,
            positions=positions,
            height=height,
            dxf=dxf,
            segments=segments,
        )

    def geometry_request(self) -> WellGeometryRequest:
        return WellGeometryRequest.from_fields(
            dims=self.dims,
            height=self.height,
            dxf=self.dxf,
            segments=self.segments,
        )

    def with_positions(self, positions: List[Position2D]) -> "WellPatternContext":
        return WellPatternContext(
            dims=self.dims,
            positions=positions,
            height=self.height,
            dxf=self.dxf,
            segments=self.segments,
        )

    @property
    def is_2d(self) -> bool:
        return self.dxf or self.height is None

    @property
    def z_offset(self) -> float:
        if self.is_2d:
            return 0
        assert self.height is not None
        return self.height / 2.0


def _translate_well(
    well_shape: solid.OpenSCADObject,
    position: Position2D,
    context: WellPatternContext,
) -> solid.OpenSCADObject:
    if context.is_2d:
        return solid.translate([position[0], position[1]])(well_shape)
    return solid.translate([position[0], position[1], context.z_offset])(well_shape)


def _compose_well_pattern(context: WellPatternContext) -> solid.OpenSCADObject:
    well_shape = context.geometry_request().build()
    wells = [_translate_well(well_shape, position, context) for position in context.positions]
    return union()(*wells)


def wells_top_bottom(context: WellPatternContext) -> solid.OpenSCADObject:
    """Create 2 wells in vertical (top-bottom) configuration.

    Parameters
    ----------
    context : WellPatternContext
        Shared well-pattern context for the two-well layout.

    Returns
    -------
    solid.OpenSCADObject
        Union of 2 wells positioned vertically.

    Examples
    --------
    >>> wells = wells_top_bottom(
    ...     WellPatternContext.from_fields(3.0, positions=[[5, 0], [-5, 0]], height=0.3)
    ... )
    """
    return _compose_well_pattern(context)


def four_corner(context: WellPatternContext) -> solid.OpenSCADObject:
    """Create 4 wells in corner configuration.

    Parameters
    ----------
    context : WellPatternContext
        Shared well-pattern context for the four-corner layout.

    Returns
    -------
    solid.OpenSCADObject
        Union of 4 wells positioned at corners.

    Examples
    --------
    >>> wells = four_corner(
    ...     WellPatternContext.from_fields(3.0, positions=[[5, 5], [-5, 5], [-5, -5], [5, -5]])
    ... )
    """
    return _compose_well_pattern(context)


def well_array(
    context: WellPatternContext,
    rows: int,
    cols: int,
    spacing_x: float,
    spacing_y: Optional[float] = None,
) -> solid.OpenSCADObject:
    """Create an array of wells in a grid pattern.

    Parameters
    ----------
    context : WellPatternContext
        Shared well-pattern context for the array geometry.
    rows : int
        Number of rows.
    cols : int
        Number of columns.
    spacing_x : float
        Spacing between columns.
    spacing_y : float, optional
        Spacing between rows. If None, uses spacing_x.
    Returns
    -------
    solid.OpenSCADObject
        Union of wells arranged in grid.

    Examples
    --------
    >>> wells = well_array(
    ...     WellPatternContext.from_fields(1.5, positions=[]),
    ...     8,
    ...     12,
    ...     9.0,
    ... )
    """
    from .positioning import grid_positions

    if spacing_y is None:
        spacing_y = spacing_x

    # Generate grid positions
    positions = grid_positions(rows, cols, spacing_x, spacing_y, center=True)

    return _compose_well_pattern(context.with_positions(positions))
