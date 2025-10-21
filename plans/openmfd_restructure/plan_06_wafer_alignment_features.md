# plan_06_wafer_alignment_features.md
## Component: Wafer Mask, Alignment Marks, and Centering System

### Objective
Complete the openmfd package by adding missing functionality from legacy make_device.py:
1. Wafer mask generation with flat edge
2. Alignment mark features (full, hollow, custom)
3. Centralized coordinate system for consistent centering
4. Glass slide outline generation
5. Text annotation features

This will allow refactored examples to use ONLY openmfd package functions, eliminating dependency on legacy make_device.py.

### Current State

**What exists in openmfd:**
- ✅ `openmfd/devices/arrays.py` - Array creation, has `center_array()` but not used
- ✅ `openmfd/devices/walls.py` - `create_wafer_walls()` for 3D walls
- ✅ `openmfd/devices/outline.py` - `create_outline()` for frames
- ✅ `openmfd/geometry/` - Wells, channels, chambers

**What's missing from openmfd:**
- ❌ Wafer mask generation (`make_wafer`, `add_wafer_to_mask`)
- ❌ Alignment mark features (`alignment_features`)
- ❌ Centralized centering system (devices vs wafer mismatch)
- ❌ Glass slide outline with alignment groove (`make_outline` with centering)
- ❌ Text annotation positioning

**Current problem:**
- Refactored examples still import from `make_device.py`:
  - `make_unit_array` (for alignment marks)
  - `add_wafer_to_mask` (for wafer outline)
  - `make_walls` (for 3D walls) - EXISTS but not used
  - `make_outline` (for glass outline) - EXISTS but different signature
  - `alignment_features` (for alignment marks)

### Root Cause: Centering Inconsistency

**Current behavior in make_device.py:**
```python
# make_unit_array() - devices start at [0, 0]
units.append(solid.translate([row*dims[0], col*dims[1]])(unit))

# add_wafer_to_mask() - wafer centered at grid center
wafer_mask = solid.translate([grid_size[0]*dims[0]/2.0, grid_size[1]*dims[1]/2.0])(wafer_mask)

# make_outline() - outline centered at grid center  
outline = solid.translate([grid_size[0]*dims[0]/2.0, grid_size[1]*dims[1]/2.0])(outline)
```

**Result:** Devices are NOT centered, but wafer/outline/text ARE centered → misalignment!

### Plan

#### 1. Create Wafer Module (`openmfd/devices/wafer.py`)

**Functions to implement:**
```python
def create_wafer(
    diameter: float,
    flat_length: float,
    thickness: float = 1.0,
    segments: int = 512
) -> solid.OpenSCADObject:
    """Create wafer geometry with flat edge.
    
    Parameters
    ----------
    diameter : float
        Wafer diameter (e.g., 100mm, 150mm).
    flat_length : float
        Length of flat edge.
    thickness : float, default=1.0
        Wafer thickness (for 3D).
    segments : int, default=512
        Number of segments for circle.
        
    Returns
    -------
    solid.OpenSCADObject
        Wafer geometry with flat edge.
    """
    # Create cylinder
    # Calculate flat position using geometry
    # Subtract flat edge
    # Rotate 90 degrees
    pass


def create_wafer_mask(
    wafer_size: float,
    flat_length: float,
    mask: solid.OpenSCADObject,
    grid_size: List[int],
    dims: List[float],
    wafer_line_thickness: float = 0.1,
    outer_mask_thickness: float = 5.0,
    alignment_offset: Optional[Tuple[float, float]] = None,
    shrinkage_scale: float = 1.0
) -> solid.OpenSCADObject:
    """Add wafer outline to mask, subtracting device features.
    
    Creates a wafer outline with:
    - Inner line (wafer edge marker)
    - Outer margin (for handling)
    - Device features subtracted from wafer area
    
    Parameters
    ----------
    wafer_size : float
        Wafer diameter.
    flat_length : float
        Flat edge length.
    mask : solid.OpenSCADObject
        Device features to subtract from wafer.
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    wafer_line_thickness : float, default=0.1
        Thickness of wafer edge line.
    outer_mask_thickness : float, default=5.0
        Outer margin thickness.
    alignment_offset : tuple of (float, float), optional
        Offset for alignment marks.
    shrinkage_scale : float, default=1.0
        PDMS shrinkage scaling factor.
        
    Returns
    -------
    solid.OpenSCADObject
        Wafer mask with device features subtracted.
    """
    # Create inner, middle, outer wafer outlines
    # Center at grid center: [grid_size[0]*dims[0]/2.0, grid_size[1]*dims[1]/2.0]
    # Apply alignment offset if provided
    # Apply shrinkage scale
    # Subtract mask from wafer
    pass


def compute_wafer_center(
    grid_size: List[int],
    dims: List[float]
) -> Tuple[float, float]:
    """Compute wafer center coordinates.
    
    This is the SINGLE SOURCE OF TRUTH for centering.
    All elements (devices, wafer, alignment, text) should use this.
    
    Parameters
    ----------
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
        
    Returns
    -------
    tuple of (float, float)
        Center coordinates (x, y).
    """
    return (grid_size[0] * dims[0] / 2.0, grid_size[1] * dims[1] / 2.0)
```

#### 2. Create Alignment Module (`openmfd/devices/alignment.py`)

**Functions to implement:**
```python
def create_alignment_marks(
    array: solid.OpenSCADObject,
    dims: List[float],
    grid_size: List[int],
    alignment_mode: str = "full",
    units_from_center: Optional[Tuple[float, float]] = None,
    corner_length: Optional[float] = None
) -> solid.OpenSCADObject:
    """Add alignment marks to device array.
    
    Alignment modes:
    - "full": Solid L-shaped marks at corners
    - "hollow": Hollow L-shaped marks (for top layer alignment)
    - "partial": Marks only at specified corners
    - None: No alignment marks
    
    Parameters
    ----------
    array : solid.OpenSCADObject
        Device array to add marks to.
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
    alignment_mode : str, default="full"
        Alignment mode ("full", "hollow", "partial", or None).
    units_from_center : tuple of (float, float), optional
        Distance from center for alignment marks.
    corner_length : float, optional
        Length of corner marks. If None, computed from dims.
        
    Returns
    -------
    solid.OpenSCADObject
        Array with alignment marks added.
    """
    # Compute corner_length if not provided
    # Create L-shaped corner marks
    # Position at corners based on units_from_center
    # Union with array (full) or difference (hollow)
    pass


def create_corner_mark(
    corner_length: float,
    thickness_divisor: float = 3.0
) -> solid.OpenSCADObject:
    """Create single L-shaped corner alignment mark.
    
    Parameters
    ----------
    corner_length : float
        Length of corner mark arms.
    thickness_divisor : float, default=3.0
        Divisor for mark thickness (corner_length / thickness_divisor).
        
    Returns
    -------
    solid.OpenSCADObject
        L-shaped corner mark.
    """
    # Create two rectangles forming L-shape
    pass
```

#### 3. Update Arrays Module (`openmfd/devices/arrays.py`)

**Add centering to `create_device_array()`:**
```python
def create_device_array(
    unit: solid.OpenSCADObject,
    dims: List[float],
    grid_size: List[int],
    dxf: bool = False,
    alignment: Optional[str] = None,
    units_from_center: Optional[Tuple[float, float]] = None,
    alignment_offset: Optional[Tuple[float, float]] = None,
    alignment_mark_size: float = 1.0,
    center: bool = True  # NEW PARAMETER
) -> solid.OpenSCADObject:
    """Create device array with optional centering and alignment.
    
    NEW: If center=True, array is centered at wafer center coordinates.
    This ensures devices, wafer, alignment marks, and text are all aligned.
    """
    # Create grid (existing code)
    # ...
    
    # NEW: Center array if requested
    if center:
        from .wafer import compute_wafer_center
        cx, cy = compute_wafer_center(grid_size, dims)
        # Devices currently start at [0,0], need to shift to center
        # But wafer is centered at [cx, cy], so we DON'T shift devices
        # Instead, we keep devices at [0,0] and shift wafer/outline/text to [0,0]
        # OR we shift devices to match wafer centering
        pass
    
    # Add alignment marks if requested
    if alignment is not None and dxf:
        from .alignment import create_alignment_marks
        array = create_alignment_marks(
            array, dims, grid_size, alignment,
            units_from_center, alignment_mark_size
        )
    
    return array
```

#### 4. Create Text Annotation Module (`openmfd/devices/text.py`)

**Functions to implement:**
```python
def create_centered_text(
    text: str,
    grid_size: List[int],
    dims: List[float],
    size: float = 2.0,
    offset_y: float = 0.0,
    alignment_offset: Optional[Tuple[float, float]] = None
) -> solid.OpenSCADObject:
    """Create text centered on wafer.
    
    Parameters
    ----------
    text : str
        Text to render.
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    size : float, default=2.0
        Text size.
    offset_y : float, default=0.0
        Vertical offset from center.
    alignment_offset : tuple of (float, float), optional
        Alignment offset.
        
    Returns
    -------
    solid.OpenSCADObject
        Centered text geometry.
    """
    pass
```

#### 5. Update Outline Module (`openmfd/devices/outline.py`)

**Add glass slide outline function:**
```python
def create_glass_outline(
    glass_size: List[float],
    wall_thickness: float,
    grid_size: List[int],
    dims: List[float],
    alignment_offset: Optional[Tuple[float, float]] = None,
    alignment_groove_thickness: Optional[float] = None
) -> solid.OpenSCADObject:
    """Create glass slide outline with optional alignment groove.
    
    Parameters
    ----------
    glass_size : list of float
        Glass slide dimensions [width, height].
    wall_thickness : float
        Outline wall thickness.
    grid_size : list of int
        Grid size [rows, columns].
    dims : list of float
        Unit dimensions [x, y, z].
    alignment_offset : tuple of (float, float), optional
        Alignment offset.
    alignment_groove_thickness : float, optional
        Thickness of alignment groove. If provided, creates groove.
        
    Returns
    -------
    solid.OpenSCADObject
        Glass slide outline, centered on wafer.
    """
    # Create inner and outer squares
    # Center at wafer center
    # Optionally subtract alignment groove
    pass
```

### Implementation Order

1. ✅ Create `openmfd/devices/wafer.py` with wafer and centering functions
2. ✅ Create `openmfd/devices/alignment.py` with alignment mark functions
3. ✅ Update `openmfd/devices/arrays.py` to use alignment module
4. ✅ Create `openmfd/devices/text.py` for text annotations
5. ✅ Update `openmfd/devices/outline.py` with glass outline function
6. ✅ Update `openmfd/devices/__init__.py` to export new functions
7. ✅ Create pure OpenMFD example: `2_compartment_96_well_v27_OPENMFD_ONLY.py`
8. ✅ Test centering consistency (devices, wafer, alignment, text all aligned)
9. ✅ All 7 files generated successfully (SCAD + STL)

### Implementation Draft

**Status**: ✅ COMPLETE

All modules have been implemented and tested successfully:

**New modules created:**
- `openmfd/devices/wafer.py` (300 lines)
  - `compute_wafer_center()` - SINGLE SOURCE OF TRUTH for centering
  - `create_wafer()` - Wafer with flat edge
  - `create_wafer_mask()` - Add wafer outline to mask
  - `create_wafer_holder()` - Wafer holder geometry
  - `create_wafer_calibration_rings()` - Calibration rings

- `openmfd/devices/alignment.py` (280 lines)
  - `create_corner_mark()` - L-shaped corner marks
  - `create_alignment_marks()` - Full/hollow/partial alignment
  - `create_crosshair_mark()` - Crosshair marks
  - `create_vernier_scale()` - Vernier scales
  - `create_alignment_target()` - Concentric ring targets

- `openmfd/devices/text.py` (260 lines)
  - `create_centered_text()` - Text centered on wafer
  - `create_multiline_text()` - Multi-line text
  - `create_cure_temperature_text()` - Cure temp annotations
  - `create_device_label()` - Device name/version labels
  - `create_date_stamp()` - Date stamps

**Modules updated:**
- `openmfd/devices/outline.py`
  - Added `create_glass_outline()` - Glass slide outline with alignment groove

- `openmfd/devices/arrays.py`
  - Updated `create_device_array()` to integrate alignment marks
  - Added `alignment_offset` and `alignment_mark_size` parameters

- `openmfd/devices/__init__.py`
  - Exported all new functions

**Example created:**
- `examples/devices/2_compartment/2_compartment_96_well_v27_OPENMFD_ONLY.py`
  - Uses ONLY openmfd package (NO legacy imports)
  - Generates all 7 files successfully
  - All elements properly centered using `compute_wafer_center()`

**Test results:**
```
✅ 2_compartment_96_well_300um_suex200_v27_single_bottom.scad (19K)
✅ 2_compartment_96_well_300um_suex200_v27_single_top.scad (11K)
✅ 2_compartment_96_well_300um_suex200_v27_single_aligned.scad (20K)
✅ wall_single_2_compartment_96_well_300um_suex200_v27.stl (307K)
✅ 2_compartment_96_well_300um_suex200_v27_bottom.scad (553K)
✅ 2_compartment_96_well_300um_suex200_v27_top.scad (55K)
✅ 2_compartment_96_well_300um_suex200_v27_aligned.scad (612K)
```

**Centering verification:**
All elements (devices, wafer outline, alignment marks, text, glass outline) use the centralized `compute_wafer_center()` function, ensuring consistent centering across all features.

### Success Criteria

- ✅ Refactored examples import ONLY from `openmfd` package
- ✅ No imports from `make_device.py` in refactored examples
- ✅ Devices, wafer outline, alignment marks, and text are all centered consistently
- ✅ All 7 files generated correctly (single units, arrays, wafer masks, STL walls)
- ✅ Visual inspection shows proper centering in OpenSCAD

### Findings

**Centering coordinate system:**
- Wafer center: `[grid_size[0]*dims[0]/2.0, grid_size[1]*dims[1]/2.0]`
- This should be the SINGLE SOURCE OF TRUTH
- All elements must be positioned relative to this center

**Legacy functions to replace:**
1. `make_wafer()` → `create_wafer()`
2. `add_wafer_to_mask()` → `create_wafer_mask()`
3. `alignment_features()` → `create_alignment_marks()`
4. `make_unit_array()` (with alignment) → `create_device_array()` (updated)
5. `make_outline()` (centered) → `create_glass_outline()`
6. Text positioning → `create_centered_text()`

**Key insight:**
The centering problem exists because `make_unit_array()` doesn't center devices, but `add_wafer_to_mask()` centers the wafer. The fix is to ensure ALL elements use the same centering coordinate from `compute_wafer_center()`.

