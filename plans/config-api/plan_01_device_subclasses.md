# plan_01_device_subclasses.md
## Component: Device-Specific Configuration Subclasses

### Objective
Create device-specific configuration subclasses that inherit from base configurations and provide sensible defaults, reducing boilerplate in example scripts. This follows the inheritance pattern from OpenHCS's config framework.

### Plan

#### 1. Multi-Layer ABC Hierarchy for Type Safety
**File:** `openmfd/devices/presets.py`

Create a **multi-layer inheritance hierarchy** for increased type safety and semantics:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

@dataclass
class DevicePreset(ABC):
    """Abstract base class for device configuration presets.

    All device-specific presets must inherit from this class and implement
    the required methods. This ensures a consistent interface across all
    device types.

    This follows OpenHCS's pattern of using ABCs for extensible components
    (similar to how OpenHCS uses ABCs for pipeline stages, processors, etc.).
    """

    # Common parameters all devices share
    cure_temp: int = 100
    grid_size: Tuple[int, int] = (6, 8)
    device_name: str = ""

    @abstractmethod
    def bottom_layer(self) -> CompleteDeviceConfiguration:
        """Generate bottom layer configuration.

        Returns
        -------
        CompleteDeviceConfiguration
            Complete configuration for bottom layer (typically channels only).
        """
        pass

    @abstractmethod
    def top_layer(self) -> CompleteDeviceConfiguration:
        """Generate top layer configuration.

        Returns
        -------
        CompleteDeviceConfiguration
            Complete configuration for top layer (typically wells + chambers).
        """
        pass

    @abstractmethod
    def insert_config(self) -> CompleteInsertConfiguration:
        """Generate 3D printed insert configuration.

        Returns
        -------
        CompleteInsertConfiguration
            Complete configuration for 3D printed insert.
        """
        pass

    @abstractmethod
    def validate(self) -> None:
        """Validate configuration parameters.

        Raises
        ------
        ValueError
            If configuration parameters are invalid or incompatible.
        """
        pass
```

**Why ABC?**
- ✅ **Enforces interface consistency** - All presets must implement the same methods
- ✅ **Type safety** - Static type checkers can verify implementations
- ✅ **Self-documenting** - Abstract methods show what must be implemented
- ✅ **OpenHCS-style** - Matches OpenHCS's use of ABCs for extensibility
- ✅ **IDE support** - IDEs can warn about missing implementations

#### 2. Two-Compartment Device Preset (Concrete Implementation)
**Class:** `TwoCompartmentDeviceConfig(DevicePreset)`

Create a concrete implementation of `DevicePreset` for the 2-compartment 96-well device with defaults:
- **Casing dimensions:** 18mm x 9mm (standard for 2-compartment)
- **Well configuration:** 2 circular wells, radius 2.5mm
- **Channel configuration:** 83 channels, 0.01mm width, standard spacing
- **Chamber configuration:** 0.2mm height, standard width
- **Array configuration:** 6x8 grid (96-well plate compatible)
- **PDMS configuration:** 100°C cure temperature (standard)
- **Wafer mask:** 150mm wafer, 57.5mm flat length (4-inch wafer)
- **Alignment:** Standard offset and mark size

**Override pattern:**
```python
# Minimal usage - all defaults
config = TwoCompartmentDeviceConfig()

# Override specific parameters
config = TwoCompartmentDeviceConfig(
    cure_temp=80,  # Different cure temperature
    grid_size=(4, 6),  # Different array size
)
```

#### 3. Four-Compartment Device Preset (Concrete Implementation)
**Class:** `FourCompartmentDeviceConfig(DevicePreset)`

Create a concrete implementation of `DevicePreset` for 4-compartment devices with defaults:
- **Casing dimensions:** 18mm x 18mm (square for 4 wells)
- **Well configuration:** 4 circular wells at corners
- **Channel configuration:** Similar to 2-compartment but adjusted for 4 wells
- **Chamber configuration:** Standard settings
- **Array configuration:** Configurable grid
- **PDMS/Wafer:** Same as 2-compartment

#### 4. Inheritance Strategy (OpenHCS-Style)

Use ABC + dataclass pattern (OpenHCS style) with `field(default=...)` to provide defaults:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Tuple

@dataclass
class TwoCompartmentDeviceConfig(DevicePreset):
    """Preset configuration for 2-compartment 96-well devices.
    
    Provides sensible defaults for all parameters. Override only what you need.
    
    Examples
    --------
    >>> # Use all defaults
    >>> config = TwoCompartmentDeviceConfig()
    >>> 
    >>> # Override cure temperature
    >>> config = TwoCompartmentDeviceConfig(cure_temp=80)
    >>> 
    >>> # Override grid size
    >>> config = TwoCompartmentDeviceConfig(grid_size=(4, 6))
    """
    
    # Device-specific defaults
    casing_x: float = 18.0
    casing_y: float = 9.0
    well_radius: float = 2.5
    channel_length: float = 6.3
    channel_width: float = 0.01
    num_channels: int = 83
    
    # Array defaults
    grid_rows: int = 6
    grid_columns: int = 8
    
    # PDMS defaults
    cure_temp: int = 100
    
    # Wafer defaults
    wafer_size: float = 150.0
    wafer_flat_length: float = 57.5
    
    def validate(self) -> None:
        """Validate configuration parameters (required by ABC)."""
        if self.cure_temp < 0 or self.cure_temp > 200:
            raise ValueError(f"cure_temp must be 0-200°C, got {self.cure_temp}")
        if self.grid_rows < 1 or self.grid_columns < 1:
            raise ValueError(f"grid_size must be positive, got ({self.grid_rows}, {self.grid_columns})")

    def bottom_layer(self) -> CompleteDeviceConfiguration:
        """Generate bottom layer config (required by ABC)."""
        # Implementation here
        ...

    def top_layer(self) -> CompleteDeviceConfiguration:
        """Generate top layer config (required by ABC)."""
        # Implementation here
        ...

    def insert_config(self) -> CompleteInsertConfiguration:
        """Generate insert config (required by ABC)."""
        # Implementation here
        ...
```

#### 5. Builder Pattern Integration

The preset classes should integrate with the existing builder:

```python
# Old way (127 lines of config)
bottom_config = CompleteDeviceConfiguration(
    device=DeviceConfiguration(
        casing=CasingConfiguration(x=18, y=9),
        channels_config=ChannelConfiguration(...),
        ...
    ),
    array=ArrayConfiguration(...),
    pdms=PDMSConfiguration(...),
    ...
)

# New way (3 lines!)
config = TwoCompartmentDeviceConfig(cure_temp=100)
device_stack = build_device_stack(
    config.bottom_layer(),
    config.top_layer()
)
```

#### 6. Layer Separation

Each preset should provide methods to generate bottom and top layer configs:

```python
class TwoCompartmentDeviceConfig:
    def bottom_layer(self) -> CompleteDeviceConfiguration:
        """Generate bottom layer configuration (channels only)."""
        return CompleteDeviceConfiguration(
            device=DeviceConfiguration(
                casing=CasingConfiguration(x=self.casing_x, y=self.casing_y),
                channels_config=self._build_channels_config(),
                add_wells=False,
                add_chambers=False,
                dxf=True
            ),
            array=self._build_array_config(),
            text_annotations=self._build_text_annotations(),
            pdms=self._build_pdms_config(),
            wafer_mask=self._build_wafer_mask_config(),
            alignment_offset=self.alignment_offset,
            alignment_mark_size=self.alignment_mark_size
        )
    
    def top_layer(self) -> CompleteDeviceConfiguration:
        """Generate top layer configuration (wells + chambers + insert holes)."""
        return CompleteDeviceConfiguration(
            device=DeviceConfiguration(
                casing=CasingConfiguration(x=self.casing_x, y=self.casing_y),
                wells_config=self._build_wells_config(),
                channels_config=self._build_channels_config(),
                chambers_config=self._build_chambers_config(),
                insert_holes=self._build_insert_holes_config(),
                add_wells=True,
                add_chambers=True,
                dxf=True
            ),
            array=self._build_array_config(),
            outline=self._build_outline_config(),
            pdms=self._build_pdms_config(),
            wafer_mask=self._build_wafer_mask_config(),
            alignment_offset=self.alignment_offset,
            alignment_mark_size=self.alignment_mark_size
        )
```

#### 7. Insert Configuration Integration

Each preset should also provide insert configuration:

```python
class TwoCompartmentDeviceConfig:
    def insert_config(self) -> CompleteInsertConfiguration:
        """Generate 3D printed insert configuration."""
        return CompleteInsertConfiguration(
            wells=self._build_wells_config(),
            channels=self._build_channels_config(),
            chambers=self._build_chambers_config(),
            outer_taper=self._build_outer_taper_config(),
            inner_taper=self._build_inner_taper_config(),
            pins=self._build_pins_config(),
            skirts=self._build_skirts_config(),
            pdms_scale=self._build_pdms_config().scale_factor(),
            well_positions=self._calculate_well_positions(),
            dims=(self.casing_x, self.casing_y, self.insert_height)
        )
```

#### 8. Example Script Transformation

**Before (367 lines):**
```python
# 100+ lines of configuration setup
channels_config = ChannelConfiguration(...)
array_config = ArrayConfiguration(...)
pdms_config = PDMSConfiguration(...)
wafer_mask_config = WaferMaskConfiguration(...)
bottom_text_annotations = [...]
outline_config = OutlineConfiguration(...)

bottom_complete_config = CompleteDeviceConfiguration(...)
top_complete_config = CompleteDeviceConfiguration(...)

device_stack = build_device_stack(bottom_complete_config, top_complete_config)
```

**After (~50 lines):**
```python
# Single preset with minimal overrides
preset = TwoCompartmentDeviceConfig(
    cure_temp=100,
    grid_size=(6, 8),
    device_name="2_compartment_96_well_300um_suex200_v27"
)

# Generate all outputs
insert = build_insert(preset.insert_config(), grid_size=preset.grid_size)
device_stack = build_device_stack(preset.bottom_layer(), preset.top_layer())
walls = create_wafer_walls(...)

# Save everything
save_models(...)
```

**Expected reduction:** 367 → ~50 lines (86% reduction!)

### OpenHCS-Style Design Patterns

This design follows several key OpenHCS patterns:

#### 1. ABC for Extensibility
**OpenHCS precedent:** `PipelineStage`, `Processor`, `DataSource` are all ABCs
- Defines clear interface contracts
- Enforces implementation of required methods
- Enables polymorphism and type safety
- Self-documenting through abstract method signatures

#### 2. Dataclass + ABC Combination
**OpenHCS precedent:** Many OpenHCS components combine `@dataclass` with `ABC`
```python
@dataclass
class DevicePreset(ABC):
    # Common fields with defaults
    cure_temp: int = 100

    # Abstract methods enforce interface
    @abstractmethod
    def bottom_layer(self) -> CompleteDeviceConfiguration:
        pass
```

#### 3. Frozen Dataclasses for Immutability
**OpenHCS precedent:** Most OpenHCS configs use `@dataclass(frozen=True)`
- Prevents accidental mutation
- Makes configs hashable (can be used as dict keys)
- Signals intent: configs are immutable once created

**Should we use `frozen=True`?**
- ✅ Yes for `DevicePreset` - configs should be immutable
- ✅ Matches OpenHCS's immutable config philosophy
- ✅ Prevents bugs from accidental mutation

#### 4. Validation in `__post_init__` or `validate()`
**OpenHCS precedent:** Configs validate themselves on construction
- Fail-loud philosophy: catch errors early
- Provide helpful error messages with solutions
- Use `validate()` method for complex validation

#### 5. Type Hints Everywhere
**OpenHCS precedent:** Full type coverage with strict mypy
- All methods have return type hints
- All parameters have type hints
- Enables static analysis and IDE support

#### 6. Builder Pattern for Complex Objects
**OpenHCS precedent:** `ParameterFormManager.from_dataclass_instance()`
- High-level presets hide complexity
- Users work with simple parameters
- Internal methods build complex nested structures

### Findings

#### Existing Config Framework
- ✅ `CompleteDeviceConfiguration` already exists with all necessary fields
- ✅ `CompleteInsertConfiguration` already exists for insert generation
- ✅ All base configs use `@dataclass` which supports inheritance
- ✅ Builder functions (`build_device_stack`, `build_insert`) already accept configs

#### Dataclass Inheritance Patterns
From Python dataclasses documentation:
- Subclasses can override field defaults
- `field(default=...)` can be used for complex defaults
- `__post_init__` can construct nested objects from simple parameters
- Type hints are preserved in subclasses

#### OpenHCS Precedent
OpenHCS uses similar pattern with `@global_pipeline_config` decorator:
- Base configs define structure
- Subclasses provide domain-specific defaults
- Users override only what they need
- Full type safety maintained

#### Well Position Calculations
Current code uses helper functions:
- `wells_pos_from_center_2()` - Calculate 2-well positions
- `four_corner()` - Calculate 4-well positions
- These should be encapsulated in preset classes

#### Device-Specific Constants
Each device type has standard values:
- **2-compartment:** 18x9mm casing, 2.5mm well radius, 83 channels
- **4-compartment:** 18x18mm casing, 4 wells at corners
- **PDMS:** 100°C cure is standard, 80°C for special cases
- **Wafer:** 150mm (4-inch) is standard, 100mm (3-inch) for smaller devices

### Implementation Draft

#### File Structure
```
openmfd/devices/
├── __init__.py          # Export DevicePreset and concrete presets
├── config.py            # Existing config dataclasses
├── assembly.py          # Existing assembly functions
├── builder.py           # Existing high-level builders
└── presets.py           # NEW: ABC + concrete preset implementations
```

#### Key Implementation Points

**1. Use `@dataclass(frozen=True)` for immutability (OpenHCS-style)**
```python
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class DevicePreset(ABC):
    """Abstract base for all device presets (immutable)."""
    ...
```

**2. Enforce interface with `@abstractmethod`**
```python
@abstractmethod
def bottom_layer(self) -> CompleteDeviceConfiguration:
    """All presets MUST implement this."""
    pass
```

**3. Validate in `validate()` method (fail-loud)**
```python
def validate(self) -> None:
    """Validate configuration (OpenHCS fail-loud philosophy)."""
    if self.cure_temp < 0 or self.cure_temp > 200:
        raise ValueError(
            f"cure_temp must be 0-200°C, got {self.cure_temp}. "
            f"Solution: Use cure_temp between 80-120°C for PDMS."
        )
```

**4. Type hints everywhere**
```python
def bottom_layer(self) -> CompleteDeviceConfiguration:
    """Return type explicitly declared."""
    ...
```

**5. Export through `__init__.py`**
```python
# openmfd/devices/__init__.py
from .presets import (
    DevicePreset,
    TwoCompartmentDeviceConfig,
    FourCompartmentDeviceConfig,
)

__all__ = [
    # ... existing exports ...
    "DevicePreset",
    "TwoCompartmentDeviceConfig",
    "FourCompartmentDeviceConfig",
]
```

*Full code will be written here after smell loop approval.*

### Benefits

1. **Massive boilerplate reduction:** 367 → ~50 lines (86% reduction)
2. **Type-safe defaults:** IDE autocomplete for all parameters
3. **Easy customization:** Override only what you need
4. **Consistent naming:** Standard parameter names across device types
5. **Self-documenting:** Preset class name indicates device type
6. **Testable:** Each preset can have unit tests for default values
7. **Extensible:** Easy to add new device types (e.g., `SingleCompartmentDeviceConfig`)

### Next Steps After Implementation

1. Update example scripts to use presets
2. Create presets for other device types (4-compartment, single-compartment)
3. Add unit tests for preset configurations
4. Document preset usage in README
5. Consider adding validation in `__post_init__` for parameter combinations

