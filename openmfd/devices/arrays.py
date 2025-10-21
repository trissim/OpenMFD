"""Array generation for creating grids of device units.

This module provides functions for creating NxM arrays of device units
with various alignment and positioning options.
"""

from typing import List, Optional, Tuple
import solid
from solid.utils import union

from .config import ArrayConfiguration, CasingConfiguration
from .wafer import compute_wafer_center


def create_device_array(
    unit: solid.OpenSCADObject,
    dims: List[float],
    grid_size: List[int],
    dxf: bool = False,
    alignment: Optional[str] = None,
    units_from_center: Optional[Tuple[float, float]] = None,
    alignment_offset: Optional[Tuple[float, float]] = None,
    alignment_mark_size: float = 1.0
) -> solid.OpenSCADObject:
    """Create an array of device units in a grid pattern.

    Creates a grid of device units with optional alignment marks.
    Devices are positioned starting at [0, 0] to match the wafer
    centering coordinate system.

    Parameters
    ----------
    unit : solid.OpenSCADObject
        Single device unit to replicate.
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
    dxf : bool, default=False
        If True, create 2D array for DXF export.
    alignment : str, optional
        Alignment mode ("full", "hollow", or None).
        If specified, adds alignment marks.
    units_from_center : tuple of (float, float), optional
        Distance from center for alignment marks (in units).
    alignment_offset : tuple of (float, float), optional
        Offset to apply before adding alignment marks.
    alignment_mark_size : float, default=1.0
        Size of alignment marks.

    Returns
    -------
    solid.OpenSCADObject
        Array of units with optional alignment marks.

    Examples
    --------
    >>> # Create 8x12 array of units
    >>> array = create_device_array(unit, [9.0, 9.0, 0], [8, 12], dxf=True)

    >>> # Create 6x8 array with full alignment marks
    >>> array = create_device_array(
    ...     unit, [9.0, 9.0, 0], [6, 8],
    ...     dxf=True, alignment='full', units_from_center=(3, 4),
    ...     alignment_mark_size=1.0
    ... )

    >>> # Create array with hollow marks (for top layer)
    >>> array = create_device_array(
    ...     unit, [9.0, 9.0, 0], [6, 8],
    ...     dxf=True, alignment='hollow', units_from_center=(3, 4),
    ...     alignment_mark_size=1.0
    ... )
    """
    units = []
    rows, cols = grid_size[0], grid_size[1]

    # Create grid of units starting at [0, 0]
    # Each device is positioned so its BOTTOM-LEFT CORNER is at the grid position
    # (not the center), so we offset by half the casing dimensions
    offset_x = dims[0] / 2.0
    offset_y = dims[1] / 2.0

    for col in range(cols):
        for row in range(rows):
            if dxf:
                positioned_unit = solid.translate([row * dims[0] + offset_x, col * dims[1] + offset_y])(unit)
            else:
                positioned_unit = solid.translate([row * dims[0] + offset_x, col * dims[1] + offset_y, dims[2] / 2.0])(unit)
            units.append(positioned_unit)

    array = union()(*units)

    # Add alignment marks if requested
    if alignment is not None and dxf:
        # Apply alignment offset before adding marks
        if alignment_offset is not None:
            array = solid.translate([alignment_offset[0], alignment_offset[1]])(array)

        # Add alignment marks
        from .alignment import create_alignment_marks
        array = create_alignment_marks(
            array, dims, grid_size, alignment,
            units_from_center, alignment_mark_size
        )

        # Reverse alignment offset after adding marks
        if alignment_offset is not None:
            array = solid.translate([-alignment_offset[0], -alignment_offset[1]])(array)

    return array


def create_device_array_from_config(
    unit: solid.OpenSCADObject,
    casing: CasingConfiguration,
    array_config: ArrayConfiguration,
    dxf: bool = False
) -> solid.OpenSCADObject:
    """Create device array from configuration objects.
    
    Parameters
    ----------
    unit : solid.OpenSCADObject
        Single device unit to replicate.
    casing : CasingConfiguration
        Casing configuration for unit dimensions.
    array_config : ArrayConfiguration
        Array configuration.
    dxf : bool, default=False
        If True, create 2D array for DXF export.
        
    Returns
    -------
    solid.OpenSCADObject
        Array of units.
        
    Examples
    --------
    >>> from openmfd.devices.config import CasingConfiguration, ArrayConfiguration
    >>> 
    >>> casing = CasingConfiguration(x=9.0, y=9.0)
    >>> array_config = ArrayConfiguration(rows=8, columns=12)
    >>> array = create_device_array_from_config(unit, casing, array_config, dxf=True)
    """
    dims = casing.as_list()
    grid_size = array_config.grid_size()
    
    return create_device_array(
        unit=unit,
        dims=dims,
        grid_size=grid_size,
        dxf=dxf,
        alignment=array_config.alignment,
        units_from_center=array_config.units_from_center
    )


def compute_array_dimensions(
    unit_dims: List[float],
    grid_size: List[int]
) -> Tuple[float, float, float]:
    """Compute total dimensions of device array.
    
    Parameters
    ----------
    unit_dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
        
    Returns
    -------
    tuple of (float, float, float)
        Total array dimensions (width, length, height).
        
    Examples
    --------
    >>> dims = compute_array_dimensions([9.0, 9.0, 0.3], [8, 12])
    >>> # Returns: (72.0, 108.0, 0.3)
    """
    rows, cols = grid_size[0], grid_size[1]
    width = rows * unit_dims[0]
    length = cols * unit_dims[1]
    height = unit_dims[2]
    return (width, length, height)


def center_array(
    array: solid.OpenSCADObject,
    unit_dims: List[float],
    grid_size: List[int]
) -> solid.OpenSCADObject:
    """Center an array at the origin.
    
    Parameters
    ----------
    array : solid.OpenSCADObject
        Array to center.
    unit_dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
        
    Returns
    -------
    solid.OpenSCADObject
        Centered array.
        
    Examples
    --------
    >>> centered = center_array(array, [9.0, 9.0, 0], [8, 12])
    """
    width, length, _ = compute_array_dimensions(unit_dims, grid_size)
    return solid.translate([-width / 2, -length / 2, 0])(array)


def create_partial_array(
    unit: solid.OpenSCADObject,
    dims: List[float],
    grid_size: List[int],
    positions: List[Tuple[int, int]],
    dxf: bool = False
) -> solid.OpenSCADObject:
    """Create a partial array with units at specific grid positions.
    
    Parameters
    ----------
    unit : solid.OpenSCADObject
        Single device unit to replicate.
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns] (defines grid spacing).
    positions : list of (int, int)
        List of (row, col) positions to place units.
    dxf : bool, default=False
        If True, create 2D array for DXF export.
        
    Returns
    -------
    solid.OpenSCADObject
        Partial array of units.
        
    Examples
    --------
    >>> # Create units only at corners
    >>> positions = [(0, 0), (0, 11), (7, 0), (7, 11)]
    >>> array = create_partial_array(unit, [9.0, 9.0, 0], [8, 12], positions, dxf=True)
    """
    units = []
    
    for row, col in positions:
        if dxf:
            positioned_unit = solid.translate([row * dims[0], col * dims[1]])(unit)
        else:
            positioned_unit = solid.translate([row * dims[0], col * dims[1], dims[2] / 2.0])(unit)
        units.append(positioned_unit)
    
    return union()(*units)


def create_hollow_array(
    unit: solid.OpenSCADObject,
    dims: List[float],
    grid_size: List[int],
    dxf: bool = False
) -> solid.OpenSCADObject:
    """Create a hollow array (perimeter only, no center units).
    
    Parameters
    ----------
    unit : solid.OpenSCADObject
        Single device unit to replicate.
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
    dxf : bool, default=False
        If True, create 2D array for DXF export.
        
    Returns
    -------
    solid.OpenSCADObject
        Hollow array of units.
        
    Examples
    --------
    >>> # Create hollow 8x12 array
    >>> array = create_hollow_array(unit, [9.0, 9.0, 0], [8, 12], dxf=True)
    """
    rows, cols = grid_size[0], grid_size[1]
    positions = []
    
    # Add perimeter positions
    for row in range(rows):
        for col in range(cols):
            # Include if on perimeter
            if row == 0 or row == rows - 1 or col == 0 or col == cols - 1:
                positions.append((row, col))
    
    return create_partial_array(unit, dims, grid_size, positions, dxf)

