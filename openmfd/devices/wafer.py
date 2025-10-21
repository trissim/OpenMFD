"""Wafer geometry and mask generation.

This module provides functions for creating wafer geometries with flat edges
and generating wafer masks for photolithography.
"""

from typing import List, Tuple, Optional
import math
import numpy as np
import solid
from solid.utils import union, difference


def compute_wafer_center(
    grid_size: List[int],
    dims: List[float]
) -> Tuple[float, float]:
    """Compute wafer center coordinates.
    
    This is the SINGLE SOURCE OF TRUTH for centering coordinates.
    All elements (devices, wafer, alignment marks, text, outlines) should
    use this function to ensure consistent centering.
    
    Parameters
    ----------
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
        
    Returns
    -------
    tuple of (float, float)
        Center coordinates (x, y).
        
    Examples
    --------
    >>> center = compute_wafer_center([6, 8], [9.0, 9.0, 0])
    >>> # Returns: (27.0, 36.0)
    """
    return (grid_size[0] * dims[0] / 2.0, grid_size[1] * dims[1] / 2.0)


def create_wafer(
    diameter: float,
    flat_length: float,
    thickness: float = 1.0,
    segments: int = 512
) -> solid.OpenSCADObject:
    """Create wafer geometry with flat edge.
    
    Creates a circular wafer with a flat edge (standard wafer geometry).
    The flat edge is used for orientation during fabrication.
    
    Parameters
    ----------
    diameter : float
        Wafer diameter (e.g., 100mm, 150mm).
    flat_length : float
        Length of flat edge.
    thickness : float, default=1.0
        Wafer thickness (for 3D geometry).
    segments : int, default=512
        Number of segments for circle (higher = smoother).
        
    Returns
    -------
    solid.OpenSCADObject
        Wafer geometry with flat edge.
        
    Examples
    --------
    >>> # Create 100mm wafer with 32.5mm flat
    >>> wafer = create_wafer(diameter=100, flat_length=32.5, thickness=0.5)
    """
    # Create circular wafer
    wafer = solid.cylinder(r1=diameter / 2, r2=diameter / 2, h=thickness, segments=segments)()
    
    # Calculate flat edge position using geometry
    # The flat is a chord of the circle
    x_start_flat = flat_length / 2
    y_start_flat = math.sqrt(((diameter / 2) ** 2) - (x_start_flat ** 2))
    height_delete_flat = diameter / 2 - y_start_flat
    
    # Create flat edge by subtracting a cube
    flat_delete = solid.cube([flat_length, height_delete_flat, thickness], center=False)()
    flat_delete = solid.translate([-flat_length / 2, y_start_flat, 0])(flat_delete)
    
    # Subtract flat from wafer
    wafer = difference()(wafer, flat_delete)
    
    # Rotate 90 degrees for standard orientation
    wafer = solid.rotate(90)(wafer)
    
    return wafer


def create_wafer_mask(
    wafer_size: float,
    flat_length: float,
    mask: solid.OpenSCADObject,
    grid_size: List[int],
    dims: List[float],
    wafer_line_thickness: float = 0.1,
    outer_mask_thickness: float = 5.0,
    alignment_offset: Optional[Tuple[float, float]] = None,
    shrinkage_scale: float = 1.0
) -> solid.OpenSCADObject:
    """Add wafer outline to mask, subtracting device features.
    
    Creates a wafer outline mask with:
    - Inner line marking the wafer edge
    - Outer margin for handling
    - Device features subtracted from wafer area
    
    This is used for photolithography mask generation.
    
    Parameters
    ----------
    wafer_size : float
        Wafer diameter.
    flat_length : float
        Flat edge length.
    mask : solid.OpenSCADObject
        Device features to subtract from wafer.
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    wafer_line_thickness : float, default=0.1
        Thickness of wafer edge line.
    outer_mask_thickness : float, default=5.0
        Outer margin thickness.
    alignment_offset : tuple of (float, float), optional
        Offset for alignment marks.
    shrinkage_scale : float, default=1.0
        PDMS shrinkage scaling factor (e.g., 0.8 for 100°C cure).
        
    Returns
    -------
    solid.OpenSCADObject
        Wafer mask with device features subtracted.
        
    Examples
    --------
    >>> # Create wafer mask for 100mm wafer
    >>> mask = create_wafer_mask(
    ...     wafer_size=100, flat_length=32.5, mask=devices,
    ...     grid_size=[6, 8], dims=[9.0, 9.0, 0],
    ...     shrinkage_scale=0.8
    ... )
    """
    def make_wafer_mask_at_size(size: float) -> solid.OpenSCADObject:
        """Helper to create wafer mask at specific size."""
        # Create 3D wafer
        wafer = create_wafer(size, flat_length, thickness=1)
        
        # Project to 2D
        wafer_2d = solid.projection()(wafer)
        
        # Center at wafer center (SINGLE SOURCE OF TRUTH)
        cx, cy = compute_wafer_center(grid_size, dims)
        wafer_2d = solid.translate(np.array([cx, cy]) * shrinkage_scale)(wafer_2d)
        
        # Apply alignment offset if provided
        if alignment_offset is not None:
            wafer_2d = solid.translate(
                np.array([-alignment_offset[0], -alignment_offset[1]]) * shrinkage_scale
            )(wafer_2d)
        
        return wafer_2d
    
    # Create three wafer outlines at different sizes
    inner_wafer_line = make_wafer_mask_at_size(wafer_size - wafer_line_thickness / 2)
    outer_wafer_line = make_wafer_mask_at_size(wafer_size + wafer_line_thickness / 2)
    outer_wafer_mask = make_wafer_mask_at_size(wafer_size + outer_mask_thickness)
    
    # Create wafer edge line (ring between inner and outer)
    # Outer margin is the area outside the wafer line
    outer_margin = difference()(outer_wafer_mask, outer_wafer_line)

    # Combine inner line and outer margin
    wafer_outline = union()(outer_margin, inner_wafer_line)

    # Subtract device features from wafer outline
    # NOTE: Device arrays are already centered by the example script,
    # so we don't need to translate them here. Just subtract as-is.
    return difference()(wafer_outline, mask)


def create_wafer_holder(
    diameter: float,
    flat_length: float,
    thickness: float,
    margin: float,
    notch_length: float = 20,
    notch_height: float = 5,
    oversize: float = 1.01
) -> solid.OpenSCADObject:
    """Create wafer holder (negative space for wafer).
    
    Creates a holder that fits a wafer, with a notch for easy removal.
    
    Parameters
    ----------
    diameter : float
        Wafer diameter.
    flat_length : float
        Flat edge length.
    thickness : float
        Wafer thickness.
    margin : float
        Margin around wafer.
    notch_length : float, default=20
        Length of removal notch.
    notch_height : float, default=5
        Height of removal notch.
    oversize : float, default=1.01
        Oversize factor for clearance.
        
    Returns
    -------
    solid.OpenSCADObject
        Wafer holder geometry.
        
    Examples
    --------
    >>> holder = create_wafer_holder(
    ...     diameter=100, flat_length=32.5, thickness=0.5, margin=2
    ... )
    """
    # Apply oversize
    diameter *= oversize
    flat_length *= oversize
    
    # Create wafer negative
    wafer = create_wafer(diameter, flat_length, thickness)
    
    # Create holder cylinder
    holder = solid.cylinder(
        r1=diameter / 2 + margin,
        r2=diameter / 2 + margin,
        h=thickness,
        segments=512
    )()
    
    # Subtract wafer from holder
    holder = difference()(holder, wafer)
    
    # Add removal notch at flat edge
    x_start_flat = flat_length / 2
    y_start_flat = math.sqrt(((diameter / 2) ** 2) - (x_start_flat ** 2))
    
    notch = solid.cube([notch_length, notch_height, thickness], center=False)()
    notch = solid.translate([-notch_length / 2, y_start_flat, 0])(notch)
    notch = solid.rotate(90)(notch)
    
    return difference()(holder, notch)


def create_wafer_calibration_rings(
    diameter: float,
    thickness: float,
    height: float,
    z_offset: float
) -> solid.OpenSCADObject:
    """Create concentric calibration rings for wafer alignment.
    
    Creates concentric rings at different radii for visual calibration
    and alignment verification.
    
    Parameters
    ----------
    diameter : float
        Wafer diameter.
    thickness : float
        Ring thickness.
    height : float
        Ring height (z-direction).
    z_offset : float
        Z-offset for rings.
        
    Returns
    -------
    solid.OpenSCADObject
        Calibration rings.
        
    Examples
    --------
    >>> rings = create_wafer_calibration_rings(
    ...     diameter=100, thickness=0.5, height=1.0, z_offset=0
    ... )
    """
    circles = []
    
    # Create rings at 80%, 60%, 40%, 20% of wafer radius
    radii = [
        diameter / 2.0 * 0.8,
        diameter / 2.0 * 0.6,
        diameter / 2.0 * 0.4,
        diameter / 2.0 * 0.2
    ]
    
    for radius in radii:
        # Create ring (outer - inner)
        inner = solid.cylinder(
            r1=radius - (thickness / 2.0),
            r2=radius - (thickness / 2.0),
            h=height,
            segments=512
        )()
        outer = solid.cylinder(
            r1=radius + (thickness / 2.0),
            r2=radius + (thickness / 2.0),
            h=height,
            segments=512
        )()
        ring = difference()(outer, inner)
        circles.append(ring)
    
    # Combine all rings
    rings = union()(*circles)
    
    # Apply z-offset
    rings = solid.translate([0, 0, z_offset])(rings)
    
    return rings

