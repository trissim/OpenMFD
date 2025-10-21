"""Sealing skirt generation for well inserts."""

import solid
from solid.utils import union, difference


def create_skirt_layer(
    insert_geometry: solid.OpenSCADObject,
    thickness: float,
    height: float,
) -> solid.OpenSCADObject:
    """Create a single skirt layer around insert geometry.

    A skirt is a ring-shaped frame that extends around the insert to provide
    better adhesion and sealing to the PDMS device.

    Parameters
    ----------
    insert_geometry : solid.OpenSCADObject
        2D projection of the insert geometry to create skirt around.
    thickness : float
        Skirt thickness (mm). Negative value shrinks inward from geometry.
    height : float
        Skirt height (mm).

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
    ...     thickness=-0.75,
    ...     height=0.66
    ... )

    Notes
    -----
    The skirt is created by:
    1. Using the insert geometry as outer boundary
    2. Offsetting inward by thickness (negative delta) for inner boundary
    3. Subtracting the inner offset from the outer
    4. Extruding the resulting ring to the specified height
    """
    # Create outer boundary (original insert geometry)
    outer = insert_geometry

    # Create inner boundary (shrink inward by thickness)
    inner = solid.offset(delta=thickness)(insert_geometry)

    # Create ring by subtracting inner from outer
    skirt_ring = difference()(outer, inner)

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
    pin_height: float,
) -> solid.OpenSCADObject:
    """Create a two-layer skirt system for better adhesion.

    A dual skirt provides improved sealing and adhesion by using two layers:
    - Layer 1 (upper): Ring with empty space fill at top for flexibility
    - Layer 2 (lower): Base ring for initial contact

    This matches the legacy implementation from make_device.py.

    Parameters
    ----------
    insert_geometry : solid.OpenSCADObject
        2D projection of the insert geometry to create skirts around.
    thickness1 : float
        First (upper) skirt thickness (mm). Negative value shrinks inward.
    height1 : float
        First skirt height (mm).
    empty1 : float
        Empty space fill height at top of skirt1 (mm).
    thickness2 : float
        Second (lower) skirt thickness (mm). Negative value shrinks inward.
    height2 : float
        Second skirt height (mm).
    pin_height : float
        Height of alignment pins (mm). Used for positioning.

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
    ...     thickness1=-0.75,
    ...     height1=0.66,
    ...     empty1=0.3,
    ...     thickness2=-0.8,
    ...     height2=0.04,
    ...     pin_height=0.06
    ... )

    Notes
    -----
    Legacy implementation (from make_device.py):
    - Skirt 1 ring: at z=pin_height, height=height1
    - Skirt 1 empty fill: at z=pin_height+(height1-empty1), height=empty1
    - Skirt 2 ring: at z=pin_height-height2, height=height2
    - Final translate: z=height2

    This creates a complex stepped profile for optimal sealing.
    """
    # Create first (upper) skirt ring
    skirt1_ring = create_skirt_layer(
        insert_geometry=insert_geometry,
        thickness=thickness1,
        height=height1,
    )
    skirt1_ring = solid.translate([0, 0, pin_height])(skirt1_ring)

    # Create empty space fill (solid fill at top of skirt1)
    skirt1_empty = solid.linear_extrude(height=empty1)(insert_geometry)
    skirt1_empty = solid.translate([0, 0, pin_height + (height1 - empty1)])(
        skirt1_empty
    )

    # Combine skirt1 ring and empty fill
    skirt1 = union()(skirt1_ring, skirt1_empty)

    # Create second (lower) skirt ring
    skirt2 = create_skirt_layer(
        insert_geometry=insert_geometry,
        thickness=thickness2,
        height=height2,
    )
    skirt2 = solid.translate([0, 0, pin_height - height2])(skirt2)

    # Combine both skirts
    combined_skirts = union()(skirt1, skirt2)

    # Final translation (legacy pattern)
    combined_skirts = solid.translate([0, 0, height2])(combined_skirts)

    return combined_skirts


def create_skirt_from_projection(
    insert_3d: solid.OpenSCADObject,
    thickness1: float,
    height1: float,
    empty1: float,
    thickness2: float,
    height2: float,
    pin_height: float,
) -> solid.OpenSCADObject:
    """Create dual skirt from 3D insert geometry.

    Convenience function that projects the 3D insert to 2D and creates
    a dual skirt system.

    Parameters
    ----------
    insert_3d : solid.OpenSCADObject
        3D insert geometry to create skirts around.
    thickness1 : float
        First (upper) skirt thickness (mm). Negative value shrinks inward.
    height1 : float
        First skirt height (mm).
    empty1 : float
        Empty space fill height at top of skirt1 (mm).
    thickness2 : float
        Second (lower) skirt thickness (mm). Negative value shrinks inward.
    height2 : float
        Second skirt height (mm).
    pin_height : float
        Height of alignment pins (mm). Used for positioning.

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
    ...     thickness1=-0.75,
    ...     height1=0.66,
    ...     empty1=0.3,
    ...     thickness2=-0.8,
    ...     height2=0.04,
    ...     pin_height=0.06
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
        pin_height=pin_height,
    )

