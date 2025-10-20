"""Wall generation for device containment and wafer integration.

This module provides functions for creating walls around device arrays,
including circular wafer walls and rectangular grid walls.
"""

from typing import List, Tuple, Optional
import solid
from solid.utils import union, difference

from .config import WallConfiguration, CasingConfiguration, ArrayConfiguration


def create_wall(
    wall_thickness: float,
    outline_thickness: float,
    dims: List[float],
    grid_size: List[int],
    wall_height: float = 2000,
    dxf: bool = False
) -> solid.OpenSCADObject:
    """Create rectangular walls around device array.
    
    Creates a rectangular wall frame around the device array with specified
    thickness and height.
    
    Parameters
    ----------
    wall_thickness : float
        Wall thickness.
    outline_thickness : float
        Outline thickness (inner boundary).
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
    wall_height : float, default=2000
        Wall height (in microns).
    dxf : bool, default=False
        If True, create 2D geometry for DXF export.
        
    Returns
    -------
    solid.OpenSCADObject
        Wall geometry.
        
    Examples
    --------
    >>> walls = create_wall(0.95, 0.05, [9.0, 9.0, 0], [8, 12], wall_height=15)
    """
    # Compute dimensions
    inner_width = grid_size[0] * dims[0] + outline_thickness * 2
    inner_length = grid_size[1] * dims[1] + outline_thickness * 2
    outer_width = inner_width + wall_thickness * 2
    outer_length = inner_length + wall_thickness * 2
    
    # Compute positions
    outer_pos_x = -outline_thickness - wall_thickness
    outer_pos_y = -outline_thickness - wall_thickness
    inner_pos_x = -outline_thickness
    inner_pos_y = -outline_thickness
    
    if dxf:
        # 2D walls
        inner_wall = solid.translate([inner_pos_x, inner_pos_y, 0])(
            solid.square([inner_width, inner_length])
        )
        outer_wall = solid.translate([outer_pos_x, outer_pos_y, 0])(
            solid.square([outer_width, outer_length])
        )
        return outer_wall - inner_wall
    else:
        # 3D walls
        inner_wall = solid.translate([inner_pos_x, inner_pos_y, 0])(
            solid.cube([inner_width, inner_length, wall_height])
        )
        outer_wall = solid.translate([outer_pos_x, outer_pos_y, 0])(
            solid.cube([outer_width, outer_length, wall_height])
        )
        return outer_wall - inner_wall


def create_wafer_walls(
    diameter: float,
    thickness: float,
    grid_size: List[int],
    dims: List[float],
    height: float = 20,
    segments: int = 256,
    make_inner: bool = True,
    padx: float = 0,
    pady: float = 0
) -> Tuple[solid.OpenSCADObject, solid.OpenSCADObject, solid.OpenSCADObject]:
    """Create circular wafer walls with optional inner grid walls.
    
    Creates a circular outer wall (for wafer integration) and optional
    inner grid walls to separate device units.
    
    Parameters
    ----------
    diameter : float
        Wafer diameter.
    thickness : float
        Wall thickness.
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    height : float, default=20
        Wall height.
    segments : int, default=256
        Number of segments for circular wall.
    make_inner : bool, default=True
        Whether to create inner grid walls.
    padx : float, default=0
        Horizontal padding.
    pady : float, default=0
        Vertical padding.
        
    Returns
    -------
    tuple of (walls, wafer_wall, wafer_walls)
        walls : Inner grid walls
        wafer_wall : Outer circular wall
        wafer_walls : Combined walls and wafer_wall
        
    Examples
    --------
    >>> walls, wafer, combined = create_wafer_walls(
    ...     diameter=100, thickness=0.95, grid_size=[8, 12],
    ...     dims=[9.0, 9.0, 0], height=15
    ... )
    """
    # Create circular wafer wall
    wafer_wall_out = solid.cylinder(r=diameter / 2, h=height, segments=segments)
    wafer_wall_in = solid.cylinder(r=(diameter / 2 - thickness), h=height, segments=segments)
    wafer_wall = difference()(wafer_wall_out, wafer_wall_in)
    
    # Center wafer wall on array
    wafer_wall = solid.translate([
        grid_size[1] * dims[1] / 2.0,
        grid_size[0] * dims[0] / 2.0
    ])(wafer_wall)
    
    # Create inner grid walls
    vertical_wall_length = grid_size[0] * dims[0] + padx
    horizontal_wall_length = grid_size[1] * dims[1] + pady
    
    # Create wall templates
    vertical_wall = solid.cube([vertical_wall_length, thickness, height], center=True)
    vertical_wall = solid.translate([
        vertical_wall_length / 2 - pady / 2,
        -padx / 2,
        height / 2
    ])(vertical_wall)
    
    horizontal_wall = solid.cube([thickness, horizontal_wall_length, height], center=True)
    horizontal_wall = solid.translate([
        -pady / 2,
        horizontal_wall_length / 2 - padx / 2,
        height / 2
    ])(horizontal_wall)
    
    # Place walls
    walls = []
    walls.append(horizontal_wall)
    walls.append(vertical_wall)
    
    # Add vertical walls (between columns)
    for col in range(grid_size[1]):
        if col == grid_size[1] - 1:
            # Last wall with padding
            walls.append(solid.translate([0, (col + 1) * dims[1] + pady])(vertical_wall))
        elif col > 0 and col < grid_size[1] - 1 and make_inner:
            # Inner walls
            walls.append(solid.translate([0, (col + 1) * dims[1]])(vertical_wall))
    
    # Add horizontal walls (between rows)
    for row in range(grid_size[0]):
        if row == grid_size[0] - 1:
            # Last wall with padding
            walls.append(solid.translate([(row + 1) * dims[0] + padx, 0])(horizontal_wall))
        elif row > 0 and row < grid_size[0] - 1 and make_inner:
            # Inner walls
            walls.append(solid.translate([(row + 1) * dims[0], 0])(horizontal_wall))
    
    # Combine walls
    walls = union()(*walls)
    wafer_walls = union()(walls, wafer_wall)
    
    return walls, wafer_wall, wafer_walls


def create_device_walls(
    casing: CasingConfiguration,
    array_config: ArrayConfiguration,
    wall_config: WallConfiguration,
    outline_thickness: float = 0.05
) -> solid.OpenSCADObject:
    """Create walls from configuration objects.
    
    Parameters
    ----------
    casing : CasingConfiguration
        Casing configuration for unit dimensions.
    array_config : ArrayConfiguration
        Array configuration.
    wall_config : WallConfiguration
        Wall configuration.
    outline_thickness : float, default=0.05
        Outline thickness.
        
    Returns
    -------
    solid.OpenSCADObject
        Wall geometry.
        
    Examples
    --------
    >>> from openmfd.devices.config import (
    ...     CasingConfiguration, ArrayConfiguration, WallConfiguration
    ... )
    >>> 
    >>> casing = CasingConfiguration(x=9.0, y=9.0)
    >>> array_config = ArrayConfiguration(rows=8, columns=12)
    >>> wall_config = WallConfiguration(thickness=0.95, height=15)
    >>> 
    >>> walls = create_device_walls(casing, array_config, wall_config)
    """
    dims = casing.as_list()
    grid_size = array_config.grid_size()
    
    if wall_config.wafer_diameter is not None:
        # Create wafer walls
        walls, wafer_wall, wafer_walls = create_wafer_walls(
            diameter=wall_config.wafer_diameter,
            thickness=wall_config.thickness,
            grid_size=grid_size,
            dims=dims,
            height=wall_config.height,
            segments=wall_config.segments,
            make_inner=wall_config.make_inner,
            padx=wall_config.padding_x,
            pady=wall_config.padding_y
        )
        return wafer_walls
    else:
        # Create rectangular walls
        return create_wall(
            wall_thickness=wall_config.thickness,
            outline_thickness=outline_thickness,
            dims=dims,
            grid_size=grid_size,
            wall_height=wall_config.height,
            dxf=False
        )

