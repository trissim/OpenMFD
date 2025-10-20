OpenMFD Documentation
=====================

Welcome to OpenMFD, an open-source Python library for designing microfluidic devices.

OpenMFD provides a comprehensive toolkit for creating multi-compartment microfluidic devices
with support for photolithography mask generation, 3D modeling, and device assembly.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started/index
   concepts/index
   api/index
   examples/index

Features
--------

* **Geometric Primitives**: Wells, channels, and chambers with configurable dimensions
* **Device Assembly**: Combine primitives into complex multi-compartment devices
* **Multiple Export Formats**: OpenSCAD, DXF, STL
* **Type-Safe**: Comprehensive type hints throughout
* **Configurable**: Dataclass-based configuration system

Quick Start
-----------

.. code-block:: python

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
   )

   # Generate and export
   device = assemble_device(config)
   export_device(device, "my_device.scad")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

