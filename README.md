# OpenMFD - Open Microfluidic Device Design Library

A Python library for designing microfluidic devices with support for photolithography mask generation, 3D modeling, and device assembly.

## Features

- **Geometric Primitives**: Wells, channels, and chambers with configurable dimensions
- **Device Assembly**: Combine primitives into complex multi-compartment devices
- **Multiple Export Formats**:
  - OpenSCAD (.scad) for 3D modeling
  - DXF (.dxf) for photolithography masks
  - STL (.stl) for 3D printing and visualization
- **Configurable Designs**: Dataclass-based configuration system
- **Type-Safe**: Comprehensive type hints throughout
- **Well-Documented**: Sphinx documentation with examples

## Installation

### From Source

```bash
git clone https://github.com/trissim/mfd.git
cd mfd
pip install -e .
```

### With Development Dependencies

```bash
pip install -e ".[dev,docs]"
```

## Quick Start

```python
from openmfd.geometry import WellConfiguration
from openmfd.devices import DeviceConfiguration
from openmfd.export import export_device

# Configure a simple 2-compartment device
config = DeviceConfiguration(
    wells=WellConfiguration(
        diameter=3.0,  # mm
        height=0.3,    # mm
        count=96
    ),
    # ... additional configuration
)

# Generate and export
device = assemble_device(config)
export_device(device, "my_device.scad")
```

## Requirements

- Python >= 3.8
- OpenSCAD (for SCAD to DXF/STL conversion)
- Dependencies: solidpython, viewscad, ezdxf, numpy

## Documentation

Full documentation is available at [openmfd.readthedocs.io](https://openmfd.readthedocs.io)

## Examples

See the `examples/` directory for complete device designs:
- 2-compartment devices (48, 96, 192, 384 wells)
- 3-compartment devices
- Custom plate designs
- Gradient devices

## Development

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
cd docs
make html
```

### Code Formatting

```bash
black openmfd tests
ruff check openmfd tests
```

## License

MIT License - see LICENSE file for details

## Citation

If you use OpenMFD in your research, please cite:

```
@software{openmfd,
  author = {Simas, Tristan},
  title = {OpenMFD: Open Microfluidic Device Design Library},
  year = {2024},
  url = {https://github.com/trissim/mfd}
}
```

## Related Projects

- [OpenHCS](https://github.com/trissim/openhcs) - High-content screening analysis library

