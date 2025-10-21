"""Text annotation for device labeling and documentation.

This module provides functions for adding text annotations to devices,
including cure temperatures, device names, and other metadata.
"""

from typing import List, Tuple, Optional
import solid
from solid.utils import union

from .wafer import compute_wafer_center


def create_centered_text(
    text: str,
    grid_size: List[int],
    dims: List[float],
    size: float = 2.0,
    offset_y: float = 0.0,
    alignment_offset: Optional[Tuple[float, float]] = None,
    halign: str = "center",
    valign: str = "center"
) -> solid.OpenSCADObject:
    """Create text centered on wafer.
    
    Creates text annotation positioned at the wafer center with optional
    vertical offset. Uses the centralized wafer centering system.
    
    Parameters
    ----------
    text : str
        Text to render.
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    size : float, default=2.0
        Text size.
    offset_y : float, default=0.0
        Vertical offset from center (positive = up, negative = down).
    alignment_offset : tuple of (float, float), optional
        Alignment offset to apply.
    halign : str, default="center"
        Horizontal alignment ("left", "center", "right").
    valign : str, default="center"
        Vertical alignment ("top", "center", "bottom", "baseline").
        
    Returns
    -------
    solid.OpenSCADObject
        Centered text geometry.
        
    Examples
    --------
    >>> # Create cure temperature text
    >>> text = create_centered_text(
    ...     "Cure at 100°C", grid_size=[6, 8], dims=[9.0, 9.0, 0],
    ...     size=2.0, offset_y=-40
    ... )
    """
    # Create text
    text_obj = solid.text(text, halign=halign, valign=valign, size=size)
    
    # Get wafer center (SINGLE SOURCE OF TRUTH)
    cx, cy = compute_wafer_center(grid_size, dims)
    
    # Apply alignment offset if provided
    if alignment_offset is not None:
        text_obj = solid.translate([alignment_offset[0], alignment_offset[1]])(text_obj)
    
    # Center at wafer center
    text_obj = solid.translate([cx, cy])(text_obj)
    
    # Apply vertical offset
    text_obj = solid.translate([0, offset_y])(text_obj)
    
    return text_obj


def create_multiline_text(
    lines: List[str],
    grid_size: List[int],
    dims: List[float],
    size: float = 2.0,
    line_spacing: float = None,
    offset_y: float = 0.0,
    alignment_offset: Optional[Tuple[float, float]] = None
) -> solid.OpenSCADObject:
    """Create multiple lines of centered text.
    
    Creates multiple lines of text, each centered and vertically spaced.
    
    Parameters
    ----------
    lines : list of str
        Lines of text to render.
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    size : float, default=2.0
        Text size.
    line_spacing : float, optional
        Spacing between lines. If None, uses dims[1] / 2.
    offset_y : float, default=0.0
        Vertical offset for first line.
    alignment_offset : tuple of (float, float), optional
        Alignment offset to apply.
        
    Returns
    -------
    solid.OpenSCADObject
        Multiline text geometry.
        
    Examples
    --------
    >>> # Create multi-line instructions
    >>> text = create_multiline_text(
    ...     ["Cure at 100°C", "Use 60mL Sylgard 184 in 1:10 ratio"],
    ...     grid_size=[6, 8], dims=[9.0, 9.0, 0],
    ...     size=2.0, offset_y=-40
    ... )
    """
    if line_spacing is None:
        line_spacing = dims[1] / 2
    
    text_objects = []
    
    for i, line in enumerate(lines):
        # Calculate vertical offset for this line
        line_offset = offset_y - i * line_spacing
        
        # Create text for this line
        text_obj = create_centered_text(
            line, grid_size, dims, size, line_offset, alignment_offset
        )
        text_objects.append(text_obj)
    
    return union()(*text_objects)


def create_cure_temperature_text(
    cure_temp: int,
    grid_size: List[int],
    dims: List[float],
    size: float = 2.0,
    include_instructions: bool = True,
    alignment_offset: Optional[Tuple[float, float]] = None
) -> solid.OpenSCADObject:
    """Create cure temperature annotation text.
    
    Creates standardized text for PDMS curing temperature with optional
    mixing instructions.
    
    Parameters
    ----------
    cure_temp : int
        Cure temperature in Celsius.
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    size : float, default=2.0
        Text size.
    include_instructions : bool, default=True
        Whether to include mixing instructions.
    alignment_offset : tuple of (float, float), optional
        Alignment offset to apply.
        
    Returns
    -------
    solid.OpenSCADObject
        Cure temperature text.
        
    Examples
    --------
    >>> # Create cure text for 100°C
    >>> text = create_cure_temperature_text(
    ...     cure_temp=100, grid_size=[6, 8], dims=[9.0, 9.0, 0]
    ... )
    """
    # Create cure temperature text
    cure_text = f"Cure at {cure_temp}°C"
    
    # Calculate offset to position below array
    offset_y = -(grid_size[1] + 3) * dims[1] / 2
    
    if include_instructions:
        # Create multi-line text with instructions
        lines = [
            cure_text,
            "Use 60mL of Sylgard 184 in 1:10 ratio"
        ]
        return create_multiline_text(
            lines, grid_size, dims, size, 
            line_spacing=dims[1] / 2,
            offset_y=offset_y,
            alignment_offset=alignment_offset
        )
    else:
        # Create single line text
        return create_centered_text(
            cure_text, grid_size, dims, size,
            offset_y=offset_y,
            alignment_offset=alignment_offset
        )


def create_device_label(
    device_name: str,
    version: str,
    grid_size: List[int],
    dims: List[float],
    size: float = 1.5,
    position: str = "top",
    alignment_offset: Optional[Tuple[float, float]] = None
) -> solid.OpenSCADObject:
    """Create device name and version label.
    
    Creates a label with device name and version number.
    
    Parameters
    ----------
    device_name : str
        Device name.
    version : str
        Version string (e.g., "v27").
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    size : float, default=1.5
        Text size.
    position : str, default="top"
        Position of label ("top", "bottom", "left", "right").
    alignment_offset : tuple of (float, float), optional
        Alignment offset to apply.
        
    Returns
    -------
    solid.OpenSCADObject
        Device label text.
        
    Examples
    --------
    >>> label = create_device_label(
    ...     "2_compartment_96_well", "v27",
    ...     grid_size=[6, 8], dims=[9.0, 9.0, 0]
    ... )
    """
    label_text = f"{device_name} {version}"
    
    # Calculate offset based on position
    if position == "top":
        offset_y = (grid_size[1] + 2) * dims[1] / 2
    elif position == "bottom":
        offset_y = -(grid_size[1] + 2) * dims[1] / 2
    elif position == "left":
        offset_y = 0
        # TODO: Rotate text for left/right positions
    elif position == "right":
        offset_y = 0
    else:
        offset_y = 0
    
    return create_centered_text(
        label_text, grid_size, dims, size,
        offset_y=offset_y,
        alignment_offset=alignment_offset
    )


def create_date_stamp(
    date_str: str,
    grid_size: List[int],
    dims: List[float],
    size: float = 1.0,
    alignment_offset: Optional[Tuple[float, float]] = None
) -> solid.OpenSCADObject:
    """Create date stamp annotation.
    
    Creates a date stamp for tracking fabrication date.
    
    Parameters
    ----------
    date_str : str
        Date string (e.g., "2024-10-21").
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    size : float, default=1.0
        Text size.
    alignment_offset : tuple of (float, float), optional
        Alignment offset to apply.
        
    Returns
    -------
    solid.OpenSCADObject
        Date stamp text.
        
    Examples
    --------
    >>> stamp = create_date_stamp(
    ...     "2024-10-21", grid_size=[6, 8], dims=[9.0, 9.0, 0]
    ... )
    """
    # Position at bottom corner
    offset_y = -(grid_size[1] + 1) * dims[1] / 2
    
    return create_centered_text(
        date_str, grid_size, dims, size,
        offset_y=offset_y,
        alignment_offset=alignment_offset
    )

