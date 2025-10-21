# Centering Bug Analysis - Context Handoff

**Date**: 2025-10-21  
**Status**: 🔴 CRITICAL BUGS REMAINING  
**Objective**: Fix device centering and alignment mark visibility issues

---

## 🐛 Remaining Bugs (User Report)

### Bug 1: Devices NOT centered on wafer
**Symptom**: Devices appear in upper-right quadrant instead of centered on wafer  
**Expected**: Devices should be centered at wafer center `[cx, cy]`  
**Actual**: Devices appear to start at `[0, 0]` and are NOT translated to center

### Bug 2: Alignment marks partially visible on bottom layer
**Symptom**: Bottom layer shows "half the cross" (only partial alignment marks visible)  
**Expected**: 4 full alignment marks at cardinal positions (right, top, left, bottom)  
**Actual**: Marks are cut off or only partially visible

### Bug 3: Alignment marks missing on top layer
**Symptom**: Top layer (with wells) shows NO alignment marks  
**Expected**: Hollow alignment marks (subtracted from geometry) at 4 cardinal positions  
**Actual**: No marks visible at all

---

## 📊 Current Architecture

### Centering System (SINGLE SOURCE OF TRUTH)

```python
# openmfd/devices/wafer.py
def compute_wafer_center(grid_size: List[int], dims: List[float]) -> Tuple[float, float]:
    """SINGLE SOURCE OF TRUTH for wafer centering coordinates."""
    return (grid_size[0] * dims[0] / 2.0, grid_size[1] * dims[1] / 2.0)
```

**For 6x8 grid with dims=[18, 9, 0]:**
- `cx = 6 * 18 / 2 = 54`
- `cy = 8 * 9 / 2 = 36`
- **Wafer center: (54, 36)**

### Current Centering Implementation

**Elements that ARE centered:**
1. ✅ **Wafer outline** - `create_wafer()` translates to `[cx, cy]`
2. ✅ **Glass outline** - `create_glass_outline()` translates to `[cx, cy]`
3. ✅ **Text** - `create_centered_text()` translates to `[cx, cy]`

**Elements that are NOT centered:**
1. ❌ **Device array** - Created at `[0, 0]` in `create_device_array()`
2. ❌ **Alignment marks** - Positioned relative to array at `[0, 0]`

### Attempted Fix (INCOMPLETE)

**File**: `openmfd/devices/wafer.py`, lines 178-206  
**Function**: `create_wafer_mask()`

```python
# Center the device features at wafer center
cx, cy = compute_wafer_center(grid_size, dims)

# Calculate translation to center devices
device_width = grid_size[0] * dims[0]
device_height = grid_size[1] * dims[1]
translate_x = (cx - device_width / 2) * shrinkage_scale
translate_y = (cy - device_height / 2) * shrinkage_scale

# Apply alignment offset to devices if provided
if alignment_offset is not None:
    translate_x -= alignment_offset[0] * shrinkage_scale
    translate_y -= alignment_offset[1] * shrinkage_scale

# Center the mask (device features)
centered_mask = solid.translate([translate_x, translate_y])(mask)

# Subtract device features from wafer outline
return difference()(wafer_outline, centered_mask)
```

**Why this doesn't work:**
- This ONLY centers the devices when they're subtracted from the wafer outline
- The devices themselves (in the SCAD file) are still at `[0, 0]`
- The alignment marks are added to the array BEFORE it's passed to `create_wafer_mask()`
- So alignment marks are positioned relative to `[0, 0]`, not `[cx, cy]`

---

## 🔍 Root Cause Analysis

### Problem 1: Device Array Positioning

**Current flow:**
```
create_device_array() 
  → Creates devices at [0, 0]
  → Adds alignment marks at positions relative to [0, 0]
  → Returns array at [0, 0]

create_wafer_mask(array, ...)
  → Translates array to [cx, cy] for subtraction
  → But this translation is ONLY for the difference() operation
  → The original array is still at [0, 0]
```

**The issue:**
- The example script creates 3 arrays: `bottom`, `top`, `aligned`
- It adds decorations (text, outline) to these arrays
- It then passes each array to `create_wafer_mask()`
- `create_wafer_mask()` translates the array for subtraction, but doesn't return the translated array
- The arrays saved to SCAD files are still at `[0, 0]`

### Problem 2: Alignment Mark Positioning

**Current implementation** (`openmfd/devices/alignment.py`, lines 118-145):

```python
center_x, center_y = width / 2, length / 2

if units_from_center is not None:
    x_offset = units_from_center[0] * dims[0]  # 7 * 18 = 126
    y_offset = units_from_center[1] * dims[1]  # 4.75 * 9 = 42.75
    
    # Four positions: right, top, left, bottom
    positions = [
        (center_x + x_offset, center_y),          # Right: (54 + 126, 36) = (180, 36)
        (center_x, center_y + y_offset),          # Top: (54, 36 + 42.75) = (54, 78.75)
        (center_x - x_offset, center_y),          # Left: (54 - 126, 36) = (-72, 36)
        (center_x, center_y - y_offset),          # Bottom: (54, 36 - 42.75) = (54, -6.75)
    ]
```

**For 6x8 grid:**
- `width = 6 * 18 = 108`
- `length = 8 * 9 = 72`
- `center_x = 54`, `center_y = 36`

**Calculated positions:**
- Right: `(180, 36)` - **OUTSIDE array bounds** (array width is 108)
- Top: `(54, 78.75)` - **OUTSIDE array bounds** (array height is 72)
- Left: `(-72, 36)` - **NEGATIVE** (outside array)
- Bottom: `(54, -6.75)` - **NEGATIVE** (outside array)

**VERIFIED FROM LEGACY OUTPUT**:

**Bottom layer** (2_compartment_96_well_300um_suex200_v27_bottom.scad):
```
Line 55:  translate(v = [180.0000000000, 36.0000000000, 0])  # Right mark
          union() { ... }  # SOLID marks (added to geometry)
Line 79:  translate(v = [54.0000000000, 78.7500000000, 0])   # Top mark
Line 103: translate(v = [-72.0000000000, 36.0000000000, 0])  # Left mark
Line 127: translate(v = [54.0000000000, -6.7500000000, 0])   # Bottom mark
```

**Top layer** (2_compartment_96_well_300um_suex200_v27_top.scad):
```
Line 55:  translate(v = [180.0000000000, 36.0000000000, 0])  # Right mark
          difference() { ... }  # HOLLOW marks (subtracted from geometry)
Line 103: translate(v = [54.0000000000, 78.7500000000, 0])   # Top mark
Line 151: translate(v = [-72.0000000000, 36.0000000000, 0])  # Left mark
Line 199: translate(v = [54.0000000000, -6.7500000000, 0])   # Bottom mark
```

**KEY INSIGHT**: The marks ARE positioned outside the device array bounds, but they're INSIDE the wafer (150mm diameter). This is CORRECT behavior! The marks are meant to be in the empty space between the device array and the wafer edge.

**Alignment mark structure verified:**
- Bottom layer: `union()` - Solid L-shaped marks added to geometry ✅
- Top layer: `difference()` - Hollow L-shaped marks subtracted from geometry ✅
- Both layers have marks at identical positions ✅

### Problem 3: Legacy Behavior Mismatch

**Legacy code** (`make_device.py`, lines 251-257):

```python
center = (width / 2, length / 2)
mask_pos = lambda x,y : (center[0] + x*(float(units_from_center[0])*dims[0]), 
                         center[1] + y*(float(units_from_center[1])*dims[1]))
positions = []
positions.append(mask_pos(1, 0))   # Right
positions.append(mask_pos(0, 1))   # Top
positions.append(mask_pos(-1, 0))  # Left
positions.append(mask_pos(0, -1))  # Bottom
```

**This is IDENTICAL to the new implementation**, so the bug exists in BOTH!

**BUT**: The legacy code works because it positions marks relative to the array's local coordinate system, and the array is ALREADY centered when passed to `add_wafer_to_mask()`.

---

## 🎯 Required Fixes

### Fix 1: Center the device array BEFORE adding decorations

**Location**: `examples/devices/2_compartment/2_compartment_96_well_v27_OPENMFD_ONLY.py`

**Current code** (lines 191-208):
```python
# Create arrays with alignment marks
arrays = {
    'bottom': create_device_array(...),
    'top': create_device_array(...),
}

# Add decorations
arrays['bottom'] = solid.union()(arrays['bottom'], text)
arrays['top'] = solid.union()(arrays['top'], outline)
```

**Required fix**:
```python
from openmfd.devices.wafer import compute_wafer_center

# Create arrays with alignment marks (at [0,0])
arrays = {
    'bottom': create_device_array(...),
    'top': create_device_array(...),
}

# CENTER ARRAYS AT WAFER CENTER (CRITICAL FIX)
cx, cy = compute_wafer_center(GRID_SIZE, DIMS)
device_width = GRID_SIZE[0] * DIMS[0]
device_height = GRID_SIZE[1] * DIMS[1]
translate_x = cx - device_width / 2
translate_y = cy - device_height / 2

arrays = {
    name: solid.translate([translate_x, translate_y])(arr)
    for name, arr in arrays.items()
}

# Add decorations (text and outline are already centered)
arrays['bottom'] = solid.union()(arrays['bottom'], text)
arrays['top'] = solid.union()(arrays['top'], outline)
```

### Fix 2: Remove centering logic from create_wafer_mask()

**Location**: `openmfd/devices/wafer.py`, lines 178-206

**Current code**: Translates mask to center before subtraction

**Required fix**: Remove translation logic since arrays will already be centered

```python
# Subtract device features from wafer outline
# (mask is already centered, no translation needed)
return difference()(wafer_outline, mask)
```

### Fix 3: Fix alignment mark positioning

**Location**: `openmfd/devices/alignment.py`, lines 118-145

**Issue**: `units_from_center` is interpreted as absolute distance, but should be relative to array edges

**Legacy interpretation**:
- `units_from_center=(7, 4.75)` means "7 units from center in X, 4.75 units from center in Y"
- For 6x8 grid: marks at `center ± (7*18, 4.75*9)` = `(54±126, 36±42.75)`
- This places marks OUTSIDE the array

**Correct interpretation** (need to verify with legacy output):
- Marks should be INSIDE the array bounds
- Possibly `units_from_center` means "distance from array edge" not "distance from center"
- OR the legacy code has a different grid_size/dims calculation

**Action needed**: 
1. Check legacy SCAD output to see actual mark positions
2. Reverse-engineer correct positioning formula
3. Update alignment.py accordingly

---

## 📝 Testing Checklist

After fixes are applied:

- [ ] Devices are centered on wafer (visual inspection in OpenSCAD)
- [ ] Wafer outline is centered (already working)
- [ ] Glass outline is centered (already working)
- [ ] Text is centered and visible (already working)
- [ ] Bottom layer shows 4 full alignment marks (solid)
- [ ] Top layer shows 4 full alignment marks (hollow/subtracted)
- [ ] Alignment marks are positioned correctly (not cut off)
- [ ] All 7 files generate successfully
- [ ] PDMS shrinkage scaling applies correctly to all elements

---

## 🔧 Files to Modify

1. **`examples/devices/2_compartment/2_compartment_96_well_v27_OPENMFD_ONLY.py`**
   - Add array centering after `create_device_array()`
   - Before adding decorations

2. **`openmfd/devices/wafer.py`**
   - Remove device centering logic from `create_wafer_mask()`
   - Assume input mask is already centered

3. **`openmfd/devices/alignment.py`**
   - Fix alignment mark positioning formula
   - Ensure marks are within array bounds
   - Match legacy behavior exactly

---

## 📚 Reference Values

**Test case**: 2-compartment 96-well device
- Grid: 6x8 (48 devices)
- Dims: [18, 9, 0]
- Wafer: 150mm diameter, 57.5mm flat
- Units from center: (7, 4.75)
- Alignment offset: [0, 0]
- PDMS shrinkage: 0.8 (100°C cure)

**Expected wafer center**: (54, 36)  
**Expected device array bounds**: [0, 0] to [108, 72] (before centering)  
**Expected centered device bounds**: [-0, -0] to [108, 72] (after centering at wafer center)

---

---

## 🔬 CRITICAL DISCOVERY: Alignment Marks Are Correct!

After examining the legacy SCAD output, the alignment mark positions ARE correct:
- They're positioned OUTSIDE the device array bounds
- But INSIDE the wafer (150mm diameter)
- This is intentional - marks go in the empty space between devices and wafer edge

**The real bug**: The new openmfd code is positioning marks correctly, but the DEVICES are not centered, so the marks appear in the wrong place relative to the wafer!

**Revised root cause**:
1. ✅ Alignment marks are positioned correctly (cardinal positions outside array)
2. ❌ Device array is NOT centered on wafer
3. ❌ This makes marks appear misaligned relative to wafer center

**Simplified fix**: Just center the device arrays at wafer center. The alignment marks will automatically be in the correct position relative to the wafer.

---

---

## 🔬 VERIFICATION: Alignment Marks in Refactored Output

**Tested**: Ran `2_compartment_96_well_v27_OPENMFD_ONLY.py` and verified output

**Bottom layer** (2_compartment_96_well_300um_suex200_v27_bottom.scad):
```
Line 15133: translate(v = [180.0000000000, 36.0000000000])  # Right mark
Line 15141: translate(v = [54.0000000000, 78.7500000000])   # Top mark
Line 15149: translate(v = [-72.0000000000, 36.0000000000])  # Left mark
Line 15157: translate(v = [54.0000000000, -6.7500000000])   # Bottom mark
```
✅ Marks present at correct positions
✅ Using `union()` (solid marks)

**Top layer** (2_compartment_96_well_300um_suex200_v27_top.scad):
```
Line 1501: translate(v = [180.0000000000, 36.0000000000])  # Right mark
Line 1509: translate(v = [54.0000000000, 78.7500000000])   # Top mark
Line 1517: translate(v = [-72.0000000000, 36.0000000000])  # Left mark
Line 1525: translate(v = [54.0000000000, -6.7500000000])   # Bottom mark
```
✅ Marks present at correct positions
❌ Using `union()` instead of `difference()` - **BUG FOUND!**

**Alignment marks code tested independently:**
- Created test script with `alignment_mode="full"` → generates `union()` ✅
- Created test script with `alignment_mode="hollow"` → generates `difference()` ✅
- The `create_alignment_marks()` function IS working correctly!

**Conclusion**: The alignment marks are being generated correctly by the openmfd code, but something in the example script or the wafer mask generation is converting the `difference()` to `union()` for the top layer.

---

**Next steps**:
1. Apply Fix 1 (center device arrays)
2. Investigate why top layer marks are using `union()` instead of `difference()`
3. Check if `create_wafer_mask()` is modifying the geometry incorrectly

---

## 🔬 Investigation Results

### Text Positioning (VERIFIED CORRECT)

Checked generated SCAD file:
```scad
translate(v = [54.0000000000, 36.0000000000]) {
    text(halign = "center", size = 2.0000000000, text = "Cure at 100°C", valign = "center");
}
```

✅ **Text IS at wafer center [54, 36]** - This confirms `compute_wafer_center()` is working correctly.

### Device Positioning (NEEDS INVESTIGATION)

Need to check in SCAD file:
1. Where are the device units positioned?
2. Are they at [0, 0] or at [54, 36]?
3. Where are the alignment marks in the union() structure?

### Alignment Mark Visibility Issue

**Hypothesis**: Alignment marks are being added to the array, but then the array is being scaled by PDMS shrinkage (0.8), which might be moving them outside the wafer bounds.

**Check**: Look at the order of operations in the example script:
1. Create array with alignment marks
2. Add decorations (text, outline)
3. **Scale by shrinkage factor** ← This might break alignment!
4. Pass to `create_wafer_mask()`

If scaling happens AFTER alignment marks are added, the marks will be scaled too, potentially moving them outside bounds.

### Hollow Alignment Marks (Top Layer)

**Issue**: Top layer uses `alignment="hollow"` which should SUBTRACT marks from the array.

**Check in alignment.py** (line 158-159):
```python
elif alignment_mode == "hollow":
    return difference()(array, all_marks)
```

This subtracts marks from the array. If the array is mostly empty (just wells and chambers), subtracting marks might not create visible features.

**Possible issue**: The marks need to be subtracted from SOLID geometry to be visible. If the array has mostly empty space, the subtraction won't show up.

---

## 🎨 Visual Debugging Needed

To properly diagnose, need to:

1. **Open the generated SCAD files in OpenSCAD**
2. **Check the coordinate system** - where is [0, 0]?
3. **Locate the device array** - what are its bounds?
4. **Locate the alignment marks** - are they in the file? Where?
5. **Check the wafer outline** - is it centered at [54, 36]?
6. **Compare with legacy output** - what's different?

**Recommended**: Generate both legacy and new versions side-by-side and compare the SCAD code structure.

