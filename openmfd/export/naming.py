"""File naming utilities for device exports.

This module provides functions for generating standardized filenames
following OpenMFD conventions.
"""

from typing import Optional, Tuple
import re
from pathlib import Path

from .config import FileNamingConfig


def generate_filename(
    prefix: str = '',
    version: Optional[str] = None,
    grid_size: Optional[Tuple[int, int]] = None,
    suffix: str = '',
    extension: str = 'scad'
) -> str:
    """Generate standardized filename.
    
    Follows pattern: {version}_{prefix}_{rows}x{cols}_units_{suffix}.{ext}
    
    Parameters
    ----------
    prefix : str, default=''
        Filename prefix (e.g., 'wells', 'channels', 'device').
    version : str, optional
        Version string (e.g., 'v1', 'v2').
    grid_size : tuple of (int, int), optional
        Grid size (rows, columns).
    suffix : str, default=''
        Additional suffix.
    extension : str, default='scad'
        File extension.
        
    Returns
    -------
    str
        Generated filename.
        
    Examples
    --------
    >>> generate_filename('device', 'v1', (8, 12), extension='scad')
    'v1_device_8x12_units_.scad'
    
    >>> generate_filename('wells', grid_size=(4, 6), extension='dxf')
    'wells_4x6_units_.dxf'
    """
    config = FileNamingConfig(
        prefix=prefix,
        version=version,
        grid_size=grid_size,
        suffix=suffix
    )
    return config.generate_filename(extension)


def parse_filename(filename: str) -> dict:
    """Parse filename to extract components.
    
    Parameters
    ----------
    filename : str
        Filename to parse.
        
    Returns
    -------
    dict
        Dictionary with extracted components (version, prefix, grid_size, etc.).
        
    Examples
    --------
    >>> info = parse_filename('v1_device_8x12_units_.scad')
    >>> print(info['version'])  # 'v1'
    >>> print(info['grid_size'])  # (8, 12)
    >>> print(info['prefix'])  # 'device'
    """
    # Remove extension
    name = Path(filename).stem
    
    info = {
        'version': None,
        'prefix': None,
        'grid_size': None,
        'suffix': None,
        'extension': Path(filename).suffix.lstrip('.')
    }
    
    # Extract version (vN pattern)
    version_match = re.search(r'v(\d+)', name)
    if version_match:
        info['version'] = f"v{version_match.group(1)}"
        name = name.replace(info['version'] + '_', '', 1)
    
    # Extract grid size (NxM_units pattern)
    grid_match = re.search(r'(\d+)x(\d+)_units', name)
    if grid_match:
        info['grid_size'] = (int(grid_match.group(1)), int(grid_match.group(2)))
        name = name.replace(f"{grid_match.group(1)}x{grid_match.group(2)}_units_", '', 1)
    
    # Remaining parts are prefix and suffix
    parts = name.split('_')
    if parts:
        info['prefix'] = parts[0] if parts[0] else None
        if len(parts) > 1:
            info['suffix'] = '_'.join(parts[1:])
    
    return info


def validate_filename(filename: str) -> bool:
    """Validate filename for invalid characters.
    
    Parameters
    ----------
    filename : str
        Filename to validate.
        
    Returns
    -------
    bool
        True if filename is valid, False otherwise.
    """
    # Check for invalid characters (platform-specific)
    invalid_chars = r'[<>:"|?*]'
    if re.search(invalid_chars, filename):
        return False
    
    # Check for empty filename
    if not filename or filename.strip() == '':
        return False
    
    # Check for reserved names (Windows)
    reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    name_without_ext = Path(filename).stem.upper()
    if name_without_ext in reserved:
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters.
    
    Parameters
    ----------
    filename : str
        Filename to sanitize.
        
    Returns
    -------
    str
        Sanitized filename.
        
    Examples
    --------
    >>> sanitize_filename('device:v1.scad')
    'device_v1.scad'
    """
    # Replace invalid characters with underscore
    invalid_chars = r'[<>:"|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    return sanitized


def increment_version(version: str) -> str:
    """Increment version string.
    
    Parameters
    ----------
    version : str
        Version string (e.g., 'v1', 'v2').
        
    Returns
    -------
    str
        Incremented version string.
        
    Examples
    --------
    >>> increment_version('v1')
    'v2'
    
    >>> increment_version('v10')
    'v11'
    """
    match = re.search(r'v(\d+)', version)
    if match:
        num = int(match.group(1))
        return f"v{num + 1}"
    else:
        return 'v1'


def find_next_version(directory: Path, base_pattern: str) -> str:
    """Find next available version number in directory.
    
    Parameters
    ----------
    directory : Path
        Directory to search.
    base_pattern : str
        Base filename pattern (without version).
        
    Returns
    -------
    str
        Next available version string.
        
    Examples
    --------
    >>> next_ver = find_next_version(Path('output'), 'device_8x12_units_')
    >>> # Returns 'v1' if no files exist, 'v3' if v1 and v2 exist, etc.
    """
    if not directory.exists():
        return 'v1'
    
    # Find all files matching pattern
    versions = []
    for file in directory.iterdir():
        if file.is_file():
            info = parse_filename(file.name)
            if info['version']:
                match = re.search(r'v(\d+)', info['version'])
                if match:
                    versions.append(int(match.group(1)))
    
    if not versions:
        return 'v1'
    
    return f"v{max(versions) + 1}"


def generate_unique_filename(
    directory: Path,
    prefix: str = '',
    grid_size: Optional[Tuple[int, int]] = None,
    suffix: str = '',
    extension: str = 'scad',
    auto_increment: bool = True
) -> str:
    """Generate unique filename that doesn't exist in directory.
    
    Parameters
    ----------
    directory : Path
        Directory to check for existing files.
    prefix : str, default=''
        Filename prefix.
    grid_size : tuple of (int, int), optional
        Grid size.
    suffix : str, default=''
        Additional suffix.
    extension : str, default='scad'
        File extension.
    auto_increment : bool, default=True
        If True, auto-increment version to avoid conflicts.
        
    Returns
    -------
    str
        Unique filename.
    """
    if auto_increment:
        # Find next version
        base_pattern = generate_filename(prefix, None, grid_size, suffix, extension)
        version = find_next_version(directory, base_pattern)
        return generate_filename(prefix, version, grid_size, suffix, extension)
    else:
        return generate_filename(prefix, None, grid_size, suffix, extension)

