Quick Reference
===============

This page provides a quick reference for common OpenMFD operations.

Basic Workflow
--------------

.. code-block:: python

   from openmfd.geometry import WellConfiguration, ChannelConfiguration
   from openmfd.devices import DeviceConfiguration, CasingConfiguration, assemble_device
   from openmfd.export import ExportConfiguration, export_device
   from pathlib import Path

   # Configure
   config = DeviceConfiguration(
       casing=CasingConfiguration(width=20, height=20, depth=10),
       wells_config=WellConfiguration(diameter=3.0, depth=5.0, num_wells=2),
       channels_config=ChannelConfiguration(length=8.0, width=0.3, height=0.1)
   )

   # Assemble
   geometry, measurements = assemble_device(config)

   # Export
   paths = export_device(
       {'device': geometry},
       ExportConfiguration(output_directory=Path('output'), formats=['scad', 'dxf'])
   )

Common Configurations
---------------------

Two-Compartment Device
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   config = DeviceConfiguration(
       casing=CasingConfiguration(width=20, height=20, depth=10),
       wells_config=WellConfiguration(diameter=3.0, depth=5.0, num_wells=2),
       channels_config=ChannelConfiguration(length=8.0, width=0.3, height=0.1)
   )

Device Array (NxM Grid)
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from openmfd.devices import ArrayConfiguration, create_device_array

   array_config = ArrayConfiguration(rows=8, columns=12, spacing_x=15.0, spacing_y=15.0)
   array_geometry = create_device_array(geometry, measurements, array_config)

Export Formats
--------------

SCAD + DXF
~~~~~~~~~~

.. code-block:: python

   config = ExportConfiguration(
       output_directory=Path('output'),
       formats=['scad', 'dxf'],
       dxf_conversion=True
   )

Next Steps
----------

* :doc:`../concepts/index` - Learn core concepts
* :doc:`../examples/index` - See more examples
