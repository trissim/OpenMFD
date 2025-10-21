#!/usr/bin/env python3
"""
Generate 3D printed well inserts for a single 2-compartment device.

This example generates inserts for just one device (2 wells) instead of a full
96-well array, making it much faster to load and preview in OpenSCAD.

Usage:
    python examples/inserts/single_device_insert.py
"""

from pathlib import Path
import solid

from openmfd.geometry import wells_pos_from_center_2, make_chambers
from openmfd.inserts.config import (
    TaperConfiguration,
    InsertConfiguration,
    PinConfiguration,
    SkirtConfiguration,
)
from openmfd.inserts.wells import assemble_well_inserts


def make_2_compartment_device(well_rad, chan_l, chamber_width, add_chambers):
    """Create a simple 2-compartment device for insert generation.

    This is a simplified version that just creates the chamber geometry
    needed for insert generation (no channels needed for inserts).
    """
    from openmfd.geometry import wells_top_bottom, make_channels

    # Well positions
    wells_pos = 4.5
    well_positions = wells_pos_from_center_2(wells_pos)

    # Create wells
    wells = wells_top_bottom(
        radius=well_rad,
        height=None,
        positions=well_positions,
        dxf=True,
        shape="circle"
    )

    if add_chambers:
        # Create channels to get measurements
        _, measurements = make_channels(
            length=chan_l,
            width=0.01,
            height=0.2,
            num_chans=int(well_rad / 0.04),
            spacing=0.03,
            dxf=True
        )

        # Create chambers
        chambers = make_chambers(
            msrs=measurements,
            height=0.2,
            width=chamber_width,
            len_until=wells_pos,
            dxf=True
        )

        geometry = solid.union()(wells, chambers)
    else:
        geometry = wells

    return (geometry, well_positions), None, None


def main():
    """Generate well inserts for a single 2-compartment device."""

    # Device parameters (from 2_compartment_96_well_v27)
    WELL_RAD = 5.0 / 2.0
    CHAN_L = 0.3
    CHAMBER_WIDTH = WELL_RAD * 2
    WELLS_POS = 4.5

    # Insert parameters
    INSERT_PIN_OFFSET = -0.5

    # Single device dimensions (no array)
    DIMS = [18, 9, 0]
    GRID_SIZE = [1, 1]

    # Well positions for pins
    well_positions = wells_pos_from_center_2(WELLS_POS + INSERT_PIN_OFFSET)

    # Configure outer taper (easier pipetting access)
    outer_taper = TaperConfiguration(
        height=3.8,
        degrees=16,
        extra_length=0.300,
        segments=20,
    )

    # Configure inner taper (liquid containment)
    inner_taper = TaperConfiguration(
        height=0.40,
        degrees=35,
        extra_length=0.91,
        segments=20,
    )

    # Configure well insert geometry
    insert_config = InsertConfiguration(
        outer_taper=outer_taper,
        inner_taper=inner_taper,
        well_radius=WELL_RAD,
        channel_length=CHAN_L,
    )

    # Configure alignment pins
    pin_config = PinConfiguration(
        dims=(1.85, 1.85),
        height=0.06,
        inner_height=2.0,
        offset=INSERT_PIN_OFFSET,
        hole_dims=(2.0, 2.0),
    )

    # Configure sealing skirts
    skirt_config = SkirtConfiguration(
        thickness1=0.75,
        height1=0.66,
        empty1=0.3,
        thickness2=0.8,
        height2=0.04,
    )

    # Generate the complete insert assembly
    print("Generating well inserts for single device (2 wells)...")
    insert_assembly = assemble_well_inserts(
        device_function=make_2_compartment_device,
        insert_config=insert_config,
        pin_config=pin_config,
        skirt_config=skirt_config,
        dims=DIMS,
        grid_size=GRID_SIZE,
        well_positions=well_positions,
        alignment_offset=None,
        pdms_scale=0.8,  # PDMS shrinkage compensation
    )

    # Export to SCAD file
    output_dir = Path("designs/inserts")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "single_device_insert.scad"

    print(f"Writing to {output_file}...")
    solid.scad_render_to_file(insert_assembly, str(output_file))
    print(f"✓ Done! Open {output_file} in OpenSCAD to preview.")
    print("\nTo generate STL:")
    print(f"  openscad -o {output_dir}/single_device_insert.stl {output_file}")


if __name__ == "__main__":
    main()
