"""Geometric primitives for microfluidic devices.

This module provides basic geometric shapes (wells, channels, chambers) that can be
combined to create complex microfluidic devices.
"""

from typing import Optional, Union, Literal
import solid
from solid.utils import union

from .types import Dimensions


ShapeType = Literal["circle", "square", "cylinder", "cube"]


def make_well(
    dims: Dimensions,
    shape: Optional[ShapeType] = None,
    height: Optional[float] = None,
    dxf: bool = False,
    segments: int = 64
) -> solid.OpenSCADObject:
    """Create a well geometry (circle/square for 2D, cylinder/cube for 3D).
    
    Parameters
    ----------
    dims : float or tuple
        Well dimensions. If float, creates circular well with radius=dims.
        If tuple of length 2, creates square well with size=dims.
        If tuple of length 3, creates cube well with size=dims.
    shape : {'circle', 'square', 'cylinder', 'cube'}, optional
        Explicit shape type. If None, inferred from dims.
    height : float, optional
        Height for 3D geometries. If None or dxf=True, creates 2D geometry.
    dxf : bool, default=False
        If True, create 2D geometry for DXF export.
    segments : int, default=64
        Number of segments for circular shapes.
        
    Returns
    -------
    solid.OpenSCADObject
        Well geometry (circle, square, cylinder, or cube).
        
    Raises
    ------
    ValueError
        If dims is None or invalid type.
        
    Examples
    --------
    >>> # Create circular well with 3mm radius
    >>> well = make_well(3.0, height=0.3)
    
    >>> # Create square well 4x4mm
    >>> well = make_well((4.0, 4.0), height=0.3)
    
    >>> # Create 2D circle for DXF
    >>> well = make_well(3.0, dxf=True)
    """
    if dims is None:
        raise ValueError("dims cannot be None")
    
    # Determine if we're making 2D or 3D geometry
    is_2d = dxf or (height is None)
    
    # Handle different dimension types
    if isinstance(dims, (int, float)):
        # Single number = circular well
        if is_2d:
            return solid.circle(r=dims, segments=segments)
        else:
            return solid.cylinder(r=dims, h=height, segments=segments, center=True)
    
    elif isinstance(dims, (tuple, list)):
        if len(dims) == 1:
            # Single element tuple = circular well
            if isinstance(dims[0], (int, float)):
                if is_2d:
                    return solid.circle(r=dims[0], segments=segments)
                else:
                    return solid.cylinder(r=dims[0], h=height, segments=segments, center=True)
            else:
                raise ValueError("dims[0] must be a number")
        
        elif len(dims) == 2:
            # Two elements = square well
            return solid.square(dims, center=True)
        
        elif len(dims) == 3:
            # Three elements = cube well
            return solid.cube(dims, center=True)
        
        else:
            raise ValueError(f"dims tuple must have 1, 2, or 3 elements, got {len(dims)}")
    
    else:
        raise ValueError(f"dims must be a number or tuple, got {type(dims)}")


def make_channel(
    length: float,
    width: float,
    height: Optional[float] = None,
    dxf: bool = False
) -> solid.OpenSCADObject:
    """Create a single channel geometry.
    
    Parameters
    ----------
    length : float
        Channel length (along flow direction).
    width : float
        Channel width (perpendicular to flow).
    height : float, optional
        Channel height. If None or dxf=True, creates 2D geometry.
    dxf : bool, default=False
        If True, create 2D geometry for DXF export.
        
    Returns
    -------
    solid.OpenSCADObject
        Channel geometry (square for 2D, cube for 3D).
        
    Raises
    ------
    ValueError
        If length or width are not positive.
        
    Examples
    --------
    >>> # Create 3D channel 10mm long, 0.5mm wide, 0.3mm high
    >>> channel = make_channel(10.0, 0.5, 0.3)
    
    >>> # Create 2D channel for DXF
    >>> channel = make_channel(10.0, 0.5, dxf=True)
    """
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    if width <= 0:
        raise ValueError(f"width must be positive, got {width}")
    
    if dxf or (height is None):
        # 2D geometry
        return solid.square([length, width], center=True)
    else:
        # 3D geometry
        if height <= 0:
            raise ValueError(f"height must be positive, got {height}")
        return solid.cube([length, width, height], center=True)


def make_chamber(
    length: float,
    width: float,
    height: Optional[float] = None,
    dxf: bool = False
) -> solid.OpenSCADObject:
    """Create a single chamber geometry.
    
    Chambers are larger compartments, typically rectangular. This is essentially
    an alias for make_channel but semantically represents a chamber.
    
    Parameters
    ----------
    length : float
        Chamber length.
    width : float
        Chamber width.
    height : float, optional
        Chamber height. If None or dxf=True, creates 2D geometry.
    dxf : bool, default=False
        If True, create 2D geometry for DXF export.
        
    Returns
    -------
    solid.OpenSCADObject
        Chamber geometry (square for 2D, cube for 3D).
        
    Raises
    ------
    ValueError
        If dimensions are not positive.
        
    Examples
    --------
    >>> # Create chamber 5mm x 8mm x 0.3mm
    >>> chamber = make_chamber(5.0, 8.0, 0.3)
    """
    return make_channel(length, width, height, dxf)

