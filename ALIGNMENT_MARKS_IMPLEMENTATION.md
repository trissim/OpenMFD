# Alignment Marks Implementation

## Overview

This document describes the implementation of alignment marks for multi-layer photolithography in the `openmfd` package. Alignment marks are critical for precise layer-to-layer registration in microfluidic device fabrication.

## Problem Statement

The original implementation had a fundamental misunderstanding of how alignment marks work in the context of wafer mask generation:

1. **Incorrect approach**: Used `difference()` to subtract hollow marks from the array
2. **Issue**: Nested `difference()` operations caused marks to be "protected" from wafer mask subtraction
3. **Result**: Hollow marks (for top layer) were invisible in the final DXF output

## Legacy Behavior Analysis

From `make_device.py` line 263:
```python
return solid.union()(*masks, unit)  # ALWAYS union, for both full and hollow!
```

**Key insight**: The legacy code ALWAYS uses `union()` to add marks to the array, regardless of mode. The difference between "full" and "hollow" is in the **mark geometry**, not the boolean operation.

### Mark Types

1. **Full marks (bottom layer)**:
   - Two L-shapes rotated 180° apart
   - Form a solid crosshair (+) at their intersection
   - Used for bottom layer (channels)

2. **Hollow marks (top layer)**:
   - Outer crosshair minus inner crosshair
   - Creates a ring-shaped mark
   - When subtracted by wafer mask, creates registration holes
   - Used for top layer (wells/chambers)

## Implementation

### New Functions

#### `create_single_L_mark(corner_length, thickness_divisor=3.0)`
Creates a single L-shaped mark from two perpendicular rectangles.

**Parameters**:
- `corner_length`: Length of L-mark arms
- `thickness_divisor`: Divisor for mark thickness (default: 3.0)

**Returns**: L-shaped OpenSCAD object

#### `create_full_alignment_mark(corner_length, thickness_divisor=8.0)`
Creates a solid crosshair by combining two L-shapes rotated 180° apart.

**Algorithm**:
1. Create base L-shape using `create_single_L_mark()`
2. Create top-right L: rotate 180°, translate by `[thickness/2, thickness/2]`
3. Create bottom-left L: rotate 0°, translate by `[-thickness/2, -thickness/2]`
4. Union both L-shapes to form crosshair

**Parameters**:
- `corner_length`: Length of corner mark arms
- `thickness_divisor`: Divisor for mark thickness (default: 8.0)

**Returns**: Solid crosshair OpenSCAD object

#### `create_alignment_marks(array, dims, grid_size, alignment_mode="full", units_from_center=None, corner_length=None)`
Adds alignment marks to a device array.

**Alignment Modes**:
- `"full"`: Solid crosshair marks (for bottom layer)
- `"hollow"`: Hollow ring marks (for top layer)
- `"partial"`: Marks only at specified corners (future)
- `None`: No alignment marks

**Mark Positioning**:
- If `units_from_center` is specified: Marks at 4 cardinal positions (right, top, left, bottom)
- If `units_from_center` is None: Marks at array corners

**Critical Implementation Detail**:
```python
# ALWAYS use union() to add marks to array (legacy behavior)
# The wafer mask's difference() operation will handle the subtraction
return union()(array, all_marks)
```

This ensures that:
- Solid marks get subtracted by wafer mask → visible on photomask
- Ring marks get subtracted by wafer mask → create registration holes

### Modified Functions

#### `create_device_array()` in `arrays.py`
Added alignment mark support:
- New parameters: `alignment`, `units_from_center`, `alignment_offset`, `alignment_mark_size`
- Calls `create_alignment_marks()` when `alignment` is specified
- Applies alignment offset before/after adding marks

**Device Positioning Fix**:
```python
# Each device is positioned so its BOTTOM-LEFT CORNER is at the grid position
offset_x = dims[0] / 2.0
offset_y = dims[1] / 2.0
positioned_unit = solid.translate([row * dims[0] + offset_x, col * dims[1] + offset_y])(unit)
```

This ensures devices are centered in their grid cells, with the first device's bottom-left corner at [0, 0].

## Wafer Mask Integration

The wafer mask structure is:
```
difference() {  // From create_wafer_mask()
    wafer_outline
    union() {   // Device array with marks
        array
        alignment_marks  // Added via union()
    }
}
```

When the wafer mask subtracts the array:
- **Bottom layer**: Subtracts `union(array, solid_marks)` → both array and marks removed from wafer
- **Top layer**: Subtracts `union(array, ring_marks)` → array removed, ring marks create holes

## Usage Example

```python
from openmfd.devices import create_device_array

# Bottom layer with solid alignment marks
bottom_array = create_device_array(
    channels, dims=[18, 9, 0], grid_size=[6, 8],
    dxf=True, alignment="full",
    units_from_center=(3, 4),
    alignment_mark_size=1.0
)

# Top layer with hollow alignment marks
top_array = create_device_array(
    wells, dims=[18, 9, 0], grid_size=[6, 8],
    dxf=True, alignment="hollow",
    units_from_center=(3, 4),
    alignment_mark_size=1.0
)
```

## Files Modified

1. **`openmfd/devices/alignment.py`** (NEW)
   - `create_single_L_mark()`: Single L-shaped mark
   - `create_full_alignment_mark()`: Solid crosshair from two L-shapes
   - `create_alignment_marks()`: Add marks to array
   - Additional functions: `create_crosshair_mark()`, `create_vernier_scale()`, `create_alignment_target()`, etc.

2. **`openmfd/devices/arrays.py`**
   - Updated `create_device_array()` to support alignment marks
   - Fixed device positioning to center devices in grid cells
   - Added alignment offset support

3. **`openmfd/devices/__init__.py`**
   - Exported new alignment functions
   - Exported wafer, text, and outline functions

4. **`examples/devices/2_compartment/2_compartment_96_well_v27_OPENMFD_ONLY.py`**
   - Example usage of alignment marks
   - Demonstrates full vs hollow alignment modes

## Testing

Verified with 2-compartment 96-well device (6x8 grid):
- ✅ Bottom layer: 4 solid crosshair marks visible in DXF
- ✅ Top layer: 4 hollow ring marks (registration holes) visible in DXF
- ✅ Marks positioned at cardinal positions (right, top, left, bottom)
- ✅ Marks centered at wafer center with proper offset

## Documentation Requirements

### Sphinx Documentation

The following sections need to be added to `docs/source/api/devices.rst`:

1. **Alignment Marks Section**:
   - Overview of alignment mark types
   - Explanation of full vs hollow modes
   - Mark positioning strategies
   - Integration with wafer masks

2. **API Reference**:
   - `create_single_L_mark()`
   - `create_full_alignment_mark()`
   - `create_alignment_marks()`
   - `create_crosshair_mark()`
   - `create_vernier_scale()`
   - `create_alignment_target()`
   - `create_custom_alignment_pattern()`

3. **Examples**:
   - Basic alignment mark usage
   - Multi-layer device with alignment
   - Custom mark positioning

4. **Best Practices**:
   - When to use full vs hollow marks
   - Mark size selection
   - Positioning for optimal alignment

### User Guide

Add section on multi-layer alignment:
- Purpose of alignment marks
- How to design for alignment
- Troubleshooting alignment issues
- Verification in DXF viewer

## Future Enhancements

1. **Partial alignment mode**: Allow specifying which corners get marks
2. **Custom mark shapes**: Support for different mark geometries
3. **Vernier scales**: Fine alignment with vernier patterns
4. **Alignment targets**: Concentric ring targets for optical alignment
5. **Mark validation**: Check mark visibility and positioning

## References

- Legacy implementation: `make_device.py` lines 229-263
- Wafer mask generation: `openmfd/devices/wafer.py`
- Device array generation: `openmfd/devices/arrays.py`

