"""Chamber patterns and configurations for microfluidic devices.

This module provides functions for creating chambers (larger compartments)
that are typically connected to channels.
"""

from typing import Optional
from dataclasses import dataclass
import solid
from solid.utils import union

from .types import Measurements
from .primitives import make_chamber


@dataclass
class ChamberConfiguration:
    """Configuration for chamber geometry.
    
    Attributes
    ----------
    height : float, optional
        Chamber height. If None, uses channel height.
    extra : float, default=0
        Extra length to add to chamber beyond channel length.
    len_until : float, optional
        Extend chamber to reach this absolute length from center.
        If specified, overrides extra.
    width : float, optional
        Override chamber width. If None, uses channel width.
    """
    height: Optional[float] = None
    extra: float = 0
    len_until: Optional[float] = None
    width: Optional[float] = None
    
    def __post_init__(self):
        """Validate configuration."""
        if self.height is not None and self.height <= 0:
            raise ValueError(f"height must be positive, got {self.height}")
        if self.width is not None and self.width <= 0:
            raise ValueError(f"width must be positive, got {self.width}")


def make_chambers(
    msrs: Measurements,
    height: Optional[float] = None,
    extra: float = 0,
    len_until: Optional[float] = None,
    width: Optional[float] = None,
    dxf: bool = False
) -> solid.OpenSCADObject:
    """Create chambers adjacent to channels.
    
    Creates two chambers (top and bottom) positioned adjacent to a channel array.
    Chamber dimensions are calculated based on channel measurements.
    
    Parameters
    ----------
    msrs : Measurements
        Measurements from channel array (x, y, z ranges).
    height : float, optional
        Chamber height. If None, uses channel height from msrs.
    extra : float, default=0
        Extra length to add to chamber beyond channel length.
    len_until : float, optional
        Extend chamber to reach this absolute length from center.
        If specified, overrides extra parameter.
    width : float, optional
        Override chamber width. If None, uses channel width from msrs.
    dxf : bool, default=False
        If True, create 2D geometry for DXF export.
        
    Returns
    -------
    solid.OpenSCADObject
        Union of top and bottom chambers.
        
    Examples
    --------
    >>> from openmfd.geometry.channels import make_channels
    >>> # Create channels first
    >>> channels, msrs = make_channels(10.0, 5.0, 0.3, num_chans=3)
    >>> 
    >>> # Create chambers with same height as channels
    >>> chambers = make_chambers(msrs)
    >>> 
    >>> # Create chambers with extra 2mm length
    >>> chambers = make_chambers(msrs, extra=2.0)
    >>> 
    >>> # Create chambers extending to 15mm from center
    >>> chambers = make_chambers(msrs, len_until=15.0)
    >>> 
    >>> # Create chambers with custom width and height
    >>> chambers = make_chambers(msrs, height=0.5, width=8.0)
    """
    # Helper function to compute total dimension
    def total(x):
        return abs(x[0]) + abs(x[1])
    
    # Set chamber height
    if dxf:
        chamber_z = (0, 0)
    elif height is not None:
        chamber_z = (height, 0)
    else:
        chamber_z = msrs.z
    
    # Make copy of measurements to modify for chamber dimensions
    chamber_dims = Measurements(
        x=msrs.x,
        y=msrs.y,
        z=chamber_z
    )
    
    # Calculate chamber length
    if len_until is not None:
        # Extend to specific absolute position
        chamber_len = len_until - msrs.x[0]
    else:
        # Add extra length to channel length
        chamber_len = msrs.x[0] + extra
    
    # Set chamber length
    chamber_dims.x = (chamber_len / 2.0, -(chamber_len / 2.0))
    
    # Override width if specified
    if width is not None:
        chamber_dims.y = (width / 2.0, -width / 2.0)
    
    # Compute final dimensions as list [x, y, z]
    dims = [total(chamber_dims.x), total(chamber_dims.y), total(chamber_dims.z)]
    
    # Calculate chamber translation offset to place adjacent to channels
    chamber_trslt = msrs.x[0] + (chamber_len / 2.0)
    
    # Create translation function
    # x=1 moves chamber above channels, x=-1 moves below
    if dxf or chamber_z == (0, 0):
        def trslt(x):
            return [x * chamber_trslt, 0]
    else:
        def trslt(x):
            return [x * chamber_trslt, 0, chamber_z[0] / 2.0]
    
    # Create chamber geometry function
    if dxf or chamber_z == (0, 0):
        def move(x):
            return solid.translate(trslt(x))(
                solid.square([dims[0], dims[1]], center=True)
            )
    else:
        def move(x):
            return solid.translate(trslt(x))(
                solid.cube(dims, center=True)
            )
    
    # Create top and bottom chambers
    top = move(1)
    bottom = move(-1)
    
    return union()(top, bottom)

