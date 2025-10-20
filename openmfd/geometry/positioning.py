"""Positioning utilities for placing geometric elements.

This module provides functions for calculating positions of wells, channels,
and other geometric elements in various patterns (grids, corners, etc.).
"""

from typing import List, Tuple, Optional
import numpy as np

from .types import Position2D


def wells_pos_from_center_4(offset: float) -> List[Position2D]:
    """Generate positions for 4 wells in corners around center.
    
    Parameters
    ----------
    offset : float
        Distance from center to each well.
        
    Returns
    -------
    list of (float, float)
        List of 4 positions: top-left, top-right, bottom-left, bottom-right.
        
    Examples
    --------
    >>> positions = wells_pos_from_center_4(5.0)
    >>> # Returns: [[-5, 5], [5, 5], [-5, -5], [5, -5]]
    """
    return [
        [-offset, offset],   # top-left
        [offset, offset],    # top-right
        [-offset, -offset],  # bottom-left
        [offset, -offset]    # bottom-right
    ]


def wells_pos_from_center_2(offset: float) -> List[Position2D]:
    """Generate positions for 2 wells vertically aligned around center.
    
    Parameters
    ----------
    offset : float
        Distance from center to each well.
        
    Returns
    -------
    list of (float, float)
        List of 2 positions: right, left.
        
    Examples
    --------
    >>> positions = wells_pos_from_center_2(5.0)
    >>> # Returns: [[5, 0], [-5, 0]]
    """
    return [
        [offset, 0],   # right
        [-offset, 0]   # left
    ]


def corners_from_x_y(x: float, y: float) -> List[Position2D]:
    """Generate corner positions from x and y dimensions.
    
    Parameters
    ----------
    x : float
        Half-width (distance from center to edge in x).
    y : float
        Half-height (distance from center to edge in y).
        
    Returns
    -------
    list of (float, float)
        List of 4 corner positions.
        
    Examples
    --------
    >>> corners = corners_from_x_y(10.0, 8.0)
    >>> # Returns: [[10, 8], [-10, 8], [-10, -8], [10, -8]]
    """
    return [
        [x, y],      # top-right
        [-x, y],     # top-left
        [-x, -y],    # bottom-left
        [x, -y]      # bottom-right
    ]


def grid_positions(
    rows: int,
    cols: int,
    spacing_x: float,
    spacing_y: Optional[float] = None,
    center: bool = True
) -> List[Position2D]:
    """Generate positions for a regular grid of elements.
    
    Parameters
    ----------
    rows : int
        Number of rows in grid.
    cols : int
        Number of columns in grid.
    spacing_x : float
        Spacing between columns.
    spacing_y : float, optional
        Spacing between rows. If None, uses spacing_x.
    center : bool, default=True
        If True, center the grid at origin. If False, start at origin.
        
    Returns
    -------
    list of (float, float)
        List of grid positions.
        
    Raises
    ------
    ValueError
        If rows or cols are not positive.
        
    Examples
    --------
    >>> # Create 3x4 grid with 9mm spacing
    >>> positions = grid_positions(3, 4, 9.0)
    
    >>> # Create 2x3 grid with different x/y spacing
    >>> positions = grid_positions(2, 3, 9.0, 14.0)
    """
    if rows <= 0:
        raise ValueError(f"rows must be positive, got {rows}")
    if cols <= 0:
        raise ValueError(f"cols must be positive, got {cols}")
    
    if spacing_y is None:
        spacing_y = spacing_x
    
    positions = []
    for row in range(rows):
        for col in range(cols):
            x = col * spacing_x
            y = row * spacing_y
            positions.append([x, y])
    
    if center:
        # Center the grid at origin
        center_x = (cols - 1) * spacing_x / 2.0
        center_y = (rows - 1) * spacing_y / 2.0
        positions = [[x - center_x, y - center_y] for x, y in positions]
    
    return positions


def circular_positions(
    count: int,
    radius: float,
    start_angle: float = 0.0
) -> List[Position2D]:
    """Generate positions arranged in a circle.
    
    Parameters
    ----------
    count : int
        Number of positions.
    radius : float
        Radius of circle.
    start_angle : float, default=0.0
        Starting angle in degrees.
        
    Returns
    -------
    list of (float, float)
        List of positions arranged in circle.
        
    Raises
    ------
    ValueError
        If count is not positive or radius is not positive.
        
    Examples
    --------
    >>> # Create 6 positions in circle of radius 10mm
    >>> positions = circular_positions(6, 10.0)
    
    >>> # Start at 45 degrees
    >>> positions = circular_positions(6, 10.0, start_angle=45.0)
    """
    if count <= 0:
        raise ValueError(f"count must be positive, got {count}")
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}")
    
    positions = []
    angle_step = 360.0 / count
    
    for i in range(count):
        angle_deg = start_angle + i * angle_step
        angle_rad = np.radians(angle_deg)
        x = radius * np.cos(angle_rad)
        y = radius * np.sin(angle_rad)
        positions.append([float(x), float(y)])
    
    return positions


def custom_positions(positions: List[Tuple[float, float]]) -> List[Position2D]:
    """Validate and return custom positions.
    
    This is mainly for validation and type conversion.
    
    Parameters
    ----------
    positions : list of (float, float)
        Custom positions.
        
    Returns
    -------
    list of (float, float)
        Validated positions.
        
    Raises
    ------
    ValueError
        If positions are invalid.
        
    Examples
    --------
    >>> positions = custom_positions([[0, 0], [5, 5], [-5, 5]])
    """
    if not positions:
        raise ValueError("positions cannot be empty")
    
    validated = []
    for i, pos in enumerate(positions):
        if not isinstance(pos, (list, tuple)) or len(pos) != 2:
            raise ValueError(f"Position {i} must be a 2-element tuple/list, got {pos}")
        try:
            validated.append([float(pos[0]), float(pos[1])])
        except (TypeError, ValueError) as e:
            raise ValueError(f"Position {i} contains invalid values: {e}")
    
    return validated

