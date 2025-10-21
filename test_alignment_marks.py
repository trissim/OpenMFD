"""Test alignment marks generation."""

import solid
from openmfd.devices.alignment import create_alignment_marks

# Create a simple test array
test_array = solid.square([10, 10])

# Test full alignment (solid marks)
full_marks = create_alignment_marks(
    test_array,
    dims=[5, 5, 0],
    grid_size=[2, 2],
    alignment_mode="full",
    units_from_center=(1, 1),
    corner_length=1.0
)

# Test hollow alignment (subtracted marks)
hollow_marks = create_alignment_marks(
    test_array,
    dims=[5, 5, 0],
    grid_size=[2, 2],
    alignment_mode="hollow",
    units_from_center=(1, 1),
    corner_length=1.0
)

# Render to SCAD
solid.scad_render_to_file(full_marks, "test_full_marks.scad")
solid.scad_render_to_file(hollow_marks, "test_hollow_marks.scad")

print("Generated test files:")
print("  test_full_marks.scad - Should use union()")
print("  test_hollow_marks.scad - Should use difference()")

