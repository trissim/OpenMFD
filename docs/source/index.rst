OpenMFD: Open Microfluidic Device Design
=========================================

Welcome to **OpenMFD**, an open-source Python library for designing and fabricating microfluidic devices using parametric CAD generation.

OpenMFD provides a comprehensive toolkit for creating multi-compartment microfluidic devices
with support for photolithography mask generation, 3D modeling, and device assembly.

Key Features
------------

* **Parametric Design**: Define devices using configuration dataclasses with type hints
* **Geometry Primitives**: Wells, channels, and chambers with precise dimensional control
* **Array Generation**: Create NxM grids of device units with flexible alignment
* **Multiple Export Formats**:

  * **SCAD**: OpenSCAD files for 3D modeling and visualization
  * **DXF**: 2D drawings for photolithography mask fabrication
  * **STL**: 3D models for direct 3D printing or visualization

* **Type-Safe Configuration**: Comprehensive type hints and validation throughout
* **Modular Architecture**: Separate geometry, assembly, and export concerns
* **Fabrication-Ready**: Designed for SU-8 photolithography and soft lithography workflows

Quick Start
-----------

Install OpenMFD:

.. code-block:: bash

   pip install openmfd

Create your first device:

.. code-block:: python

   from openmfd.geometry import WellConfiguration, ChannelConfiguration
   from openmfd.devices import DeviceConfiguration, CasingConfiguration, assemble_device
   from openmfd.export import ExportConfiguration, export_device
   from pathlib import Path

   # Configure device components
   wells_config = WellConfiguration(
       diameter=3.0,
       depth=5.0,
       num_wells=2,
       spacing=10.0
   )

   channels_config = ChannelConfiguration(
       length=8.0,
       width=0.3,
       height=0.1,
       num_channels=10
   )

   # Assemble device
   device_config = DeviceConfiguration(
       casing=CasingConfiguration(width=20, height=20, depth=10),
       wells_config=wells_config,
       channels_config=channels_config
   )

   geometry, measurements = assemble_device(device_config)

   # Export to SCAD and DXF
   export_config = ExportConfiguration(
       output_directory=Path('output'),
       formats=['scad', 'dxf'],
       dxf_conversion=True
   )

   paths = export_device({'device': geometry}, export_config)

Documentation Structure
-----------------------

This documentation is organized to support different learning paths:

**For New Users:**

1. :doc:`getting_started/installation` - Install OpenMFD and dependencies
2. :doc:`getting_started/first_device` - Create your first device
3. :doc:`concepts/index` - Understand core concepts

**For Device Designers:**

1. :doc:`user_guide/device_design` - Device design workflow
2. :doc:`examples/index` - Example devices and patterns
3. :doc:`user_guide/export_workflow` - Export for fabrication

**For Developers:**

1. :doc:`api/index` - Complete API reference
2. :doc:`concepts/configuration_system` - Configuration architecture

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   getting_started/installation
   getting_started/first_device
   getting_started/quick_reference

.. toctree::
   :maxdepth: 2
   :caption: Core Concepts
   :hidden:

   concepts/index
   concepts/geometry_primitives
   concepts/device_assembly
   concepts/arrays_and_grids
   concepts/export_formats
   concepts/configuration_system

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   user_guide/index
   user_guide/device_design
   user_guide/configuration
   user_guide/export_workflow
   user_guide/troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Examples
   :hidden:

   examples/index
   examples/two_compartment
   examples/gradient_device
   examples/multi_well_plate
   examples/custom_device

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   :hidden:

   api/index
   api/geometry
   api/devices
   api/export

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

