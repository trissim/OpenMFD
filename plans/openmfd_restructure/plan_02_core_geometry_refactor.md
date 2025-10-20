# plan_02_core_geometry_refactor.md
## Component: Core Geometry Module Refactoring

### Objective
Refactor the existing geometry generation code from `make_device.py` into a clean, modular, well-documented geometry module following OpenHCS architectural principles. This includes creating proper abstractions for wells, channels, and chambers with type hints, dataclasses for configuration, and comprehensive documentation.

### Plan

1. **Create geometry primitives module** (`openmfd/geometry/primitives.py`)
   - Extract and refactor basic shape functions:
     - `make_well()` - Support circle, square, custom shapes
     - `make_channel()` - Single channel primitive
     - `make_chamber()` - Single chamber primitive
   - Add type hints to all functions
   - Make functions pure (no side effects)
   - Add comprehensive docstrings with parameters, returns, examples

2. **Create well patterns module** (`openmfd/geometry/wells.py`)
   - Refactor well positioning functions:
     - `wells_top_bottom()` - 2-well vertical configuration
     - `four_corner()` - 4-well corner configuration
     - `well_array()` - Generic NxM well array
   - Create `WellConfiguration` dataclass:
     - radius/dimensions
     - height
     - positions
     - shape type (circle, square, custom)
   - Support both 2D (DXF) and 3D (STL) generation

3. **Create channel patterns module** (`openmfd/geometry/channels.py`)
   - Refactor channel generation:
     - `make_channels()` - Channel array with spacing
     - Support max_chans and num_chans modes
     - Return both geometry and measurements
   - Create `ChannelConfiguration` dataclass:
     - length, width, height
     - spacing/gap
     - number of channels
     - rotation
   - Add channel measurement utilities

4. **Create chamber patterns module** (`openmfd/geometry/chambers.py`)
   - Refactor chamber generation:
     - `make_chambers()` - Chamber geometry from channel measurements
     - Support custom dimensions and extensions
   - Create `ChamberConfiguration` dataclass:
     - height
     - length_until parameter
     - width override
     - extra extension
   - Link chamber dimensions to channel measurements

5. **Create positioning utilities** (`openmfd/geometry/positioning.py`)
   - Extract positioning helper functions:
     - `wells_pos_from_center_4()` - 4-corner positions
     - `wells_pos_from_center_2()` - 2-position vertical
     - `corners_from_x_y()` - Generic corner positioning
   - Create generic positioning functions:
     - `grid_positions()` - NxM grid
     - `circular_positions()` - Radial arrangement
     - `custom_positions()` - User-defined positions
   - Add position validation and transformation utilities

6. **Create measurement utilities** (`openmfd/geometry/measurements.py`)
   - Extract measurement calculation logic
   - Create `Measurements` dataclass for x, y, z dimensions
   - Add utility functions:
     - `total_length()` - Compute total dimension
     - `bounding_box()` - Compute bounding box
     - `center_offset()` - Compute centering offsets

7. **Add comprehensive type hints**
   - Use `typing` module for all function signatures
   - Define type aliases for common types:
     - `Position = Tuple[float, float]`
     - `Position3D = Tuple[float, float, float]`
     - `Dimensions = Union[float, Tuple[float, ...]]`
   - Use `Optional` for optional parameters
   - Use `Union` for polymorphic parameters

8. **Add validation and error handling**
   - Validate input parameters (positive dimensions, valid positions)
   - Raise descriptive errors for invalid inputs
   - Follow OpenHCS "fail-loud" principle
   - No defensive programming - explicit validation only

### Findings

**Current Geometry Code Analysis:**

1. **Well Generation (`make_well()` lines 27-47):**
   - Accepts `dims` as number or tuple
   - Supports circle (cylinder) and square (cube) shapes
   - Has `dxf` flag for 2D vs 3D output
   - Uses `solid.circle()` for 2D, `solid.cylinder()` for 3D
   - Centers all shapes
   - 64 segments for circles

2. **Well Patterns:**
   - `wells_top_bottom()` (lines 49-76) - 2 wells vertically aligned
   - `four_corner()` (lines 56-76) - 4 wells in corners
   - Both use lambda functions for position calculation
   - Default offset: `radius + radius/2.0`
   - Support custom positions via `positions` parameter

3. **Channel Generation (`make_channels()` lines 79-172):**
   - Parameters: length, width, height, num_chans, max_chans, spacing
   - Two modes:
     - `num_chans` - explicit channel count
     - `max_chans` - fit channels within width
   - Returns tuple: (geometry, measurements dict)
   - Measurements dict has 'x', 'y', 'z' keys with (positive, negative) tuples
   - Handles even/odd channel counts differently for centering
   - Creates channel array with proper spacing

4. **Chamber Generation (`make_chambers()` lines 175-232):**
   - Takes measurements from channels
   - Parameters: height, extra, len_until, width
   - Computes chamber dimensions based on channel measurements
   - `len_until` - extends chamber to specific length
   - `width` - override chamber width
   - Returns chamber geometry

5. **Positioning Helpers:**
   - `wells_pos_from_center_4` (line 20-23) - Lambda for 4 corners
   - `wells_pos_from_center_2` (line 24-25) - Lambda for 2 vertical
   - `corners_from_x_y` (plate_maker.py line 67-70) - Generic corners
   - All use center-based coordinate system

6. **SolidPython Usage:**
   - `solid.circle()`, `solid.cylinder()` - Wells
   - `solid.square()`, `solid.cube()` - Channels, chambers
   - `solid.union()` - Combine geometries
   - `solid.translate()` - Position geometries
   - `solid.rotate()` - Rotate geometries
   - All use `center=True` for centering

7. **Current Issues to Address:**
   - No type hints
   - Inconsistent parameter naming
   - Mixed 2D/3D logic in same functions
   - Lambda functions for positioning (not reusable)
   - No validation of inputs
   - Measurements dict is opaque (should be dataclass)
   - No comprehensive documentation

**OpenHCS Patterns to Apply:**

1. **Stateless Functions:**
   - All geometry functions are pure
   - No global state
   - Explicit parameters

2. **Dataclass Configuration:**
   - Replace parameter dicts with typed dataclasses
   - Use `@dataclass` decorator
   - Provide sensible defaults
   - Enable validation

3. **Type Safety:**
   - Full type hints on all functions
   - Use `TypedDict` or dataclass for measurements
   - Define type aliases for clarity

4. **Documentation:**
   - NumPy-style docstrings
   - Parameter descriptions with types
   - Return value descriptions
   - Usage examples in docstrings

5. **Error Handling:**
   - Explicit validation at function entry
   - Descriptive error messages
   - No silent failures
   - Fail-loud on invalid inputs

### Implementation Draft
(Code will be written here after smell loop approval)

