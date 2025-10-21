# OpenMFD ↔ OpenHCS: Cross-Comparison & Extension Roadmap

**Status**: CANONICAL  
**Purpose**: Guide for extending OpenMFD using OpenHCS architectural patterns

---

## Executive Summary

OpenMFD and OpenHCS share the same author and follow similar architectural principles, but OpenHCS is more mature with advanced features that can be adopted by OpenMFD. This document provides a systematic comparison and roadmap for extending OpenMFD.

### Shared DNA
- **Dataclass-based configuration**
- **Type hints throughout**
- **Stateless functions**
- **Fail-loud error handling**
- **Sphinx documentation**
- **Separation of concerns**

### OpenHCS Advantages to Adopt
1. **Config Framework** - Dual-axis lazy resolution system
2. **Validation System** - AST-based + runtime validation
3. **UI Engine** - PyQt6 GUI with reusable widgets
4. **Error Handling** - Specific exceptions with context
5. **Logging Strategy** - Structured logging with discovery
6. **Testing Infrastructure** - Comprehensive test patterns

---

## 1. Configuration Systems

### Current State: OpenMFD

**Simple Dataclass Configs:**
```python
@dataclass
class WellConfiguration:
    diameter: float
    depth: float
    num_wells: int = 2
    spacing: float = 10.0
```

**Limitations:**
- No inheritance resolution
- No context-aware defaults
- Manual parameter passing everywhere
- No UI placeholder generation

### OpenHCS Pattern: Lazy Config Framework

**Dual-Axis Resolution System:**
```python
from openhcs.config_framework import auto_create_decorator

@auto_create_decorator  # Creates LazyDeviceConfiguration automatically
@dataclass
class DeviceConfiguration:
    wells_config: WellConfiguration = None
    channels_config: ChannelConfiguration = None
    export_dir: Path = None
    
# Usage with context:
with config_context(global_device_config):
    # Fields auto-resolve from context hierarchy:
    # Step → Pipeline → Global → Static defaults
    device = LazyDeviceConfiguration()
    # device.export_dir resolves from global_device_config automatically
```

**Key Features:**
- **X-Axis**: Context hierarchy (Step → Pipeline → Global → Defaults)
- **Y-Axis**: Sibling inheritance (related configs inherit from each other)
- **Lazy resolution**: Fields resolve on access, not construction
- **UI integration**: Automatic placeholder generation for forms

### Recommendation for OpenMFD

**Phase 1: Add Basic Context System**
```python
# openmfd/config_framework/context.py
from contextvars import ContextVar
from dataclasses import dataclass, replace

_current_device_context: ContextVar[Optional['GlobalDeviceConfig']] = ContextVar(
    'device_context', default=None
)

@contextmanager
def device_context(config: 'GlobalDeviceConfig'):
    """Set device configuration context."""
    token = _current_device_context.set(config)
    try:
        yield config
    finally:
        _current_device_context.reset(token)

def get_current_device_config() -> 'GlobalDeviceConfig':
    """Get current device configuration from context."""
    config = _current_device_context.get()
    if config is None:
        raise RuntimeError("No device context set")
    return config
```

**Phase 2: Add Lazy Resolution** (adopt OpenHCS's `lazy_factory.py`)

---

## 2. Validation Systems

### Current State: OpenMFD

**Basic `__post_init__` Validation:**
```python
@dataclass
class CasingConfiguration:
    x: float
    y: float
    z: float = 0
    
    def __post_init__(self):
        if self.x <= 0:
            raise ValueError(f"x must be positive, got {self.x}")
```

**Limitations:**
- No fabrication constraint validation
- No cross-field validation
- No AST-level validation
- Generic error messages

### OpenHCS Pattern: Multi-Layer Validation

**1. AST-Level Validation** (`openhcs/validation/ast_validator.py`):
```python
class FabricationConstraintValidator(ASTValidator):
    """Validate fabrication constraints at compile time."""
    
    def visit_Call(self, node: ast.Call):
        # Check for channel width < 10μm
        if self._is_channel_config(node):
            width_arg = self._get_arg(node, 'width')
            if width_arg and width_arg < 0.010:
                self.add_violation(
                    node=node,
                    violation_type="fabrication_constraint",
                    message=f"Channel width {width_arg}mm < 10μm minimum"
                )
```

**2. Runtime Validation** (specific exceptions):
```python
class FabricationConstraintError(Exception):
    """Raised when device violates fabrication constraints."""
    def __init__(self, constraint: str, value: float, limit: float):
        self.constraint = constraint
        self.value = value
        self.limit = limit
        super().__init__(
            f"Fabrication constraint violated: {constraint}\n"
            f"  Value: {value}mm\n"
            f"  Limit: {limit}mm"
        )
```

**3. Configuration Validation**:
```python
@dataclass
class FabricationConstraints:
    """Physical fabrication constraints."""
    min_channel_width: float = 0.010  # 10μm
    max_channel_width: float = 1.000  # 1mm
    min_well_spacing: float = 1.0     # 1mm
    max_su8_height: float = 0.500     # 500μm
    min_su8_height: float = 0.025     # 25μm

def validate_device_config(
    config: DeviceConfiguration,
    constraints: FabricationConstraints
) -> List[ValidationError]:
    """Validate device against fabrication constraints."""
    errors = []
    
    if config.channels_config:
        width = config.channels_config.width
        if width < constraints.min_channel_width:
            errors.append(ValidationError(
                field="channels_config.width",
                value=width,
                constraint=f">= {constraints.min_channel_width}mm",
                message="Channel too narrow for photolithography"
            ))
    
    return errors
```

### Recommendation for OpenMFD

**Create `openmfd/validation/` module:**
```
openmfd/validation/
├── __init__.py
├── constraints.py      # FabricationConstraints dataclass
├── validators.py       # Runtime validation functions
├── exceptions.py       # Specific exception types
└── ast_validator.py    # AST-level validation (optional)
```

---

## 3. Error Handling Strategy

### Current State: OpenMFD

**Generic Exception Handling:**
```python
try:
    dxf_path = scad_to_dxf(scad_path)
except Exception as e:  # ❌ Too broad
    print(f"Warning: DXF conversion failed: {e}")  # ❌ Silent failure
```

### OpenHCS Pattern: Fail-Loud with Context

**Specific Exceptions:**
```python
# openmfd/export/exceptions.py
class OpenMFDError(Exception):
    """Base exception for OpenMFD."""
    pass

class ExportError(OpenMFDError):
    """Base exception for export operations."""
    pass

class OpenSCADError(ExportError):
    """OpenSCAD CLI execution failed."""
    def __init__(self, command: str, returncode: int, stderr: str):
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(
            f"OpenSCAD command failed (exit {returncode}):\n"
            f"  Command: {command}\n"
            f"  Error: {stderr}"
        )

class DXFConversionError(ExportError):
    """DXF conversion failed."""
    def __init__(self, scad_path: Path, reason: str):
        self.scad_path = scad_path
        self.reason = reason
        super().__init__(
            f"Failed to convert SCAD to DXF:\n"
            f"  File: {scad_path}\n"
            f"  Reason: {reason}"
        )
```

**Usage:**
```python
import logging
logger = logging.getLogger(__name__)

def scad_to_dxf(scad_path: Path, config: ExportConfiguration) -> Path:
    """Convert SCAD to DXF using OpenSCAD CLI."""
    try:
        result = subprocess.run(
            ['openscad', '-o', dxf_path, scad_path],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise OpenSCADError(
            command=' '.join(e.cmd),
            returncode=e.returncode,
            stderr=e.stderr.decode()
        ) from e
    except FileNotFoundError:
        raise DXFConversionError(
            scad_path=scad_path,
            reason="OpenSCAD not found in PATH. Install from https://openscad.org"
        )
    
    if not dxf_path.exists():
        raise DXFConversionError(
            scad_path=scad_path,
            reason="DXF file not created (OpenSCAD succeeded but no output)"
        )
    
    logger.info(f"Successfully converted {scad_path.name} → {dxf_path.name}")
    return dxf_path
```

**OpenHCS Principle: FAIL-LOUD**
- ❌ No `except Exception`
- ❌ No silent failures with `print()`
- ❌ No defensive programming (`hasattr`, `getattr` with defaults)
- ✅ Specific exceptions with context
- ✅ Structured logging
- ✅ Let Python fail naturally for programmer errors

---

## 4. Logging Strategy

### Current State: OpenMFD

**No logging infrastructure**

### OpenHCS Pattern: Structured Logging

**1. Log Configuration** (`openhcs/core/log_utils.py`):
```python
import logging
from pathlib import Path
from datetime import datetime

def setup_logging(
    log_dir: Path,
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True
) -> Path:
    """Setup structured logging for OpenMFD."""
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"openmfd_{timestamp}.log"
    
    # Configure root logger
    logger = logging.getLogger("openmfd")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # File handler with detailed format
    if log_to_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(file_handler)
    
    # Console handler with simple format
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized: {log_file}")
    return log_file
```

**2. Usage in Modules:**
```python
import logging
logger = logging.getLogger(__name__)  # openmfd.export.dxf

def export_dxf(geometry, config):
    logger.info(f"Starting DXF export: {config.output_directory}")
    logger.debug(f"Export config: {config}")
    
    try:
        result = _do_export(geometry, config)
        logger.info(f"DXF export successful: {result}")
        return result
    except OpenSCADError as e:
        logger.error(f"OpenSCAD failed: {e}", exc_info=True)
        raise
```

### Recommendation for OpenMFD

Add `openmfd/core/logging.py` with OpenHCS-style structured logging.

---

## 5. UI Engine: PyQt6 GUI

### Current State: OpenMFD

**No UI** - Command-line only

### OpenHCS Pattern: Reusable PyQt6 Architecture

**Architecture:**
```
openhcs/pyqt_gui/
├── app.py                    # Main QApplication
├── main.py                   # Main window with dock system
├── services/
│   ├── service_adapter.py    # Bridge to business logic
│   └── theme_manager.py      # Centralized theming
├── widgets/
│   ├── config_editor.py      # Generic config editing
│   ├── parameter_form.py     # Auto-generated forms from dataclasses
│   └── system_monitor.py     # System resource monitoring
└── windows/
    └── config_window.py      # Floating config windows
```

**Key Reusable Components:**

**1. Parameter Form Manager** - Auto-generates forms from dataclasses:
```python
from openhcs.pyqt_gui.widgets.parameter_form import ParameterFormManager

# Automatically creates Qt form from DeviceConfiguration dataclass
form = ParameterFormManager.from_dataclass_instance(
    dataclass_instance=device_config,
    field_id="device_config",
    color_scheme=color_scheme
)

# Get values back
values = form.get_current_values()
updated_config = DeviceConfiguration(**values)
```

**2. Config Window** - Generic configuration editing:
```python
from openhcs.pyqt_gui.windows.config_window import ConfigWindow

def edit_device_config(current_config: DeviceConfiguration):
    def on_save(new_config):
        # Handle save
        save_device_config(new_config)
    
    window = ConfigWindow(
        config_class=DeviceConfiguration,
        current_config=current_config,
        on_save_callback=on_save,
        color_scheme=color_scheme
    )
    window.show()
```

**3. Service Adapter** - Bridges UI to business logic:
```python
class OpenMFDServiceAdapter:
    """Adapter for OpenMFD services in PyQt context."""
    
    def export_device(self, config: DeviceConfiguration) -> Path:
        """Export device with progress dialog."""
        progress = QProgressDialog("Exporting device...", "Cancel", 0, 100)
        progress.show()
        
        try:
            result = openmfd.export.export_device(config)
            progress.setValue(100)
            return result
        except ExportError as e:
            QMessageBox.critical(None, "Export Failed", str(e))
            raise
```

### Recommendation for OpenMFD

**Phase 1: Create Basic GUI Structure**
```
openmfd_gui/
├── __init__.py
├── app.py              # Main application (copy from OpenHCS)
├── main.py             # Main window
└── widgets/
    ├── device_editor.py    # Device configuration editor
    └── preview_widget.py   # 3D preview (ViewSCAD integration)
```

**Phase 2: Reuse OpenHCS Components**
- Copy `ParameterFormManager` → auto-generate forms from OpenMFD configs
- Copy `ConfigWindow` → edit DeviceConfiguration, ExportConfiguration
- Copy `ThemeManager` → consistent dark theme
- Copy `ServiceAdapter` pattern → bridge to openmfd.export

---

## 6. Testing Infrastructure

### Current State: OpenMFD

**No tests**

### OpenHCS Pattern: Comprehensive Testing

**Test Structure:**
```
tests/
├── unit/
│   ├── test_geometry_primitives.py
│   ├── test_device_assembly.py
│   └── test_export_scad.py
├── integration/
│   ├── test_full_workflow.py
│   └── test_export_pipeline.py
└── golden/
    ├── test_dxf_output.py      # Compare DXF files
    └── fixtures/
        ├── expected_device.dxf
        └── expected_device.scad
```

**Example Unit Test:**
```python
import pytest
from openmfd.geometry import make_well, WellConfiguration

def test_make_well_circular():
    """Test circular well creation."""
    well = make_well(diameter=3.0, depth=5.0, shape='circular')
    assert well is not None
    # Add geometry assertions

def test_well_configuration_validation():
    """Test configuration validation."""
    with pytest.raises(ValueError, match="diameter must be positive"):
        WellConfiguration(diameter=-1.0, depth=5.0)

@pytest.mark.parametrize("diameter,depth", [
    (1.0, 5.0),
    (3.0, 5.0),
    (5.0, 10.0),
])
def test_well_dimensions(diameter, depth):
    """Test various well dimensions."""
    config = WellConfiguration(diameter=diameter, depth=depth)
    well = make_well(**config.__dict__)
    # Verify dimensions
```

**Golden File Testing:**
```python
def test_dxf_export_matches_golden(tmp_path):
    """Test DXF export matches expected output."""
    config = DeviceConfiguration(...)
    geometry, _ = assemble_device(config)
    
    output_path = tmp_path / "device.dxf"
    export_dxf_from_geometry(geometry, output_path)
    
    # Compare with golden file
    golden_path = Path(__file__).parent / "fixtures" / "expected_device.dxf"
    assert_dxf_equivalent(output_path, golden_path)
```

### Recommendation for OpenMFD

1. **Add pytest infrastructure**
2. **Unit tests for all primitives**
3. **Integration tests for workflows**
4. **Golden file tests for export formats**
5. **Property-based tests** (hypothesis) for geometric invariants

---

## Summary: Extension Roadmap

### Priority 1: Core Infrastructure
1. ✅ **Validation module** - Fabrication constraints
2. ✅ **Error handling** - Specific exceptions
3. ✅ **Logging** - Structured logging
4. ✅ **Testing** - Unit + integration tests

### Priority 2: Configuration Framework
5. **Context system** - Basic context management
6. **Lazy resolution** - Adopt OpenHCS lazy factory (optional)

### Priority 3: UI Engine
7. **Basic PyQt6 GUI** - Main window + device editor
8. **Reuse OpenHCS widgets** - ParameterFormManager, ConfigWindow
9. **3D Preview** - ViewSCAD integration

### Priority 4: Advanced Features
10. **AST validation** - Compile-time constraint checking
11. **Plugin system** - Custom device types
12. **Batch processing** - Multi-device export

---

## Conclusion

OpenMFD has a solid foundation. By adopting OpenHCS patterns, it can gain:
- **Robustness**: Better error handling and validation
- **Usability**: GUI for non-programmers
- **Maintainability**: Structured logging and testing
- **Extensibility**: Config framework for complex workflows

**Next Step**: Start with Priority 1 (validation, errors, logging, tests) before adding UI.

