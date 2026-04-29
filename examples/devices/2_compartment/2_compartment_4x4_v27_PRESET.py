#!/usr/bin/env python3
"""2-Compartment 4x4 Device - Preset-Based Configuration.

This example demonstrates the power of inheritance in the preset system.
FourByFourDeviceConfig inherits from TwoCompartmentDeviceConfig and only
overrides the 8 parameters that differ for 4x4 format.

Expected line count: ~50 lines (vs 240 in REFACTORED version)
Reduction: 79% from REFACTORED
"""

from pathlib import Path

# OpenMFD imports
from openmfd.devices import (
    FourByFourDeviceConfig,
    build_device_stack,
    create_wafer_walls,
)
from openmfd.inserts import build_insert
from openmfd.export import export_scad

# ============================================================================
# Configuration (Preset-Based - Use 4x4 Defaults!)
# ============================================================================

# Create preset - FourByFourDeviceConfig has all the right defaults!
preset = FourByFourDeviceConfig(
    device_name="2_compartment_4x4_300um_suex200_v27",
    cure_temp=100,
    # That's it! All 4x4-specific parameters are already set as defaults.
    # No need to override wells_pos, well_radius, casing_x, casing_y, etc.
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
    # 3D INSERT GENERATION
    # ========================================================================
    
    print("Generating 4x4 array insert...")
    array_insert = build_insert(
        config=preset.insert_config(),
        grid_size=preset.grid_size,
        alignment_offset=preset.alignment_offset,
    )
    
    save_models(BASE_PATH, {f"{preset.device_name}_wells_insert": array_insert})
    
    if RENDER_INSERT_STL:
        from openmfd.export import render_stl_with_viewscad
        print("Rendering insert STL (this may take 5-10 minutes)...")
        render_stl_with_viewscad(
            array_insert,
            BASE_PATH / f"{preset.device_name}_wells_insert.stl"
        )
        print(f"Saved: {BASE_PATH / f'{preset.device_name}_wells_insert.stl'}")
    else:
        print(f"⏭️  Skipping STL render (set RENDER_INSERT_STL=True to enable)")
    
    # Generate single insert
    print("\nGenerating single insert...")
    single_insert = build_insert(config=preset.insert_config(), grid_size=(1, 1))
    save_models(BASE_PATH, {f"{preset.device_name}_single_insert": single_insert})
    
    # ========================================================================
    # 2D DEVICE GENERATION
    # ========================================================================
    
    print("\nGenerating 2D device layers...")
    device_stack = build_device_stack(preset.bottom_layer(), preset.top_layer())
    
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
    walls = create_wafer_walls(
        diameter=preset.wafer_size,
        thickness=preset.wall_thickness,
        grid_size=preset.grid_size,
        dims=[preset.casing_x, preset.casing_y, 0],
        height=preset.wall_height,
        padx=preset.wall_padx,
        pady=preset.wall_pady
    )
    
    # Create wafer mask with walls
    from openmfd.devices import create_wafer_mask
    walls_mask = create_wafer_mask(
        wafer_size=preset.wafer_size,
        flat_length=preset.wafer_flat_length,
        mask=walls[2],  # walls_combined
        grid_size=preset.grid_size,
        dims=[preset.casing_x, preset.casing_y, 0],
        wafer_line_thickness=0.3,
        outer_mask_thickness=1.0
    )
    
    save_models(BASE_PATH, {f"{preset.device_name}_walls": walls_mask})
    
    print(f"\n✅ All files saved to: {BASE_PATH}")
    print(f"📊 Generated {len(list(BASE_PATH.glob('*.scad')))} SCAD files")
