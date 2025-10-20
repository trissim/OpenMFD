# plan_05_sphinx_documentation.md
## Component: Sphinx Documentation Setup

### Objective
Set up comprehensive Sphinx documentation for OpenMFD following OpenHCS documentation patterns. This includes installation, configuration, API documentation, concept guides, examples, and building/deployment.

### Plan

1. **Initialize Sphinx structure** (`docs/`)
   - Create `docs/source/` directory
   - Create `docs/source/conf.py` following OpenHCS pattern
   - Create `docs/source/index.rst` as main entry point
   - Create `docs/Makefile` and `docs/make.bat` for building
   - Set up `.readthedocs.yaml` for RTD deployment

2. **Configure Sphinx** (`docs/source/conf.py`)
   - Set project metadata (name, author, version)
   - Configure extensions:
     - `sphinx.ext.autodoc` - API documentation
     - `sphinx.ext.napoleon` - NumPy/Google docstrings
     - `sphinx.ext.viewcode` - Source code links
     - `sphinx.ext.intersphinx` - Cross-references
     - `sphinx.ext.autosummary` - API summaries
     - `sphinx_rtd_theme` - Read the Docs theme
   - Configure autodoc options:
     - `members: True`
     - `member-order: bysource`
     - `special-members: __init__`
     - `undoc-members: True`
   - Set up intersphinx mapping (Python, NumPy, SolidPython)
   - Configure HTML theme and options

3. **Create Getting Started guide** (`docs/source/getting_started/`)
   - Create `getting_started.rst`:
     - Installation instructions
     - Dependencies (solidpython, viewscad, ezdxf)
     - Quick start example
     - First device creation
   - Create `installation.rst`:
     - pip installation
     - Development installation
     - OpenSCAD installation
     - Verification steps
   - Create `first_device.rst`:
     - Simple 2-compartment device
     - Step-by-step walkthrough
     - Output explanation

4. **Create Concepts documentation** (`docs/source/concepts/`)
   - Create `index.rst` - Concepts overview
   - Create `geometry_primitives.rst`:
     - Wells, channels, chambers
     - Geometric parameters
     - 2D vs 3D generation
   - Create `device_assembly.rst`:
     - Device configuration
     - Assembly process
     - Component composition
   - Create `arrays_and_grids.rst`:
     - Unit arrays
     - Grid positioning
     - Alignment modes
   - Create `export_formats.rst`:
     - SCAD format
     - DXF for photolithography
     - STL for 3D printing
   - Create `configuration_system.rst`:
     - Configuration dataclasses
     - Hierarchical configuration
     - Configuration validation

5. **Create API Reference** (`docs/source/api/`)
   - Create `index.rst` - API overview
   - Create `geometry/index.rst`:
     - `primitives.rst` - Basic shapes
     - `wells.rst` - Well patterns
     - `channels.rst` - Channel patterns
     - `chambers.rst` - Chamber patterns
     - `positioning.rst` - Positioning utilities
   - Create `devices/index.rst`:
     - `config.rst` - Configuration classes
     - `assembly.rst` - Assembly functions
     - `arrays.rst` - Array generation
     - `templates.rst` - Device templates
   - Create `export/index.rst`:
     - `scad.rst` - SCAD export
     - `dxf.rst` - DXF export
     - `stl.rst` - STL export
     - `exporter.rst` - Export orchestrator

6. **Create Examples gallery** (`docs/source/examples/`)
   - Create `index.rst` - Examples overview
   - Create `two_compartment.rst`:
     - 2-compartment device example
     - Parameter variations
     - Output visualization
   - Create `gradient_device.rst`:
     - Gradient generation device
     - Channel configuration
     - Chamber design
   - Create `multi_well_plate.rst`:
     - 96-well plate device
     - Array configuration
     - Wall generation
   - Create `custom_device.rst`:
     - Custom device from scratch
     - Advanced configuration
     - Custom geometries

7. **Create User Guide** (`docs/source/user_guide/`)
   - Create `index.rst` - User guide overview
   - Create `device_design.rst`:
     - Design workflow
     - Parameter selection
     - Best practices
   - Create `configuration.rst`:
     - Configuration patterns
     - Reusable configurations
     - Configuration files
   - Create `export_workflow.rst`:
     - Export pipeline
     - Format selection
     - Output organization
   - Create `troubleshooting.rst`:
     - Common issues
     - Error messages
     - Debugging tips

8. **Add documentation build tools**
   - Create `docs/requirements.txt`:
     - sphinx
     - sphinx-rtd-theme
     - sphinx-autodoc-typehints
   - Create build scripts:
     - `make html` - Build HTML docs
     - `make clean` - Clean build
     - `make linkcheck` - Check links
   - Set up GitHub Actions for doc building (optional)

### Findings

**OpenHCS Documentation Structure Analysis:**

1. **Sphinx Configuration (`docs/source/conf.py`):**
   - Project: 'OpenHCS'
   - Extensions: autodoc, viewcode, napoleon, intersphinx, autosummary, mathjax, doctest, sphinx_rtd_theme
   - Theme: sphinx_rtd_theme
   - Autodoc options:
     - members: True
     - member-order: bysource
     - special-members: __init__
     - undoc-members: True
     - exclude-members: __weakref__
   - Intersphinx: python, numpy, scipy, matplotlib, pandas, scikit-image
   - Mock imports for Read the Docs

2. **Documentation Structure:**
   ```
   docs/source/
   ├── index.rst                    # Main entry
   ├── getting_started/
   │   └── getting_started.rst      # Installation & quick start
   ├── concepts/
   │   ├── index.rst
   │   ├── module_structure.rst     # Module organization
   │   ├── function_library.rst     # Available functions
   │   └── storage_system.rst       # Storage backends
   ├── api/
   │   └── index.rst                # API reference
   ├── user_guide/
   │   └── index.rst                # User guides
   └── guides/
       └── index.rst                # Integration guides
   ```

3. **Index Structure (`docs/source/index.rst`):**
   - Project overview
   - Key features
   - Quick start
   - Core capabilities
   - Documentation structure with learning path
   - TOC trees for each section

4. **Getting Started Pattern:**
   - Installation options (standard, CPU-only, development)
   - Basic example with code
   - Understanding the example
   - Interactive development (GUI/TUI)
   - Next steps with links

5. **Concepts Pattern:**
   - High-level explanations
   - Architecture diagrams
   - Code examples
   - Cross-references to API
   - Progressive complexity

6. **API Reference Pattern:**
   - Module-level documentation
   - Class documentation with autodoc
   - Function signatures with type hints
   - Parameter descriptions
   - Return value descriptions
   - Examples in docstrings

7. **Documentation Standards:**
   - NumPy-style docstrings
   - Type hints in signatures
   - Code examples in docstrings
   - Cross-references with `:doc:`, `:class:`, `:func:`
   - Progressive learning paths
   - Clear navigation

**OpenMFD Documentation Needs:**

1. **Core Concepts to Document:**
   - Microfluidic device fundamentals
   - Wells, channels, chambers
   - Device assembly process
   - Array generation
   - Export formats (SCAD, DXF, STL)
   - Photolithography workflow

2. **API Documentation:**
   - All geometry functions
   - All device assembly functions
   - All export functions
   - Configuration dataclasses
   - Utility functions

3. **Examples:**
   - 2-compartment devices (most common)
   - 3-compartment devices
   - Gradient devices
   - Multi-well plates
   - Custom geometries

4. **User Guides:**
   - Device design workflow
   - Parameter selection
   - Fabrication considerations
   - Export for manufacturing

### Implementation Draft
(Code will be written here after smell loop approval)

