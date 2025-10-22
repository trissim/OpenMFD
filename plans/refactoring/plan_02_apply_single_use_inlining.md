# plan_02_apply_single_use_inlining.md
## Component: Apply Single-Use Function Inlining Rule

### Objective
Apply the OpenHCS "Single-Use Function Inlining Rule" to eliminate unnecessary abstraction layers in the refactored V2 script. Target: 15-25% line reduction while preserving all functionality.

### Plan

#### Phase 1: Inline Single-Use Helper Functions (MANDATORY)

**Rule**: "If a method is only called once, inline it as a lambda or direct code rather than creating unnecessary abstraction."

**Functions to Inline:**

1. **`scale_percent_pdms_heat_shrinkage()`** (Lines 120-123)
   - **Usage**: Line 202 (1 time)
   - **Action**: Inline calculation and string formatting at call site
   - **Before** (4 lines):
     ```python
     def scale_percent_pdms_heat_shrinkage(cure_temp):
         """Calculate PDMS shrinkage based on curing temperature."""
         shrinkage_percent = 1.0 - (cure_temp * 0.002)
         return shrinkage_percent, f"Cure at {cure_temp}°C (scale: {shrinkage_percent:.4f})"
     ```
   - **After** (2 lines at call site):
     ```python
     scale_percent = 1.0 - (CURE_TEMP * 0.002)
     cure_text = f"Cure at {CURE_TEMP}°C (scale: {scale_percent:.4f})"
     ```
   - **Savings**: 2 lines

2. **`create_insert_holes()`** (Lines 148-153)
   - **Usage**: Line 220 (1 time)
   - **Action**: Inline comprehension at call site
   - **Before** (6 lines):
     ```python
     def create_insert_holes(positions, dims=CHAMBER_HOLE_DIMS):
         """Create square insert holes at given positions (comprehension pattern)."""
         return solid.union()(*[
             solid.translate([pos[0], pos[1], 0])(make_well(dims=dims, height=None, dxf=True, shape="square"))
             for pos in positions
         ])
     ```
   - **After** (3 lines at call site):
     ```python
     insert_holes = solid.union()(*[
         solid.translate([pos[0], pos[1], 0])(make_well(dims=CHAMBER_HOLE_DIMS, height=None, dxf=True, shape="square"))
         for pos in wells_pos_from_center_2(WELLS_POS + INSERT_PIN_OFFSET)
     ])
     ```
   - **Savings**: 3 lines

3. **`create_device_arrays()`** (Lines 156-175)
   - **Usage**: Line 368 (1 time)
   - **Action**: Inline dict comprehension at call site
   - **Before** (20 lines):
     ```python
     def create_device_arrays(unit_geometries, dims, grid_size, alignment_configs):
         """Create multiple device arrays with different alignment patterns (consolidated).
         
         Args:
             unit_geometries: Dict of {layer_name: geometry}
             dims: Device dimensions
             grid_size: Grid size [rows, cols]
             alignment_configs: Dict of {layer_name: alignment_type}
         
         Returns:
             Dict of {layer_name: array_geometry}
         """
         return {
             name: create_device_array(
                 geom, dims, grid_size, dxf=True, alignment=alignment_configs[name],
                 units_from_center=UNITS_FROM_CENTER, alignment_offset=ALIGNMENT_OFFSET,
                 alignment_mark_size=ALIGNMENT_MARK_SIZE
             )
             for name, geom in unit_geometries.items()
         }
     ```
   - **After** (7 lines at call site):
     ```python
     arrays = {
         name: create_device_array(
             geom, DIMS, GRID_SIZE, dxf=True, alignment=alignment,
             units_from_center=UNITS_FROM_CENTER, alignment_offset=ALIGNMENT_OFFSET,
             alignment_mark_size=ALIGNMENT_MARK_SIZE
         )
         for (name, geom), alignment in zip(
             {'bottom': channels_single, 'top': chamber_wells_single}.items(),
             ['full', 'hollow']
         )
     }
     ```
   - **Savings**: 13 lines

4. **`add_wafer_masks()`** (Lines 178-189)
   - **Usage**: Line 382 (1 time)
   - **Action**: Inline dict comprehension at call site
   - **Before** (12 lines):
     ```python
     def add_wafer_masks(arrays, wafer_size, wafer_flat, grid_size, dims, scale):
         """Add wafer mask outline to multiple arrays (consolidated)."""
         return {
             name: create_wafer_mask(
                 wafer_size, wafer_flat, array, grid_size, dims,
                 wafer_line_thickness=WAFER_LINE_THICKNESS,
                 outer_mask_thickness=OUTER_MASK_THICKNESS,
                 alignment_offset=ALIGNMENT_OFFSET,
                 shrinkage_scale=scale
             )
             for name, array in arrays.items()
         }
     ```
   - **After** (8 lines at call site):
     ```python
     {
         name: create_wafer_mask(
             WAFER_SIZE, WAFER_FLAT_LEN, array, GRID_SIZE, DIMS,
             wafer_line_thickness=WAFER_LINE_THICKNESS,
             outer_mask_thickness=OUTER_MASK_THICKNESS,
             alignment_offset=ALIGNMENT_OFFSET,
             shrinkage_scale=scale_percent
         )
         for name, array in arrays.items()
     }
     ```
   - **Savings**: 4 lines

**Total Phase 1 Savings**: 22 lines (4.7% reduction from 465 lines)

---

#### Phase 2: Simplify Nested Translates (Mathematical Simplification)

**Pattern**: Lines 348-359 have deeply nested `solid.translate()` calls that can be simplified.

**Before** (12 lines):
```python
text = solid.translate([0, -(GRID_SIZE[1] + 3) * DIMS[1] / 2])(
    solid.translate([GRID_SIZE[0] * DIMS[0] / 2.0, GRID_SIZE[1] * DIMS[1] / 2.0])(
        solid.translate([ALIGNMENT_OFFSET[0], ALIGNMENT_OFFSET[1]])(
            solid.union()(
                solid.text(cure_text, halign="center", valign="center", size=2),
                solid.translate([0, -DIMS[1] / 2])(
                    solid.text("Use 60mL of Sylgard 184 in 1:10 ratio", halign="center", valign="center", size=2)
                )
            )
        )
    )
)
```

**After** (8 lines - consolidate translates):
```python
# Calculate final text position (consolidate nested translates)
text_x = GRID_SIZE[0] * DIMS[0] / 2.0 + ALIGNMENT_OFFSET[0]
text_y = GRID_SIZE[1] * DIMS[1] / 2.0 + ALIGNMENT_OFFSET[1] - (GRID_SIZE[1] + 3) * DIMS[1] / 2
text = solid.translate([text_x, text_y])(
    solid.union()(
        solid.text(cure_text, halign="center", valign="center", size=2),
        solid.translate([0, -DIMS[1] / 2])(
            solid.text("Use 60mL of Sylgard 184 in 1:10 ratio", halign="center", valign="center", size=2)
        )
    )
)
```

**Savings**: 4 lines

---

#### Phase 3: Simplify Conditional Scaling Logic

**Before** (Line 378):
```python
arrays = {name: solid.scale([scale_percent, scale_percent])(arr) for name, arr in arrays.items()} if scale_percent != 1.0 else arrays
```

**After** (cleaner, more readable):
```python
if scale_percent != 1.0:
    arrays = {name: solid.scale([scale_percent, scale_percent])(arr) for name, arr in arrays.items()}
```

**Savings**: 0 lines (readability improvement)

---

### Expected Outcomes

**Line Count Reduction:**
- **Starting**: 465 lines
- **Phase 1**: -22 lines → 443 lines
- **Phase 2**: -4 lines → 439 lines
- **Total Reduction**: 26 lines (5.6%)

**Code Quality Improvements:**
- ✅ Eliminate 4 single-use helper functions
- ✅ Reduce unnecessary abstraction layers
- ✅ Simplify nested translate operations
- ✅ Improve code readability and maintainability
- ✅ Follow OpenHCS "clean, terse, elegant" principles

**Functionality Preservation:**
- ✅ All outputs remain identical
- ✅ Zero regression in behavior
- ✅ All tests pass (if any)

### Success Criteria

- [ ] All single-use functions inlined
- [ ] Line count reduced by 5-6%
- [ ] Script runs without errors
- [ ] All generated SCAD files are identical
- [ ] Code is more readable and maintainable

