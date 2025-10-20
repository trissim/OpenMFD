# plan_03_device_assembly.md
## Component: Device Assembly and Configuration System

### Objective
Create a high-level device assembly system that combines geometric primitives into complete microfluidic devices. This includes device configuration dataclasses, assembly orchestration, unit arrays, outlines, and walls following OpenHCS configuration and orchestration patterns.

### Plan

1. **Create device configuration module** (`openmfd/devices/config.py`)
   - Create `DeviceConfiguration` dataclass:
     - wells_config: WellConfiguration
     - channels_config: ChannelConfiguration
     - chambers_config: ChamberConfiguration
     - casing dimensions (x, y, z)
     - rotation angle
     - alignment settings
   - Create `ArrayConfiguration` dataclass:
     - grid_size (rows, columns)
     - units_from_center
     - alignment mode
   - Create `WallConfiguration` dataclass:
     - thickness
     - height
     - wafer diameter
   - Support hierarchical configuration (device → array → output)

2. **Create device assembly module** (`openmfd/devices/assembly.py`)
   - Refactor `make_taylor()` and `make_device()` into clean assembly functions
   - Create `assemble_device()` function:
     - Takes DeviceConfiguration
     - Assembles wells, channels, chambers
     - Returns combined geometry
   - Create `assemble_unit()` function:
     - Creates single device unit
     - Handles rotation and translation
     - Returns positioned unit
   - Support selective component inclusion (add_wells, add_channels, add_chambers)

3. **Create array generation module** (`openmfd/devices/arrays.py`)
   - Refactor `make_unit_array()` function
   - Create `create_device_array()` function:
     - Takes unit geometry and ArrayConfiguration
     - Creates NxM grid of units
     - Handles alignment modes (full, partial, custom)
     - Supports units_from_center positioning
   - Add array positioning utilities:
     - Center array on origin
     - Custom offset positioning
     - Alignment to reference points

4. **Create outline/casing module** (`openmfd/devices/outline.py`)
   - Refactor `create_outline()` function
   - Create `create_device_outline()`:
     - Takes array geometry and outline thickness
     - Creates bounding outline/frame
     - Supports custom outline shapes
   - Add outline utilities:
     - Compute outline dimensions from array
     - Create custom outline shapes
     - Merge outline with device

5. **Create wall generation module** (`openmfd/devices/walls.py`)
   - Refactor `create_wall()` and `make_walls()` functions
   - Create `create_wafer_walls()`:
     - Takes WallConfiguration
     - Creates circular wafer walls
     - Supports inner walls for grid divisions
   - Create `create_device_walls()`:
     - Creates walls for device containment
     - Supports variable thickness
     - Handles wall locking mechanisms
   - Add wall utilities:
     - Wall positioning relative to device
     - Wall thickness variations
     - Lock/key features for assembly

6. **Create device templates** (`openmfd/devices/templates/`)
   - Create template functions for common device types:
     - `two_compartment_device()` - 2-compartment standard
     - `three_compartment_device()` - 3-compartment standard
     - `gradient_device()` - Gradient generation devices
     - `plate_device()` - Multi-well plate format
   - Each template returns pre-configured DeviceConfiguration
   - Support customization via parameters

7. **Create device registry** (`openmfd/devices/registry.py`)
   - Create device type registry system
   - Register standard device types:
     - "2_compartment_96_well"
     - "3_compartment"
     - "gradient"
     - "plate_12_well"
   - Support custom device registration
   - Enable device lookup by name

8. **Add device validation**
   - Validate device configurations before assembly
   - Check dimensional constraints
   - Verify component compatibility
   - Ensure valid grid sizes and positioning

### Findings

**Current Device Assembly Code Analysis:**

1. **`make_taylor()` Function (lines 437-495):**
   - High-level device assembly function
   - Parameters:
     - Well config: wells_pos, well_rad, well_height
     - Channel config: chan_w, chan_l, chan_h, chan_gap, max_chans, num_chans
     - Chamber config: chamber_height, chamber_len_until
     - Array config: rows, columns, alignment, units_from_center
     - Casing: casing_x, casing_y, casing_z
     - Output: save_path, dxf, render_stl
     - Wall: wall_height, wall_thickness
   - Assembly process:
     1. Create wells with `four_corner()`
     2. Create channels with `make_channels()`
     3. Create chambers with `make_chambers()`
     4. Union selected components
     5. Rotate device
     6. Translate to casing position
     7. Create unit array
     8. Create outline
     9. Create walls
     10. Save outputs

2. **`make_device()` Function (lines 497-623):**
   - Similar to make_taylor but for 2-compartment devices
   - Uses `wells_top_bottom()` instead of `four_corner()`
   - Additional features:
     - Chamber width override
     - Well shape customization
     - Separate outputs for wells, channels, device, chambers_wells
   - Returns tuple of (geometry, filename) pairs

3. **`make_unit_array()` Function (lines 234-298):**
   - Creates NxM grid of device units
   - Parameters:
     - unit: geometry to replicate
     - dims: unit dimensions [x, y, z]
     - grid_size: [rows, columns]
     - alignment: positioning mode
     - units_from_center: offset from center
   - Alignment modes:
     - "full" - full grid
     - Custom tuple - partial grid with offset
   - Returns array geometry

4. **`create_outline()` Function (lines 300-334):**
   - Creates bounding outline around array
   - Parameters:
     - thickness: outline thickness
     - array: device array geometry
     - dims: unit dimensions
     - grid_size: array size
   - Computes total dimensions
   - Creates rectangular outline
   - Returns outline geometry

5. **`create_wall()` Function (lines 336-433):**
   - Creates walls for device
   - Two implementations:
     - Grid-based walls (horizontal/vertical)
     - Circular wafer walls
   - Parameters:
     - thickness: wall thickness
     - outline_thickness: outline thickness
     - dims: unit dimensions
     - grid_size: array size
     - wall_height: wall height
   - Supports thicker wall sections
   - Supports lock/key mechanisms
   - Returns wall geometry

6. **`make_walls()` Function (lines 661-695):**
   - Creates circular wafer walls
   - Parameters:
     - diameter: wafer diameter
     - thickness: wall thickness
     - grid_size, dims: array configuration
     - height: wall height
     - segments: circle segments
     - make_inner: create inner walls
     - padx, pady: padding
   - Creates outer circular wall
   - Optionally creates inner grid walls
   - Returns (walls, wafer_wall, wafer_walls) tuple

7. **File Naming Convention:**
   - Pattern: `{prefix}_{rows}x{columns}_units_.{ext}`
   - Prefixes: "chans", "wells", "chambers" based on components
   - Version prefix: "v{version}_" if specified
   - Extensions: .scad, .dxf, .stl

8. **Current Issues:**
   - Too many parameters (15-20 per function)
   - No configuration objects
   - Inconsistent return types
   - Mixed concerns (assembly + I/O)
   - No validation
   - Hardcoded file naming

**OpenHCS Patterns to Apply:**

1. **Configuration Dataclasses:**
   - Replace long parameter lists with config objects
   - Use hierarchical configuration
   - Enable configuration inheritance
   - Support configuration validation

2. **Separation of Concerns:**
   - Assembly logic separate from I/O
   - Device creation separate from file saving
   - Configuration separate from execution

3. **Orchestration Pattern:**
   - Device assembly orchestrator
   - Step-by-step assembly process
   - Clear assembly pipeline

4. **Registry Pattern:**
   - Register device types
   - Enable device lookup
   - Support custom devices

5. **Template Pattern:**
   - Pre-configured device templates
   - Customizable via parameters
   - Reusable device definitions

### Implementation Draft
(Code will be written here after smell loop approval)

