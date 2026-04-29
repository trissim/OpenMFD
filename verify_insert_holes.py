#!/usr/bin/env python3
"""Verify insert hole positions and alignment marks."""

from openmfd.devices import TwoCompartmentDeviceConfig

# Create preset
preset = TwoCompartmentDeviceConfig(
    device_name="2_compartment_96_well_300um_suex200_v27",
    cure_temp=100,
    grid_size=(6, 8),
)

# V2 Reference values
WELLS_POS = 4.5
INSERT_PIN_OFFSET = -0.5
UNITS_FROM_CENTER = (7, 4.75)

print("=" * 80)
print("INSERT HOLE POSITIONS VERIFICATION")
print("=" * 80)

# Expected insert hole positions
expected_insert_hole_pos = WELLS_POS + INSERT_PIN_OFFSET  # 4.5 + (-0.5) = 4.0
expected_positions = [(expected_insert_hole_pos, 0.0), (-expected_insert_hole_pos, 0.0)]

print(f"\nV2 Reference:")
print(f"  WELLS_POS = {WELLS_POS}")
print(f"  INSERT_PIN_OFFSET = {INSERT_PIN_OFFSET}")
print(f"  Insert hole offset from center = {expected_insert_hole_pos}")
print(f"  Expected positions: {expected_positions}")

# Get preset values
top_layer = preset.top_layer()
insert_holes_config = top_layer.device.insert_holes

print(f"\nPreset:")
print(f"  wells_pos = {preset.wells_pos}")
print(f"  insert_pin_offset = {preset.insert_pin_offset}")
print(f"  Insert hole offset from center = {preset.wells_pos + preset.insert_pin_offset}")
print(f"  Actual positions: {insert_holes_config.well_positions}")
print(f"  Offset applied: {insert_holes_config.offset}")

# Verify
positions_match = insert_holes_config.well_positions == expected_positions
offset_correct = insert_holes_config.offset == 0.0

print(f"\n{'✅' if positions_match else '❌'} Insert hole positions match: {positions_match}")
print(f"{'✅' if offset_correct else '❌'} Offset is 0.0 (already applied to positions): {offset_correct}")

print("\n" + "=" * 80)
print("ALIGNMENT MARKS VERIFICATION")
print("=" * 80)

print(f"\nV2 Reference:")
print(f"  UNITS_FROM_CENTER = {UNITS_FROM_CENTER}")

print(f"\nPreset:")
print(f"  units_from_center = {preset.units_from_center}")

array_config = preset.array_config()
print(f"  Array config units_from_center = {array_config.units_from_center}")

units_match = preset.units_from_center == UNITS_FROM_CENTER
print(f"\n{'✅' if units_match else '❌'} Units from center match: {units_match}")

print("\n" + "=" * 80)

if positions_match and offset_correct and units_match:
    print("\n🎉 ALL CHECKS PASSED!")
else:
    print("\n⚠️  SOME CHECKS FAILED!")
    exit(1)

