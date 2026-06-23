"""Well insert generation with chamfered walls."""

from typing import Callable, List, Optional, Tuple
import solid
from solid.utils import union, difference

from openmfd.geometry.chambers import make_chambers
from openmfd.geometry.channels import make_channels
from openmfd.geometry.wells import WellPatternContext, four_corner, wells_top_bottom

from .config import (
    CompleteInsertConfiguration,
    InsertConfiguration,
    PinConfiguration,
    SkirtConfiguration,
)
from .chamfer import deg_taper_len, linear_extrude_if_flat
from .pins import create_pin_array
from .skirts import SkirtProfileContext, create_dual_skirt


def _taper_length(taper) -> float:
    return deg_taper_len(taper.height, taper.degrees) + taper.extra_length


def _build_insert_pattern(
    config: CompleteInsertConfiguration,
    well_radius: float,
    channel_length: float,
    chamber_width: Optional[float],
) -> solid.OpenSCADObject:
    wells_cfg = config.wells
    positions = wells_cfg.positions or []
    if not positions:
        raise ValueError("CompleteInsertConfiguration.wells.positions must be provided")

    if len(positions) == 2:
        wells = wells_top_bottom(
            WellPatternContext.from_fields(well_radius, positions=positions, dxf=True)
        )
    elif len(positions) == 4:
        dims = well_radius if wells_cfg.shape == "circle" else (well_radius, well_radius)
        wells = four_corner(WellPatternContext.from_fields(dims, positions=positions, dxf=True))
    else:
        raise ValueError(f"Unsupported number of well positions for insert build: {len(positions)}")

    channels, measurements = make_channels(
        length=channel_length,
        width=config.channels.width,
        height=None,
        num_chans=config.channels.num_channels,
        max_chans=config.channels.max_channels,
        spacing=config.channels.spacing,
        dxf=True,
        rotate_channels=config.channels.rotate,
    )

    geometry_parts = [wells]
    if config.chambers is not None:
        geometry_parts.append(
            make_chambers(
                msrs=measurements,
                height=None,
                extra=config.chambers.extra,
                len_until=config.chambers.len_until,
                width=chamber_width,
                dxf=True,
            )
        )

    return union()(*geometry_parts)


def _adjust_insert_dimensions(
    config: CompleteInsertConfiguration,
    taper_len: float,
) -> Tuple[float, float, float]:
    if config.wells.radius is None:
        raise ValueError("CompleteInsertConfiguration.wells.radius must be provided")

    well_radius = config.wells.radius - taper_len
    channel_length = config.channels.length + taper_len * 2
    configured_chamber_width = None
    if config.chambers is not None:
        configured_chamber_width = config.chambers.width
    chamber_width = (configured_chamber_width or config.wells.radius * 2) - taper_len * 2
    return well_radius, channel_length, chamber_width


def _build_insert_footprint_array(
    config: CompleteInsertConfiguration,
    grid_size: Tuple[int, int],
    well_radius: float,
    channel_length: float,
    chamber_width: float,
    alignment_offset: Optional[Tuple[float, float]],
) -> solid.OpenSCADObject:
    footprint = _build_insert_pattern(config, well_radius, channel_length, chamber_width)
    return create_well_insert_array(
        insert_unit=footprint,
        dims=list(config.dims),
        grid_size=list(grid_size),
        alignment_offset=alignment_offset,
    )


def _create_tapered_insert_array(
    config: CompleteInsertConfiguration,
    grid_size: Tuple[int, int],
    alignment_offset: Optional[Tuple[float, float]],
) -> solid.OpenSCADObject:
    taper_len = _taper_length(config.outer_taper)
    well_radius, channel_length, chamber_width = _adjust_insert_dimensions(config, taper_len)

    outer_footprint = _build_insert_footprint_array(
        config,
        grid_size,
        well_radius,
        channel_length,
        chamber_width,
        alignment_offset,
    )
    insert_array = linear_extrude_if_flat(
        outer_footprint,
        height=config.outer_taper.height,
        degrees=config.outer_taper.degrees,
        segments=config.outer_taper.segments,
    )

    if config.inner_taper is not None:
        inner_taper_len = _taper_length(config.inner_taper)
        inner_well_radius, inner_channel_length, inner_chamber_width = _adjust_insert_dimensions(
            config,
            taper_len + inner_taper_len,
        )
        inner_footprint = _build_insert_footprint_array(
            config,
            grid_size,
            inner_well_radius,
            inner_channel_length,
            inner_chamber_width,
            alignment_offset,
        )
        inner_insert = linear_extrude_if_flat(
            inner_footprint,
            height=config.inner_taper.height,
            degrees=config.inner_taper.degrees,
            segments=config.inner_taper.segments,
        )
        insert_array = difference()(insert_array, inner_insert)

    return insert_array


def _base_feature_offsets(config: CompleteInsertConfiguration) -> Tuple[float, float, float]:
    pin_height = config.pins.height if config.pins is not None else 0.0
    skirt_height = 0.0
    if config.skirts is not None:
        skirt_height = config.skirts.height1 + config.skirts.height2
    return pin_height, skirt_height, pin_height + skirt_height


def _create_insert_skirts(
    insert_array: solid.OpenSCADObject,
    config: CompleteInsertConfiguration,
) -> solid.OpenSCADObject:
    assert config.skirts is not None
    pin_height, _, _ = _base_feature_offsets(config)
    return create_dual_skirt(
        insert_geometry=solid.projection()(insert_array),
        context=SkirtProfileContext.from_fields(
            thickness1=-config.skirts.thickness1,
            height1=config.skirts.height1,
            empty1=config.skirts.empty1,
            thickness2=-config.skirts.thickness2,
            height2=config.skirts.height2,
            pin_height=pin_height,
        ),
    )


def _create_insert_pin_unit(config: CompleteInsertConfiguration) -> solid.OpenSCADObject:
    assert config.pins is not None
    positions = config.well_positions or config.wells.positions or []
    pin_height, skirt_height, _ = _base_feature_offsets(config)
    return create_pin_array(
        well_positions=positions,
        dims=config.pins.dims,
        height=pin_height + config.pins.inner_height + skirt_height,
        offset=config.pins.offset,
        rotation=config.pins.rotation,
    )


def build_insert(
    config: CompleteInsertConfiguration,
    grid_size: Tuple[int, int],
    alignment_offset: Optional[Tuple[float, float]] = None,
) -> solid.OpenSCADObject:
    """Build an insert array directly from a nominal complete insert config."""
    insert_array = _create_tapered_insert_array(config, grid_size, alignment_offset)
    _, _, insert_z_offset = _base_feature_offsets(config)
    insert_array = solid.translate([0, 0, insert_z_offset])(insert_array)

    components = [insert_array]
    if config.skirts is not None:
        components.append(_create_insert_skirts(insert_array, config))
    if config.pins is not None:
        pin_array = create_well_insert_array(
            insert_unit=_create_insert_pin_unit(config),
            dims=list(config.dims),
            grid_size=list(grid_size),
            alignment_offset=alignment_offset,
        )
        components.append(pin_array)

    assembly = union()(*components)
    return solid.scale([config.pdms_scale, config.pdms_scale, 1])(assembly)


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
    taper_len = deg_taper_len(insert_config.outer_taper.height, insert_config.outer_taper.degrees)
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
        dxf=True,  # Keep existing z placement for already-extruded insert geometry.
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
            context=SkirtProfileContext.from_fields(
                thickness1=-skirt_config.thickness1,
                height1=skirt_config.height1,
                empty1=skirt_config.empty1,
                thickness2=-skirt_config.thickness2,
                height2=skirt_config.height2,
                pin_height=pin_height,
            ),
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
            rotation=pin_config.rotation,
        )
        components.append(pins)

    # Combine all components
    assembly = union()(*components)

    # Apply PDMS shrinkage compensation (x, y only, not z)
    assembly = solid.scale([pdms_scale, pdms_scale, 1])(assembly)

    return assembly
