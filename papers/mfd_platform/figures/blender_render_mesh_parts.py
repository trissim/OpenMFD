#!/usr/bin/env python3

"""Render a manifest of STL mesh parts with Blender's depth buffer."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy


def rgba(hex_color: str, alpha: float) -> tuple[float, float, float, float]:
    value = hex_color.lstrip("#")
    rgb = tuple(int(value[index : index + 2], 16) / 255 for index in (0, 2, 4))
    return (*rgb, alpha)


def material_for(
    index: int,
    color: str,
    alpha: float,
    roughness: float,
    metallic: float,
    emission_strength: float,
    transparency_overlap: bool,
    transmission_weight: float | None,
) -> bpy.types.Material:
    material = bpy.data.materials.new(f"part-{index}")
    material.diffuse_color = rgba(color, alpha)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = rgba(color, 1.0)
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Alpha"].default_value = alpha
    if emission_strength > 0.0:
        principled.inputs["Emission Color"].default_value = rgba(color, 1.0)
        principled.inputs["Emission Strength"].default_value = emission_strength
    if alpha < 1.0:
        # Alpha-hashed transparency participates in depth rendering without a
        # blended front surface masking recessed cavity faces behind it. This
        # is the schematic behavior required for translucent PDMS solids.
        material.surface_render_method = (
            "DITHERED" if transmission_weight == 0.0 else "BLENDED"
        )
        if material.surface_render_method == "BLENDED":
            material.use_transparency_overlap = transparency_overlap
        material.use_transparent_shadow = False
        principled.inputs["Transmission Weight"].default_value = (
            min(0.92, (1.0 - alpha) * 1.05)
            if transmission_weight is None
            else transmission_weight
        )
        principled.inputs["IOR"].default_value = 1.43
        principled.inputs["Roughness"].default_value = 0.22
    return material


def point_camera_at(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = mathutils.Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def main() -> int:
    if "--" not in sys.argv:
        raise SystemExit("Expected a scene manifest after --")
    manifest_path = Path(sys.argv[sys.argv.index("--") + 1])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = manifest["width"]
    scene.render.resolution_y = manifest["height"]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.filepath = manifest["output"]
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.eevee.use_shadows = True
    scene.eevee.taa_samples = 64
    scene.eevee.taa_render_samples = 128
    scene.eevee.shadow_ray_count = 4
    scene.eevee.shadow_step_count = 8

    for index, part in enumerate(manifest["parts"]):
        bpy.ops.wm.stl_import(filepath=part["path"])
        obj = bpy.context.object
        obj.name = f"part-{index}"
        if part.get("dissolve_coplanar", False):
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.dissolve_limited(angle_limit=math.radians(0.5))
            bpy.ops.object.mode_set(mode="OBJECT")
        obj.data.materials.append(
            material_for(
                index,
                part["color"],
                part["alpha"],
                part.get("roughness", 0.48),
                part.get("metallic", 0.0),
                part.get("emission_strength", 0.0),
                part.get("transparency_overlap", True),
                part.get("transmission_weight"),
            )
        )

    camera_data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.location = (0.0, 0.0, manifest["camera_z"])
    camera.rotation_euler = (0.0, 0.0, 0.0)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = manifest["ortho_scale"]
    camera_data.lens = 50
    camera_data.clip_start = 0.01
    camera_data.clip_end = manifest["camera_clip_end"]

    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.30

    key_data = bpy.data.lights.new("Key", type="AREA")
    key_data.energy = 1325.0
    key_data.color = (1.0, 0.97, 0.93)
    key_data.use_shadow = True
    key_data.shape = "DISK"
    key_data.size = manifest["ortho_scale"] * 0.34
    key = bpy.data.objects.new("Key", key_data)
    scene.collection.objects.link(key)
    key.location = (
        -manifest["ortho_scale"] * 0.85,
        -manifest["ortho_scale"] * 0.70,
        manifest["camera_z"] * 0.72,
    )
    point_camera_at(key, (0.0, 0.0, 0.0))

    fill_data = bpy.data.lights.new("Fill", type="AREA")
    fill_data.energy = 285.0
    fill_data.color = (0.88, 0.94, 1.0)
    fill_data.use_shadow = True
    fill_data.size = manifest["ortho_scale"] * 0.85
    fill = bpy.data.objects.new("Fill", fill_data)
    scene.collection.objects.link(fill)
    fill.location = (
        manifest["ortho_scale"] * 0.75,
        -manifest["ortho_scale"] * 0.15,
        manifest["camera_z"] * 0.42,
    )
    point_camera_at(fill, (0.0, 0.0, 0.0))

    rim_data = bpy.data.lights.new("Rim", type="AREA")
    rim_data.energy = 440.0
    rim_data.color = (0.92, 0.96, 1.0)
    rim_data.use_shadow = True
    rim_data.shape = "RECTANGLE"
    rim_data.size = manifest["ortho_scale"] * 0.45
    rim_data.size_y = manifest["ortho_scale"] * 0.18
    rim = bpy.data.objects.new("Rim", rim_data)
    scene.collection.objects.link(rim)
    rim.location = (
        manifest["ortho_scale"] * 0.65,
        manifest["ortho_scale"] * 0.80,
        manifest["camera_z"] * 0.35,
    )
    point_camera_at(rim, (0.0, 0.0, 0.0))

    bpy.ops.render.render(write_still=True)
    return 0


if __name__ == "__main__":
    import mathutils

    raise SystemExit(main())
