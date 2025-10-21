# Architectural Fix Plan: Device Centering & Alignment Marks

## 🎯 Problem Statement

Three related bugs in the wafer device layout:
1. **Devices off-center** - Devices appear in upper-right quadrant instead of centered on wafer
2. **Alignment marks cut off** - Only half of the alignment crosses are visible (clipped by wafer edge)
3. **Top layer marks using union()** - Top layer alignment marks use `union()` instead of `difference()` (should be hollow)

## 📐 Understanding the Coordinate System

**Key insight from user:** "the coordinate system is at the single device casing edge"

This means:
- **Origin [0, 0]** = Edge of the first device casing (bottom-left corner)
- **Device array** = 6×8 grid of 18×9mm devices
- **Array bounds** = [0, 0] to [108, 72]
- **Array center** = [54, 36] (midpoint of the array)

**Current positioning:**
```
[0, 0] ─────────────────────────► [108, 0]
  │                                    │
  │     Device Array (108×72mm)        │
  │     Center at [54, 36]             │
  │                                    │
[0, 72] ────────────────────────► [108, 72]
```

**Alignment marks positioned at:**
- Right: [180, 36] (126mm to the right of center)
- Top: [54, 78.75] (42.75mm above center)
- Left: [-72, 36] (126mm to the left of center)
- Bottom: [54, -6.75] (42.75mm below center)

**User clarification:** "the alignment mark positions are okay for the first layer, they should be the same in the second layer"

This means the alignment marks at [180, 36], [-72, 36], etc. are CORRECT. They're positioned outside the device array but inside the wafer when everything is properly centered.

## 🔍 Root Cause Analysis

### The Core Issue: Device Array Not Centered

**From legacy code analysis:**
The legacy `add_wafer_to_mask()` function does this:
```python
# Translate wafer to device array center
wafer_mask = solid.translate([grid_size[0]*dims[0]/2.0, grid_size[1]*dims[1]/2.0])(wafer_mask)
# Result: Wafer centered at [54, 36]
```

So the wafer IS centered at [54, 36] (the device array center).

**But the devices are at [0, 0]!**

This means:
- Wafer center: [54, 36]
- Wafer radius: 75mm
- Wafer bounds: [-21, -39] to [129, 111]
- Device array: [0, 0] to [108, 72] ✅ Fits inside wafer
- Alignment marks: [180, 36], [-72, 36], [54, 78.75], [54, -6.75] ❌ OUTSIDE wafer bounds!

**Wait, that can't be right either...**

Let me check the legacy SCAD output. The wafer is translated to [43.2, 28.8] in the generated file. Let me calculate what this means:

```
Wafer translation: [43.2, 28.8]
Wafer radius: 75mm
Wafer bounds: [43.2-75, 28.8-75] to [43.2+75, 28.8+75]
            = [-31.8, -46.2] to [118.2, 103.8]
```

Now check if alignment marks fit:
- Right mark [180, 36]: 180 > 118.2 ❌ Still outside!
- Left mark [-72, 36]: -72 < -31.8 ❌ Still outside!

**This doesn't make sense. Let me reconsider the wafer size...**

Actually, looking at the SCAD file, the wafer radius is ~76.5mm (line 12), which suggests the wafer diameter might be ~153mm, not exactly 150mm. But even with 153mm diameter (radius 76.5mm), the marks at 180mm and -72mm are still way outside.

**NEW HYPOTHESIS:** The alignment marks are positioned in a DIFFERENT coordinate system than I think. Let me check if there's a translation applied to the entire geometry that I'm missing.

## 🔧 The Architectural Fix

Based on user feedback:
- "the alignment mark positions are okay for the first layer" ✅
- "the devices are still not centered to the wafer" ❌
- "the top layer should also be subtract" (use difference()) ❌

### Fix 1: Center Device Arrays

**The Problem:** Devices are created at [0, 0] but the wafer and all other elements expect them to be centered.

**The Solution:** The `create_wafer_mask()` function ALREADY has centering logic (lines 185-203), but it's being applied to the mask AFTER alignment marks are added. This causes the alignment marks to be positioned incorrectly.

**The Real Fix:** Remove the centering logic from `create_wafer_mask()` and instead center the device arrays BEFORE passing them to `create_wafer_mask()`.

**Why this is better architecturally:**
- Device arrays are created at [0, 0] (local coordinate system)
- They're then translated to be centered in the wafer coordinate system
- The wafer mask just subtracts them as-is (no additional translation needed)
- This keeps the coordinate systems clean and separate

### Fix 2: Top Layer Alignment Marks (Use difference())

**The Problem:** Top layer marks use `union()` instead of `difference()` because we wrap the array in `union()` when adding the outline:

```python
arrays['top'] = create_device_array(..., alignment="hollow", ...)  # Returns difference()
arrays['top'] = solid.union()(arrays['top'], outline)  # Wraps difference() in union() ❌
```

**The Solution:** Add outline to the base geometry BEFORE creating alignment marks:

```python
# Add outline to base geometry first
chamber_wells_with_outline = solid.union()(chamber_wells_single, outline)

# Then create array with alignment marks (difference will be at top level)
arrays['top'] = create_device_array(
    chamber_wells_with_outline, DIMS, GRID_SIZE, dxf=True,
    alignment="hollow", ...
)
```

This way, the `difference()` operation for alignment marks stays at the top level and isn't wrapped in `union()`.

## 📋 Implementation Steps

### Step 1: Fix top layer alignment marks (Use difference())

**File:** `examples/devices/2_compartment/2_compartment_96_well_v27_OPENMFD_ONLY.py`
**Lines:** 180-207

**Change:** Add outline to base geometry BEFORE creating alignment marks

```python
# OLD: Add outline after creating array (wraps difference() in union())
arrays = {
    'top': create_device_array(
        chamber_wells_single, DIMS, GRID_SIZE, dxf=True, alignment="hollow", ...
    ),
}
arrays['top'] = solid.union()(arrays['top'], outline)  # ❌ Wraps difference()

# NEW: Add outline before creating array (preserves difference())
chamber_wells_with_outline = solid.union()(chamber_wells_single, outline)
arrays = {
    'top': create_device_array(
        chamber_wells_with_outline, DIMS, GRID_SIZE, dxf=True, alignment="hollow", ...
    ),
}
# No need to add outline again - it's already in the geometry ✅
```

### Step 2: Center device arrays in example script

**File:** `examples/devices/2_compartment/2_compartment_96_well_v27_OPENMFD_ONLY.py`
**Lines:** After creating arrays (around line 203)

**Change:** Add translation to center arrays before adding to wafer mask

```python
from openmfd.devices.wafer import compute_wafer_center

# Create arrays with alignment marks
arrays = {
    'bottom': create_device_array(...),
    'top': create_device_array(...),
}

# CENTER ARRAYS (NEW CODE)
cx, cy = compute_wafer_center(GRID_SIZE, DIMS)
device_width = GRID_SIZE[0] * DIMS[0]
device_height = GRID_SIZE[1] * DIMS[1]
translate_x = cx - device_width / 2
translate_y = cy - device_height / 2

# Apply centering translation to all arrays
arrays = {
    name: solid.translate([translate_x, translate_y])(arr)
    for name, arr in arrays.items()
}

# Add decorations (text is already centered, so add it after translation)
arrays['bottom'] = solid.union()(arrays['bottom'], text)
# outline is already in top array, so don't add it again
arrays['aligned'] = solid.union()(arrays['top'], arrays['bottom'])
```

### Step 3: Remove centering logic from create_wafer_mask()

**File:** `openmfd/devices/wafer.py`
**Lines:** 185-206

**Change:** Delete the device centering logic (arrays are now centered by the example script)

```python
# DELETE LINES 185-206 (the centering logic)
# The mask geometry is already centered by the example script

# Keep only:
# Subtract device features from wafer outline
return difference()(wafer_outline, mask)
```

## ✅ Implementation Complete!

### Fixes Applied

**Fix 1: Top layer alignment marks (Use difference())** ✅
- Add outline to ARRAY after creation (not to single device)
- This preserves `difference()` operation for alignment marks
- File: `examples/devices/2_compartment/2_compartment_96_well_v27_OPENMFD_ONLY.py` line 209

**Fix 2: Device positioning** ✅
- Offset each device by half casing dimensions [dims[0]/2, dims[1]/2]
- Bottom-left corner of first device casing is now at [0, 0]
- Device centers at [9, 4.5], [27, 4.5], etc. (for 18×9mm casing)
- File: `openmfd/devices/arrays.py` lines 71-83

**Fix 3: Single glass outline** ✅
- Removed outline from single device unit
- Add ONE outline to entire array (already centered at wafer center)
- File: `examples/devices/2_compartment/2_compartment_96_well_v27_OPENMFD_ONLY.py` line 209

**Fix 4: Remove centering from create_wafer_mask()** ✅
- Deleted device centering logic (lines 185-206)
- Wafer mask just subtracts geometry as-is
- File: `openmfd/devices/wafer.py` lines 185-188

### Verification

**SCAD file structure (top layer):**
```
Line 4:  difference() {           // Wafer mask (top level)
Line 51:   scale() {               // PDMS shrinkage
Line 54:     difference() {        // ✅ Alignment marks subtraction!
Line 56:       union() {            // Array of 48 device units
Line 2266:     union() {            // All 4 marks combined (to subtract)
```

**The `difference()` operation IS present on line 54!**

This means the alignment marks SHOULD be hollow (subtracted) when rendered in OpenSCAD.

### Remaining Issue: Device Centering

The centering translation calculated as `[0, 0]` because:
- Device array center: `[54, 36]`
- Device array size: `[108, 72]`
- Translation: `54 - 108/2 = 0`, `36 - 72/2 = 0`

This suggests the devices are already "centered" in their own coordinate system (array spans [0,0] to [108,72], center at [54,36]).

**The issue is that the WAFER needs to be positioned to contain both devices AND alignment marks.**

The user said "the devices are still not centered to the wafer" - this means we need to adjust how the wafer is positioned relative to the devices, OR adjust the alignment mark positions.

## 🧪 Testing Checklist

- [x] Run the example script ✅
- [x] Check SCAD file for `difference()` operation ✅ (present on line 54)
- [ ] Open bottom layer SCAD in OpenSCAD and verify rendering
- [ ] Open top layer SCAD in OpenSCAD and verify rendering
  - [ ] Verify 4 hollow alignment marks are visible
  - [ ] Verify devices are centered on wafer
- [ ] Verify glass outline is centered correctly
- [ ] Verify text is centered correctly

