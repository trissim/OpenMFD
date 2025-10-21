# OpenMFD Extension Guide: Practical Implementation

**Based on**: OpenHCS architectural patterns  
**Goal**: Add validation, error handling, logging, and testing to OpenMFD

---

## Phase 1: Validation System

### Step 1.1: Create Fabrication Constraints

**File**: `openmfd/validation/constraints.py`

```python
"""Fabrication constraints for microfluidic devices."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class FabricationConstraints:
    """Physical constraints for microfluidic device fabrication.
    
    These constraints are based on standard photolithography and
    soft lithography fabrication methods.
    
    Attributes
    ----------
    min_channel_width : float
        Minimum channel width in mm (default: 0.010 = 10μm)
    max_channel_width : float
        Maximum channel width in mm (default: 1.000 = 1mm)
    min_well_diameter : float
        Minimum well diameter in mm (default: 0.5mm)
    max_well_diameter : float
        Maximum well diameter in mm (default: 10.0mm)
    min_well_spacing : float
        Minimum spacing between wells in mm (default: 1.0mm)
    min_su8_height : float
        Minimum SU-8 photoresist height in mm (default: 0.025 = 25μm)
    max_su8_height : float
        Maximum SU-8 photoresist height in mm (default: 0.500 = 500μm)
    min_feature_size : float
        Minimum feature size for photolithography in mm (default: 0.005 = 5μm)
    """
    
    # Channel constraints
    min_channel_width: float = 0.010  # 10μm
    max_channel_width: float = 1.000  # 1mm
    
    # Well constraints
    min_well_diameter: float = 0.5    # 500μm
    max_well_diameter: float = 10.0   # 10mm
    min_well_spacing: float = 1.0     # 1mm
    
    # SU-8 photoresist constraints
    min_su8_height: float = 0.025     # 25μm
    max_su8_height: float = 0.500     # 500μm
    
    # General fabrication
    min_feature_size: float = 0.005   # 5μm
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            'min_channel_width': self.min_channel_width,
            'max_channel_width': self.max_channel_width,
            'min_well_diameter': self.min_well_diameter,
            'max_well_diameter': self.max_well_diameter,
            'min_well_spacing': self.min_well_spacing,
            'min_su8_height': self.min_su8_height,
            'max_su8_height': self.max_su8_height,
            'min_feature_size': self.min_feature_size,
        }


# Standard constraint sets for different fabrication methods
PHOTOLITHOGRAPHY_CONSTRAINTS = FabricationConstraints()

SOFT_LITHOGRAPHY_CONSTRAINTS = FabricationConstraints(
    min_channel_width=0.050,  # 50μm (PDMS molding less precise)
    min_feature_size=0.020,   # 20μm
)

MICROMILLING_CONSTRAINTS = FabricationConstraints(
    min_channel_width=0.100,  # 100μm (milling tool size)
    min_feature_size=0.100,   # 100μm
    max_su8_height=5.000,     # 5mm (can mill deeper)
)
```

### Step 1.2: Create Validation Exceptions

**File**: `openmfd/validation/exceptions.py`

```python
"""Validation exceptions for OpenMFD."""

from typing import Optional


class ValidationError(Exception):
    """Base exception for validation errors."""
    pass


class FabricationConstraintError(ValidationError):
    """Raised when device violates fabrication constraints."""
    
    def __init__(
        self,
        field: str,
        value: float,
        constraint: str,
        message: Optional[str] = None
    ):
        self.field = field
        self.value = value
        self.constraint = constraint
        
        error_msg = (
            f"Fabrication constraint violated: {field}\n"
            f"  Value: {value}mm\n"
            f"  Constraint: {constraint}"
        )
        if message:
            error_msg += f"\n  Details: {message}"
        
        super().__init__(error_msg)


class GeometryValidationError(ValidationError):
    """Raised when geometry is invalid."""
    
    def __init__(self, message: str, geometry_type: Optional[str] = None):
        self.geometry_type = geometry_type
        
        error_msg = "Geometry validation failed"
        if geometry_type:
            error_msg += f" ({geometry_type})"
        error_msg += f": {message}"
        
        super().__init__(error_msg)


class ConfigurationValidationError(ValidationError):
    """Raised when configuration is invalid."""
    
    def __init__(self, config_type: str, field: str, message: str):
        self.config_type = config_type
        self.field = field
        
        error_msg = (
            f"Configuration validation failed: {config_type}.{field}\n"
            f"  {message}"
        )
        
        super().__init__(error_msg)
```

### Step 1.3: Create Validators

**File**: `openmfd/validation/validators.py`

```python
"""Validation functions for device configurations."""

import logging
from typing import List
from dataclasses import dataclass

from openmfd.geometry import WellConfiguration, ChannelConfiguration
from openmfd.devices import DeviceConfiguration
from .constraints import FabricationConstraints, PHOTOLITHOGRAPHY_CONSTRAINTS
from .exceptions import FabricationConstraintError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation check."""
    is_valid: bool
    errors: List[FabricationConstraintError]
    warnings: List[str]


def validate_well_configuration(
    config: WellConfiguration,
    constraints: FabricationConstraints = PHOTOLITHOGRAPHY_CONSTRAINTS
) -> ValidationResult:
    """Validate well configuration against fabrication constraints."""
    errors = []
    warnings = []
    
    # Check diameter
    if config.diameter < constraints.min_well_diameter:
        errors.append(FabricationConstraintError(
            field="wells_config.diameter",
            value=config.diameter,
            constraint=f">= {constraints.min_well_diameter}mm",
            message="Well too small for reliable fabrication"
        ))
    
    if config.diameter > constraints.max_well_diameter:
        errors.append(FabricationConstraintError(
            field="wells_config.diameter",
            value=config.diameter,
            constraint=f"<= {constraints.max_well_diameter}mm",
            message="Well too large for standard wafer"
        ))
    
    # Check spacing
    if hasattr(config, 'spacing') and config.spacing < constraints.min_well_spacing:
        errors.append(FabricationConstraintError(
            field="wells_config.spacing",
            value=config.spacing,
            constraint=f">= {constraints.min_well_spacing}mm",
            message="Wells too close together"
        ))
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_channel_configuration(
    config: ChannelConfiguration,
    constraints: FabricationConstraints = PHOTOLITHOGRAPHY_CONSTRAINTS
) -> ValidationResult:
    """Validate channel configuration against fabrication constraints."""
    errors = []
    warnings = []
    
    # Check width
    if config.width < constraints.min_channel_width:
        errors.append(FabricationConstraintError(
            field="channels_config.width",
            value=config.width,
            constraint=f">= {constraints.min_channel_width}mm",
            message="Channel too narrow for photolithography"
        ))
    
    if config.width > constraints.max_channel_width:
        warnings.append(
            f"Channel width {config.width}mm is unusually large (>{constraints.max_channel_width}mm)"
        )
    
    # Check height (SU-8 constraints)
    if config.height < constraints.min_su8_height:
        errors.append(FabricationConstraintError(
            field="channels_config.height",
            value=config.height,
            constraint=f">= {constraints.min_su8_height}mm",
            message="Channel height below minimum SU-8 thickness"
        ))
    
    if config.height > constraints.max_su8_height:
        errors.append(FabricationConstraintError(
            field="channels_config.height",
            value=config.height,
            constraint=f"<= {constraints.max_su8_height}mm",
            message="Channel height exceeds maximum SU-8 thickness"
        ))
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_device_configuration(
    config: DeviceConfiguration,
    constraints: FabricationConstraints = PHOTOLITHOGRAPHY_CONSTRAINTS,
    strict: bool = False
) -> ValidationResult:
    """Validate complete device configuration.
    
    Parameters
    ----------
    config : DeviceConfiguration
        Device configuration to validate
    constraints : FabricationConstraints
        Fabrication constraints to check against
    strict : bool
        If True, raise exception on first error. If False, collect all errors.
    
    Returns
    -------
    ValidationResult
        Validation result with errors and warnings
    
    Raises
    ------
    FabricationConstraintError
        If strict=True and validation fails
    """
    all_errors = []
    all_warnings = []
    
    # Validate wells
    if config.wells_config:
        result = validate_well_configuration(config.wells_config, constraints)
        all_errors.extend(result.errors)
        all_warnings.extend(result.warnings)
        
        if strict and result.errors:
            raise result.errors[0]
    
    # Validate channels
    if config.channels_config:
        result = validate_channel_configuration(config.channels_config, constraints)
        all_errors.extend(result.errors)
        all_warnings.extend(result.warnings)
        
        if strict and result.errors:
            raise result.errors[0]
    
    # Log results
    if all_errors:
        logger.error(f"Device validation failed with {len(all_errors)} errors")
        for error in all_errors:
            logger.error(f"  - {error}")
    
    if all_warnings:
        logger.warning(f"Device validation has {len(all_warnings)} warnings")
        for warning in all_warnings:
            logger.warning(f"  - {warning}")
    
    return ValidationResult(
        is_valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings
    )
```

### Step 1.4: Update `__init__.py`

**File**: `openmfd/validation/__init__.py`

```python
"""Validation module for OpenMFD."""

from .constraints import (
    FabricationConstraints,
    PHOTOLITHOGRAPHY_CONSTRAINTS,
    SOFT_LITHOGRAPHY_CONSTRAINTS,
    MICROMILLING_CONSTRAINTS,
)

from .exceptions import (
    ValidationError,
    FabricationConstraintError,
    GeometryValidationError,
    ConfigurationValidationError,
)

from .validators import (
    ValidationResult,
    validate_well_configuration,
    validate_channel_configuration,
    validate_device_configuration,
)

__all__ = [
    # Constraints
    'FabricationConstraints',
    'PHOTOLITHOGRAPHY_CONSTRAINTS',
    'SOFT_LITHOGRAPHY_CONSTRAINTS',
    'MICROMILLING_CONSTRAINTS',
    # Exceptions
    'ValidationError',
    'FabricationConstraintError',
    'GeometryValidationError',
    'ConfigurationValidationError',
    # Validators
    'ValidationResult',
    'validate_well_configuration',
    'validate_channel_configuration',
    'validate_device_configuration',
]
```

---

## Usage Example

```python
from openmfd.geometry import WellConfiguration, ChannelConfiguration
from openmfd.devices import DeviceConfiguration, CasingConfiguration
from openmfd.validation import (
    validate_device_configuration,
    PHOTOLITHOGRAPHY_CONSTRAINTS,
    FabricationConstraintError
)

# Create device configuration
config = DeviceConfiguration(
    casing=CasingConfiguration(width=20, height=20, depth=10),
    wells_config=WellConfiguration(diameter=3.0, depth=5.0, num_wells=2),
    channels_config=ChannelConfiguration(length=8.0, width=0.005, height=0.1)  # Too narrow!
)

# Validate (non-strict mode - collect all errors)
result = validate_device_configuration(config, PHOTOLITHOGRAPHY_CONSTRAINTS)

if not result.is_valid:
    print("Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
    # Don't proceed with fabrication
else:
    print("Device validated successfully!")
    # Proceed with export

# Or use strict mode (raises on first error)
try:
    validate_device_configuration(config, PHOTOLITHOGRAPHY_CONSTRAINTS, strict=True)
except FabricationConstraintError as e:
    print(f"Validation failed: {e}")
```

---

## Next Steps

After implementing validation:

1. **Add logging** (see `docs/OPENHCS_COMPARISON.md` Section 4)
2. **Improve error handling** (see Section 3)
3. **Add tests** (see Section 6)
4. **Consider GUI** (see Section 5)

This gives OpenMFD the robustness needed for scientific reproducibility!

