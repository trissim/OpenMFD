Your First Device
=================

This tutorial will guide you through creating your first microfluidic device with OpenMFD.

Step 1: Import Required Modules
--------------------------------

.. code-block:: python

   from openmfd.geometry import WellConfiguration, ChannelConfiguration
   from openmfd.devices import DeviceConfiguration, CasingConfiguration
   from openmfd.devices import assemble_device
   from openmfd.export import ExportConfiguration, export_device
   from pathlib import Path

Step 2: Configure Wells
------------------------

.. code-block:: python

   wells_config = WellConfiguration(
       diameter=3.0,      # 3mm diameter wells
       depth=5.0,         # 5mm deep
       num_wells=2,       # Two wells (top and bottom)
       spacing=10.0       # 10mm apart
   )

Step 3: Configure Channels
---------------------------

.. code-block:: python

   channels_config = ChannelConfiguration(
       length=8.0,        # 8mm long channels
       width=0.3,         # 300μm wide (0.3mm)
       height=0.1,        # 100μm tall (0.1mm)
       num_channels=10    # 10 parallel channels
   )

Step 4: Assemble the Device
----------------------------

.. code-block:: python

   device_config = DeviceConfiguration(
       casing=CasingConfiguration(width=20, height=20, depth=10),
       wells_config=wells_config,
       channels_config=channels_config
   )

   geometry, measurements = assemble_device(device_config)

Step 5: Export the Device
--------------------------

.. code-block:: python

   export_config = ExportConfiguration(
       output_directory=Path('output'),
       formats=['scad', 'dxf'],
       dxf_conversion=True
   )

   paths = export_device({'device': geometry}, export_config)
   print(f"Device exported to {paths['device']['scad']}")

Next Steps
----------

* :doc:`../examples/two_compartment` - More examples
* :doc:`../user_guide/device_design` - Design best practices
