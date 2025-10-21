"""Sealing skirt generation for well inserts."""

import solid
from solid.utils import union, difference


def create_skirt_layer(
    insert_geometry: solid.OpenSCADObject,
    thickness: float,
    height: float,
    empty_space: float = 0.0,
) -> solid.OpenSCADObject:
    """Create a single skirt layer around insert geometry.

    A skirt is a ring-shaped frame that extends around the insert to provide
    better adhesion and sealing to the PDMS device.

    Parameters
    ----------
    insert_geometry : solid.OpenSCADObject
        2D projection of the insert geometry to create skirt around.
    thickness : float
        Skirt thickness (mm).
    height : float
        Skirt height (mm).
    empty_space : float, default=0.0
        Empty space inside the skirt (mm). Creates a gap between the
        insert and the skirt.

    Returns
    -------
    solid.OpenSCADObject
        3D skirt geometry.

    Examples
    --------
    >>> from solid import circle, projection
    >>> # Create insert geometry (2D)
    >>> insert_2d = circle(r=5.0)
    >>>
    >>> # Create skirt layer
    >>> skirt = create_skirt_layer(
    ...     insert_geometry=insert_2d,
    ...     thickness=0.75,
    ...     height=0.66,
    ...     empty_space=0.3
    ... )

    Notes
    -----
    The skirt is created by:
    1. Offsetting the insert geometry outward by (thickness + empty_space)
    2. Offsetting the insert geometry outward by empty_space
    3. Subtracting the inner offset from the outer offset
    4. Extruding the resulting ring to the specified height
    """
    # Create outer boundary (insert + empty_space + thickness)
    outer_offset = solid.offset(r=thickness + empty_space)(insert_geometry)

    # Create inner boundary (insert + empty_space)
    if empty_space > 0:
        inner_offset = solid.offset(r=empty_space)(insert_geometry)
    else:
        inner_offset = insert_geometry

    # Create ring by subtracting inner from outer
    skirt_ring = difference()(outer_offset, inner_offset)

    # Extrude to height
    skirt_3d = solid.linear_extrude(height=height)(skirt_ring)

    return skirt_3d


def create_dual_skirt(
    insert_geometry: solid.OpenSCADObject,
    thickness1: float,
    height1: float,
    empty1: float,
    thickness2: float,
    height2: float,
) -> solid.OpenSCADObject:
    """Create a two-layer skirt system for better adhesion.

    A dual skirt provides improved sealing and adhesion by using two layers:
    - Layer 1 (upper): Thicker, taller, with empty space for flexibility
    - Layer 2 (lower): Thinner, shorter, base layer for initial contact

    Parameters
    ----------
    insert_geometry : solid.OpenSCADObject
        2D projection of the insert geometry to create skirts around.
    thickness1 : float
        First (upper) skirt thickness (mm).
    height1 : float
        First skirt height (mm).
    empty1 : float
        Empty space inside first skirt (mm).
    thickness2 : float
        Second (lower) skirt thickness (mm).
    height2 : float
        Second skirt height (mm).

    Returns
    -------
    solid.OpenSCADObject
        Combined dual skirt geometry.

    Examples
    --------
    >>> from solid import circle
    >>> # Create insert geometry (2D)
    >>> insert_2d = circle(r=5.0)
    >>>
    >>> # Create dual skirt with standard parameters
    >>> skirts = create_dual_skirt(
    ...     insert_geometry=insert_2d,
    ...     thickness1=0.75,
    ...     height1=0.66,
    ...     empty1=0.3,
    ...     thickness2=0.8,
    ...     height2=0.04
    ... )

    Notes
    -----
    The skirts are stacked vertically:
    - Layer 2 (base) is at z=0
    - Layer 1 (upper) is at z=height2

    This creates a stepped profile that provides both initial contact
    (layer 2) and flexible sealing (layer 1 with empty space).
    """
    # Create first (upper) skirt layer
    skirt1 = create_skirt_layer(
        insert_geometry=insert_geometry,
        thickness=thickness1,
        height=height1,
        empty_space=empty1,
    )

    # Create second (lower) skirt layer
    skirt2 = create_skirt_layer(
        insert_geometry=insert_geometry,
        thickness=thickness2,
        height=height2,
        empty_space=0.0,  # No empty space in base layer
    )

    # Position upper skirt on top of lower skirt
    skirt1_positioned = solid.translate([0, 0, height2])(skirt1)

    # Combine both layers
    combined_skirts = union()(skirt2, skirt1_positioned)

    return combined_skirts


def create_skirt_from_projection(
    insert_3d: solid.OpenSCADObject,
    thickness1: float,
    height1: float,
    empty1: float,
    thickness2: float,
    height2: float,
) -> solid.OpenSCADObject:
    """Create dual skirt from 3D insert geometry.

    Convenience function that projects the 3D insert to 2D and creates
    a dual skirt system.

    Parameters
    ----------
    insert_3d : solid.OpenSCADObject
        3D insert geometry to create skirts around.
    thickness1 : float
        First (upper) skirt thickness (mm).
    height1 : float
        First skirt height (mm).
    empty1 : float
        Empty space inside first skirt (mm).
    thickness2 : float
        Second (lower) skirt thickness (mm).
    height2 : float
        Second skirt height (mm).

    Returns
    -------
    solid.OpenSCADObject
        Combined dual skirt geometry.

    Examples
    --------
    >>> # Create 3D insert
    >>> insert_3d = create_well_insert(...)
    >>>
    >>> # Create skirts from 3D geometry
    >>> skirts = create_skirt_from_projection(
    ...     insert_3d=insert_3d,
    ...     thickness1=0.75,
    ...     height1=0.66,
    ...     empty1=0.3,
    ...     thickness2=0.8,
    ...     height2=0.04
    ... )
    """
    # Project 3D insert to 2D
    insert_2d = solid.projection()(insert_3d)

    # Create dual skirt
    return create_dual_skirt(
        insert_geometry=insert_2d,
        thickness1=thickness1,
        height1=height1,
        empty1=empty1,
        thickness2=thickness2,
        height2=height2,
    )

