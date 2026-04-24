"""Shared OpenSCAD CLI helpers for export backends."""

from pathlib import Path
import subprocess

from .config import OpenSCADConfig


def run_openscad_export(
    scad_path: Path,
    output_path: Path,
    openscad_config: OpenSCADConfig | None = None,
) -> Path:
    """Run an OpenSCAD CLI export with shared validation and error handling."""

    if not scad_path.exists():
        raise FileNotFoundError(f"SCAD file not found: {scad_path}")

    if openscad_config is None:
        openscad_config = OpenSCADConfig()

    cmd = [openscad_config.openscad_path, "-o", str(output_path), str(scad_path)]
    cmd.extend(openscad_config.extra_args)

    try:
        result = subprocess.run(
            cmd,
            timeout=openscad_config.timeout,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"OpenSCAD conversion timed out after {openscad_config.timeout} seconds"
        ) from exc
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"OpenSCAD executable not found: {openscad_config.openscad_path}. "
            "Make sure OpenSCAD is installed and in PATH."
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"OpenSCAD conversion failed with code {result.returncode}:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    if not output_path.exists():
        raise IOError(f"Output file was not created: {output_path}")

    return output_path
