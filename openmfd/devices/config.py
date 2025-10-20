"""Configuration dataclasses for device assembly.

This module provides configuration objects for assembling complete microfluidic
devices from geometric primitives.
"""

from typing import Optional, Tuple, List, Literal
from dataclasses import dataclass, field

from openmfd.geometry.types import Position2D
from openmfd.geometry.wells import WellConfiguration
from openmfd.geometry.channels import ChannelConfiguration
from openmfd.geometry.chambers import ChamberConfiguration


AlignmentMode = Literal["full", "hollow", "partial"]


@dataclass
class CasingConfiguration:
    """Configuration for device casing/bounding box.
    
    Attributes
    ----------
    x : float
        Casing width (x dimension).
    y : float
        Casing length (y dimension).
    z : float, default=0
        Casing height (z dimension). 0 for 2D devices.
    """
    x: float
    y: float
    z: float = 0
    
    def __post_init__(self):
        """Validate configuration."""
        if self.x <= 0:
            raise ValueError(f"x must be positive, got {self.x}")
        if self.y <= 0:
            raise ValueError(f"y must be positive, got {self.y}")
        if self.z < 0:
            raise ValueError(f"z must be non-negative, got {self.z}")
    
    def as_list(self) -> List[float]:
        """Return as [x, y, z] list."""
        return [self.x, self.y, self.z]


@dataclass
class ArrayConfiguration:
    """Configuration for device array generation.
    
    Attributes
    ----------
    rows : int
        Number of rows in array.
    columns : int
        Number of columns in array.
    alignment : AlignmentMode, default='full'
        Alignment mode for array generation.
        - 'full': Complete grid of units
        - 'hollow': Hollow grid (no center units)
        - 'partial': Partial grid with custom offset
    units_from_center : tuple of (float, float), optional
        Offset from center for partial alignment mode.
    """
    rows: int
    columns: int
    alignment: AlignmentMode = "full"
    units_from_center: Optional[Tuple[float, float]] = None
    
    def __post_init__(self):
        """Validate configuration."""
        if self.rows <= 0:
            raise ValueError(f"rows must be positive, got {self.rows}")
        if self.columns <= 0:
            raise ValueError(f"columns must be positive, got {self.columns}")
    
    def grid_size(self) -> List[int]:
        """Return as [rows, columns] list."""
        return [self.rows, self.columns]


@dataclass
class OutlineConfiguration:
    """Configuration for device outline/frame.
    
    Attributes
    ----------
    thickness : float
        Outline thickness.
    enabled : bool, default=True
        Whether to create outline.
    """
    thickness: float
    enabled: bool = True
    
    def __post_init__(self):
        """Validate configuration."""
        if self.thickness <= 0:
            raise ValueError(f"thickness must be positive, got {self.thickness}")


@dataclass
class WallConfiguration:
    """Configuration for device walls.
    
    Attributes
    ----------
    thickness : float
        Wall thickness.
    height : float
        Wall height.
    wafer_diameter : float, optional
        Wafer diameter for circular walls. If None, creates rectangular walls.
    make_inner : bool, default=False
        Whether to create inner grid walls.
    padding_x : float, default=0
        Horizontal padding for walls.
    padding_y : float, default=0
        Vertical padding for walls.
    segments : int, default=128
        Number of segments for circular walls.
    enabled : bool, default=True
        Whether to create walls.
    """
    thickness: float
    height: float
    wafer_diameter: Optional[float] = None
    make_inner: bool = False
    padding_x: float = 0
    padding_y: float = 0
    segments: int = 128
    enabled: bool = True
    
    def __post_init__(self):
        """Validate configuration."""
        if self.thickness <= 0:
            raise ValueError(f"thickness must be positive, got {self.thickness}")
        if self.height <= 0:
            raise ValueError(f"height must be positive, got {self.height}")
        if self.wafer_diameter is not None and self.wafer_diameter <= 0:
            raise ValueError(f"wafer_diameter must be positive, got {self.wafer_diameter}")


@dataclass
class DeviceConfiguration:
    """Complete configuration for a microfluidic device.
    
    Attributes
    ----------
    wells_config : WellConfiguration, optional
        Configuration for wells.
    channels_config : ChannelConfiguration, optional
        Configuration for channels.
    chambers_config : ChamberConfiguration, optional
        Configuration for chambers.
    casing : CasingConfiguration
        Casing/bounding box configuration.
    rotation : float, default=0
        Rotation angle in degrees.
    add_wells : bool, default=True
        Whether to include wells in assembly.
    add_channels : bool, default=True
        Whether to include channels in assembly.
    add_chambers : bool, default=True
        Whether to include chambers in assembly.
    dxf : bool, default=False
        Whether to create 2D geometry for DXF export.
    """
    casing: CasingConfiguration
    wells_config: Optional[WellConfiguration] = None
    channels_config: Optional[ChannelConfiguration] = None
    chambers_config: Optional[ChamberConfiguration] = None
    rotation: float = 0
    add_wells: bool = True
    add_channels: bool = True
    add_chambers: bool = True
    dxf: bool = False
    
    def __post_init__(self):
        """Validate configuration."""
        # At least one component must be enabled
        if not any([self.add_wells, self.add_channels, self.add_chambers]):
            raise ValueError("At least one component (wells, channels, chambers) must be enabled")
        
        # If component is enabled, config must be provided
        if self.add_wells and self.wells_config is None:
            raise ValueError("wells_config must be provided when add_wells=True")
        if self.add_channels and self.channels_config is None:
            raise ValueError("channels_config must be provided when add_channels=True")
        if self.add_chambers and self.chambers_config is None:
            raise ValueError("chambers_config must be provided when add_chambers=True")


@dataclass
class CompleteDeviceConfiguration:
    """Complete configuration including device, array, outline, and walls.
    
    This is the top-level configuration for generating a complete device
    with all features.
    
    Attributes
    ----------
    device : DeviceConfiguration
        Device configuration.
    array : ArrayConfiguration, optional
        Array configuration. If None, creates single unit.
    outline : OutlineConfiguration, optional
        Outline configuration. If None, no outline created.
    walls : WallConfiguration, optional
        Wall configuration. If None, no walls created.
    """
    device: DeviceConfiguration
    array: Optional[ArrayConfiguration] = None
    outline: Optional[OutlineConfiguration] = None
    walls: Optional[WallConfiguration] = None
    
    def has_array(self) -> bool:
        """Check if array is configured."""
        return self.array is not None and (self.array.rows > 1 or self.array.columns > 1)
    
    def has_outline(self) -> bool:
        """Check if outline is configured and enabled."""
        return self.outline is not None and self.outline.enabled
    
    def has_walls(self) -> bool:
        """Check if walls are configured and enabled."""
        return self.walls is not None and self.walls.enabled

