Installation
============

This guide covers installing OpenMFD and its dependencies.

Requirements
------------

* Python 3.8 or higher
* pip package manager

Installing OpenMFD
------------------

Standard Installation
~~~~~~~~~~~~~~~~~~~~~

Install OpenMFD using pip:

.. code-block:: bash

   pip install openmfd

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

To install OpenMFD for development:

.. code-block:: bash

   git clone https://github.com/trissim/mfd.git
   cd mfd
   pip install -e ".[dev]"

Installing OpenSCAD
-------------------

OpenSCAD is required for converting SCAD files to DXF and STL formats.

Download from https://openscad.org/downloads.html

Verifying Installation
----------------------

Verify that OpenMFD is installed correctly:

.. code-block:: python

   import openmfd
   from openmfd.geometry import make_well
   from openmfd.export import export_scad
   from pathlib import Path

   # Create a simple well
   well = make_well(diameter=3.0, height=5.0)

   # Export to SCAD
   output_path = Path('test_well.scad')
   export_scad(well, output_path)

   print(f"Successfully created {output_path}")

Next Steps
----------

* :doc:`first_device` - Create your first microfluidic device
* :doc:`quick_reference` - Quick reference guide
