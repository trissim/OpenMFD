"""Configuration dataclasses for device assembly.

This module provides configuration objects for assembling complete microfluidic
devices from geometric primitives.
"""

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Tuple

from openmfd.core import ConfigurationContract, PositiveFieldsConfiguration
from openmfd.geometry.types import Position2D
from openmfd.geometry.wells import WellConfiguration
from openmfd.geometry.channels import ChannelConfiguration
from openmfd.geometry.chambers import ChamberConfiguration


AlignmentMode = Literal["full", "hollow", "partial"]


@dataclass
class CasingConfiguration(ConfigurationContract):
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

    def _validate(self) -> None:
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
class ArrayConfiguration(ConfigurationContract):
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

    def _validate(self) -> None:
        if self.rows <= 0:
            raise ValueError(f"rows must be positive, got {self.rows}")
        if self.columns <= 0:
            raise ValueError(f"columns must be positive, got {self.columns}")

    def grid_size(self) -> List[int]:
        """Return as [rows, columns] list."""
        return [self.rows, self.columns]


@dataclass
class OutlineConfiguration(ConfigurationContract):
    """Configuration for device outline/frame.

    Attributes
    ----------
    thickness : float
        Outline thickness.
    enabled : bool, default=True
        Whether to create outline.
    """

    thickness: Optional[float] = None
    glass_size: Optional[List[float]] = None
    wall_thickness: Optional[float] = None
    alignment_groove_thickness: Optional[float] = None
    enabled: bool = True

    def _normalize(self) -> None:
        if self.wall_thickness is None and self.thickness is not None:
            self.wall_thickness = self.thickness
        if self.thickness is None and self.wall_thickness is not None:
            self.thickness = self.wall_thickness

    def _validate(self) -> None:
        if self.thickness is None or self.thickness <= 0:
            raise ValueError(f"thickness must be positive, got {self.thickness}")
        if self.glass_size is not None and len(self.glass_size) != 2:
            raise ValueError("glass_size must contain exactly two values")
        if self.alignment_groove_thickness is not None and self.alignment_groove_thickness <= 0:
            raise ValueError("alignment_groove_thickness must be positive when provided")


@dataclass
class WallConfiguration(PositiveFieldsConfiguration):
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

    def _positive_fields(self) -> dict[str, float | None]:
        return {
            "thickness": self.thickness,
            "height": self.height,
            "wafer_diameter": self.wafer_diameter,
        }


@dataclass
class InsertHolesConfiguration(ConfigurationContract):
    """Configuration for square insert-hole cutouts in well layers."""

    hole_dims: Tuple[float, float]
    well_positions: List[Position2D]
    offset: float = 0.0

    def _validate(self) -> None:
        if len(self.hole_dims) != 2 or any(value <= 0 for value in self.hole_dims):
            raise ValueError("hole_dims must contain exactly two positive values")
        if not self.well_positions:
            raise ValueError("well_positions must contain at least one position")


@dataclass
class TextConfiguration(ConfigurationContract):
    """Configuration for text annotations in built device layers."""

    text: str
    position: Tuple[float, float]
    size: float = 2.0
    halign: str = "center"
    valign: str = "center"

    def _validate(self) -> None:
        if not self.text:
            raise ValueError("text must be non-empty")
        if len(self.position) != 2:
            raise ValueError("position must contain exactly two values")
        if self.size <= 0:
            raise ValueError(f"size must be positive, got {self.size}")


@dataclass
class PDMSConfiguration(ConfigurationContract):
    """Configuration for PDMS shrinkage compensation."""

    cure_temp: int = 100
    shrinkage_per_degree: float = 0.002

    def _validate(self) -> None:
        if self.cure_temp <= 0:
            raise ValueError(f"cure_temp must be positive, got {self.cure_temp}")
        if self.shrinkage_per_degree < 0:
            raise ValueError(
                f"shrinkage_per_degree must be non-negative, got {self.shrinkage_per_degree}"
            )
        if self.scale_factor() <= 0:
            raise ValueError("PDMS scale_factor must remain positive")

    def scale_factor(self) -> float:
        return 1.0 - (self.cure_temp * self.shrinkage_per_degree)


@dataclass
class WaferMaskConfiguration(ConfigurationContract):
    """Configuration for final wafer-mask projection."""

    wafer_size: float
    flat_length: float
    wafer_line_thickness: float = 0.3
    outer_mask_thickness: float = 3.0

    def _validate(self) -> None:
        if self.wafer_size <= 0:
            raise ValueError(f"wafer_size must be positive, got {self.wafer_size}")
        if self.flat_length <= 0:
            raise ValueError(f"flat_length must be positive, got {self.flat_length}")
        if self.wafer_line_thickness <= 0:
            raise ValueError(
                f"wafer_line_thickness must be positive, got {self.wafer_line_thickness}"
            )
        if self.outer_mask_thickness <= 0:
            raise ValueError(
                f"outer_mask_thickness must be positive, got {self.outer_mask_thickness}"
            )


@dataclass
class DeviceConfiguration(ConfigurationContract):
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
    insert_holes: Optional[InsertHolesConfiguration] = None
    rotation: float = 0
    add_wells: bool = True
    add_channels: bool = True
    add_chambers: bool = True
    dxf: bool = False

    def _validate(self) -> None:
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
class CompleteDeviceConfiguration(ConfigurationContract):
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
    text_annotations: List[TextConfiguration] = field(default_factory=list)
    pdms: Optional[PDMSConfiguration] = None
    wafer_mask: Optional[WaferMaskConfiguration] = None
    alignment_offset: Optional[Tuple[float, float]] = None
    alignment_mark_size: float = 1.0

    def _validate(self) -> None:
        if self.device is None:
            raise ValueError("device must be provided")
        if self.alignment_mark_size <= 0:
            raise ValueError("alignment_mark_size must be positive")

    def has_array(self) -> bool:
        """Check if array is configured."""
        return self.array is not None and (self.array.rows > 1 or self.array.columns > 1)

    def has_outline(self) -> bool:
        """Check if outline is configured and enabled."""
        return self.outline is not None and self.outline.enabled

    def has_walls(self) -> bool:
        """Check if walls are configured and enabled."""
        return self.walls is not None and self.walls.enabled

    def has_pdms_scaling(self) -> bool:
        """Check if PDMS scaling is configured."""
        return self.pdms is not None

    def has_wafer_mask(self) -> bool:
        """Check if wafer-mask projection is configured."""
        return self.wafer_mask is not None
