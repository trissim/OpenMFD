"""Configuration dataclasses for 3D printed insert generation."""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from openmfd.core import ConfigurationContract, PositiveFieldsConfiguration
from openmfd.geometry.channels import ChannelConfiguration
from openmfd.geometry.chambers import ChamberConfiguration
from openmfd.geometry.wells import WellConfiguration


@dataclass
class TaperConfiguration(ConfigurationContract):
    """Configuration for tapered/chamfered extrusion.

    Parameters
    ----------
    height : float
        Height of the tapered section (mm).
    degrees : float
        Taper angle in degrees from vertical.
    extra_length : float, default=0.0
        Extra taper length to add beyond calculated value (mm).
    segments : int, default=20
        Number of segments for chamfer extrusion.

    Examples
    --------
    >>> # 16° outer taper, 3.8mm height
    >>> outer_taper = TaperConfiguration(height=3.8, degrees=16, extra_length=0.3)
    >>> # 35° inner taper, 0.4mm height
    >>> inner_taper = TaperConfiguration(height=0.4, degrees=35, extra_length=0.91)
    """

    height: float
    degrees: float
    extra_length: float = 0.0
    segments: int = 20

    def _validate(self) -> None:
        if self.height <= 0:
            raise ValueError(f"height must be positive, got {self.height}")
        if self.segments <= 0:
            raise ValueError(f"segments must be positive, got {self.segments}")


@dataclass
class InsertConfiguration(PositiveFieldsConfiguration):
    """Configuration for well insert geometry.

    Parameters
    ----------
    outer_taper : TaperConfiguration
        Configuration for outer chamfered walls.
    inner_taper : TaperConfiguration, optional
        Configuration for inner chamfered cavity. If None, no inner cavity.
    well_radius : float
        Base well radius before taper adjustment (mm).
    channel_length : float
        Channel length (mm).
    chamber_width : float, optional
        Chamber width (mm). If None, computed from well_radius.
    add_chambers : bool, default=True
        Whether to include chambers in the insert.

    Examples
    --------
    >>> # Standard 2-compartment insert
    >>> insert_config = InsertConfiguration(
    ...     outer_taper=TaperConfiguration(height=3.8, degrees=16, extra_length=0.3),
    ...     inner_taper=TaperConfiguration(height=0.4, degrees=35, extra_length=0.91),
    ...     well_radius=3.2,
    ...     channel_length=1.0,
    ...     chamber_width=None,
    ...     add_chambers=True
    ... )
    """

    outer_taper: TaperConfiguration
    inner_taper: Optional[TaperConfiguration] = None
    well_radius: float = 3.2
    channel_length: float = 1.0
    chamber_width: Optional[float] = None
    add_chambers: bool = True

    def _positive_fields(self) -> dict[str, float | None]:
        return {
            "well_radius": self.well_radius,
            "channel_length": self.channel_length,
            "chamber_width": self.chamber_width,
        }


@dataclass
class PinConfiguration(ConfigurationContract):
    """Configuration for alignment pins.

    Alignment pins fit into square holes in the PDMS wafer to ensure
    precise alignment between the insert and the device.

    Parameters
    ----------
    dims : tuple of (float, float)
        Pin dimensions (x, y) in mm.
    height : float
        Pin height above base (mm).
    inner_height : float
        Additional inner pin height (mm).
    offset : float
        Offset from well center (mm). Negative values move pins inward.
    hole_dims : tuple of (float, float)
        Dimensions of square holes in wafer for pins (x, y) in mm.
    rotation : float, default=0.0
        Rotation of each pin (and its matching hole) about its own center
        (degrees). Used to align the square pins with non-axis-aligned
        channels, e.g. 45 deg for diamond-arranged devices.

    Examples
    --------
    >>> # Standard pin configuration
    >>> pin_config = PinConfiguration(
    ...     dims=(1.85, 1.85),
    ...     height=0.06,
    ...     inner_height=2.0,
    ...     offset=-0.5,
    ...     hole_dims=(2.0, 2.0)
    ... )
    """

    dims: Tuple[float, float]
    height: float
    inner_height: float
    offset: float
    hole_dims: Tuple[float, float]
    rotation: float = 0.0

    def _validate(self) -> None:
        if self.height <= 0:
            raise ValueError(f"height must be positive, got {self.height}")
        if self.inner_height <= 0:
            raise ValueError(f"inner_height must be positive, got {self.inner_height}")
        if any(value <= 0 for value in (*self.dims, *self.hole_dims)):
            raise ValueError("dims and hole_dims must contain only positive values")


@dataclass
class SkirtConfiguration(ConfigurationContract):
    """Configuration for sealing skirts.

    Skirts provide better adhesion and sealing between the insert and
    the PDMS device. A two-layer system is typically used.

    Parameters
    ----------
    thickness1 : float
        First (upper) skirt thickness (mm). Use positive values (will be
        negated internally to shrink inward from insert geometry).
    height1 : float
        First skirt height (mm).
    empty1 : float
        Empty space fill height at top of skirt1 (mm).
    thickness2 : float
        Second (lower) skirt thickness (mm). Use positive values (will be
        negated internally to shrink inward from insert geometry).
    height2 : float
        Second skirt height (mm).

    Examples
    --------
    >>> # Standard two-layer skirt (legacy values)
    >>> skirt_config = SkirtConfiguration(
    ...     thickness1=0.75,
    ...     height1=0.66,
    ...     empty1=0.3,
    ...     thickness2=0.8,
    ...     height2=0.04
    ... )
    """

    thickness1: float
    height1: float
    empty1: float
    thickness2: float
    height2: float

    def _validate(self) -> None:
        if self.thickness1 <= 0 or self.thickness2 <= 0:
            raise ValueError("thickness1 and thickness2 must be positive")
        if self.height1 <= 0 or self.height2 <= 0:
            raise ValueError("height1 and height2 must be positive")
        if self.empty1 < 0:
            raise ValueError(f"empty1 must be non-negative, got {self.empty1}")


@dataclass
class CompleteInsertConfiguration(ConfigurationContract):
    """Top-level nominal configuration for complete insert assemblies."""

    wells: WellConfiguration
    channels: ChannelConfiguration
    chambers: ChamberConfiguration
    outer_taper: TaperConfiguration
    inner_taper: Optional[TaperConfiguration] = None
    pins: Optional[PinConfiguration] = None
    skirts: Optional[SkirtConfiguration] = None
    pdms_scale: float = 1.0
    well_positions: Optional[List[Tuple[float, float]]] = None
    dims: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    def _validate(self) -> None:
        if self.pdms_scale <= 0:
            raise ValueError(f"pdms_scale must be positive, got {self.pdms_scale}")
        if len(self.dims) != 3 or self.dims[0] <= 0 or self.dims[1] <= 0 or self.dims[2] < 0:
            raise ValueError("dims must contain positive x/y pitch and a non-negative z offset")
