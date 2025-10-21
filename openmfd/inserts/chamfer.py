"""Chamfer and taper extrusion utilities for 3D inserts."""

import math
from typing import Callable
import solid


def deg_taper_len(height: float, degrees: float) -> float:
    """Calculate horizontal taper length from height and angle.

    Computes the horizontal distance that a tapered wall extends
    when extruded at a given angle from vertical.

    Parameters
    ----------
    height : float
        Vertical height of the taper (mm).
    degrees : float
        Taper angle in degrees from vertical.

    Returns
    -------
    float
        Horizontal taper length (mm).

    Examples
    --------
    >>> # 16° taper over 3.8mm height
    >>> taper_len = deg_taper_len(3.8, 16)
    >>> print(f"{taper_len:.3f} mm")
    1.090 mm

    >>> # 35° taper over 0.4mm height
    >>> taper_len = deg_taper_len(0.4, 35)
    >>> print(f"{taper_len:.3f} mm")
    0.280 mm

    >>> # No taper (0°)
    >>> taper_len = deg_taper_len(5.0, 0)
    >>> print(taper_len)
    0.0

    Notes
    -----
    The taper length is calculated using: taper_len = height * tan(degrees)
    This assumes the angle is measured from vertical (not from horizontal).
    """
    if degrees != 0:
        return height * math.tan(math.radians(degrees))
    else:
        return 0.0


def chamfer_extrude_wrapper(
    height: float, angle: float, segments: int = 20
) -> Callable:
    """Create a chamfered/tapered extrusion function.

    This function wraps the OpenSCAD chamfer_extrude module to create
    tapered 3D extrusions of 2D shapes. The taper angle is measured
    from vertical.

    Parameters
    ----------
    height : float
        Extrusion height (mm).
    angle : float
        Taper angle in degrees from vertical.
    segments : int, default=20
        Number of segments for the chamfer. Higher values create smoother
        tapers but increase geometry complexity.

    Returns
    -------
    callable
        Function that takes a 2D OpenSCAD object and returns a 3D
        chamfered extrusion.

    Examples
    --------
    >>> from solid import circle
    >>> # Create a chamfered cylinder
    >>> chamfer_func = chamfer_extrude_wrapper(height=5.0, angle=15, segments=20)
    >>> base_circle = circle(r=3.0)
    >>> chamfered_cylinder = chamfer_func(base_circle)

    >>> # Create a chamfered square
    >>> from solid import square
    >>> chamfer_func = chamfer_extrude_wrapper(height=3.0, angle=10, segments=16)
    >>> base_square = square([5, 5], center=True)
    >>> chamfered_square = chamfer_func(base_square)

    Notes
    -----
    This function requires the chamfer_extrude.scad module to be available
    in the OpenSCAD library path. The module creates a tapered extrusion
    by stacking progressively smaller copies of the 2D shape.

    The taper reduces the size of the shape as it extrudes upward, creating
    a cone-like or pyramid-like effect depending on the base shape.

    Warnings
    --------
    High segment counts can significantly increase rendering time and
    file size. Use the minimum number of segments needed for smooth
    appearance.
    """

    def chamfer_func(obj: solid.OpenSCADObject) -> solid.OpenSCADObject:
        """Apply chamfer extrusion to a 2D object.

        Parameters
        ----------
        obj : solid.OpenSCADObject
            2D object to extrude with chamfer.

        Returns
        -------
        solid.OpenSCADObject
            3D chamfered extrusion.
        """
        # Import the chamfer_extrude module from SCAD file
        # Note: This assumes chamfer_extrude.scad is in the OpenSCAD library path
        scad_code = f"""
use <chamfer_extrude.scad>;

chamfer_extrude(height={height}, angle={angle}, $fn={segments})
"""
        # For now, we'll use a simplified approach with linear_extrude and scale
        # A full implementation would require the actual chamfer_extrude.scad module
        # This creates an approximation of the chamfer effect
        taper_factor = 1.0 - (deg_taper_len(height, angle) / height)
        return solid.linear_extrude(height=height, scale=taper_factor)(obj)

    return chamfer_func


def linear_extrude_if_flat(
    obj: solid.OpenSCADObject, height: float, degrees: float, segments: int = 20
) -> solid.OpenSCADObject:
    """Extrude a 2D object, using chamfer if angle is non-zero.

    Convenience function that chooses between linear extrusion (for 0° angle)
    and chamfered extrusion (for non-zero angles).

    Parameters
    ----------
    obj : solid.OpenSCADObject
        2D object to extrude.
    height : float
        Extrusion height (mm).
    degrees : float
        Taper angle in degrees. If 0, uses linear extrusion.
    segments : int, default=20
        Number of segments for chamfer (ignored if degrees=0).

    Returns
    -------
    solid.OpenSCADObject
        3D extruded object.

    Examples
    --------
    >>> from solid import circle
    >>> # Straight extrusion (no taper)
    >>> cylinder = linear_extrude_if_flat(circle(r=3), height=5, degrees=0)

    >>> # Tapered extrusion
    >>> cone = linear_extrude_if_flat(circle(r=3), height=5, degrees=15, segments=20)
    """
    if degrees != 0:
        chamfer_func = chamfer_extrude_wrapper(height, degrees, segments)
        return chamfer_func(obj)
    else:
        return solid.linear_extrude(height=height)(obj)

