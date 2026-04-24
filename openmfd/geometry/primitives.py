"""Geometric primitives for microfluidic devices.

This module provides basic geometric shapes (wells, channels, chambers) that can be
combined to create complex microfluidic devices.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional
import solid

from .types import Dimensions


ShapeType = Literal["circle", "square", "cylinder", "cube"]


class WellDimensionsKind(Enum):
    """Closed set of well-dimension families."""

    SCALAR = 1
    PLANAR = 2
    VOLUMETRIC = 3


@dataclass(frozen=True)
class WellGeometryRequest:
    """Authoritative builder record for well-geometry creation."""

    dims: Dimensions
    height: Optional[float] = None
    dxf: bool = False
    segments: int = 64

    @classmethod
    def from_fields(
        cls,
        dims: Dimensions,
        height: Optional[float] = None,
        dxf: bool = False,
        segments: int = 64,
    ) -> "WellGeometryRequest":
        return cls(dims=dims, height=height, dxf=dxf, segments=segments)

    def build(self) -> solid.OpenSCADObject:
        return make_well(
            self.dims,
            height=self.height,
            dxf=self.dxf,
            segments=self.segments,
        )


def _is_2d_well(height: Optional[float], dxf: bool) -> bool:
    return dxf or height is None


def _round_well(
    radius: float, height: Optional[float], dxf: bool, segments: int
) -> solid.OpenSCADObject:
    if _is_2d_well(height, dxf):
        return solid.circle(r=radius, segments=segments)
    return solid.cylinder(r=radius, h=height, segments=segments, center=True)


def _rectangular_well(dims: Dimensions, height: Optional[float], dxf: bool) -> solid.OpenSCADObject:
    if len(dims) == 2 or _is_2d_well(height, dxf):
        return solid.square(dims[:2], center=True)
    return solid.cube(dims, center=True)


def _normalize_well_dimensions(dims: Dimensions) -> tuple[WellDimensionsKind, Dimensions]:
    if isinstance(dims, (int, float)):
        return WellDimensionsKind.SCALAR, dims
    if not isinstance(dims, (tuple, list)):
        raise ValueError(f"dims must be a number or tuple, got {type(dims)}")
    seq = list(dims)
    if len(seq) == 1:
        scalar = seq[0]
        if not isinstance(scalar, (int, float)):
            raise ValueError("dims[0] must be a number")
        return WellDimensionsKind.SCALAR, scalar
    if len(seq) == 2:
        return WellDimensionsKind.PLANAR, (seq[0], seq[1])
    if len(seq) == 3:
        return WellDimensionsKind.VOLUMETRIC, (seq[0], seq[1], seq[2])
    raise ValueError(f"dims tuple must have 1, 2, or 3 elements, got {len(seq)}")


def make_well(
    dims: Dimensions,
    shape: Optional[ShapeType] = None,
    height: Optional[float] = None,
    dxf: bool = False,
    segments: int = 64,
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

    kind, normalized_dims = _normalize_well_dimensions(dims)
    dispatch = {
        WellDimensionsKind.SCALAR: lambda value: _round_well(value, height, dxf, segments),
        WellDimensionsKind.PLANAR: lambda value: _rectangular_well(value, height, dxf),
        WellDimensionsKind.VOLUMETRIC: lambda value: _rectangular_well(value, height, dxf),
    }
    return dispatch[kind](normalized_dims)


def make_channel(
    length: float, width: float, height: Optional[float] = None, dxf: bool = False
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
    length: float, width: float, height: Optional[float] = None, dxf: bool = False
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
