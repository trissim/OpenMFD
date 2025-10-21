"""Configuration dataclasses for 3D printed insert generation."""

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class TaperConfiguration:
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


@dataclass
class InsertConfiguration:
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


@dataclass
class PinConfiguration:
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


@dataclass
class SkirtConfiguration:
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

