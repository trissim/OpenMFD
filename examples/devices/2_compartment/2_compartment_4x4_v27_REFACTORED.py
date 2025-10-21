"""
2-Compartment 4x4 Device - Refactored to use OpenMFD package

This is a refactored version of 2_compartment_4x4_v27_300um_suex200.py
using the new openmfd package structure.

Original: 2_compartment_4x4_v27_300um_suex200.py
Version: 27
SU-8 Height: 200μm
"""

from pathlib import Path
import solid

# Import from new openmfd package
from openmfd.geometry import (
    WellConfiguration,
    ChannelConfiguration,
    ChamberConfiguration,
    wells_pos_from_center_2,
)
from openmfd.devices import (
    DeviceConfiguration,
    CasingConfiguration,
    ArrayConfiguration,
    assemble_device,
    create_device_array_from_config,
)
from openmfd.export import (
    export_scad,
)

# ============================================================================
# Configuration Parameters
# ============================================================================

VERSION = 27
BASE_PATH = Path(f"./designs/open_chamber/2_compartment_4x4_300um_suex200_v{VERSION}/")
DEVICE_NAME = f"2_compartment_4x4_300um_suex200_v{VERSION}"

# Device geometry
WELLS_POS = 3.0  # Distance between wells
WELL_RAD = 2.0   # Well radius
CHAN_GAP = 0.03  # Gap between channels
CHAN_W = 0.01    # Channel width
CHAN_L = 0.3     # Channel length
CHAN_L_EXTRA = 6.0  # Extra channel length
NUM_CHANS = int(WELL_RAD / (CHAN_GAP + CHAN_W))

# Chamber parameters
CHAMBER_LEN_UNTIL = WELLS_POS
CHAMBER_WIDTH = WELL_RAD * 2

# Casing dimensions
ROWS = 1
COLUMNS = 2
CASING_X = 12.0
CASING_Y = 6.0

# Array parameters
GRID_SIZE = [4, 4]
DIMS = [17.5, 17.5, 0]
ALIGNMENT_OFFSET = [(DIMS[0] - CASING_X * ROWS) / 2.0, (DIMS[1] - CASING_Y * COLUMNS) / 2]
UNITS_FROM_CENTER = (2.3, 2.3)
ALIGNMENT_MARK_SIZE = 1

# Wafer parameters
WAFER_SIZE = 100
WAFER_FLAT_LEN = 32.5
WAFER_THICKNESS = 0.500
OUTER_MASK_THICKNESS = 1
WAFER_LINE_THICKNESS = 0.3

# Wall parameters
WALL_HEIGHT = 10
WALL_THICKNESS = 7
WALL_PADX = 0
WALL_PADY = 0

# Outline parameters
GLASS_SIZE = [110, 74]
GLASS_ERROR = 4
OUTLINE_ALIGNMENT_THICKNESS = 1

# PDMS curing parameters
CURE_TEMP = 0  # Celsius

# ============================================================================
# Helper Functions (from legacy make_device.py)
# ============================================================================

def scale_percent_pdms_heat_shrinkage(cure_temp):
    """Calculate PDMS shrinkage based on curing temperature."""
    # PDMS shrinks ~0.2% per 10°C above room temp
    shrinkage_percent = 1.0 - (cure_temp * 0.002)
    cure_text = f"Cure at {cure_temp}°C (scale: {shrinkage_percent:.4f})"
    return shrinkage_percent, cure_text


def save_model(model, base_path, name, dxf=True):
    """Save model to SCAD file."""
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    
    scad_path = base_path / f"{name}.scad"
    solid.scad_render_to_file(model, str(scad_path))
    print(f"Saved: {scad_path}")


# ============================================================================
# Main Device Generation
# ============================================================================

def main():
    """Generate 2-compartment 4x4 device using new OpenMFD package."""
    
    # Create output directory
    BASE_PATH.mkdir(parents=True, exist_ok=True)
    
    # Calculate PDMS shrinkage
    scale_percent, cure_text = scale_percent_pdms_heat_shrinkage(CURE_TEMP)
    print(f"PDMS Shrinkage: {cure_text}")
    
    # ========================================================================
    # Step 1: Create Single Device Unit using OpenMFD
    # ========================================================================
    
    print("\n=== Creating Single Device Unit ===")

    # Calculate well positions (2 wells separated by WELLS_POS distance)
    well_positions = wells_pos_from_center_2(WELLS_POS)
    print(f"Well positions: {well_positions}")

    # Configure wells
    wells_config = WellConfiguration(
        radius=WELL_RAD,
        height=None,  # 2D geometry for DXF export
        positions=well_positions,
        shape="circle"
    )
    
    # Configure channels
    channels_config = ChannelConfiguration(
        length=CHAN_L,
        width=CHAN_W,
        height=0.2,  # 200μm SU-8 height
        num_channels=NUM_CHANS,
        spacing=CHAN_GAP
    )
    
    # Configure chambers
    chambers_config = ChamberConfiguration(
        height=0.2,  # 200μm SU-8 height
        width=CHAMBER_WIDTH,
        len_until=CHAMBER_LEN_UNTIL
    )
    
    # Configure device casing
    casing_config = CasingConfiguration(
        x=CASING_X,
        y=CASING_Y,
        z=0  # 2D device
    )
    
    # Create device configuration
    device_config = DeviceConfiguration(
        casing=casing_config,
        wells_config=wells_config,
        channels_config=channels_config,
        chambers_config=chambers_config,
        add_wells=True,
        add_channels=True,
        add_chambers=True,
        dxf=True
    )
    
    # Assemble single device unit
    print("Assembling device...")
    device_geometry = assemble_device(device_config)

    # Export single unit
    print("Exporting single unit...")
    export_scad(device_geometry, BASE_PATH / f"{DEVICE_NAME}_single_aligned.scad")
    
    # ========================================================================
    # Step 2: Create Device Array (4x4 grid)
    # ========================================================================

    print("\n=== Creating 4x4 Device Array ===")

    # Configure array
    array_config = ArrayConfiguration(
        rows=GRID_SIZE[0],
        columns=GRID_SIZE[1],
        alignment="full",
        units_from_center=UNITS_FROM_CENTER
    )

    # Create device array using config
    array_geometry = create_device_array_from_config(
        unit=device_geometry,
        casing=casing_config,
        array_config=array_config,
        dxf=True
    )

    # Apply PDMS shrinkage scaling
    if scale_percent != 1.0:
        print(f"Applying PDMS shrinkage scale: {scale_percent}")
        array_geometry = solid.scale([scale_percent, scale_percent, 1.0])(array_geometry)
    
    # Export array
    print("Exporting device array...")
    export_scad(array_geometry, BASE_PATH / f"{DEVICE_NAME}_array_4x4.scad")
    
    # ========================================================================
    # Summary
    # ========================================================================
    
    print("\n=== Export Summary ===")
    print(f"Output directory: {BASE_PATH}")
    print(f"Device name: {DEVICE_NAME}")
    print(f"Grid size: {GRID_SIZE[0]}x{GRID_SIZE[1]}")
    print(f"Wells: 2 @ {WELL_RAD * 2}mm diameter")
    print(f"Channels: {NUM_CHANS} @ {CHAN_W}mm width")
    print(f"SU-8 height: {channels_config.height}mm ({channels_config.height * 1000}μm)")
    print(f"PDMS scale: {scale_percent:.4f}")
    print("\nFiles generated:")
    print(f"  - {DEVICE_NAME}_single_aligned.scad")
    print(f"  - {DEVICE_NAME}_array_4x4.scad")
    print("\nNext steps:")
    print("  1. Open SCAD files in OpenSCAD to visualize")
    print("  2. Export to DXF for photolithography masks")
    print("  3. Export to STL for 3D printing molds")


if __name__ == "__main__":
    main()

