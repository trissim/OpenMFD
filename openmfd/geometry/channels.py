"""Channel patterns and configurations for microfluidic devices.

This module provides functions for creating microfluidic channels with
various configurations (single, arrays, custom spacing).
"""

from typing import Optional, Tuple
from dataclasses import dataclass
import math
import solid
from solid.utils import union

from .types import Measurements
from .primitives import make_channel


@dataclass
class ChannelConfiguration:
    """Configuration for channel geometry.
    
    Attributes
    ----------
    length : float
        Channel length (along flow direction).
    width : float
        Channel width (perpendicular to flow).
    height : float, optional
        Channel height. If None, creates 2D geometry.
    num_channels : int, default=1
        Number of parallel channels.
    max_channels : int, optional
        Maximum number of channels to fit within a given width.
        If specified, num_channels is calculated automatically.
    spacing : float, optional
        Gap between channels. If None, uses width.
    rotate : bool, default=False
        If True, rotate channels 90 degrees.
    """
    length: float
    width: float
    height: Optional[float] = None
    num_channels: int = 1
    max_channels: Optional[int] = None
    spacing: Optional[float] = None
    rotate: bool = False
    
    def __post_init__(self):
        """Validate configuration."""
        if self.length <= 0:
            raise ValueError(f"length must be positive, got {self.length}")
        if self.width <= 0:
            raise ValueError(f"width must be positive, got {self.width}")
        if self.height is not None and self.height <= 0:
            raise ValueError(f"height must be positive, got {self.height}")
        if self.num_channels <= 0:
            raise ValueError(f"num_channels must be positive, got {self.num_channels}")


def make_channels(
    length: float,
    width: float,
    height: Optional[float] = None,
    num_chans: int = 1,
    max_chans: Optional[int] = None,
    spacing: Optional[float] = None,
    dxf: bool = False,
    rotate_channels: bool = False
) -> Tuple[solid.OpenSCADObject, Measurements]:
    """Create an array of parallel microfluidic channels.
    
    This function creates multiple parallel channels with specified spacing.
    Channels are centered and can be created in 2D (for DXF) or 3D (for STL).
    
    Parameters
    ----------
    length : float
        Channel length (along flow direction).
    width : float
        Channel width (perpendicular to flow).
    height : float, optional
        Channel height. If None or dxf=True, creates 2D geometry.
    num_chans : int, default=1
        Number of parallel channels. Ignored if max_chans is specified.
    max_chans : int, optional
        Maximum width to fit channels within. If specified, num_chans
        is calculated automatically to fit channels with spacing.
    spacing : float, optional
        Gap between channels. If None, uses width.
    dxf : bool, default=False
        If True, create 2D geometry for DXF export.
    rotate_channels : bool, default=False
        If True, rotate channels 90 degrees.
        
    Returns
    -------
    channels : solid.OpenSCADObject
        Union of all channels.
    measurements : Measurements
        Measurements of the channel array (x, y, z ranges from center).
        
    Examples
    --------
    >>> # Create single channel
    >>> channels, msrs = make_channels(10.0, 0.5, 0.3)
    
    >>> # Create 5 parallel channels with 0.5mm spacing
    >>> channels, msrs = make_channels(10.0, 0.5, 0.3, num_chans=5, spacing=0.5)
    
    >>> # Fit maximum channels in 20mm width
    >>> channels, msrs = make_channels(10.0, 0.5, 0.3, max_chans=20, spacing=0.5)
    
    >>> # Create 2D channels for DXF
    >>> channels, msrs = make_channels(10.0, 0.5, dxf=True, num_chans=3)
    """
    # Set default spacing
    if spacing is None:
        spacing = width
    
    # Calculate number of channels if fitting max within given width
    if max_chans is not None:
        num_chans = math.floor((max_chans - spacing) / (width + spacing))
    
    # Calculate total width of channel section
    total_width = (width * num_chans) + (spacing * (num_chans - 1))
    
    # Create template channel
    channel_t = make_channel(length, width, height, dxf)
    
    # Center the channels
    # If even number of channels, offset to center the gap
    if num_chans % 2 == 0:
        centering = -(width / 2.0 + spacing / 2.0)
    else:
        centering = 0
    
    # Move template channel to align and center
    z_offset = 0 if (dxf or height is None) else height / 2.0
    if dxf or height is None:
        channel_t = solid.translate([0, centering])(channel_t)
    else:
        channel_t = solid.translate([0, centering, z_offset])(channel_t)
    
    # Create channels array
    channels = []
    for i in range(num_chans):
        # Calculate direction for this channel
        # i=0: no translation
        # i=1: first channel adjacent to center
        # i>=1: alternate left and right
        direction = i
        
        if i >= 1:
            direction = -(i / 2.0)
            if i % 2 == 1:
                direction = (-direction) + 0.5
        
        # Create channel at right position
        translation_coords = [0, direction * (width + spacing)]
        if dxf or height is None:
            channel = solid.translate(translation_coords)(channel_t)
        else:
            channel = solid.translate([*translation_coords, 0])(channel_t)
        channels.append(channel)
    
    # Group all channels
    channels = union()(*channels)
    
    # Compute measurements
    measurements = Measurements(
        x=(length / 2.0, -length / 2.0),
        y=(total_width / 2.0, -total_width / 2.0),
        z=(height, 0) if (height is not None and not dxf) else (0, 0)
    )
    
    # Rotate if requested
    if rotate_channels:
        channels = solid.rotate(90)(channels)
        # Swap x and y measurements
        measurements = Measurements(
            x=measurements.y,
            y=measurements.x,
            z=measurements.z
        )
    
    return channels, measurements

