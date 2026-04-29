# 4x4 Preset Refactoring - Following OpenHCS Principles

## Problem

Initial implementation of `FourByFourDeviceConfig` duplicated **274 lines** of code from `TwoCompartmentDeviceConfig`:
- All methods (`wells_config()`, `channels_config()`, `chambers_config()`, `insert_config()`, `bottom_layer()`, `top_layer()`)
- All computed properties (`_chamber_len_until()`, `_chamber_width()`, `_num_channels()`)
- Validation logic

This violated the **Algebraic Common Factors Principle**: "If you see the same logical structure repeated with only parameter variations, extract the common pattern into a parameterized function."

## Solution

Applied **inheritance** instead of duplication. The 4x4 device is just a 2-compartment device with different default parameters.

### Before (274 lines of duplication):

```python
@dataclass(frozen=True)
class FourByFourDeviceConfig(CompartmentalizedDevicePreset):
    """Concrete preset for 4x4 2-compartment devices."""
    
    # 70 lines of parameter definitions (mostly duplicates)
    casing_x: float = 12.0
    casing_y: float = 6.0
    well_radius: float = 2.0
    wells_pos: float = 3.0
    channel_length: float = 0.3  # DUPLICATE!
    channel_length_extra: float = 6.0  # DUPLICATE!
    channel_width: float = 0.01  # DUPLICATE!
    channel_gap: float = 0.03  # DUPLICATE!
    # ... 60+ more lines of duplicates ...
    
    # 204 lines of duplicated methods
    def validate(self) -> None:
        # 20 lines - DUPLICATE!
        
    def _chamber_len_until(self) -> float:
        # DUPLICATE!
        
    def _chamber_width(self) -> float:
        # DUPLICATE!
        
    def _num_channels(self) -> int:
        # DUPLICATE!
        
    def wells_config(self) -> WellConfiguration:
        # 15 lines - DUPLICATE!
        
    def channels_config(self, use_extra_length: bool = False) -> ChannelConfiguration:
        # 18 lines - DUPLICATE!
        
    def chambers_config(self) -> ChamberConfiguration:
        # 8 lines - DUPLICATE!
        
    def insert_config(self) -> CompleteInsertConfiguration:
        # 50 lines - DUPLICATE!
        
    def bottom_layer(self) -> CompleteDeviceConfiguration:
        # 40 lines - DUPLICATE!
        
    def top_layer(self) -> CompleteDeviceConfiguration:
        # 45 lines - DUPLICATE!
```

### After (34 lines - only overrides):

```python
@dataclass(frozen=True)
class FourByFourDeviceConfig(TwoCompartmentDeviceConfig):
    """Preset for 4x4 2-compartment devices (smaller scale production).
    
    Inherits all behavior from TwoCompartmentDeviceConfig, only overriding
    the parameters that differ for 4x4 format:
    - Smaller wells and closer spacing
    - Smaller wafer (100mm vs 150mm)
    - No wall padding
    - Different alignment mark positions
    - Default 4x4 grid
    """
    
    # Override only 4x4-specific geometry
    casing_x: float = 12.0  # vs 18.0 for 96-well
    casing_y: float = 6.0   # vs 9.0 for 96-well
    well_radius: float = 2.0  # vs 2.5 for 96-well
    wells_pos: float = 3.0  # vs 4.5 for 96-well
    
    # Override 4x4-specific wafer parameters
    wafer_size: float = 100.0  # vs 150.0 for 96-well
    wafer_flat_length: float = 32.5  # vs 57.5 for 96-well
    
    # Override 4x4-specific alignment
    units_from_center: Tuple[float, float] = (2.3, 2.3)  # vs (7.0, 4.75) for 96-well
    
    # Override 4x4-specific wall parameters (no padding)
    wall_padx: float = 0.0  # vs 9.0 for 96-well
    wall_pady: float = 0.0  # vs 9.0 for 96-well
    
    # Default grid size for 4x4
    grid_size: Tuple[int, int] = (4, 4)  # vs (6, 8) for 96-well
    
    # All other parameters and methods inherited from TwoCompartmentDeviceConfig!
```

## Results

### Quantitative Improvements

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| **FourByFourDeviceConfig lines** | 274 | 34 | **88%** ✅ |
| **Duplicated methods** | 8 methods | 0 methods | **100%** ✅ |
| **Duplicated parameters** | 60+ params | 8 params | **87%** ✅ |
| **presets.py total lines** | 777 | 538 | **31%** ✅ |

### Example Usage Simplification

**Before (needed to override 15+ parameters):**
```python
preset = TwoCompartmentDeviceConfig(
    device_name="2_compartment_4x4_300um_suex200_v27",
    cure_temp=100,
    wells_pos=3.0,
    well_radius=2.0,
    casing_x=12.0,
    casing_y=6.0,
    grid_size=(4, 4),
    wafer_size=100.0,
    wafer_flat_length=32.5,
    units_from_center=(2.3, 2.3),
    wall_padx=0.0,
    wall_pady=0.0,
    # ... still need to remember all the differences!
)
```

**After (use dedicated preset with correct defaults):**
```python
preset = FourByFourDeviceConfig(
    device_name="2_compartment_4x4_300um_suex200_v27",
    cure_temp=100,
    # That's it! All 4x4-specific parameters are already set as defaults.
)
```

### Example File Comparison

| Version | Lines | Reduction |
|---------|-------|-----------|
| **REFACTORED** | 239 lines | Baseline |
| **PRESET** | 142 lines | **41%** ✅ |

## OpenHCS Principles Applied

### 1. Algebraic Common Factors Principle ✅

**Before:** Duplicate code patterns (like `3x + 3y`)  
**After:** Factored out common pattern (like `3(x + y)`)

The 4x4 device is mathematically equivalent to:
```
FourByFourDeviceConfig = TwoCompartmentDeviceConfig(
    casing_x=12.0,
    casing_y=6.0,
    well_radius=2.0,
    wells_pos=3.0,
    wafer_size=100.0,
    wafer_flat_length=32.5,
    units_from_center=(2.3, 2.3),
    wall_padx=0.0,
    wall_pady=0.0,
    grid_size=(4, 4)
)
```

### 2. Single Responsibility Principle ✅

Each preset class has a single responsibility:
- `TwoCompartmentDeviceConfig`: Define 2-compartment device behavior
- `FourByFourDeviceConfig`: Override parameters for 4x4 format

### 3. DRY (Don't Repeat Yourself) ✅

**Before:** 274 lines of duplicated code  
**After:** 0 lines of duplicated code

### 4. Inheritance Over Composition ✅

Used inheritance to specialize behavior rather than duplicating implementation.

## Key Insight

The 4x4 device is **not a different device type** - it's the **same 2-compartment device** with different dimensions for smaller-scale production. This is exactly what inheritance is for!

## Validation

✅ All tests pass  
✅ Generated SCAD files identical to previous version  
✅ 88% reduction in code duplication  
✅ Cleaner, more maintainable codebase  
✅ Follows OpenHCS refactoring principles  

## Future Extensions

This pattern makes it trivial to add more device variants:

```python
@dataclass(frozen=True)
class PrototypeDeviceConfig(TwoCompartmentDeviceConfig):
    """Single-device prototype format."""
    grid_size: Tuple[int, int] = (1, 1)
    # That's it!

@dataclass(frozen=True)
class HighThroughputDeviceConfig(TwoCompartmentDeviceConfig):
    """High-throughput 12x8 format."""
    grid_size: Tuple[int, int] = (12, 8)
    # That's it!
```

Each new variant is just a few lines of parameter overrides, not hundreds of lines of duplicated code.

