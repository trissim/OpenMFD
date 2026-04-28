"""Device configuration presets with multi-layer ABC hierarchy.

This module provides a type-safe, extensible hierarchy of device presets
following OpenHCS-style design patterns:
- Abstract Base Classes (ABC) for interface enforcement
- Frozen dataclasses for immutability
- Multi-layer inheritance for semantic clarity and type safety
- Fail-loud validation with helpful error messages
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, Optional

from .config import (
    ArrayConfiguration,
    CompleteDeviceConfiguration,
    PDMSConfiguration,
    WaferMaskConfiguration,
)
from openmfd.geometry.wells import WellConfiguration
from openmfd.geometry.channels import ChannelConfiguration
from openmfd.geometry.chambers import ChamberConfiguration
from openmfd.inserts.config import CompleteInsertConfiguration


@dataclass(frozen=True)
class DevicePreset(ABC):
    """Base abstract class for all device configuration presets.
    
    This is the most abstract layer - defines the minimal interface
    that ALL device presets must implement, regardless of device type.
    
    Following OpenHCS patterns:
    - ABC for interface enforcement
    - Frozen dataclass for immutability
    - Abstract methods for required implementations
    """
    
    # Minimal common parameters
    device_name: str = ""
    
    @abstractmethod
    def bottom_layer(self) -> CompleteDeviceConfiguration:
        """Generate bottom layer configuration.
        
        Returns
        -------
        CompleteDeviceConfiguration
            Complete configuration for bottom layer.
        """
        pass
    
    @abstractmethod
    def top_layer(self) -> CompleteDeviceConfiguration:
        """Generate top layer configuration.
        
        Returns
        -------
        CompleteDeviceConfiguration
            Complete configuration for top layer.
        """
        pass
    
    @abstractmethod
    def validate(self) -> None:
        """Validate configuration parameters.
        
        Raises
        ------
        ValueError
            If configuration parameters are invalid or incompatible.
            Error messages should follow OpenHCS fail-loud philosophy:
            include the problem AND a suggested solution.
        """
        pass


@dataclass(frozen=True)
class MicrofluidicDevicePreset(DevicePreset):
    """Abstract class for microfluidic devices with PDMS and wafer fabrication.
    
    This intermediate layer adds PDMS-specific and wafer-specific parameters
    that are common to all microfluidic devices but not necessarily to
    other device types (e.g., purely mechanical devices).
    
    Semantic meaning: This device requires PDMS fabrication and wafer masks.
    """
    
    # PDMS fabrication parameters
    cure_temp: int = 100
    
    # Array parameters
    grid_size: Tuple[int, int] = (6, 8)
    
    # Wafer parameters
    wafer_size: float = 150.0
    wafer_flat_length: float = 57.5
    
    @abstractmethod
    def pdms_config(self) -> PDMSConfiguration:
        """Generate PDMS configuration.
        
        Returns
        -------
        PDMSConfiguration
            PDMS shrinkage compensation configuration.
        """
        pass
    
    @abstractmethod
    def wafer_mask_config(self) -> WaferMaskConfiguration:
        """Generate wafer mask configuration.
        
        Returns
        -------
        WaferMaskConfiguration
            Wafer mask configuration for photolithography.
        """
        pass
    
    @abstractmethod
    def array_config(self) -> ArrayConfiguration:
        """Generate array configuration.
        
        Returns
        -------
        ArrayConfiguration
            Device array configuration.
        """
        pass


@dataclass(frozen=True)
class CompartmentalizedDevicePreset(MicrofluidicDevicePreset):
    """Abstract class for devices with compartments (wells + channels + chambers).

    This layer adds compartment-specific parameters and requires
    insert configuration for 3D printed inserts.

    Semantic meaning: This device has wells, channels, chambers, and
    requires a 3D printed insert.

    Note: All fields have defaults to satisfy dataclass inheritance rules.
    Concrete classes should override these with device-specific values.
    """

    # Compartment geometry (defaults provided for dataclass compatibility)
    casing_x: float = 18.0
    casing_y: float = 9.0
    well_radius: float = 2.5
    channel_length: float = 0.3  # Base channel length (for chamber measurements)
    channel_length_extra: float = 6.0  # Extra length for bottom layer
    channel_width: float = 0.01
    channel_gap: float = 0.03
    num_channels: int = 83
    
    @abstractmethod
    def insert_config(self) -> CompleteInsertConfiguration:
        """Generate 3D printed insert configuration.
        
        Returns
        -------
        CompleteInsertConfiguration
            Complete configuration for 3D printed insert.
        """
        pass
    
    @abstractmethod
    def wells_config(self) -> WellConfiguration:
        """Generate wells configuration.
        
        Returns
        -------
        WellConfiguration
            Wells configuration.
        """
        pass
    
    @abstractmethod
    def channels_config(self) -> ChannelConfiguration:
        """Generate channels configuration.
        
        Returns
        -------
        ChannelConfiguration
            Channels configuration.
        """
        pass
    
    @abstractmethod
    def chambers_config(self) -> ChamberConfiguration:
        """Generate chambers configuration.

        Returns
        -------
        ChamberConfiguration
            Chambers configuration.
        """
        pass


@dataclass(frozen=True)
class TwoCompartmentDeviceConfig(CompartmentalizedDevicePreset):
    """Concrete preset for 2-compartment 96-well devices.

    This is a fully concrete implementation with all defaults
    specific to the 2-compartment device type.

    Provides sensible defaults for all parameters. Override only what you need.

    Examples
    --------
    >>> # Use all defaults
    >>> config = TwoCompartmentDeviceConfig()
    >>>
    >>> # Override cure temperature
    >>> config = TwoCompartmentDeviceConfig(cure_temp=80)
    >>>
    >>> # Override grid size
    >>> config = TwoCompartmentDeviceConfig(grid_size=(4, 6))
    >>>
    >>> # Generate device stack
    >>> from openmfd.devices import build_device_stack
    >>> device_stack = build_device_stack(config.bottom_layer(), config.top_layer())
    """

    # Core geometry parameters
    casing_x: float = 18.0
    casing_y: float = 9.0
    well_radius: float = 2.5
    wells_pos: float = 4.5  # Distance from center to wells

    # Channel parameters
    channel_length: float = 0.3  # Base channel length
    channel_length_extra: float = 6.0  # Extra length for bottom layer
    channel_width: float = 0.01
    channel_gap: float = 0.03

    # Chamber parameters
    chamber_height: float = 0.2

    # Type-driven computed parameters (can be overridden)
    chamber_len_until: Optional[float] = None  # Defaults to wells_pos
    chamber_width: Optional[float] = None  # Defaults to well_radius * 2
    num_channels: Optional[int] = None  # Computed from well_radius / (channel_gap + channel_width)

    # Insert parameters
    insert_height: float = 3.8
    insert_height_inner: float = 0.40
    outer_taper_degrees: float = 16.0
    inner_taper_degrees: float = 35.0
    outer_taper_extra_length: float = 0.300
    inner_taper_extra_length: float = 0.91
    insert_hole_dims: Tuple[float, float] = (2.0, 2.0)  # Square hole dimensions
    insert_pin_dims: Tuple[float, float] = (1.85, 1.85)
    insert_pin_height: float = 0.14
    insert_pin_inner_height: float = 2.0
    insert_pin_offset: float = -0.5  # Offset for pin positioning
    skirt_thickness1: float = 0.75
    skirt_height1: float = 0.660
    skirt_empty1: float = 0.3
    skirt_thickness2: float = 0.8
    skirt_height2: float = 0.04

    # Alignment parameters
    alignment_offset: Tuple[float, float] = (0.0, 0.0)
    alignment_mark_size: float = 1.0
    units_from_center: Tuple[float, float] = (7.0, 4.75)  # Alignment mark positions in units from center

    # Glass outline parameters
    glass_size: Tuple[float, float] = (110.0, 74.0)
    glass_error: float = 4.0

    # Wall parameters
    wall_height: float = 10.0
    wall_thickness: float = 7.0
    wall_padx: float = 9.0
    wall_pady: float = 9.0

    def validate(self) -> None:
        """Validate configuration parameters (fail-loud).

        Raises
        ------
        ValueError
            If configuration parameters are invalid, with helpful solution.
        """
        if self.cure_temp < 0 or self.cure_temp > 200:
            raise ValueError(
                f"cure_temp must be 0-200°C, got {self.cure_temp}. "
                f"Solution: Use 80-120°C for PDMS (100°C is standard)."
            )

        if self.grid_size[0] < 1 or self.grid_size[1] < 1:
            raise ValueError(
                f"grid_size must be positive, got {self.grid_size}. "
                f"Solution: Use (6, 8) for 96-well plate compatibility."
            )

        if self.casing_x <= 0 or self.casing_y <= 0:
            raise ValueError(
                f"casing dimensions must be positive, got ({self.casing_x}, {self.casing_y}). "
                f"Solution: Use (18.0, 9.0) for standard 2-compartment devices."
            )

    # Type-driven computed properties
    def _chamber_len_until(self) -> float:
        """Compute chamber_len_until (defaults to wells_pos)."""
        return self.chamber_len_until if self.chamber_len_until is not None else self.wells_pos

    def _chamber_width(self) -> float:
        """Compute chamber_width (defaults to well_radius * 2)."""
        return self.chamber_width if self.chamber_width is not None else self.well_radius * 2

    def _num_channels(self) -> int:
        """Compute num_channels from well_radius / (channel_gap + channel_width)."""
        if self.num_channels is not None:
            return self.num_channels
        return int(self.well_radius / (self.channel_gap + self.channel_width))

    def pdms_config(self) -> PDMSConfiguration:
        """Generate PDMS configuration."""
        return PDMSConfiguration(cure_temp=self.cure_temp)

    def wafer_mask_config(self) -> WaferMaskConfiguration:
        """Generate wafer mask configuration."""
        return WaferMaskConfiguration(
            wafer_size=self.wafer_size,
            flat_length=self.wafer_flat_length
        )

    def array_config(self) -> ArrayConfiguration:
        """Generate array configuration."""
        return ArrayConfiguration(
            rows=self.grid_size[0],
            columns=self.grid_size[1],
            units_from_center=self.units_from_center
        )

    def wells_config(self) -> WellConfiguration:
        """Generate wells configuration for 2 wells."""
        # 2-compartment: wells at left and right (using wells_pos from center)
        well_positions = [
            (self.wells_pos, 0.0),
            (-self.wells_pos, 0.0)
        ]

        return WellConfiguration(
            radius=self.well_radius,
            positions=well_positions,
            shape="circle"
        )

    def channels_config(self, use_extra_length: bool = False) -> ChannelConfiguration:
        """Generate channels configuration.

        Parameters
        ----------
        use_extra_length : bool, default=False
            If True, use channel_length + channel_length_extra (for bottom layer).
            If False, use channel_length only (for top layer chamber measurements).
        """
        length = self.channel_length + self.channel_length_extra if use_extra_length else self.channel_length
        return ChannelConfiguration(
            length=length,
            width=self.channel_width,
            height=0.2,
            num_channels=self._num_channels(),  # Use computed value
            spacing=self.channel_gap
        )

    def chambers_config(self) -> ChamberConfiguration:
        """Generate chambers configuration."""
        return ChamberConfiguration(
            height=self.chamber_height,
            len_until=self._chamber_len_until(),  # Use computed value
            width=self._chamber_width()  # Use computed value
        )

    def insert_config(self) -> CompleteInsertConfiguration:
        """Generate 3D printed insert configuration."""
        from openmfd.inserts.config import (
            TaperConfiguration,
            PinConfiguration,
            SkirtConfiguration,
        )

        wells_cfg = self.wells_config()
        channels_cfg = self.channels_config()
        chambers_cfg = self.chambers_config()
        insert_pin_offset_from_center = self.wells_pos + self.insert_pin_offset
        insert_pin_positions = [
            (insert_pin_offset_from_center, 0.0),
            (-insert_pin_offset_from_center, 0.0),
        ]

        return CompleteInsertConfiguration(
            wells=wells_cfg,
            channels=channels_cfg,
            chambers=chambers_cfg,
            outer_taper=TaperConfiguration(
                height=self.insert_height,
                degrees=self.outer_taper_degrees,
                extra_length=self.outer_taper_extra_length
            ),
            inner_taper=None,
            pins=PinConfiguration(
                dims=self.insert_pin_dims,
                height=self.insert_pin_height,
                inner_height=self.insert_pin_inner_height,
                offset=0.0,
                hole_dims=self.insert_hole_dims
            ),
            skirts=SkirtConfiguration(
                thickness1=self.skirt_thickness1,
                height1=self.skirt_height1,
                empty1=self.skirt_empty1,
                thickness2=self.skirt_thickness2,
                height2=self.skirt_height2
            ),
            pdms_scale=self.pdms_config().scale_factor(),
            well_positions=insert_pin_positions,
            dims=(self.casing_x, self.casing_y, 0.0)
        )

    def bottom_layer(self) -> CompleteDeviceConfiguration:
        """Generate bottom layer configuration (channels only + text)."""
        from .config import (
            CasingConfiguration,
            DeviceConfiguration,
            OutlineConfiguration,
            TextConfiguration,
        )

        # Text annotations for bottom layer
        cure_text = f"Cure at {self.cure_temp}°C"
        text_x = self.grid_size[0] * self.casing_x / 2.0 + self.alignment_offset[0]
        text_y = (self.grid_size[1] * self.casing_y / 2.0 + self.alignment_offset[1]
                  - (self.grid_size[1] + 3) * self.casing_y / 2)

        text_annotations = [
            TextConfiguration(text=cure_text, position=(text_x, text_y), size=2.0),
            TextConfiguration(
                text="Use 60mL of Sylgard 184 in 1:10 ratio",
                position=(text_x, text_y - self.casing_y / 2),
                size=2.0
            )
        ]

        return CompleteDeviceConfiguration(
            device=DeviceConfiguration(
                casing=CasingConfiguration(x=self.casing_x, y=self.casing_y),
                channels_config=self.channels_config(use_extra_length=True),  # Bottom layer uses longer channels
                add_wells=False,
                add_chambers=False,
                dxf=True
            ),
            array=self.array_config(),
            text_annotations=text_annotations,
            pdms=self.pdms_config(),
            wafer_mask=self.wafer_mask_config(),
            alignment_offset=self.alignment_offset,
            alignment_mark_size=self.alignment_mark_size
        )

    def top_layer(self) -> CompleteDeviceConfiguration:
        """Generate top layer configuration (wells + chambers + insert holes + outline)."""
        from .config import (
            CasingConfiguration,
            DeviceConfiguration,
            InsertHolesConfiguration,
            OutlineConfiguration,
        )

        # Calculate insert hole positions (wells_pos + insert_pin_offset from center)
        wells_cfg = self.wells_config()
        insert_hole_offset_from_center = self.wells_pos + self.insert_pin_offset
        insert_hole_positions = [
            (insert_hole_offset_from_center, 0.0),
            (-insert_hole_offset_from_center, 0.0)
        ]

        # Outline configuration
        outline_config = OutlineConfiguration(
            glass_size=self.glass_size,
            wall_thickness=self.glass_error,
            alignment_groove_thickness=1.0
        )

        return CompleteDeviceConfiguration(
            device=DeviceConfiguration(
                casing=CasingConfiguration(x=self.casing_x, y=self.casing_y),
                wells_config=wells_cfg,
                channels_config=self.channels_config(),
                chambers_config=self.chambers_config(),
                insert_holes=InsertHolesConfiguration(
                    hole_dims=self.insert_hole_dims,
                    well_positions=insert_hole_positions,
                    offset=0.0  # Offset already applied to positions
                ),
                add_wells=True,
                add_chambers=True,
                dxf=True
            ),
            array=self.array_config(),
            outline=outline_config,
            pdms=self.pdms_config(),
            wafer_mask=self.wafer_mask_config(),
            alignment_offset=self.alignment_offset,
            alignment_mark_size=self.alignment_mark_size
        )


@dataclass(frozen=True)
class FourByFourDeviceConfig(TwoCompartmentDeviceConfig):
    """Preset for 4x4 2-compartment devices (smaller scale production).

    Inherits all behavior from TwoCompartmentDeviceConfig, only overriding
    the parameters that differ for 4x4 format:
    - Smaller wells and closer spacing
    - Smaller wafer (100mm vs 150mm)
    - No wall padding
    - Different alignment mark positions
    - Default 4x4 grid
    """

    # Override only 4x4-specific geometry
    casing_x: float = 12.0  # vs 18.0 for 96-well
    casing_y: float = 6.0   # vs 9.0 for 96-well
    well_radius: float = 2.0  # vs 2.5 for 96-well
    wells_pos: float = 3.0  # vs 4.5 for 96-well

    # Override 4x4-specific wafer parameters
    wafer_size: float = 100.0  # vs 150.0 for 96-well
    wafer_flat_length: float = 32.5  # vs 57.5 for 96-well

    # Override 4x4-specific alignment
    units_from_center: Tuple[float, float] = (2.3, 2.3)  # vs (7.0, 4.75) for 96-well

    # Override 4x4-specific wall parameters (no padding)
    wall_padx: float = 0.0  # vs 9.0 for 96-well
    wall_pady: float = 0.0  # vs 9.0 for 96-well

    # Default grid size for 4x4
    grid_size: Tuple[int, int] = (4, 4)  # vs (6, 8) for 96-well

    # All other parameters and methods inherited from TwoCompartmentDeviceConfig!
