#!/usr/bin/env python3
"""Verify that preset-generated geometry matches V2 reference values."""

from openmfd.devices import TwoCompartmentDeviceConfig

# Create preset
preset = TwoCompartmentDeviceConfig(
    device_name="2_compartment_96_well_300um_suex200_v27",
    cure_temp=100,
    grid_size=(6, 8),
)

# V2 Reference values
V2_VALUES = {
    "WELLS_POS": 4.5,
    "WELL_RAD": 2.5,
    "CHAN_GAP": 0.03,
    "CHAN_W": 0.01,
    "CHAN_L": 0.3,
    "CHAN_L_EXTRA": 6.0,
    "NUM_CHANS": 83,
    "CHAMBER_LEN_UNTIL": 4.5,
    "CHAMBER_WIDTH": 5.0,
    "CASING_X": 18.0,
    "CASING_Y": 9.0,
    "CHAMBER_HOLE_DIMS": (2, 2),
    "INSERT_PIN_OFFSET": -0.5,
}

# Preset values
PRESET_VALUES = {
    "WELLS_POS": preset.wells_pos,
    "WELL_RAD": preset.well_radius,
    "CHAN_GAP": preset.channel_gap,
    "CHAN_W": preset.channel_width,
    "CHAN_L": preset.channel_length,
    "CHAN_L_EXTRA": preset.channel_length_extra,
    "NUM_CHANS": preset.num_channels,
    "CHAMBER_LEN_UNTIL": preset.chamber_len_until,
    "CHAMBER_WIDTH": preset.chamber_width,
    "CASING_X": preset.casing_x,
    "CASING_Y": preset.casing_y,
    "CHAMBER_HOLE_DIMS": preset.insert_hole_dims,
    "INSERT_PIN_OFFSET": preset.insert_pin_offset,
}

# Compare
print("=" * 80)
print("GEOMETRY VERIFICATION: Preset vs V2 Reference")
print("=" * 80)

all_match = True
for key in V2_VALUES:
    v2_val = V2_VALUES[key]
    preset_val = PRESET_VALUES[key]
    match = v2_val == preset_val
    all_match = all_match and match

    status = "✅" if match else "❌"
    print(f"{status} {key:25s} V2: {str(v2_val):>10} | Preset: {str(preset_val):>10}")

print("=" * 80)

# Check channel configurations
print("\nCHANNEL CONFIGURATION CHECK:")
print("-" * 80)

# Bottom layer (should use extra length)
bottom_channels = preset.channels_config(use_extra_length=True)
print(f"Bottom layer channel length: {bottom_channels.length} (expected: {V2_VALUES['CHAN_L'] + V2_VALUES['CHAN_L_EXTRA']})")
bottom_match = bottom_channels.length == (V2_VALUES['CHAN_L'] + V2_VALUES['CHAN_L_EXTRA'])
print(f"  {'✅ MATCH' if bottom_match else '❌ MISMATCH'}")

# Top layer (should NOT use extra length)
top_channels = preset.channels_config(use_extra_length=False)
print(f"Top layer channel length: {top_channels.length} (expected: {V2_VALUES['CHAN_L']})")
top_match = top_channels.length == V2_VALUES['CHAN_L']
print(f"  {'✅ MATCH' if top_match else '❌ MISMATCH'}")

print("=" * 80)

# Check well positions
print("\nWELL POSITIONS CHECK:")
print("-" * 80)
wells_cfg = preset.wells_config()
print(f"Well positions: {wells_cfg.positions}")
print(f"Expected: [({V2_VALUES['WELLS_POS']}, 0.0), (-{V2_VALUES['WELLS_POS']}, 0.0)]")
wells_match = (
    wells_cfg.positions[0] == (V2_VALUES['WELLS_POS'], 0.0) and
    wells_cfg.positions[1] == (-V2_VALUES['WELLS_POS'], 0.0)
)
print(f"  {'✅ MATCH' if wells_match else '❌ MISMATCH'}")

print("=" * 80)

if all_match and bottom_match and top_match and wells_match:
    print("\n🎉 ALL CHECKS PASSED! Preset geometry matches V2 reference.")
else:
    print("\n⚠️  SOME CHECKS FAILED! Review mismatches above.")
    exit(1)

