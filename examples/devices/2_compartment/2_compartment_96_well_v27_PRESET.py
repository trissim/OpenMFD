#!/usr/bin/env python3
"""2-Compartment 96-Well Device - Preset-Based Configuration.

This example demonstrates the preset-based configuration approach using
the TwoCompartmentDeviceConfig preset class.

This is the most concise way to generate devices - just override the
parameters you need to change from the defaults.

Expected line count: ~50 lines (vs 367 in CONFIG_API, 432 in V2)
Reduction: 86% from V2, 85% from CONFIG_API
"""

from pathlib import Path

# OpenMFD imports
from openmfd.devices import (
    TwoCompartmentDeviceConfig,
    build_device_stack,
    create_wafer_walls,
)
from openmfd.inserts import build_insert
from openmfd.export import export_scad

# ============================================================================
# Configuration (Preset-Based - Override Only What You Need!)
# ============================================================================

# Create preset with minimal overrides
preset = TwoCompartmentDeviceConfig(
    device_name="2_compartment_96_well_300um_suex200_v27",
    cure_temp=100,
    grid_size=(6, 8),
    # All other parameters use sensible defaults!
)

# Validate configuration (fail-loud if invalid)
preset.validate()

# ============================================================================
# Output Configuration
# ============================================================================

BASE_PATH = Path("designs/open_chamber") / preset.device_name
BASE_PATH.mkdir(parents=True, exist_ok=True)

RENDER_INSERT_STL = False  # Set to True to render STL (slow)

# ============================================================================
# Helper Functions
# ============================================================================

def save_models(base_path: Path, models: dict):
    """Save all models to SCAD files."""
    for name, model in models.items():
        filepath = base_path / f"{name}.scad"
        export_scad(model, filepath)
        print(f"Saved: {filepath}")

# ============================================================================
# Main Generation
# ============================================================================

if __name__ == "__main__":
    # ========================================================================
    # 3D INSERT GENERATION (Preset-Based)
    # ========================================================================
    
    print(f"Generating {preset.grid_size[0]}x{preset.grid_size[1]} array insert...")
    
    # Generate array insert
    array_insert = build_insert(
        config=preset.insert_config(),
        grid_size=preset.grid_size
    )

    # Generate single insert from the same configuration so SCAD/STL outputs stay paired.
    single_insert = build_insert(config=preset.insert_config(), grid_size=(1, 1))

    save_models(BASE_PATH, {
        f"{preset.device_name}_wells_insert": array_insert,
        f"{preset.device_name}_single_insert": single_insert,
    })

    if RENDER_INSERT_STL:
        from openmfd.export import render_stl_with_viewscad
        insert_models = {
            f"{preset.device_name}_wells_insert": array_insert,
            f"{preset.device_name}_single_insert": single_insert,
        }
        for name, model in insert_models.items():
            render_stl_with_viewscad(model, BASE_PATH / f"{name}.stl")
    else:
        print("⏭️  Skipping STL render (set RENDER_INSERT_STL=True to enable)")
    
    # ========================================================================
    # 2D DEVICE GENERATION (Preset-Based - Single Function Call!)
    # ========================================================================
    
    print("\nGenerating 2D device layers...")
    
    # Build complete device stack (all decorations, scaling, wafer masks handled automatically!)
    device_stack = build_device_stack(preset.bottom_layer(), preset.top_layer())
    
    # Save all device models
    save_models(BASE_PATH, {
        f"{preset.device_name}_bottom": device_stack['bottom'],
        f"{preset.device_name}_top": device_stack['top'],
        f"{preset.device_name}_aligned": device_stack['aligned'],
        f"{preset.device_name}_single_bottom": device_stack['single_bottom'],
        f"{preset.device_name}_single_top": device_stack['single_top'],
        f"{preset.device_name}_single_aligned": device_stack['single_aligned'],
    })
    
    # ========================================================================
    # WALLS
    # ========================================================================
    
    print("\nGenerating walls...")

    walls_outer, walls_inner, walls_combined = create_wafer_walls(
        diameter=preset.wafer_size,
        thickness=3.0,
        grid_size=list(preset.grid_size),
        dims=[preset.casing_x, preset.casing_y, 0],
        height=3.0
    )

    save_models(BASE_PATH, {
        f"{preset.device_name}_walls": walls_combined
    })
    
    # ========================================================================
    # Summary
    # ========================================================================
    
    print(f"\n✅ All files saved to: {BASE_PATH}")
    print(f"📊 Generated 14 SCAD files")
