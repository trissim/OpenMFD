"""STL file export and rendering functions.

This module provides functions for rendering geometries to STL format
using viewscad or OpenSCAD CLI.
"""

from typing import Optional
from pathlib import Path
import subprocess

from .config import OpenSCADConfig, RenderConfiguration


def scad_to_stl(
    scad_path: Path,
    stl_path: Optional[Path] = None,
    openscad_config: Optional[OpenSCADConfig] = None
) -> Path:
    """Convert SCAD file to STL using OpenSCAD CLI.
    
    Parameters
    ----------
    scad_path : Path
        Path to input SCAD file.
    stl_path : Path, optional
        Path to output STL file. If None, uses same name as SCAD with .stl extension.
    openscad_config : OpenSCADConfig, optional
        OpenSCAD configuration. If None, uses defaults.
        
    Returns
    -------
    Path
        Path to created STL file.
        
    Raises
    ------
    FileNotFoundError
        If SCAD file doesn't exist.
    RuntimeError
        If OpenSCAD conversion fails.
    IOError
        If STL file cannot be written.
        
    Examples
    --------
    >>> from pathlib import Path
    >>> scad_path = Path('output/device.scad')
    >>> stl_path = scad_to_stl(scad_path)
    """
    # Validate input
    if not scad_path.exists():
        raise FileNotFoundError(f"SCAD file not found: {scad_path}")
    
    # Determine output path
    if stl_path is None:
        stl_path = scad_path.with_suffix('.stl')
    
    # Get OpenSCAD config
    if openscad_config is None:
        openscad_config = OpenSCADConfig()
    
    # Build OpenSCAD command
    cmd = [openscad_config.openscad_path, '-o', str(stl_path), str(scad_path)]
    
    # Add extra arguments
    if openscad_config.extra_args:
        cmd.extend(openscad_config.extra_args)
    
    # Run OpenSCAD
    try:
        result = subprocess.run(
            cmd,
            timeout=openscad_config.timeout,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(
                f"OpenSCAD conversion failed with code {result.returncode}:\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"OpenSCAD conversion timed out after {openscad_config.timeout} seconds"
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"OpenSCAD executable not found: {openscad_config.openscad_path}. "
            "Make sure OpenSCAD is installed and in PATH."
        )
    
    # Validate output
    if not stl_path.exists():
        raise IOError(f"STL file was not created: {stl_path}")
    
    return stl_path


def render_stl_with_viewscad(
    geometry: 'solid.OpenSCADObject',
    stl_path: Path,
    render_config: Optional[RenderConfiguration] = None
) -> Path:
    """Render geometry to STL using viewscad.
    
    Parameters
    ----------
    geometry : solid.OpenSCADObject
        Geometry to render.
    stl_path : Path
        Output STL path.
    render_config : RenderConfiguration, optional
        Rendering configuration. If None, uses defaults.
        
    Returns
    -------
    Path
        Path to created STL file.
        
    Raises
    ------
    ImportError
        If viewscad is not available.
    IOError
        If STL file cannot be written.
        
    Examples
    --------
    >>> import solid
    >>> geometry = solid.cube([10, 10, 10])
    >>> stl_path = render_stl_with_viewscad(geometry, Path('output/device.stl'))
    """
    try:
        import viewscad
    except ImportError:
        raise ImportError(
            "viewscad is required for STL rendering. "
            "Install with: pip install viewscad"
        )
    
    # Get render config
    if render_config is None:
        render_config = RenderConfiguration()
    
    # Create renderer
    renderer = viewscad.Renderer(
        width=render_config.width,
        height=render_config.height
    )
    
    # Ensure parent directory exists
    stl_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Render to STL
    try:
        renderer.render(geometry, outfile=str(stl_path))
    except Exception as e:
        raise IOError(f"Failed to render STL file to {stl_path}: {e}")
    
    # Validate output
    if not stl_path.exists():
        raise IOError(f"STL file was not created: {stl_path}")
    
    return stl_path


def validate_stl_file(stl_path: Path) -> bool:
    """Validate that STL file exists and has content.
    
    Parameters
    ----------
    stl_path : Path
        Path to STL file.
        
    Returns
    -------
    bool
        True if file is valid, False otherwise.
    """
    if not stl_path.exists():
        return False
    
    if not stl_path.is_file():
        return False
    
    # Check file size (STL should have some content)
    if stl_path.stat().st_size == 0:
        return False
    
    # Try to read first few bytes to check format
    try:
        with open(stl_path, 'rb') as f:
            header = f.read(80)
            # STL files should have at least 80 bytes (header)
            return len(header) == 80
    except Exception:
        return False


def get_stl_info(stl_path: Path) -> dict:
    """Get basic information about STL file.
    
    Parameters
    ----------
    stl_path : Path
        Path to STL file.
        
    Returns
    -------
    dict
        Dictionary with STL information (file size, format, etc.).
        
    Examples
    --------
    >>> info = get_stl_info(Path('output/device.stl'))
    >>> print(f"File size: {info['size_bytes']} bytes")
    """
    if not stl_path.exists():
        return {'error': 'File not found'}
    
    try:
        size = stl_path.stat().st_size
        
        # Determine if ASCII or binary
        with open(stl_path, 'rb') as f:
            header = f.read(80)
            is_ascii = header.startswith(b'solid')
        
        info = {
            'size_bytes': size,
            'format': 'ASCII' if is_ascii else 'Binary',
            'path': str(stl_path)
        }
        
        return info
    except Exception as e:
        return {'error': str(e)}


def export_stl_from_geometry(
    geometry: 'solid.OpenSCADObject',
    stl_path: Path,
    use_viewscad: bool = True,
    render_config: Optional[RenderConfiguration] = None,
    openscad_config: Optional[OpenSCADConfig] = None
) -> Path:
    """Export geometry to STL using viewscad or OpenSCAD CLI.
    
    Parameters
    ----------
    geometry : solid.OpenSCADObject
        Geometry to export.
    stl_path : Path
        Output STL path.
    use_viewscad : bool, default=True
        If True, use viewscad. If False, use OpenSCAD CLI via temp SCAD file.
    render_config : RenderConfiguration, optional
        Rendering configuration (for viewscad).
    openscad_config : OpenSCADConfig, optional
        OpenSCAD configuration (for CLI method).
        
    Returns
    -------
    Path
        Path to created STL file.
    """
    if use_viewscad:
        return render_stl_with_viewscad(geometry, stl_path, render_config)
    else:
        # Use OpenSCAD CLI via temporary SCAD file
        from .scad import export_scad
        
        temp_scad = stl_path.with_suffix('.scad')
        export_scad(geometry, temp_scad)
        
        try:
            result = scad_to_stl(temp_scad, stl_path, openscad_config)
            return result
        finally:
            # Clean up temporary SCAD file (optional)
            # temp_scad.unlink(missing_ok=True)
            pass

