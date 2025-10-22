# plan_01_fluent_device_builder_api.md
## Component: Fluent Device Builder API (OpenMFD Pipeline DSL)

### Objective
Design and implement a fluent, pipeline-style API for OpenMFD that eliminates boilerplate, reduces inline math, and provides an intuitive, modular interface similar to OpenHCS's Pipeline DSL.

### Problem Analysis

#### Current Issues in V2 Script:

1. **Duplicate `create_device_array()` calls** with identical parameters (lines 252-255, 265-266)
2. **Inline math scattered everywhere**:
   - `taper_len_out = deg_taper_len(INSERT_HEIGHT, DEGREES_OUT) + TAPER_LEN_OUT_EXTRA`
   - `well_rad_outer = WELL_RAD - taper_len_out`
   - `chan_l_outer = CHAN_L + taper_len_out * 2`
   - `chamber_width_outer = CHAMBER_WIDTH - taper_len_out * 2`
3. **Repeated geometry creation patterns** (outer vs inner insert - nearly identical code)
4. **Low-level SolidPython operations** exposed everywhere
5. **No clear separation** between configuration and execution
6. **Verbose parameter passing** (alignment config as 4-tuple)

#### Desired API Style (Inspired by OpenHCS):

```python
# OpenHCS Pipeline Pattern
pipeline = Pipeline([
    FunctionStep(
        func=[normalize, segment, measure],
        name="cell_analysis"
    )
])
```

**Key Principles:**
- **Method chaining** for fluent construction
- **Declarative configuration** separated from execution
- **Minimal boilerplate** - sensible defaults
- **Composable operations** - build complex from simple
- **Type-safe** - clear parameter names, not tuples

---

### Proposed OpenMFD Fluent API

#### Example 1: Insert Builder (Replaces lines 205-267)

**Current (67 lines, lots of inline math):**
```python
# Calculate outer taper dimensions
taper_len_out = deg_taper_len(INSERT_HEIGHT, DEGREES_OUT) + TAPER_LEN_OUT_EXTRA
well_rad_outer = WELL_RAD - taper_len_out
chan_l_outer = CHAN_L + taper_len_out * 2
chamber_width_outer = CHAMBER_WIDTH - taper_len_out * 2

# Create outer insert geometry (2D)
_, measurements_outer = make_channels(...)
outer_insert_2d = solid.union()(
    wells_top_bottom(...),
    make_chambers(...)
)

# Calculate inner taper dimensions
taper_len_in = deg_taper_len(INSERT_HEIGHT_IN, DEGREES_IN) + TAPER_LEN_IN_EXTRA
well_rad_inner = well_rad_outer - taper_len_in
...

# Create pins
pins = create_pin_array(...)

# Helper function to create insert
def create_insert(grid_size, alignment_config=None):
    outer_2d_array = create_device_array(...)
    inner_2d_array = create_device_array(...)
    insert_3d = solid.difference()(...)
    ...
```

**Proposed (~20 lines, declarative):**
```python
from openmfd.builders import InsertBuilder

# Define insert geometry once
insert = (
    InsertBuilder()
    .with_wells(radius=WELL_RAD, positions=well_positions)
    .with_channels(length=CHAN_L, width=CHAN_W, num_channels=NUM_CHANS, spacing=CHAN_GAP)
    .with_chambers(width=CHAMBER_WIDTH, length_until=CHAMBER_LEN_UNTIL)
    .with_outer_chamfer(height=INSERT_HEIGHT, degrees=DEGREES_OUT, extra_taper=TAPER_LEN_OUT_EXTRA)
    .with_inner_chamfer(height=INSERT_HEIGHT_IN, degrees=DEGREES_IN, extra_taper=TAPER_LEN_IN_EXTRA)
    .with_pins(dims=PIN_DIMS, offset=INSERT_PIN_OFFSET, height=PIN_HEIGHT + SKIRT_HEIGHT1 + SKIRT_HEIGHT2 + PIN_INNER_HEIGHT)
    .with_dual_skirt(
        thickness1=SKIRT_THICKNESS1, height1=SKIRT_HEIGHT1, empty1=SKIRT_EMPTY1,
        thickness2=SKIRT_THICKNESS2, height2=SKIRT_HEIGHT2
    )
    .build()
)

# Generate arrays with different grid sizes
array_insert = insert.to_array(grid_size=GRID_SIZE, alignment='full')
single_insert = insert.to_array(grid_size=[1, 1])

# Apply PDMS shrinkage and export
array_insert.scale(scale_percent).export_scad(BASE_PATH / f"{DEVICE_NAME}_wells_insert.scad")
single_insert.scale(scale_percent).export_scad(BASE_PATH / f"{DEVICE_NAME}_single_insert.scad")
```

**Benefits:**
- ✅ **70% line reduction** (67 → 20 lines)
- ✅ **No inline math** - all calculations encapsulated
- ✅ **Declarative** - clear intent
- ✅ **Reusable** - build once, array multiple times
- ✅ **Type-safe** - named parameters, not tuples

---

#### Example 2: Device Builder (Replaces lines 150-180)

**Current (30 lines):**
```python
well_positions = wells_pos_from_center_2(WELLS_POS)

# Create top layer
_, measurements = create_channels(CHAN_L)
insert_holes = solid.union()(*[...])
chamber_wells_single = solid.difference()(
    solid.union()(
        wells_top_bottom(...),
        make_chambers(...)
    ),
    insert_holes
)

# Create bottom layer
channels_single, _ = create_channels(CHAN_L + CHAN_L_EXTRA)

# Export
save_models(BASE_PATH, {
    f"{DEVICE_NAME}_single_bottom": channels_single,
    f"{DEVICE_NAME}_single_top": chamber_wells_single,
    f"{DEVICE_NAME}_single_aligned": solid.union()(chamber_wells_single, channels_single),
})
```

**Proposed (~15 lines):**
```python
from openmfd.builders import DeviceBuilder

device = (
    DeviceBuilder(name=DEVICE_NAME, dims=[CASING_X, CASING_Y, 0])
    .add_layer('bottom')
        .with_channels(length=CHAN_L + CHAN_L_EXTRA, width=CHAN_W, num_channels=NUM_CHANS, spacing=CHAN_GAP)
    .add_layer('top')
        .with_wells(radius=WELL_RAD, positions_from_center=WELLS_POS)
        .with_chambers(width=CHAMBER_WIDTH, length_until=CHAMBER_LEN_UNTIL)
        .with_insert_holes(dims=CHAMBER_HOLE_DIMS, offset=INSERT_PIN_OFFSET)
    .build()
)

# Export single device
device.export_all(BASE_PATH, suffix='single')
```

**Benefits:**
- ✅ **50% line reduction** (30 → 15 lines)
- ✅ **Layer-based API** - clear separation
- ✅ **Automatic alignment** - handles union/difference internally
- ✅ **Batch export** - single call for all variants

---

### Implementation Plan

#### Phase 1: Core Builder Classes

**File**: `openmfd/builders/base.py`
```python
class FluentBuilder:
    """Base class for fluent builder pattern."""
    def __init__(self):
        self._operations = []
    
    def build(self):
        """Execute all operations and return result."""
        raise NotImplementedError
```

**File**: `openmfd/builders/insert.py`
```python
class InsertBuilder(FluentBuilder):
    """Fluent API for building 3D well inserts."""
    
    def with_wells(self, radius, positions):
        """Add wells to insert geometry."""
        self._operations.append(('wells', {'radius': radius, 'positions': positions}))
        return self
    
    def with_channels(self, length, width, num_channels, spacing):
        """Add channels to insert geometry."""
        self._operations.append(('channels', {...}))
        return self
    
    def with_outer_chamfer(self, height, degrees, extra_taper=0):
        """Add outer chamfer with automatic taper calculation."""
        self._operations.append(('outer_chamfer', {...}))
        return self
    
    def build(self) -> 'Insert':
        """Build the insert geometry."""
        # Execute all operations and return Insert object
        return Insert(self._operations)
```

**File**: `openmfd/builders/device.py`
```python
class DeviceBuilder(FluentBuilder):
    """Fluent API for building microfluidic devices."""
    
    def add_layer(self, name):
        """Start defining a new layer."""
        self._current_layer = name
        return self
    
    def with_wells(self, radius, positions_from_center):
        """Add wells to current layer."""
        return self
    
    def with_channels(self, length, width, num_channels, spacing):
        """Add channels to current layer."""
        return self
```

---

#### Phase 2: Geometry Objects

**File**: `openmfd/geometry/insert.py`
```python
class Insert:
    """Represents a 3D well insert with fluent operations."""
    
    def to_array(self, grid_size, alignment=None):
        """Convert to device array."""
        return InsertArray(self, grid_size, alignment)
    
    def scale(self, factor):
        """Apply scaling (for PDMS shrinkage)."""
        return ScaledInsert(self, factor)
```

---

#### Phase 3: Export Utilities

**File**: `openmfd/export/fluent.py`
```python
class ExportableMixin:
    """Mixin for fluent export operations."""
    
    def export_scad(self, path):
        """Export to SCAD file."""
        solid.scad_render_to_file(self.geometry, str(path))
        return self
    
    def export_stl(self, path):
        """Export to STL file."""
        render_stl_with_viewscad(self.geometry, path)
        return self
```

---

### Expected Outcomes

**Line Count Reduction:**
- **Insert generation**: 67 → 20 lines (70% reduction)
- **Device generation**: 30 → 15 lines (50% reduction)
- **Array creation**: 19 → 5 lines (74% reduction)
- **Total**: ~116 → ~40 lines (65% reduction)

**Code Quality:**
- ✅ Eliminate inline math (encapsulated in builders)
- ✅ Eliminate duplicate `create_device_array()` calls
- ✅ Clear, declarative API
- ✅ Type-safe parameter passing
- ✅ Composable and reusable

**API Consistency:**
- ✅ Similar to OpenHCS Pipeline DSL
- ✅ Method chaining for fluent construction
- ✅ Separation of configuration and execution
- ✅ Minimal boilerplate

### Success Criteria

- [ ] InsertBuilder implemented with fluent API
- [ ] DeviceBuilder implemented with layer-based API
- [ ] Inline math eliminated (moved to builder methods)
- [ ] Duplicate code eliminated
- [ ] Example script reduced by 50%+ lines
- [ ] All outputs identical to current implementation
- [ ] API documentation with examples

---

## ⚠️ CRITICAL ISSUE: UI Integration & Config Framework

### Problem Identified

The proposed fluent builder API **will NOT work** with OpenHCS's UI engine and parameter form manager because:

❌ **Fluent builders are imperative code**, not declarative configuration
❌ **No way to introspect** available parameters for UI generation
❌ **Can't leverage config framework** - no dataclass structure
❌ **Incompatible with ParameterFormManager** - requires dataclass fields

### Discovery: OpenMFD Already Has Dataclasses!

**Existing configs in OpenMFD:**
- `WellConfiguration` (openmfd/geometry/wells.py)
- `ChannelConfiguration` (openmfd/geometry/channels.py)
- `ChamberConfiguration` (openmfd/geometry/chambers.py)
- `DeviceConfiguration` (openmfd/devices/config.py)
- `CasingConfiguration` (openmfd/devices/config.py)
- `ArrayConfiguration` (openmfd/devices/config.py)

**But the V2 script doesn't use them!** It uses low-level functions:
```python
# Current V2 script (NOT using configs)
_, measurements_outer = make_channels(
    length=chan_l_outer, width=CHAN_W, height=0.2,
    num_chans=NUM_CHANS, spacing=CHAN_GAP, dxf=True
)
outer_insert_2d = solid.union()(
    wells_top_bottom(radius=well_rad_outer, height=None,
                     positions=well_positions, dxf=True, shape="circle"),
    make_chambers(msrs=measurements_outer, height=0.2,
                  width=chamber_width_outer, len_until=CHAMBER_LEN_UNTIL, dxf=True)
)
```

**Why?** Because the existing configs are **too basic** for 3D printed inserts. They don't support:
- ❌ Chamfered extrusion with taper calculations
- ❌ Dual skirt systems
- ❌ Pin arrays
- ❌ PDMS shrinkage scaling
- ❌ Nested insert geometry (outer/inner chamfers)

The existing configs are designed for **simple 2D/3D devices**, not **complex 3D printed inserts**.

### OpenHCS UI Engine Requirements

OpenHCS's parameter form manager works by:
1. **Introspecting dataclass fields** using `dataclasses.fields()`
2. **Auto-generating UI widgets** based on type hints
3. **Using lazy config framework** for resolution and validation

Example from OpenHCS:
```python
from openhcs.pyqt_gui.widgets.parameter_form import ParameterFormManager

# Automatically creates Qt form from dataclass
form = ParameterFormManager.from_dataclass_instance(
    dataclass_instance=device_config,  # Must be a dataclass!
    field_id="device_config",
    color_scheme=color_scheme
)
```

**The fluent builder API can't do this** because it's code, not configuration.

---

## ✅ REVISED APPROACH: Extend Existing Configs for Inserts

### Strategy: Add Insert-Specific Configs (Not Replace)

**Create new configs for insert features** (in addition to existing device configs):

```python
from dataclasses import dataclass
from typing import Optional

# NEW: Insert-specific configurations
@dataclass
class ChamferConfig:
    """Configuration for chamfered extrusion.

    Attributes
    ----------
    height : float
        Extrusion height in mm.
    degrees : int
        Chamfer angle in degrees.
    extra_taper : float, default=0.0
        Additional taper length in mm beyond calculated taper.
    """
    height: float
    degrees: int
    extra_taper: float = 0.0

@dataclass
class SkirtConfig:
    """Configuration for a single skirt layer.

    Attributes
    ----------
    thickness : float
        Skirt wall thickness in mm (negative for outward offset).
    height : float
        Skirt height in mm.
    empty_height : float
        Height of empty space below skirt in mm.
    """
    thickness: float
    height: float
    empty_height: float

@dataclass
class DualSkirtConfig:
    """Configuration for dual skirt system.

    Attributes
    ----------
    inner : SkirtConfig
        Inner skirt configuration.
    outer : SkirtConfig
        Outer skirt configuration.
    pin_height : float
        Height of pin base in mm.
    """
    inner: SkirtConfig
    outer: SkirtConfig
    pin_height: float

@dataclass
class PinConfig:
    """Configuration for alignment pins.

    Attributes
    ----------
    dims : tuple[float, float]
        Pin dimensions (width, depth) in mm.
    offset : float
        Offset from well positions in mm.
    height : float
        Total pin height in mm.
    """
    dims: tuple[float, float]
    offset: float
    height: float

@dataclass
class InsertConfig:
    """Configuration for 3D printed well insert with chamfers.

    This extends the basic device configs with insert-specific features:
    - Nested chamfered geometry (outer/inner)
    - Dual skirt system
    - Alignment pins
    - PDMS shrinkage compensation

    Attributes
    ----------
    wells : WellConfiguration
        Well configuration (reuses existing OpenMFD config).
    channels : ChannelConfiguration
        Channel configuration (reuses existing OpenMFD config).
    chambers : ChamberConfiguration
        Chamber configuration (reuses existing OpenMFD config).
    outer_chamfer : ChamferConfig
        Outer chamfer configuration.
    inner_chamfer : ChamferConfig
        Inner chamfer configuration.
    skirts : DualSkirtConfig, optional
        Dual skirt configuration. If None, no skirts created.
    pins : PinConfig, optional
        Pin configuration. If None, no pins created.
    pdms_scale : float, default=1.0
        PDMS shrinkage compensation scale factor (e.g., 0.8 for 100°C cure).
    """
    wells: WellConfiguration  # Reuse existing!
    channels: ChannelConfiguration  # Reuse existing!
    chambers: ChamberConfiguration  # Reuse existing!
    outer_chamfer: ChamferConfig
    inner_chamfer: ChamferConfig
    skirts: Optional[DualSkirtConfig] = None
    pins: Optional[PinConfig] = None
    pdms_scale: float = 1.0
```

**UI auto-generates forms:**
```python
from openhcs.pyqt_gui.widgets.parameter_form import ParameterFormManager

# OpenHCS UI engine auto-generates forms from nested dataclasses!
# Nested configs create collapsible sections automatically
form = ParameterFormManager.from_dataclass_instance(
    dataclass_instance=InsertConfig(
        wells=WellConfiguration(radius=2.5),
        channels=ChannelConfiguration(length=0.3, width=0.01),
        chambers=ChamberConfiguration(height=0.2),
        outer_chamfer=ChamferConfig(height=3.8, degrees=16),
        inner_chamfer=ChamferConfig(height=0.4, degrees=35),
        skirts=DualSkirtConfig(...),
        pins=PinConfig(...)
    ),
    field_id="insert_config"
)
```

**Build geometry from config:**
```python
from openmfd.inserts import build_insert
from openmfd.geometry import WellConfiguration, ChannelConfiguration, ChamberConfiguration

# Define configuration (reuses existing OpenMFD configs!)
config = InsertConfig(
    wells=WellConfiguration(radius=2.5, positions=[(4.5, 0), (-4.5, 0)]),
    channels=ChannelConfiguration(length=0.3, width=0.01, num_channels=83, spacing=0.03),
    chambers=ChamberConfiguration(height=0.2, len_until=4.5),
    outer_chamfer=ChamferConfig(height=3.8, degrees=16, extra_taper=0.3),
    inner_chamfer=ChamferConfig(height=0.4, degrees=35, extra_taper=0.0),
    skirts=DualSkirtConfig(
        inner=SkirtConfig(thickness=-0.5, height=0.5, empty_height=0.2),
        outer=SkirtConfig(thickness=-1.0, height=1.0, empty_height=0.0),
        pin_height=0.3
    ),
    pins=PinConfig(dims=(0.5, 0.5), offset=0.2, height=5.0),
    pdms_scale=0.8  # 100°C cure shrinkage
)

# Simple function-based API (like OpenHCS FunctionStep)
insert_geometry = build_insert(config)

# Export
from openmfd.export import export_scad
export_scad(insert_geometry, "output.scad")
```

**Benefits:**
- ✅ **Full UI integration** - ParameterFormManager works with nested dataclasses
- ✅ **Reuses existing configs** - WellConfiguration, ChannelConfiguration, ChamberConfiguration
- ✅ **Extends for inserts** - ChamferConfig, SkirtConfig, PinConfig
- ✅ **Config framework** - lazy resolution, validation
- ✅ **Type-safe** - dataclass fields with type hints
- ✅ **Self-documenting** - docstrings become tooltips in UI
- ✅ **Consistent with OpenHCS** - same architectural patterns

---

### Option 2: Hybrid (Config + Optional Fluent Layer)

**Primary API: Config-driven (for UI)**
```python
@dataclass
class InsertConfig:
    well_radius: float = 2.5
    channel_length: float = 0.3
    # ...

# UI uses this
config = InsertConfig()
insert = build_insert(config)
```

**Secondary API: Fluent convenience (for advanced scripting)**
```python
# Advanced users can bypass config for quick prototyping
insert = (
    InsertBuilder()
    .with_wells(radius=2.5)
    .with_channels(length=0.3)
    .build()
)

# Or convert fluent to config
config = InsertBuilder().with_wells(...).to_config()
```

**Benefits:**
- ✅ UI integration (via config)
- ✅ Convenience for scripting (via fluent)
- ⚠️ Two APIs to maintain

---

### Option 3: Pipeline-Based (Most Integrated)

**Treat device generation as a pipeline step:**
```python
from openhcs.core.steps.function_step import FunctionStep
from openmfd.steps import DeviceGenerationStep

# Define device config
@dataclass
class DeviceConfig:
    insert: InsertConfig
    array_size: Tuple[int, int] = (6, 8)
    # ...

# Use in OpenHCS pipeline
pipeline = Pipeline([
    DeviceGenerationStep(
        config=DeviceConfig(),
        output_path="./designs/"
    )
])

# Or standalone
device_step = DeviceGenerationStep(config=DeviceConfig())
device_step.execute()
```

**Benefits:**
- ✅ **Fully integrated** with OpenHCS ecosystem
- ✅ **Reusable in pipelines** - can combine with image processing
- ✅ **UI integration** - config-driven
- ✅ **Consistent architecture** - same as OpenHCS steps

---

## 🎯 RECOMMENDED APPROACH

**Use Option 1 (Pure Config-Driven) with Option 3 (Pipeline Integration)**

### Architecture:

```
openmfd/
├── config/
│   ├── __init__.py
│   ├── wells.py          # WellConfig dataclass
│   ├── channels.py       # ChannelConfig dataclass
│   ├── inserts.py        # InsertConfig dataclass
│   └── devices.py        # DeviceConfig dataclass
├── builders/
│   ├── __init__.py
│   ├── insert.py         # build_insert(config) function
│   └── device.py         # build_device(config) function
└── steps/
    ├── __init__.py
    └── generation.py     # DeviceGenerationStep for pipelines
```

### Example Usage:

**1. Define configuration (UI-compatible):**
```python
from openmfd.config import InsertConfig, WellConfig, ChannelConfig

config = InsertConfig(
    wells=WellConfig(radius=2.5, positions_from_center=4.5),
    channels=ChannelConfig(length=0.3, width=0.01, num_channels=83),
    # ...
)
```

**2. Generate UI form automatically:**
```python
# OpenHCS UI engine auto-generates this
form = ParameterFormManager.from_dataclass_instance(config, "insert_config")
```

**3. Build geometry from config:**
```python
from openmfd.builders import build_insert

insert = build_insert(config)
insert.export_scad("output.scad")
```

**4. Use in pipelines:**
```python
from openmfd.steps import DeviceGenerationStep

step = DeviceGenerationStep(config=config, output_path="./designs/")
pipeline = Pipeline([step])
```

---

## 📋 Updated Success Criteria

- [ ] Config dataclasses defined (WellConfig, ChannelConfig, InsertConfig, DeviceConfig)
- [ ] Config framework integration (`@device_config` decorator)
- [ ] Builder functions implemented (`build_insert()`, `build_device()`)
- [ ] UI integration verified (ParameterFormManager works)
- [ ] Pipeline step implemented (DeviceGenerationStep)
- [ ] Inline math eliminated (encapsulated in builder functions)
- [ ] Example script uses config-driven API
- [ ] Documentation with UI screenshots

