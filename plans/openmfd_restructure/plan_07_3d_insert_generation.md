# plan_07_3d_insert_generation.md
## Component: 3D Printed Well Insert Generation

### Objective
Implement 3D printed well insert generation functionality in OpenMFD, including chamfered/tapered extrusion, pins, skirts, and glue cavities. This is a critical missing feature from the legacy `make_device.py` that enables easier pipetting access, precise alignment, and better sealing for microfluidic devices.

### Plan

1. **Create `openmfd/inserts/` module structure**
   - Create `openmfd/inserts/__init__.py` with module exports
   - Create `openmfd/inserts/config.py` for insert configuration dataclasses
   - Create `openmfd/inserts/chamfer.py` for chamfer/taper functionality
   - Create `openmfd/inserts/wells.py` for well insert generation
   - Create `openmfd/inserts/pins.py` for pin generation
   - Create `openmfd/inserts/skirts.py` for skirt generation

2. **Port chamfer extrusion functionality** (`openmfd/inserts/chamfer.py`)
   - Import `chamfer_extrude` from `chamfer_extrude.scad` using SolidPython
   - Create `deg_taper_len(height: float, degrees: float) -> float` function
   - Create `chamfer_extrude_wrapper()` function to wrap SCAD import
   - Add comprehensive docstrings with examples
   - Add type hints throughout

3. **Create insert configuration dataclasses** (`openmfd/inserts/config.py`)
   - `InsertConfiguration`:
     - `degrees_out: float` - Outer chamfer angle
     - `degrees_in: float` - Inner chamfer angle
     - `height_out: float` - Outer insert height
     - `height_in: float` - Inner insert height
     - `taper_len_out_extra: float` - Extra taper length (outer)
     - `taper_len_in_extra: float` - Extra taper length (inner)
   - `PinConfiguration`:
     - `dims: Tuple[float, float]` - Pin dimensions (x, y)
     - `height: float` - Pin height
     - `inner_height: float` - Inner pin height
     - `offset: float` - Pin offset from well center
   - `SkirtConfiguration`:
     - `thickness1: float` - First skirt thickness
     - `height1: float` - First skirt height
     - `empty1: float` - First skirt empty space
     - `thickness2: float` - Second skirt thickness
     - `height2: float` - Second skirt height
   - `TaperConfiguration`:
     - `height: float` - Taper height
     - `degrees: float` - Taper angle

4. **Implement well insert generation** (`openmfd/inserts/wells.py`)
   - `create_well_insert()`:
     - Parameters: insert_config, well_rad, chan_l, chamber_width, add_chambers
     - Computes taper length from angle and height
     - Adjusts well radius and chamber width for taper
     - Creates 2D geometry using device functions
     - Applies chamfer extrusion or linear extrusion
     - Returns: (insert_geometry, adjusted_well_rad, adjusted_chan_l)
   - `create_well_insert_array()`:
     - Takes single insert and creates array
     - Applies grid positioning
     - Handles alignment offset
     - Returns array of inserts

5. **Implement pin generation** (`openmfd/inserts/pins.py`)
   - `create_insert_pin()`:
     - Creates rectangular pin geometry
     - Applies linear extrusion to specified height
     - Positions at well location with offset
     - Returns 3D pin geometry
   - `create_pin_array()`:
     - Creates array of pins matching well positions
     - Handles grid positioning and alignment
     - Returns union of all pins

6. **Implement skirt generation** (`openmfd/inserts/skirts.py`)
   - `create_skirt_layer()`:
     - Takes insert geometry projection
     - Creates offset inner boundary
     - Subtracts to create ring/frame
     - Extrudes to specified height
     - Returns skirt layer
   - `create_dual_skirt()`:
     - Creates two-layer skirt system
     - First layer: thicker, taller, with empty space
     - Second layer: thinner, shorter, base layer
     - Combines both layers
     - Returns complete skirt geometry

7. **Create complete insert assembly function** (`openmfd/inserts/wells.py`)
   - `assemble_well_inserts()`:
     - Parameters: insert_config, pin_config, skirt_config, device_params
     - Creates outer chamfered wells
     - Creates inner chamfered cavity (if specified)
     - Creates optional taper top (for reduced adhesion)
     - Creates pins
     - Creates skirts
     - Combines all components with proper z-offsets
     - Applies PDMS shrinkage scaling (x, y only, not z)
     - Returns complete insert assembly

8. **Add insert hole generation to device module** (`openmfd/devices/arrays.py`)
   - `create_insert_holes()`:
     - Creates square holes for insert pins
     - Positions at well locations with offset
     - Returns geometry to subtract from top layer
   - Update `create_device_array()` to optionally add insert holes

9. **Update exports** (`openmfd/inserts/__init__.py`)
   - Export all configuration dataclasses
   - Export chamfer functions
   - Export insert generation functions
   - Export pin and skirt functions
   - Export complete assembly function

10. **Add Sphinx documentation** (`docs/source/api/inserts.rst`)
    - Create new API section for inserts module
    - Document all configuration classes
    - Document chamfer extrusion
    - Document insert generation workflow
    - Add examples for common use cases
    - Add cross-references to device and geometry modules

11. **Create example script** (`examples/inserts/well_inserts_example.py`)
    - Demonstrate basic insert generation
    - Show configuration options
    - Export to STL for 3D printing
    - Include comments explaining each step

12. **Update main documentation** (`docs/source/index.rst`)
    - Add inserts to module list
    - Add to API reference TOC
    - Update quick start to mention inserts

### Findings

**Legacy Implementation Analysis (`make_device.py` and example files):**

1. **Chamfer Extrusion:**
   - Imported from external SCAD file: `chamfer_extrude.scad`
   - Function signature: `chamfer_extrude(height, angle, segments=20)`
   - Creates tapered/chamfered extrusion of 2D shapes
   - Used for creating angled well walls

2. **Taper Length Calculation:**
   ```python
   def deg_taper_len(height, deg):
       if not deg == 0:
           return height * math.tan(math.radians(deg))
       else:
           return 0
   ```
   - Computes horizontal taper distance from vertical height and angle
   - Used to adjust well radius and chamber width

3. **Insert Generation Pattern:**
   ```python
   def make_well_insert(make_fun, degrees, height, add_chambers, 
                        taper_len_extra=0, well_rad=well_rad, chan_l=chan_l):
       taper_len = deg_taper_len(height, degrees)
       taper_len = taper_len + taper_len_extra
       chamber_width_edit = chamber_width
       chan_l_edit = chan_l + taper_len * 2
       if not (type(well_rad) is tuple or type(well_rad) is list):
           chamber_width_edit = well_rad * 2
           well_rad = well_rad - taper_len
       (inserts, _), _, _ = make_fun(well_rad=well_rad, chan_l=chan_l_edit,
                                     chamber_width=chamber_width_edit - taper_len * 2,
                                     add_chambers=add_chambers)
       inserts = make_unit_array(inserts, dims, grid_size, dxf=True, 
                                 alignment=None, ...)
       if not degrees == 0:
           inserts = chamfer_extrude(height, degrees, segments=20)(inserts)
       else:
           inserts = solid.linear_extrude(height=height)(inserts)
       return inserts, well_rad, chan_l_edit
   ```

4. **Pin Generation:**
   - Creates rectangular pins with specified dimensions
   - Extruded to height: `pin_height + skirt_height1 + skirt_height2 + pin_inner_height`
   - Positioned with offset from well center
   - Arrayed to match well positions

5. **Skirt Generation:**
   - Two-layer system for better adhesion/sealing
   - Layer 1: Thicker (.75mm), taller (.66mm), with empty space (.3mm)
   - Layer 2: Thinner (.8mm), shorter (.04mm), base layer
   - Created by projecting insert, offsetting, and differencing

6. **Complete Assembly:**
   ```python
   all_well_inserts = make_well_insert_all(degrees_in, degrees_out, 
                                           insert_height_in, insert_height)
   # Translate to account for pin and skirt heights
   all_well_inserts = solid.translate([0, 0, pin_height + skirt_height1 + skirt_height2])(all_well_inserts)
   # Add pins and skirts
   all_well_inserts = solid.union()(all_well_inserts, pins, skirts)
   # Apply PDMS shrinkage (x, y only)
   all_well_inserts = solid.scale([scale_percent, scale_percent, 1])(all_well_inserts)
   ```

7. **Insert Holes in Wafer:**
   - Square holes created at well positions with offset
   - Dimensions: `chamber_hole_dims = (2, 2)` mm
   - Subtracted from top layer (wells/chambers)
   - Allows pins to fit through for alignment

8. **Key Parameters from Legacy Code:**
   - `degrees_out = 16` - Outer chamfer angle
   - `degrees_in = 35` - Inner chamfer angle
   - `insert_height = 3.8` mm - Outer insert height
   - `insert_height_in = 0.40` mm - Inner insert height
   - `taper_len_out_extra = 0.300` mm
   - `taper_len_in_extra = 0.91` mm
   - `pin_height = 0.06` mm
   - `pin_inner_height = 2` mm
   - `chamber_hole_dims = (2, 2)` mm
   - `pin_dims = (1.85, 1.85)` mm
   - `insert_pin_offset = -0.5` mm

**Missing Features Not Yet Ported:**

1. **3D Printed Well Inserts** ❌ (THIS PLAN)
   - Chamfered/tapered wells
   - Insert pins
   - Skirts
   - Glue cavities

2. **Tip Racks** ❌
   - `make_rack()` function
   - `make_pillar()` function
   - Bolt holes and support structures

3. **Wafer Holders** ⚠️ (Partially implemented)
   - `create_wafer_holder()` exists in `wafer.py`
   - Needs verification against legacy implementation

4. **Humidity Reservoirs** ❌
   - `make_water_wells()` function
   - Creates wells in PDMS for humidity control

5. **Tip Rack Pillars** ❌
   - Tapered pillars for pipette tip storage
   - Bolt positioning

**Documentation Status:**

✅ **Fully Documented Modules:**
- `openmfd/geometry/` - All submodules have Sphinx docs
- `openmfd/devices/alignment.py` - Complete with examples
- `openmfd/devices/wafer.py` - Complete with examples
- `openmfd/devices/text.py` - Complete with examples
- `openmfd/devices/arrays.py` - Complete with examples
- `openmfd/devices/outline.py` - Complete with examples

⚠️ **Partially Documented:**
- `openmfd/devices/walls.py` - Has docstrings, needs Sphinx section
- `openmfd/devices/assembly.py` - Has docstrings, needs examples
- `openmfd/export/` - Has docstrings, needs comprehensive guide

❌ **Not Yet Documented:**
- `openmfd/inserts/` - Doesn't exist yet (THIS PLAN)

### Implementation Draft

✅ **Implementation Complete**

**Modules Created:**

1. **`openmfd/inserts/__init__.py`** - Module exports
2. **`openmfd/inserts/config.py`** - Configuration dataclasses
   - `TaperConfiguration` - Taper/chamfer settings
   - `InsertConfiguration` - Well insert geometry
   - `PinConfiguration` - Alignment pin settings
   - `SkirtConfiguration` - Sealing skirt settings

3. **`openmfd/inserts/chamfer.py`** - Chamfer utilities
   - `deg_taper_len()` - Calculate taper length from angle
   - `chamfer_extrude_wrapper()` - Chamfered extrusion function
   - `linear_extrude_if_flat()` - Conditional extrusion

4. **`openmfd/inserts/pins.py`** - Pin generation
   - `create_insert_pin()` - Single alignment pin
   - `create_pin_array()` - Array of pins
   - `create_insert_holes()` - Holes for pins in wafer

5. **`openmfd/inserts/skirts.py`** - Skirt generation
   - `create_skirt_layer()` - Single skirt layer
   - `create_dual_skirt()` - Two-layer skirt system
   - `create_skirt_from_projection()` - Skirts from 3D geometry

6. **`openmfd/inserts/wells.py`** - Well insert assembly
   - `create_well_insert()` - Chamfered well insert
   - `create_well_insert_array()` - Array of inserts
   - `assemble_well_inserts()` - Complete assembly with pins and skirts

**Key Features Implemented:**
- ✅ Chamfered/tapered extrusion with configurable angles
- ✅ Taper length calculation and dimension adjustment
- ✅ Outer and inner chamfered wells
- ✅ Alignment pins with configurable dimensions and offset
- ✅ Two-layer skirt system for adhesion/sealing
- ✅ Insert holes for wafer (pin alignment)
- ✅ PDMS shrinkage compensation (x, y only)
- ✅ Complete assembly function combining all components
- ✅ Comprehensive docstrings with examples
- ✅ Type hints throughout

**Next Steps:**
- Add unit tests for insert generation
- Add Sphinx documentation
- Create example script
- Update main documentation index

