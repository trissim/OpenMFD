# plan_04_export_system.md
## Component: Export and File Generation System

### Objective
Create a clean export system for generating SCAD, DXF, and STL files from device geometries. This includes file naming conventions, output organization, format conversion, and rendering following OpenHCS I/O patterns.

### Plan

1. **Create export configuration module** (`openmfd/export/config.py`)
   - Create `ExportConfiguration` dataclass:
     - output_directory: Path
     - base_name: str
     - formats: List[str] (scad, dxf, stl)
     - render_stl: bool
     - dxf_conversion: bool
   - Create `FileNamingConfig` dataclass:
     - prefix: str
     - version: Optional[str]
     - grid_size: Tuple[int, int]
     - suffix: str
   - Add path validation and creation utilities

2. **Create SCAD export module** (`openmfd/export/scad.py`)
   - Create `export_scad()` function:
     - Takes geometry and output path
     - Uses `solid.scad_render_to_file()`
     - Returns Path to generated file
   - Create `export_multiple_scad()` function:
     - Exports multiple geometries with prefixes
     - Handles batch export
   - Add SCAD-specific utilities:
     - SCAD header generation
     - Module wrapping
     - Parameter documentation in SCAD

3. **Create DXF export module** (`openmfd/export/dxf.py`)
   - Create `export_dxf()` function:
     - Converts SCAD to DXF via OpenSCAD CLI
     - Uses subprocess to call openscad
     - Post-processes with ezdxf
   - Create `scad_to_dxf()` function:
     - Takes SCAD path, returns DXF path
     - Handles conversion errors
     - Validates DXF output
   - Add DXF utilities:
     - DXF validation
     - Layer management
     - Unit conversion

4. **Create STL export module** (`openmfd/export/stl.py`)
   - Create `export_stl()` function:
     - Renders geometry to STL
     - Uses viewscad.Renderer
     - Handles rendering parameters
   - Create `scad_to_stl()` function:
     - Converts SCAD to STL via OpenSCAD CLI
     - Alternative to viewscad rendering
   - Add STL utilities:
     - STL validation
     - Mesh quality checks
     - Resolution settings

5. **Create file naming module** (`openmfd/export/naming.py`)
   - Create `generate_filename()` function:
     - Takes FileNamingConfig
     - Generates standardized filenames
     - Follows pattern: `{version}_{prefix}_{rows}x{cols}_units_{suffix}`
   - Create filename parsing utilities:
     - Parse existing filenames
     - Extract version, grid size, etc.
   - Add filename validation:
     - Check for invalid characters
     - Ensure uniqueness
     - Prevent overwrites (optional)

6. **Create output organization module** (`openmfd/export/organization.py`)
   - Create `organize_outputs()` function:
     - Organizes files by type/version
     - Creates subdirectories as needed
   - Create directory structure utilities:
     - Create output directories
     - Archive old versions
     - Clean temporary files
   - Support output organization modes:
     - By format (scad/, dxf/, stl/)
     - By device type
     - By version
     - Flat (all in one directory)

7. **Create unified export orchestrator** (`openmfd/export/exporter.py`)
   - Create `DeviceExporter` class:
     - Manages export pipeline
     - Handles multiple formats
     - Coordinates conversions
   - Create `export_device()` function:
     - High-level export interface
     - Takes geometry dict and ExportConfiguration
     - Exports all requested formats
     - Returns dict of output paths
   - Add export validation:
     - Verify all files created
     - Check file sizes
     - Validate formats

8. **Create rendering utilities** (`openmfd/export/rendering.py`)
   - Create `RenderConfiguration` dataclass:
     - width, height: int
     - camera settings
     - lighting settings
   - Create rendering functions:
     - `render_preview()` - Quick preview render
     - `render_high_quality()` - High-quality render
   - Add image export:
     - PNG/JPG rendering
     - Multiple views (top, side, perspective)

### Findings

**Current Export Code Analysis:**

1. **SCAD Export:**
   - Uses `solid.scad_render_to_file(model, path)`
   - Direct rendering to .scad files
   - No post-processing
   - Absolute paths used: `os.path.abspath(save_path + file_name + ".scad")`

2. **DXF Conversion (`to_dxf()` function, lines 625-630):**
   - Takes SCAD path as input
   - Calls OpenSCAD CLI: `subprocess.call(["openscad", "-o", dxf_path, scad_path])`
   - Post-processes with ezdxf:
     ```python
     temp_dxf = ezdxf.readfile(dxf_path)
     temp_dxf.saveas(dxf_path)
     ```
   - Returns nothing (void function)

3. **STL Rendering:**
   - Uses viewscad.Renderer: `r = viewscad.Renderer(width=800, height=800)`
   - Renders with: `r.render(model, outfile=path)`
   - Renderer is global variable
   - Fixed resolution (800x800)

4. **File Naming Patterns:**
   - In `make_taylor()`:
     ```python
     file_name = str(rows)+'x'+str(columns)+'_units_'
     if add_channels: file_name = "chans_" + file_name
     if add_wells: file_name = "wells_" + file_name
     if add_chambers: file_name = "chambers_" + file_name
     if version: file_name = "v"+str(version) + "_" + file_name
     ```
   - Pattern: `v{version}_{components}_{rows}x{columns}_units_`
   - Components: chans, wells, chambers (in reverse order added)

5. **Output Organization:**
   - `save_path` parameter specifies output directory
   - Common paths:
     - `./designs/` - General designs
     - `./designs/open_chamber/` - Open chamber devices
     - `./designs/closed_chamber/` - Closed chamber devices
     - `./designs/plasma_racks/` - Plasma racks
     - `./designs/debug/` - Debug outputs
   - No automatic directory creation in some cases

6. **Multiple Output Files:**
   - `make_device()` creates multiple files:
     - `wells_{filename}.scad`
     - `channels_{filename}.scad`
     - `device_{filename}.scad`
     - `chambers_wells_{filename}.scad`
   - Returns tuple of (geometry, filename) pairs

7. **Debug Output:**
   - `debug()` function (line 17-18):
     ```python
     def debug(model, f_name, path="/home/ts/code/projects/mfd/designs/debug"):
         solid.scad_render_to_file(model, osp.join(path, f_name)+".scad")
     ```
   - Hardcoded debug path
   - Used throughout for intermediate outputs

8. **Current Issues:**
   - Hardcoded paths
   - No error handling for file operations
   - No validation of outputs
   - Inconsistent return values
   - Global renderer instance
   - No configuration for rendering
   - File naming logic scattered
   - No output organization utilities

**OpenHCS Patterns to Apply:**

1. **Backend Pattern:**
   - Create export backends for each format
   - Abstract export interface
   - Format-specific implementations

2. **Configuration:**
   - ExportConfiguration dataclass
   - Rendering configuration
   - Path configuration

3. **File Management:**
   - Centralized file operations
   - Path validation
   - Directory creation
   - Error handling

4. **Orchestration:**
   - Export orchestrator
   - Multi-format export pipeline
   - Dependency management (SCAD → DXF, SCAD → STL)

5. **Validation:**
   - Output validation
   - Format verification
   - File existence checks

### Implementation Draft
(Code will be written here after smell loop approval)

