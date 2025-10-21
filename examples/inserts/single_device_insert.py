#!/usr/bin/env python3
"""
Generate 3D printed well inserts for a single 2-compartment device.

This example generates inserts for just one device (2 wells) instead of a full
96-well array, making it much faster to load and preview in OpenSCAD.

Usage:
    python examples/inserts/single_device_insert.py
"""

import solid
from solid.utils import scad_render_to_file

from openmfd.inserts.config import (
    TaperConfiguration,
    InsertConfiguration,
    PinConfiguration,
    SkirtConfiguration,
)
from openmfd.inserts.wells import assemble_well_inserts


def main():
    """Generate well inserts for a single 2-compartment device."""
    
    # Device parameters (from legacy 2_compartment_96_well_v27)
    well_spacing = 9.0  # mm between well centers
    
    # Well positions for a single device (2 wells)
    well_positions = [
        (0, -well_spacing / 2),  # Left well
        (0, well_spacing / 2),   # Right well
    ]
    
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
        well_radius=3.2,
        channel_length=1.0,
    )
    
    # Configure alignment pins
    pin_config = PinConfiguration(
        dims=(1.85, 1.85),
        height=0.06,
        inner_height=2.0,
        offset=-0.5,
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
        well_positions=well_positions,
        insert_config=insert_config,
        pin_config=pin_config,
        skirt_config=skirt_config,
        pdms_scale=0.8,  # PDMS shrinkage compensation
    )
    
    # Export to SCAD file
    output_file = "designs/inserts/single_device_insert.scad"
    print(f"Writing to {output_file}...")
    scad_render_to_file(insert_assembly, output_file)
    print(f"✓ Done! Open {output_file} in OpenSCAD to preview.")
    print("\nTo generate STL:")
    print(f"  openscad -o designs/inserts/single_device_insert.stl {output_file}")


if __name__ == "__main__":
    main()
