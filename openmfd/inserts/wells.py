"""Well insert generation with chamfered walls."""

from typing import Tuple, List, Optional, Callable
import solid
from solid.utils import union, difference

from .config import InsertConfiguration, PinConfiguration, SkirtConfiguration
from .chamfer import deg_taper_len, linear_extrude_if_flat
from .pins import create_pin_array
from .skirts import create_dual_skirt


def create_well_insert(
    device_function: Callable,
    insert_config: InsertConfiguration,
    dims: List[float],
    grid_size: List[int],
) -> Tuple[solid.OpenSCADObject, float, float]:
    """Create a chamfered well insert from device geometry.

    Generates a 3D printed insert with tapered walls for easier pipetting
    access and better liquid containment. The insert is created by:
    1. Adjusting well radius and chamber width for taper
    2. Generating 2D device geometry
    3. Applying chamfered extrusion

    Parameters
    ----------
    device_function : callable
        Function that generates device geometry. Should accept well_rad,
        chan_l, chamber_width, and add_chambers parameters.
    insert_config : InsertConfiguration
        Configuration for insert geometry and taper.
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].

    Returns
    -------
    tuple of (solid.OpenSCADObject, float, float)
        - 3D insert geometry
        - Adjusted well radius
        - Adjusted channel length

    Examples
    --------
    >>> from openmfd.geometry import wells_top_bottom
    >>> # Create insert configuration
    >>> from openmfd.inserts.config import InsertConfiguration, TaperConfiguration
    >>> insert_config = InsertConfiguration(
    ...     outer_taper=TaperConfiguration(height=3.8, degrees=16, extra_length=0.3),
    ...     well_radius=3.2,
    ...     channel_length=1.0
    ... )
    >>>
    >>> # Create insert
    >>> insert, well_rad, chan_l = create_well_insert(
    ...     device_function=wells_top_bottom,
    ...     insert_config=insert_config,
    ...     dims=[9.0, 9.0, 0],
    ...     grid_size=[6, 8]
    ... )
    """
    # Calculate taper length for outer chamfer
    taper_len = deg_taper_len(
        insert_config.outer_taper.height, insert_config.outer_taper.degrees
    )
    taper_len += insert_config.outer_taper.extra_length

    # Adjust dimensions for taper
    well_rad = insert_config.well_radius - taper_len
    chan_l = insert_config.channel_length + taper_len * 2

    # Determine chamber width
    if insert_config.chamber_width is None:
        chamber_width = insert_config.well_radius * 2 - taper_len * 2
    else:
        chamber_width = insert_config.chamber_width - taper_len * 2

    # Generate 2D device geometry
    # Note: This assumes device_function returns ((geometry, _), _, _)
    (insert_2d, _), _, _ = device_function(
        well_rad=well_rad,
        chan_l=chan_l,
        chamber_width=chamber_width,
        add_chambers=insert_config.add_chambers,
    )

    # Apply chamfered extrusion
    insert_3d = linear_extrude_if_flat(
        insert_2d,
        height=insert_config.outer_taper.height,
        degrees=insert_config.outer_taper.degrees,
        segments=insert_config.outer_taper.segments,
    )

    return insert_3d, well_rad, chan_l


def create_well_insert_array(
    insert_unit: solid.OpenSCADObject,
    dims: List[float],
    grid_size: List[int],
    alignment_offset: Optional[Tuple[float, float]] = None,
) -> solid.OpenSCADObject:
    """Create an array of well inserts.

    Parameters
    ----------
    insert_unit : solid.OpenSCADObject
        Single insert unit to replicate.
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
    alignment_offset : tuple of (float, float), optional
        Offset to apply to entire array (x, y) in mm.

    Returns
    -------
    solid.OpenSCADObject
        Array of inserts.

    Examples
    --------
    >>> # Create array of inserts
    >>> insert_unit = create_well_insert(...)
    >>> insert_array = create_well_insert_array(
    ...     insert_unit=insert_unit,
    ...     dims=[9.0, 9.0, 0],
    ...     grid_size=[6, 8],
    ...     alignment_offset=(0, 0)
    ... )
    """
    from openmfd.devices import create_device_array

    # Create array using existing array function
    array = create_device_array(
        unit=insert_unit,
        dims=dims,
        grid_size=grid_size,
        dxf=False,  # 3D geometry
        alignment=None,  # No alignment marks on inserts
    )

    # Apply alignment offset if specified
    if alignment_offset is not None:
        array = solid.translate([alignment_offset[0], alignment_offset[1], 0])(array)

    return array


def assemble_well_inserts(
    device_function: Callable,
    insert_config: InsertConfiguration,
    pin_config: Optional[PinConfiguration],
    skirt_config: Optional[SkirtConfiguration],
    dims: List[float],
    grid_size: List[int],
    well_positions: List[Tuple[float, float]],
    alignment_offset: Optional[Tuple[float, float]] = None,
    pdms_scale: float = 0.8,
) -> solid.OpenSCADObject:
    """Assemble complete well insert with pins and skirts.

    Creates a complete 3D printed insert assembly including:
    - Outer chamfered wells
    - Optional inner chamfered cavity
    - Optional alignment pins
    - Optional sealing skirts
    - PDMS shrinkage compensation

    Parameters
    ----------
    device_function : callable
        Function that generates device geometry.
    insert_config : InsertConfiguration
        Configuration for insert geometry and taper.
    pin_config : PinConfiguration, optional
        Configuration for alignment pins. If None, no pins.
    skirt_config : SkirtConfiguration, optional
        Configuration for sealing skirts. If None, no skirts.
    dims : list of float
        Unit dimensions [x, y, z].
    grid_size : list of int
        Grid size [rows, columns].
    well_positions : list of tuple of (float, float)
        List of well positions (x, y) for pin placement.
    alignment_offset : tuple of (float, float), optional
        Offset to apply to entire assembly (x, y) in mm.
    pdms_scale : float, default=0.8
        PDMS shrinkage scale factor. Applied to x and y only, not z.

    Returns
    -------
    solid.OpenSCADObject
        Complete insert assembly.

    Examples
    --------
    >>> from openmfd.geometry import wells_top_bottom
    >>> from openmfd.inserts.config import (
    ...     InsertConfiguration, TaperConfiguration,
    ...     PinConfiguration, SkirtConfiguration
    ... )
    >>>
    >>> # Configure insert
    >>> insert_config = InsertConfiguration(
    ...     outer_taper=TaperConfiguration(height=3.8, degrees=16, extra_length=0.3),
    ...     inner_taper=TaperConfiguration(height=0.4, degrees=35, extra_length=0.91),
    ...     well_radius=3.2,
    ...     channel_length=1.0
    ... )
    >>>
    >>> # Configure pins
    >>> pin_config = PinConfiguration(
    ...     dims=(1.85, 1.85),
    ...     height=0.06,
    ...     inner_height=2.0,
    ...     offset=-0.5,
    ...     hole_dims=(2.0, 2.0)
    ... )
    >>>
    >>> # Configure skirts
    >>> skirt_config = SkirtConfiguration(
    ...     thickness1=0.75, height1=0.66, empty1=0.3,
    ...     thickness2=0.8, height2=0.04
    ... )
    >>>
    >>> # Assemble complete insert
    >>> assembly = assemble_well_inserts(
    ...     device_function=wells_top_bottom,
    ...     insert_config=insert_config,
    ...     pin_config=pin_config,
    ...     skirt_config=skirt_config,
    ...     dims=[9.0, 9.0, 0],
    ...     grid_size=[6, 8],
    ...     well_positions=[(0, -4.5), (0, 4.5)],
    ...     alignment_offset=(0, 0),
    ...     pdms_scale=0.8
    ... )
    """
    components = []

    # Create outer insert
    outer_insert, well_rad_outer, chan_l_outer = create_well_insert(
        device_function=device_function,
        insert_config=insert_config,
        dims=dims,
        grid_size=grid_size,
    )

    # Create inner cavity if specified
    if insert_config.inner_taper is not None:
        # Create inner insert configuration
        inner_config = InsertConfiguration(
            outer_taper=insert_config.inner_taper,
            well_radius=well_rad_outer,
            channel_length=chan_l_outer,
            chamber_width=insert_config.chamber_width,
            add_chambers=insert_config.add_chambers,
        )

        inner_insert, _, _ = create_well_insert(
            device_function=device_function,
            insert_config=inner_config,
            dims=dims,
            grid_size=grid_size,
        )

        # Subtract inner from outer
        outer_insert = difference()(outer_insert, inner_insert)

    # Create array of inserts
    insert_array = create_well_insert_array(
        insert_unit=outer_insert,
        dims=dims,
        grid_size=grid_size,
        alignment_offset=alignment_offset,
    )

    # Calculate z-offset for inserts (above pins and skirts)
    # Legacy: inserts at z = pin_height + skirt_height1 + skirt_height2
    z_offset = 0.0
    pin_height = 0.0
    if pin_config is not None:
        pin_height = pin_config.height
        z_offset += pin_config.height
    if skirt_config is not None:
        z_offset += skirt_config.height1 + skirt_config.height2

    # Position inserts above pins and skirts
    insert_array = solid.translate([0, 0, z_offset])(insert_array)
    components.append(insert_array)

    # Add skirts if specified (must be before pins to get correct projection)
    if skirt_config is not None:
        skirts = create_dual_skirt(
            insert_geometry=solid.projection()(insert_array),
            thickness1=-skirt_config.thickness1,  # Negative to shrink inward
            height1=skirt_config.height1,
            empty1=skirt_config.empty1,
            thickness2=-skirt_config.thickness2,  # Negative to shrink inward
            height2=skirt_config.height2,
            pin_height=pin_height,
        )
        components.append(skirts)

    # Add pins if specified
    if pin_config is not None:
        # Legacy: pin height = pin_height + skirt_height1 + skirt_height2 + pin_inner_height
        total_pin_height = pin_config.height + pin_config.inner_height
        if skirt_config is not None:
            total_pin_height += skirt_config.height1 + skirt_config.height2

        pins = create_pin_array(
            well_positions=well_positions,
            dims=pin_config.dims,
            height=total_pin_height,
            offset=pin_config.offset,
        )
        components.append(pins)

    # Combine all components
    assembly = union()(*components)

    # Apply PDMS shrinkage compensation (x, y only, not z)
    assembly = solid.scale([pdms_scale, pdms_scale, 1])(assembly)

    return assembly

