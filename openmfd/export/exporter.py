"""High-level export orchestration for device geometries.

This module provides a unified interface for exporting device geometries
to multiple formats (SCAD, DXF, STL).
"""

from typing import Dict, List, Optional
from pathlib import Path
import solid

from .config import ExportConfiguration, FileNamingConfig, OpenSCADConfig, RenderConfiguration
from .scad import export_scad, export_multiple_scad
from .dxf import scad_to_dxf
from .stl import scad_to_stl, render_stl_with_viewscad


def export_device(
    geometries: Dict[str, solid.OpenSCADObject],
    config: ExportConfiguration,
    naming_config: Optional[FileNamingConfig] = None
) -> Dict[str, Dict[str, Path]]:
    """Export device geometries to multiple formats.
    
    This is the main high-level export function that handles exporting
    geometries to all requested formats.
    
    Parameters
    ----------
    geometries : dict
        Dictionary mapping component names to geometries.
        Keys: 'wells', 'channels', 'chambers', 'device', etc.
    config : ExportConfiguration
        Export configuration specifying formats and output directory.
    naming_config : FileNamingConfig, optional
        File naming configuration.
        
    Returns
    -------
    dict
        Nested dictionary mapping component names to format-to-path mappings.
        Example: {'device': {'scad': Path(...), 'dxf': Path(...)}}
        
    Examples
    --------
    >>> from openmfd.export import ExportConfiguration, FileNamingConfig
    >>> from pathlib import Path
    >>> 
    >>> geometries = {
    ...     'wells': wells_geometry,
    ...     'channels': channels_geometry,
    ...     'device': device_geometry
    ... }
    >>> 
    >>> config = ExportConfiguration(
    ...     output_directory=Path('output'),
    ...     formats=['scad', 'dxf'],
    ...     dxf_conversion=True
    ... )
    >>> 
    >>> naming = FileNamingConfig(version='v1', grid_size=(8, 12))
    >>> 
    >>> paths = export_device(geometries, config, naming)
    >>> print(paths['device']['scad'])  # Path to device SCAD file
    >>> print(paths['device']['dxf'])   # Path to device DXF file
    """
    output_paths = {}
    
    # Export SCAD files (always needed as intermediate)
    scad_paths = export_multiple_scad(geometries, config, naming_config)
    
    for component, scad_path in scad_paths.items():
        output_paths[component] = {}
        
        # Add SCAD path if requested
        if 'scad' in config.formats:
            output_paths[component]['scad'] = scad_path
        
        # Convert to DXF if requested
        if 'dxf' in config.formats and config.dxf_conversion:
            try:
                dxf_path = scad_to_dxf(scad_path)
                output_paths[component]['dxf'] = dxf_path
            except Exception as e:
                print(f"Warning: DXF conversion failed for {component}: {e}")
        
        # Convert to STL if requested
        if 'stl' in config.formats and config.render_stl:
            try:
                stl_path = scad_to_stl(scad_path)
                output_paths[component]['stl'] = stl_path
            except Exception as e:
                print(f"Warning: STL conversion failed for {component}: {e}")
    
    return output_paths


def export_single_geometry(
    geometry: solid.OpenSCADObject,
    output_path: Path,
    formats: Optional[List[str]] = None,
    openscad_config: Optional[OpenSCADConfig] = None,
    render_config: Optional[RenderConfiguration] = None
) -> Dict[str, Path]:
    """Export a single geometry to multiple formats.
    
    Parameters
    ----------
    geometry : solid.OpenSCADObject
        Geometry to export.
    output_path : Path
        Base output path (without extension).
    formats : list of str, optional
        Formats to export ('scad', 'dxf', 'stl'). If None, exports only SCAD.
    openscad_config : OpenSCADConfig, optional
        OpenSCAD configuration.
    render_config : RenderConfiguration, optional
        Rendering configuration.
        
    Returns
    -------
    dict
        Dictionary mapping formats to output paths.
        
    Examples
    --------
    >>> import solid
    >>> geometry = solid.cube([10, 10, 10])
    >>> paths = export_single_geometry(
    ...     geometry,
    ...     Path('output/device'),
    ...     formats=['scad', 'stl']
    ... )
    """
    if formats is None:
        formats = ['scad']
    
    output_paths = {}
    
    # Export SCAD
    scad_path = output_path.with_suffix('.scad')
    export_scad(geometry, scad_path)
    
    if 'scad' in formats:
        output_paths['scad'] = scad_path
    
    # Export DXF
    if 'dxf' in formats:
        try:
            dxf_path = scad_to_dxf(scad_path, openscad_config=openscad_config)
            output_paths['dxf'] = dxf_path
        except Exception as e:
            print(f"Warning: DXF export failed: {e}")
    
    # Export STL
    if 'stl' in formats:
        try:
            stl_path = output_path.with_suffix('.stl')
            render_stl_with_viewscad(geometry, stl_path, render_config)
            output_paths['stl'] = stl_path
        except Exception as e:
            print(f"Warning: STL export failed: {e}")
    
    return output_paths


def validate_exports(output_paths: Dict[str, Dict[str, Path]]) -> Dict[str, Dict[str, bool]]:
    """Validate that all exported files exist and are valid.
    
    Parameters
    ----------
    output_paths : dict
        Output paths from export_device().
        
    Returns
    -------
    dict
        Nested dictionary mapping components and formats to validation results.
        
    Examples
    --------
    >>> validation = validate_exports(output_paths)
    >>> if not validation['device']['dxf']:
    ...     print("Device DXF export failed!")
    """
    from .scad import validate_scad_file
    from .dxf import validate_dxf_file
    from .stl import validate_stl_file
    
    validators = {
        'scad': validate_scad_file,
        'dxf': validate_dxf_file,
        'stl': validate_stl_file
    }
    
    validation = {}
    for component, paths in output_paths.items():
        validation[component] = {}
        for fmt, path in paths.items():
            if fmt in validators:
                validation[component][fmt] = validators[fmt](path)
            else:
                validation[component][fmt] = path.exists()
    
    return validation


class DeviceExporter:
    """High-level device exporter with configuration management.
    
    This class provides a stateful interface for exporting devices with
    consistent configuration across multiple exports.
    
    Attributes
    ----------
    config : ExportConfiguration
        Export configuration.
    naming_config : FileNamingConfig, optional
        File naming configuration.
    openscad_config : OpenSCADConfig, optional
        OpenSCAD configuration.
    render_config : RenderConfiguration, optional
        Rendering configuration.
    """
    
    def __init__(
        self,
        config: ExportConfiguration,
        naming_config: Optional[FileNamingConfig] = None,
        openscad_config: Optional[OpenSCADConfig] = None,
        render_config: Optional[RenderConfiguration] = None
    ):
        """Initialize exporter.
        
        Parameters
        ----------
        config : ExportConfiguration
            Export configuration.
        naming_config : FileNamingConfig, optional
            File naming configuration.
        openscad_config : OpenSCADConfig, optional
            OpenSCAD configuration.
        render_config : RenderConfiguration, optional
            Rendering configuration.
        """
        self.config = config
        self.naming_config = naming_config
        self.openscad_config = openscad_config
        self.render_config = render_config
    
    def export(self, geometries: Dict[str, solid.OpenSCADObject]) -> Dict[str, Dict[str, Path]]:
        """Export geometries using configured settings.
        
        Parameters
        ----------
        geometries : dict
            Dictionary mapping component names to geometries.
            
        Returns
        -------
        dict
            Output paths for all components and formats.
        """
        return export_device(geometries, self.config, self.naming_config)
    
    def validate(self, output_paths: Dict[str, Dict[str, Path]]) -> Dict[str, Dict[str, bool]]:
        """Validate exported files.
        
        Parameters
        ----------
        output_paths : dict
            Output paths from export().
            
        Returns
        -------
        dict
            Validation results.
        """
        return validate_exports(output_paths)

