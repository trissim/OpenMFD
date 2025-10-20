"""Well patterns and configurations for microfluidic devices.

This module provides functions for creating wells in various patterns
(single, pairs, corners, grids) with configurable dimensions and positions.
"""

from typing import Optional, List, Literal
from dataclasses import dataclass
import solid
from solid.utils import union

from .types import Position2D, Dimensions
from .primitives import make_well
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
        else:
            return self.dimensions


def wells_top_bottom(
    radius: float,
    height: Optional[float] = None,
    positions: Optional[List[Position2D]] = None,
    dxf: bool = False,
    shape: WellShape = "circle",
    segments: int = 64
) -> solid.OpenSCADObject:
    """Create 2 wells in vertical (top-bottom) configuration.
    
    Parameters
    ----------
    radius : float
        Well radius (or size for square wells).
    height : float, optional
        Well height. If None or dxf=True, creates 2D geometry.
    positions : list of (float, float), optional
        Custom positions for the 2 wells. If None, uses default spacing
        of radius + radius/2.0 from center.
    dxf : bool, default=False
        If True, create 2D geometry for DXF export.
    shape : {'circle', 'square'}, default='circle'
        Well shape type.
    segments : int, default=64
        Number of segments for circular wells.
        
    Returns
    -------
    solid.OpenSCADObject
        Union of 2 wells positioned vertically.
        
    Examples
    --------
    >>> # Create 2 circular wells with 3mm radius, 0.3mm height
    >>> wells = wells_top_bottom(3.0, height=0.3)
    
    >>> # Create 2 square wells for DXF
    >>> wells = wells_top_bottom(4.0, dxf=True, shape='square')
    
    >>> # Custom positions
    >>> wells = wells_top_bottom(3.0, positions=[[5, 0], [-5, 0]])
    """
    # Generate default positions if not provided
    if positions is None:
        offset = radius + radius / 2.0
        positions = wells_pos_from_center_2(offset)
    
    # Create well shape
    dims = radius if shape == "circle" else [radius, radius]
    well_shape = make_well(dims, height=height, dxf=dxf, segments=segments)
    
    # Position wells
    wells = []
    z_offset = 0 if (dxf or height is None) else height / 2.0
    
    for position in positions:
        if dxf or height is None:
            well = solid.translate([position[0], position[1]])(well_shape)
        else:
            well = solid.translate([position[0], position[1], z_offset])(well_shape)
        wells.append(well)
    
    return union()(*wells)


def four_corner(
    radius: float,
    height: Optional[float] = None,
    positions: Optional[List[Position2D]] = None,
    dxf: bool = False,
    square: bool = False,
    segments: int = 64
) -> solid.OpenSCADObject:
    """Create 4 wells in corner configuration.
    
    Parameters
    ----------
    radius : float
        Well radius (or size for square wells).
    height : float, optional
        Well height. If None or dxf=True, creates 2D geometry.
    positions : list of (float, float), optional
        Custom positions for the 4 wells. If None, uses default spacing
        of radius + radius/2.0 from center.
    dxf : bool, default=False
        If True, create 2D geometry for DXF export.
    square : bool, default=False
        If True, create square wells. If False, create circular wells.
    segments : int, default=64
        Number of segments for circular wells.
        
    Returns
    -------
    solid.OpenSCADObject
        Union of 4 wells positioned at corners.
        
    Examples
    --------
    >>> # Create 4 circular wells
    >>> wells = four_corner(3.0, height=0.3)
    
    >>> # Create 4 square wells
    >>> wells = four_corner(4.0, height=0.3, square=True)
    
    >>> # Custom positions
    >>> positions = [[5, 5], [-5, 5], [-5, -5], [5, -5]]
    >>> wells = four_corner(3.0, positions=positions)
    """
    # Generate default positions if not provided
    if positions is None:
        offset = radius + radius / 2.0
        positions = wells_pos_from_center_4(offset)
    
    # Create wells at each position
    wells = []
    z_offset = 0 if (dxf or height is None) else height / 2.0
    
    for position in positions:
        if square:
            # Square wells
            if dxf or height is None:
                well_shape = solid.square(size=radius, center=True)
                well = solid.translate([position[0], position[1]])(well_shape)
            else:
                well_shape = solid.cube(size=[radius, radius, height], center=True)
                well = solid.translate([position[0], position[1], z_offset])(well_shape)
        else:
            # Circular wells
            if dxf or height is None:
                well_shape = solid.circle(r=radius, segments=segments)
                well = solid.translate([position[0], position[1]])(well_shape)
            else:
                well_shape = solid.cylinder(r=radius, h=height, segments=segments, center=True)
                well = solid.translate([position[0], position[1], z_offset])(well_shape)
        
        wells.append(well)
    
    return union()(*wells)


def well_array(
    radius: float,
    rows: int,
    cols: int,
    spacing_x: float,
    spacing_y: Optional[float] = None,
    height: Optional[float] = None,
    dxf: bool = False,
    shape: WellShape = "circle",
    segments: int = 64
) -> solid.OpenSCADObject:
    """Create an array of wells in a grid pattern.
    
    Parameters
    ----------
    radius : float
        Well radius (or size for square wells).
    rows : int
        Number of rows.
    cols : int
        Number of columns.
    spacing_x : float
        Spacing between columns.
    spacing_y : float, optional
        Spacing between rows. If None, uses spacing_x.
    height : float, optional
        Well height. If None or dxf=True, creates 2D geometry.
    dxf : bool, default=False
        If True, create 2D geometry for DXF export.
    shape : {'circle', 'square'}, default='circle'
        Well shape type.
    segments : int, default=64
        Number of segments for circular wells.
        
    Returns
    -------
    solid.OpenSCADObject
        Union of wells arranged in grid.
        
    Examples
    --------
    >>> # Create 8x12 array (96 wells) with 9mm spacing
    >>> wells = well_array(1.5, 8, 12, 9.0, height=0.3)
    
    >>> # Create 4x6 array with different x/y spacing
    >>> wells = well_array(2.0, 4, 6, 9.0, 14.0, height=0.3)
    """
    from .positioning import grid_positions
    
    if spacing_y is None:
        spacing_y = spacing_x
    
    # Generate grid positions
    positions = grid_positions(rows, cols, spacing_x, spacing_y, center=True)
    
    # Create well shape
    dims = radius if shape == "circle" else [radius, radius]
    well_shape = make_well(dims, height=height, dxf=dxf, segments=segments)
    
    # Position wells
    wells = []
    z_offset = 0 if (dxf or height is None) else height / 2.0
    
    for position in positions:
        if dxf or height is None:
            well = solid.translate([position[0], position[1]])(well_shape)
        else:
            well = solid.translate([position[0], position[1], z_offset])(well_shape)
        wells.append(well)
    
    return union()(*wells)

