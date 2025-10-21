"""Outline/frame generation for device arrays.

This module provides functions for creating outlines and frames around
device arrays.
"""

from typing import List, Tuple, Optional
import numpy as np
import solid

from .config import OutlineConfiguration, CasingConfiguration, ArrayConfiguration
from .wafer import compute_wafer_center


def create_outline(
    thickness: float,
    array: solid.OpenSCADObject,
    dims: List[float],
    grid_size: List[int]
) -> solid.OpenSCADObject:
    """Create an outline/frame around a device array.
    
    The outline is created by making a larger rectangle and subtracting
    the array from it, leaving a frame.
    
    Parameters
    ----------
    thickness : float
        Outline thickness.
    array : solid.OpenSCADObject
        Device array to create outline around.
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
        
    Returns
    -------
    solid.OpenSCADObject
        Outline geometry (frame around array).
        
    Examples
    --------
    >>> outline = create_outline(0.05, array, [9.0, 9.0, 0], [8, 12])
    """
    # Compute total array dimensions
    width = grid_size[0] * dims[0] + thickness * 2
    length = grid_size[1] * dims[1] + thickness * 2
    
    # Create outer rectangle
    outer = solid.translate([-thickness, -thickness, 0])(
        solid.square([width, length])
    )
    
    # Subtract array to create frame
    return outer - array


def create_device_outline(
    array: solid.OpenSCADObject,
    casing: CasingConfiguration,
    array_config: ArrayConfiguration,
    outline_config: OutlineConfiguration
) -> solid.OpenSCADObject:
    """Create outline from configuration objects.
    
    Parameters
    ----------
    array : solid.OpenSCADObject
        Device array.
    casing : CasingConfiguration
        Casing configuration for unit dimensions.
    array_config : ArrayConfiguration
        Array configuration.
    outline_config : OutlineConfiguration
        Outline configuration.
        
    Returns
    -------
    solid.OpenSCADObject
        Outline geometry.
        
    Examples
    --------
    >>> from openmfd.devices.config import (
    ...     CasingConfiguration, ArrayConfiguration, OutlineConfiguration
    ... )
    >>> 
    >>> casing = CasingConfiguration(x=9.0, y=9.0)
    >>> array_config = ArrayConfiguration(rows=8, columns=12)
    >>> outline_config = OutlineConfiguration(thickness=0.05)
    >>> 
    >>> outline = create_device_outline(array, casing, array_config, outline_config)
    """
    dims = casing.as_list()
    grid_size = array_config.grid_size()
    
    return create_outline(
        thickness=outline_config.thickness,
        array=array,
        dims=dims,
        grid_size=grid_size
    )


def compute_outline_dimensions(
    unit_dims: List[float],
    grid_size: List[int],
    thickness: float
) -> tuple:
    """Compute total dimensions of outline including thickness.
    
    Parameters
    ----------
    unit_dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
    thickness : float
        Outline thickness.
        
    Returns
    -------
    tuple of (float, float)
        Total outline dimensions (width, length).
        
    Examples
    --------
    >>> dims = compute_outline_dimensions([9.0, 9.0, 0], [8, 12], 0.05)
    >>> # Returns: (72.1, 108.1)
    """
    width = grid_size[0] * unit_dims[0] + thickness * 2
    length = grid_size[1] * unit_dims[1] + thickness * 2
    return (width, length)


def create_solid_outline(
    dims: List[float],
    grid_size: List[int],
    thickness: float
) -> solid.OpenSCADObject:
    """Create a solid outline (frame only, no subtraction).
    
    This creates just the frame geometry without subtracting the array.
    
    Parameters
    ----------
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
    thickness : float
        Outline thickness.
        
    Returns
    -------
    solid.OpenSCADObject
        Solid outline frame.
        
    Examples
    --------
    >>> outline = create_solid_outline([9.0, 9.0, 0], [8, 12], 0.05)
    """
    # Compute dimensions
    inner_width = grid_size[0] * dims[0]
    inner_length = grid_size[1] * dims[1]
    outer_width = inner_width + thickness * 2
    outer_length = inner_length + thickness * 2
    
    # Create outer and inner rectangles
    outer = solid.translate([-thickness, -thickness, 0])(
        solid.square([outer_width, outer_length])
    )
    inner = solid.square([inner_width, inner_length])
    
    # Subtract inner from outer to create frame
    return outer - inner


def create_custom_outline(
    array: solid.OpenSCADObject,
    outline_shape: solid.OpenSCADObject
) -> solid.OpenSCADObject:
    """Create outline with custom shape.

    Parameters
    ----------
    array : solid.OpenSCADObject
        Device array.
    outline_shape : solid.OpenSCADObject
        Custom outline shape (should be larger than array).

    Returns
    -------
    solid.OpenSCADObject
        Custom outline with array subtracted.

    Examples
    --------
    >>> # Create circular outline
    >>> circle = solid.circle(r=50)
    >>> outline = create_custom_outline(array, circle)
    """
    return outline_shape - array


def create_glass_outline(
    glass_size: List[float],
    wall_thickness: float,
    grid_size: List[int],
    dims: List[float],
    alignment_offset: Optional[Tuple[float, float]] = None,
    alignment_groove_thickness: Optional[float] = None
) -> solid.OpenSCADObject:
    """Create glass slide outline with optional alignment groove.

    Creates a rectangular outline for glass slide alignment, centered
    on the wafer. Optionally includes an alignment groove for precise
    positioning.

    Parameters
    ----------
    glass_size : list of float
        Glass slide dimensions [width, height].
    wall_thickness : float
        Outline wall thickness.
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    alignment_offset : tuple of (float, float), optional
        Alignment offset to apply.
    alignment_groove_thickness : float, optional
        Thickness of alignment groove. If provided, creates groove
        by subtracting a slightly larger outline.

    Returns
    -------
    solid.OpenSCADObject
        Glass slide outline, centered on wafer.

    Examples
    --------
    >>> # Create glass outline with alignment groove
    >>> outline = create_glass_outline(
    ...     glass_size=[110, 74], wall_thickness=0.95,
    ...     grid_size=[6, 8], dims=[9.0, 9.0, 0],
    ...     alignment_groove_thickness=1.0
    ... )
    """
    glass_size = np.array(glass_size)

    # Create inner and outer squares
    inner_outline = solid.square(glass_size, center=True)
    outer_dims = glass_size + wall_thickness
    outer_outline = solid.square(outer_dims, center=True)

    # Create outline frame
    outline = solid.difference()(outer_outline, inner_outline)

    # Center at wafer center (SINGLE SOURCE OF TRUTH)
    cx, cy = compute_wafer_center(grid_size, dims)
    outline = solid.translate([cx, cy])(outline)

    # Create alignment groove if requested
    if alignment_groove_thickness is not None:
        # Create slightly larger outline for groove
        groove_inner_dims = glass_size + wall_thickness / 2.0 - alignment_groove_thickness / 2.0
        groove_inner = solid.square(groove_inner_dims, center=True)
        groove_outer_dims = groove_inner_dims + alignment_groove_thickness
        groove_outer = solid.square(groove_outer_dims, center=True)

        # Create groove frame
        groove = solid.difference()(groove_outer, groove_inner)

        # Center groove at wafer center
        groove = solid.translate([cx, cy])(groove)

        # Subtract groove from outline
        outline = solid.difference()(outline, groove)

    return outline

