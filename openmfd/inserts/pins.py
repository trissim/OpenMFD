"""Alignment pin generation for well inserts."""

from typing import List, Tuple
import solid
from solid.utils import union


def create_insert_pin(
    position: Tuple[float, float],
    dims: Tuple[float, float],
    height: float,
    offset: float = 0.0,
) -> solid.OpenSCADObject:
    """Create a single alignment pin at specified position.

    Alignment pins are rectangular extrusions that fit into square holes
    in the PDMS wafer to ensure precise alignment between the insert and
    the device.

    Parameters
    ----------
    position : tuple of (float, float)
        Pin position (x, y) in mm.
    dims : tuple of (float, float)
        Pin dimensions (x, y) in mm.
    height : float
        Pin height (mm).
    offset : float, default=0.0
        Offset from position (mm). Applied in both x and y directions.

    Returns
    -------
    solid.OpenSCADObject
        3D pin geometry.

    Examples
    --------
    >>> # Create a pin at well position
    >>> pin = create_insert_pin(
    ...     position=(10.0, 20.0),
    ...     dims=(1.85, 1.85),
    ...     height=2.06,
    ...     offset=-0.5
    ... )

    >>> # Create a pin at origin
    >>> pin = create_insert_pin(
    ...     position=(0, 0),
    ...     dims=(2.0, 2.0),
    ...     height=3.0
    ... )
    """
    # Create rectangular pin base
    pin_base = solid.square([dims[0], dims[1]], center=True)

    # Extrude to height
    pin_3d = solid.linear_extrude(height=height)(pin_base)

    # Apply offset and position
    pin_positioned = solid.translate(
        [position[0] + offset, position[1] + offset, 0]
    )(pin_3d)

    return pin_positioned


def create_pin_array(
    well_positions: List[Tuple[float, float]],
    dims: Tuple[float, float],
    height: float,
    offset: float = 0.0,
) -> solid.OpenSCADObject:
    """Create an array of alignment pins at well positions.

    Creates pins at each well position to match the device layout.
    All pins are combined into a single geometry.

    Parameters
    ----------
    well_positions : list of tuple of (float, float)
        List of well positions (x, y) in mm.
    dims : tuple of (float, float)
        Pin dimensions (x, y) in mm.
    height : float
        Pin height (mm).
    offset : float, default=0.0
        Offset from well centers (mm). Applied in both x and y directions.

    Returns
    -------
    solid.OpenSCADObject
        Union of all pins.

    Examples
    --------
    >>> # Create pins for 2-well device
    >>> well_positions = [(0, -4.5), (0, 4.5)]
    >>> pins = create_pin_array(
    ...     well_positions=well_positions,
    ...     dims=(1.85, 1.85),
    ...     height=2.06,
    ...     offset=-0.5
    ... )

    >>> # Create pins for 4-well device
    >>> well_positions = [(-4.5, -4.5), (4.5, -4.5), (-4.5, 4.5), (4.5, 4.5)]
    >>> pins = create_pin_array(
    ...     well_positions=well_positions,
    ...     dims=(2.0, 2.0),
    ...     height=3.0
    ... )
    """
    pins = []

    for pos in well_positions:
        pin = create_insert_pin(position=pos, dims=dims, height=height, offset=offset)
        pins.append(pin)

    return union()(*pins)


def create_insert_holes(
    well_positions: List[Tuple[float, float]],
    hole_dims: Tuple[float, float],
    offset: float = 0.0,
) -> solid.OpenSCADObject:
    """Create square holes for insert pins in the wafer.

    These holes are subtracted from the top layer (wells/chambers) to allow
    the insert pins to fit through for alignment.

    Parameters
    ----------
    well_positions : list of tuple of (float, float)
        List of well positions (x, y) in mm.
    hole_dims : tuple of (float, float)
        Hole dimensions (x, y) in mm.
    offset : float, default=0.0
        Offset from well centers (mm). Applied in both x and y directions.

    Returns
    -------
    solid.OpenSCADObject
        Union of all holes (2D geometry for subtraction).

    Examples
    --------
    >>> # Create holes for 2-well device
    >>> well_positions = [(0, -4.5), (0, 4.5)]
    >>> holes = create_insert_holes(
    ...     well_positions=well_positions,
    ...     hole_dims=(2.0, 2.0),
    ...     offset=-0.5
    ... )

    >>> # Use in device generation
    >>> from solid.utils import difference
    >>> wells = create_wells(...)  # Your well geometry
    >>> wells_with_holes = difference()(wells, holes)
    """
    holes = []

    for pos in well_positions:
        hole = solid.square([hole_dims[0], hole_dims[1]], center=True)
        hole_positioned = solid.translate([pos[0] + offset, pos[1] + offset])(hole)
        holes.append(hole_positioned)

    return union()(*holes)

