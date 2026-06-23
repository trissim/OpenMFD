"""Unit tests for SCAD export helpers."""

from pathlib import Path

import pytest
import solid

import openmfd.export.scad as scad_export


@pytest.mark.unit
def test_export_scad_strips_trailing_whitespace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_path = tmp_path / "device.scad"

    def fake_render_to_file(_geometry: solid.OpenSCADObject, path: str) -> None:
        Path(path).write_text("cube([1, 1, 1]);   \n    \n")

    monkeypatch.setattr(scad_export.solid, "scad_render_to_file", fake_render_to_file)

    result = scad_export.export_scad(solid.cube([1, 1, 1]), output_path)

    assert result == output_path
    assert output_path.read_text() == "cube([1, 1, 1]);\n\n"
