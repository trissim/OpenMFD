# plan_01_repository_structure.md
## Component: Repository Structure and Organization

### Objective
Transform the current MFD folder into a properly structured Python package called OpenMFD, following OpenHCS organizational principles. This includes setting up the directory structure, package configuration, git repository initialization, and Sphinx documentation framework.

### Plan

1. **Create src-layout package structure**
   - Create `openmfd/` package directory with proper `__init__.py`
   - Organize modules into logical subpackages:
     - `openmfd/core/` - Core device generation logic
     - `openmfd/geometry/` - Geometric primitives (wells, channels, chambers)
     - `openmfd/devices/` - Device-specific implementations
     - `openmfd/export/` - Export functionality (DXF, SCAD, STL)
     - `openmfd/utils/` - Utility functions
   - Move existing code into appropriate modules

2. **Set up package configuration**
   - Create `pyproject.toml` with modern Python packaging standards
   - Define dependencies: solidpython, viewscad, ezdxf, numpy
   - Set up entry points for CLI tools if needed
   - Configure package metadata (name, version, author, description)

3. **Initialize git repository properly**
   - Create `.gitignore` for Python projects (exclude __pycache__, *.pyc, build artifacts)
   - Add patterns for design outputs (*.scad, *.stl, *.dxf in output directories)
   - Stage and commit clean initial state
   - Set up proper git configuration

4. **Create documentation structure**
   - Create `docs/` directory with Sphinx configuration
   - Set up `docs/source/` with:
     - `index.rst` - Main documentation entry point
     - `getting_started/` - Installation and basic usage
     - `concepts/` - Core concepts (wells, channels, chambers, devices)
     - `api/` - API reference documentation
     - `examples/` - Example device designs
   - Create `docs/source/conf.py` following OpenHCS patterns
   - Configure autodoc, napoleon, and other Sphinx extensions

5. **Organize existing device files**
   - Create `examples/` directory for device design scripts
   - Move versioned device files (2_compartment_96_well_v*.py) to `examples/devices/`
   - Create subdirectories by device type:
     - `examples/devices/2_compartment/`
     - `examples/devices/3_compartment/`
     - `examples/devices/plates/`
   - Keep `designs/` for generated output files
   - Archive old/conflicted files to `archive/`

6. **Create tests structure**
   - Create `tests/` directory with pytest structure
   - Set up `tests/unit/` for unit tests
   - Set up `tests/integration/` for integration tests
   - Create initial test files for core geometry functions

7. **Set up development tooling**
   - Create `README.md` with project overview and quick start
   - Create `CONTRIBUTING.md` with development guidelines
   - Create `LICENSE` file
   - Set up `.editorconfig` for consistent code style

### Findings

**Current MFD Structure Analysis:**

1. **Core Modules:**
   - `make_device.py` - Main device generation functions (924 lines)
     - `make_well()` - Creates well geometries (circle/square)
     - `wells_top_bottom()` - Creates 2-well configurations
     - `four_corner()` - Creates 4-well configurations
     - `make_channels()` - Creates channel arrays with spacing
     - `make_chambers()` - Creates chamber geometries
     - `make_taylor()` - High-level device assembly function
     - `make_device()` - Configurable device generation
     - `to_dxf()` - Converts SCAD to DXF format
     - `make_walls()` - Creates wafer walls
   
   - `mf_device.py` - Jupyter notebook version (922 lines, similar to make_device.py)
   
   - `plate_maker.py` - Plate/rack generation (144 lines)
     - Creates 12-well plates with specific dimensions
     - Handles plasma container racks

2. **Device Files (70+ versioned files):**
   - Pattern: `{compartments}_compartment_{wells}_well_v{version}_{thickness}um.py`
   - Examples: 2_compartment_96_well_v27_300um_suex200.py
   - Different well counts: 48, 96, 154, 192, 384
   - Different formats: 4x4, 5x5 grids
   - Thickness variations: 300um, 1000um, 200um
   - Material variations: suex100, suex200

3. **File Formats Generated:**
   - `.scad` - OpenSCAD source files
   - `.dxf` - 2D CAD drawings for photolithography masks
   - `.stl` - 3D models for visualization/3D printing
   - `.png/.jpg` - Renderings

4. **Dependencies:**
   - `solidpython` - Python → OpenSCAD generation
   - `viewscad` - OpenSCAD rendering
   - `ezdxf` - DXF file handling
   - `numpy` - Numerical operations
   - External: `openscad` command-line tool

5. **Output Organization:**
   - `designs/` - Generated design files
     - `designs/open_chamber/` - Open chamber designs
     - `designs/closed_chamber/` - Closed chamber designs
     - `designs/plasma_racks/` - Plasma container racks
     - `designs/debug/` - Debug outputs
   - `orders/` - Production order files
   - `plates/` - Plate designs
   - `gcode/` - G-code for CNC

6. **Git Status:**
   - Repository exists with remote: https://github.com/trissim/mfd
   - Many untracked files (70+ device scripts)
   - Some deleted files in staging area
   - Needs cleanup and proper organization

**OpenHCS Principles to Apply:**

1. **Module Organization:**
   - Clear separation of concerns (geometry, devices, export)
   - Explicit imports, no side effects
   - Stateless functions where possible

2. **Documentation:**
   - Sphinx with RTD theme
   - Comprehensive API documentation
   - Concept guides for wells, channels, chambers
   - Example gallery

3. **Configuration:**
   - Use dataclasses for device configurations
   - Hierarchical configuration system
   - Type hints throughout

4. **Testing:**
   - Unit tests for geometric primitives
   - Integration tests for device generation
   - Validation of output formats

### Implementation Draft
(Code will be written here after smell loop approval)

