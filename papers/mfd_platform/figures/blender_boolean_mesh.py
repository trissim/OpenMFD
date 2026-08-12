#!/usr/bin/env python3

"""Subtract one STL mesh from another with Blender's manifold Boolean solver."""

from __future__ import annotations

import sys
from pathlib import Path

import bpy


def import_stl(path: Path, name: str) -> bpy.types.Object:
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = bpy.context.object
    obj.name = name
    return obj


def main() -> int:
    if "--" not in sys.argv:
        raise SystemExit("Expected BASE_STL CUTTER_STL OUTPUT_STL after --")
    arguments = sys.argv[sys.argv.index("--") + 1 :]
    if len(arguments) < 3:
        raise SystemExit("Expected BASE_STL CUTTER_STL [CUTTER_STL ...] OUTPUT_STL")
    base_path = Path(arguments[0])
    cutter_paths = [Path(path) for path in arguments[1:-1]]
    output_path = Path(arguments[-1])

    bpy.ops.wm.read_factory_settings(use_empty=True)
    base = import_stl(base_path, "base")
    # The insert, thick-layer, and microchannel cutters overlap by design.
    # Joining them without a geometric union produces a non-manifold cutter
    # whose coincident internal faces can make Blender retain parts of the
    # inserts. Apply each closed cutter independently to preserve the complete
    # negative of every generated mold feature.
    for index, cutter_path in enumerate(cutter_paths):
        cutter = import_stl(cutter_path, f"cutter-{index}")
        modifier = base.modifiers.new(f"native-mold-negative-{index}", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "MANIFOLD"
        modifier.object = cutter
        bpy.context.view_layer.objects.active = base
        base.select_set(True)
        cutter.select_set(False)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)

    bpy.ops.object.select_all(action="DESELECT")
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.wm.stl_export(
        filepath=str(output_path),
        export_selected_objects=True,
        apply_modifiers=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
