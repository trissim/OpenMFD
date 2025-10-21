Devices Module
==============

The devices module provides device assembly and configuration.

.. currentmodule:: openmfd.devices

Configuration
-------------

.. automodule:: openmfd.devices.config
   :members:
   :undoc-members:
   :show-inheritance:

Assembly
--------

.. automodule:: openmfd.devices.assembly
   :members:
   :undoc-members:
   :show-inheritance:

Arrays
------

The arrays module provides functions for creating grids of device units with
optional alignment marks and proper positioning.

Device Positioning
^^^^^^^^^^^^^^^^^^

Devices in an array are positioned so that:

- The **bottom-left corner** of the first device is at ``[0, 0]``
- Each device is **centered** in its grid cell
- The array spans from ``[0, 0]`` to ``[grid_width, grid_height]``

This positioning ensures compatibility with the wafer centering coordinate system.

Alignment Mark Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``create_device_array()`` function supports automatic alignment mark generation:

.. code-block:: python

    array = create_device_array(
        unit, dims=[18, 9, 0], grid_size=[6, 8],
        dxf=True,
        alignment="full",              # or "hollow" for top layer
        units_from_center=(3, 4),      # mark positioning
        alignment_offset=(0, 0),       # optional offset
        alignment_mark_size=1.0        # mark size in mm
    )

**Parameters:**

- ``alignment``: "full" (solid marks), "hollow" (ring marks), or None
- ``units_from_center``: Distance from center in device units (e.g., (3, 4))
- ``alignment_offset``: Optional offset applied before adding marks
- ``alignment_mark_size``: Size of alignment marks (default: 1.0mm)

API Reference
^^^^^^^^^^^^^

.. automodule:: openmfd.devices.arrays
   :members:
   :undoc-members:
   :show-inheritance:

Outline
-------

.. automodule:: openmfd.devices.outline
   :members:
   :undoc-members:
   :show-inheritance:

Walls
-----

.. automodule:: openmfd.devices.walls
   :members:
   :undoc-members:
   :show-inheritance:

Wafer Masks
-----------

The wafer module provides functions for creating wafer outlines and masks for
photolithography. It handles wafer centering, mask generation, and integration
with device arrays.

Wafer Centering
^^^^^^^^^^^^^^^

All wafer-related features (outline, text, alignment marks) are centered at the
**wafer center**, which is computed from the device array dimensions:

.. code-block:: python

    from openmfd.devices import compute_wafer_center

    # Compute wafer center for 6x8 array of 18x9mm devices
    cx, cy = compute_wafer_center(grid_size=[6, 8], dims=[18, 9, 0])
    # Returns: (54, 36) - center of 108x72mm array

Wafer Mask Generation
^^^^^^^^^^^^^^^^^^^^^

The ``create_wafer_mask()`` function creates a photolithography mask by:

1. Creating wafer outline with flat edge
2. Adding inner line and outer margin
3. Subtracting device features from wafer area

**Structure:**

.. code-block:: python

    difference() {
        wafer_outline  # Wafer with flat edge
        union() {      # Device array with alignment marks
            array
            alignment_marks  # Added via union()
        }
    }

This structure ensures that:

- Device features are removed from the wafer (appear on photomask)
- Solid alignment marks are removed (visible on photomask)
- Ring alignment marks create registration holes

PDMS Shrinkage Compensation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The wafer mask supports PDMS shrinkage compensation via the ``shrinkage_scale``
parameter:

.. code-block:: python

    # For 100°C cure (20% shrinkage)
    mask = create_wafer_mask(
        wafer_size=150, flat_length=57.5,
        mask=array, grid_size=[6, 8], dims=[18, 9, 0],
        shrinkage_scale=0.8  # 20% shrinkage
    )

API Reference
^^^^^^^^^^^^^

.. automodule:: openmfd.devices.wafer
   :members:
   :undoc-members:
   :show-inheritance:

Alignment Marks
---------------

The alignment module provides functions for creating alignment marks used in
multi-layer photolithography for precise layer-to-layer registration.

Overview
^^^^^^^^

Alignment marks are critical features in multi-layer microfluidic device fabrication.
They enable precise alignment between different photolithography layers (e.g., channels
and wells) during the fabrication process.

**Mark Types:**

- **Full marks (solid crosshairs)**: Used on bottom layer (channels). Two L-shapes rotated 180° apart form a solid + shape.
- **Hollow marks (ring crosshairs)**: Used on top layer (wells/chambers). Ring-shaped marks create registration holes when subtracted by wafer mask.

**Key Concept:**

Both mark types are added to the device array using ``union()``. The difference between
"full" and "hollow" is in the mark **geometry**, not the boolean operation. When the
wafer mask subtracts the array, solid marks appear on the photomask while ring marks
create registration holes.

Basic Usage
^^^^^^^^^^^

.. code-block:: python

    from openmfd.devices import create_device_array

    # Bottom layer with solid alignment marks
    bottom_array = create_device_array(
        channels, dims=[18, 9, 0], grid_size=[6, 8],
        dxf=True, alignment="full",
        units_from_center=(3, 4),
        alignment_mark_size=1.0
    )

    # Top layer with hollow alignment marks
    top_array = create_device_array(
        wells, dims=[18, 9, 0], grid_size=[6, 8],
        dxf=True, alignment="hollow",
        units_from_center=(3, 4),
        alignment_mark_size=1.0
    )

Mark Positioning
^^^^^^^^^^^^^^^^

Marks can be positioned in two ways:

1. **Cardinal positions** (when ``units_from_center`` is specified):
   - Right, top, left, bottom positions
   - Distance from array center specified in device units
   - Example: ``units_from_center=(3, 4)`` places marks 3 units right/left and 4 units up/down from center

2. **Corner positions** (when ``units_from_center`` is None):
   - Bottom-left, bottom-right, top-left, top-right corners
   - Marks placed at array corners

Best Practices
^^^^^^^^^^^^^^

1. **Mark size**: Use ``alignment_mark_size`` between 0.5-2.0mm for optimal visibility
2. **Positioning**: Cardinal positions (``units_from_center``) provide better alignment than corners
3. **Layer consistency**: Use same positioning parameters for both layers
4. **Verification**: Always check DXF output in viewer before fabrication

API Reference
^^^^^^^^^^^^^

.. automodule:: openmfd.devices.alignment
   :members:
   :undoc-members:
   :show-inheritance:

Text
----

.. automodule:: openmfd.devices.text
   :members:
   :undoc-members:
   :show-inheritance:
