"""DXF file export and conversion functions.

This module provides functions for converting SCAD files to DXF format
using OpenSCAD CLI and post-processing with ezdxf.
"""

from typing import Optional
from pathlib import Path
import subprocess
import ezdxf

from .config import OpenSCADConfig


def scad_to_dxf(
    scad_path: Path,
    dxf_path: Optional[Path] = None,
    openscad_config: Optional[OpenSCADConfig] = None
) -> Path:
    """Convert SCAD file to DXF using OpenSCAD CLI.
    
    Parameters
    ----------
    scad_path : Path
        Path to input SCAD file.
    dxf_path : Path, optional
        Path to output DXF file. If None, uses same name as SCAD with .dxf extension.
    openscad_config : OpenSCADConfig, optional
        OpenSCAD configuration. If None, uses defaults.
        
    Returns
    -------
    Path
        Path to created DXF file.
        
    Raises
    ------
    FileNotFoundError
        If SCAD file doesn't exist.
    RuntimeError
        If OpenSCAD conversion fails.
    IOError
        If DXF file cannot be written.
        
    Examples
    --------
    >>> from pathlib import Path
    >>> scad_path = Path('output/device.scad')
    >>> dxf_path = scad_to_dxf(scad_path)
    """
    # Validate input
    if not scad_path.exists():
        raise FileNotFoundError(f"SCAD file not found: {scad_path}")
    
    # Determine output path
    if dxf_path is None:
        dxf_path = scad_path.with_suffix('.dxf')
    
    # Get OpenSCAD config
    if openscad_config is None:
        openscad_config = OpenSCADConfig()
    
    # Build OpenSCAD command
    cmd = [openscad_config.openscad_path, '-o', str(dxf_path), str(scad_path)]
    
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
    if not dxf_path.exists():
        raise IOError(f"DXF file was not created: {dxf_path}")
    
    # Post-process with ezdxf (normalize and re-save)
    try:
        post_process_dxf(dxf_path)
    except Exception as e:
        # Log warning but don't fail
        print(f"Warning: DXF post-processing failed: {e}")
    
    return dxf_path


def post_process_dxf(dxf_path: Path):
    """Post-process DXF file with ezdxf.
    
    This normalizes the DXF file and ensures compatibility.
    
    Parameters
    ----------
    dxf_path : Path
        Path to DXF file to post-process.
        
    Raises
    ------
    IOError
        If DXF file cannot be read or written.
    """
    try:
        # Read DXF file
        doc = ezdxf.readfile(str(dxf_path))
        
        # Save back (normalizes format)
        doc.saveas(str(dxf_path))
    except Exception as e:
        raise IOError(f"Failed to post-process DXF file {dxf_path}: {e}")


def validate_dxf_file(dxf_path: Path) -> bool:
    """Validate that DXF file exists and is readable.
    
    Parameters
    ----------
    dxf_path : Path
        Path to DXF file.
        
    Returns
    -------
    bool
        True if file is valid, False otherwise.
    """
    if not dxf_path.exists():
        return False
    
    if not dxf_path.is_file():
        return False
    
    # Try to read with ezdxf
    try:
        doc = ezdxf.readfile(str(dxf_path))
        return True
    except Exception:
        return False


def get_dxf_info(dxf_path: Path) -> dict:
    """Get information about DXF file.
    
    Parameters
    ----------
    dxf_path : Path
        Path to DXF file.
        
    Returns
    -------
    dict
        Dictionary with DXF information (version, layers, entities, etc.).
        
    Examples
    --------
    >>> info = get_dxf_info(Path('output/device.dxf'))
    >>> print(f"DXF version: {info['version']}")
    >>> print(f"Number of layers: {info['num_layers']}")
    """
    try:
        doc = ezdxf.readfile(str(dxf_path))
        
        info = {
            'version': doc.dxfversion,
            'num_layers': len(doc.layers),
            'num_entities': sum(1 for _ in doc.modelspace()),
            'layers': [layer.dxf.name for layer in doc.layers],
        }
        
        return info
    except Exception as e:
        return {'error': str(e)}


def export_dxf_from_geometry(
    geometry: 'solid.OpenSCADObject',
    dxf_path: Path,
    openscad_config: Optional[OpenSCADConfig] = None
) -> Path:
    """Export geometry directly to DXF (via temporary SCAD file).
    
    Parameters
    ----------
    geometry : solid.OpenSCADObject
        Geometry to export.
    dxf_path : Path
        Output DXF path.
    openscad_config : OpenSCADConfig, optional
        OpenSCAD configuration.
        
    Returns
    -------
    Path
        Path to created DXF file.
        
    Examples
    --------
    >>> import solid
    >>> geometry = solid.square([10, 10])
    >>> dxf_path = export_dxf_from_geometry(geometry, Path('output/device.dxf'))
    """
    import solid
    from .scad import export_scad
    
    # Create temporary SCAD file
    temp_scad = dxf_path.with_suffix('.scad')
    export_scad(geometry, temp_scad)
    
    # Convert to DXF
    try:
        result = scad_to_dxf(temp_scad, dxf_path, openscad_config)
        return result
    finally:
        # Clean up temporary SCAD file (optional)
        # temp_scad.unlink(missing_ok=True)
        pass

