"""Configuration for export and file generation.

This module provides configuration dataclasses for controlling export
of device geometries to various file formats.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from openmfd.core import ConfigurationContract


@dataclass
class FileNamingConfig(ConfigurationContract):
    """Configuration for file naming conventions.

    Attributes
    ----------
    prefix : str, default=''
        Prefix for filename (e.g., 'wells', 'channels', 'device').
    version : str, optional
        Version string (e.g., 'v1', 'v2').
    grid_size : tuple of (int, int), optional
        Grid size (rows, columns) for array devices.
    suffix : str, default=''
        Additional suffix for filename.
    """

    prefix: str = ""
    version: Optional[str] = None
    grid_size: Optional[Tuple[int, int]] = None
    suffix: str = ""

    def _validate(self) -> None:
        return None

    def generate_filename(self, extension: str) -> str:
        """Generate filename from configuration.

        Parameters
        ----------
        extension : str
            File extension (e.g., 'scad', 'dxf', 'stl').

        Returns
        -------
        str
            Generated filename.

        Examples
        --------
        >>> config = FileNamingConfig(prefix='device', version='v1', grid_size=(8, 12))
        >>> config.generate_filename('scad')
        'v1_device_8x12_units_.scad'
        """
        parts = []

        # Add version
        if self.version:
            parts.append(self.version)

        # Add prefix
        if self.prefix:
            parts.append(self.prefix)

        # Add grid size
        if self.grid_size:
            parts.append(f"{self.grid_size[0]}x{self.grid_size[1]}_units_")

        # Add suffix
        if self.suffix:
            parts.append(self.suffix)

        # Join parts and add extension
        base_name = "_".join(parts) if parts else "output"
        return f"{base_name}.{extension}"


@dataclass
class ExportConfiguration(ConfigurationContract):
    """Configuration for exporting device geometries.

    Attributes
    ----------
    output_directory : Path
        Directory for output files.
    base_name : str, default='device'
        Base name for output files.
    formats : list of str, default=['scad']
        Output formats to generate ('scad', 'dxf', 'stl').
    render_stl : bool, default=False
        Whether to render STL files (requires OpenSCAD).
    dxf_conversion : bool, default=False
        Whether to convert SCAD to DXF (requires OpenSCAD).
    create_directories : bool, default=True
        Whether to create output directories if they don't exist.
    overwrite : bool, default=True
        Whether to overwrite existing files.
    """

    output_directory: Path
    base_name: str = "device"
    formats: List[str] = field(default_factory=lambda: ["scad"])
    render_stl: bool = False
    dxf_conversion: bool = False
    create_directories: bool = True
    overwrite: bool = True

    def _normalize(self) -> None:
        if isinstance(self.output_directory, str):
            self.output_directory = Path(self.output_directory)

    def _validate(self) -> None:
        valid_formats = {"scad", "dxf", "stl"}
        for fmt in self.formats:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid format '{fmt}'. Must be one of {valid_formats}")

    def _derive(self) -> None:
        if self.create_directories:
            self.output_directory.mkdir(parents=True, exist_ok=True)

    def get_output_path(self, filename: str) -> Path:
        """Get full output path for a filename.

        Parameters
        ----------
        filename : str
            Filename (with extension).

        Returns
        -------
        Path
            Full path to output file.
        """
        return self.output_directory / filename


@dataclass
class RenderConfiguration(ConfigurationContract):
    """Configuration for rendering previews and images.

    Attributes
    ----------
    width : int, default=800
        Render width in pixels.
    height : int, default=800
        Render height in pixels.
    camera_distance : float, optional
        Camera distance from origin.
    camera_rotation : tuple of (float, float, float), optional
        Camera rotation (x, y, z) in degrees.
    """

    width: int = 800
    height: int = 800
    camera_distance: Optional[float] = None
    camera_rotation: Optional[Tuple[float, float, float]] = None

    def _validate(self) -> None:
        if self.width <= 0:
            raise ValueError(f"width must be positive, got {self.width}")
        if self.height <= 0:
            raise ValueError(f"height must be positive, got {self.height}")


@dataclass
class OpenSCADConfig(ConfigurationContract):
    """Configuration for OpenSCAD CLI operations.

    Attributes
    ----------
    openscad_path : str, default='openscad'
        Path to OpenSCAD executable.
    timeout : int, default=300
        Timeout for OpenSCAD operations in seconds.
    extra_args : list of str, optional
        Additional arguments to pass to OpenSCAD.
    """

    openscad_path: str = "openscad"
    timeout: int = 300
    extra_args: Optional[List[str]] = None

    def _normalize(self) -> None:
        if self.extra_args is None:
            self.extra_args = []

    def _validate(self) -> None:
        if self.timeout <= 0:
            raise ValueError(f"timeout must be positive, got {self.timeout}")
