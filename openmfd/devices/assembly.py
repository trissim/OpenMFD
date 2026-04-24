"""Device assembly functions for combining geometric primitives.

This module provides functions for assembling complete microfluidic devices
from wells, channels, and chambers.
"""

from typing import Dict, List, Optional, Tuple
import solid
from solid.utils import union

from openmfd.geometry.types import Dimensions, Measurements
from openmfd.geometry.primitives import WellGeometryRequest
from openmfd.geometry.positioning import wells_pos_from_center_4
from openmfd.geometry.channels import make_channels
from openmfd.geometry.chambers import make_chambers

from .config import DeviceConfiguration, InsertHolesConfiguration


def _build_channels(
    config: DeviceConfiguration,
) -> Tuple[Optional[solid.OpenSCADObject], Optional[Measurements]]:
    if not config.add_channels or config.channels_config is None:
        return None, None

    channels, measurements = make_channels(
        length=config.channels_config.length,
        width=config.channels_config.width,
        height=config.channels_config.height,
        num_chans=config.channels_config.num_channels,
        max_chans=config.channels_config.max_channels,
        spacing=config.channels_config.spacing,
        dxf=config.dxf,
        rotate_channels=config.channels_config.rotate,
    )
    return channels, measurements


def _build_chambers(
    config: DeviceConfiguration, measurements: Optional[Measurements]
) -> Optional[solid.OpenSCADObject]:
    if not config.add_chambers or config.chambers_config is None:
        return None
    if measurements is None:
        raise ValueError("Chambers require channels to be created first for measurements")

    return make_chambers(
        msrs=measurements,
        height=config.chambers_config.height,
        extra=config.chambers_config.extra,
        len_until=config.chambers_config.len_until,
        width=config.chambers_config.width,
        dxf=config.dxf,
    )


def _resolve_well_dims(config: DeviceConfiguration) -> Dimensions:
    wells_cfg = config.wells_config
    assert wells_cfg is not None
    if wells_cfg.radius is not None:
        return wells_cfg.radius
    assert wells_cfg.dimensions is not None
    return wells_cfg.dimensions


def _default_well_positions(config: DeviceConfiguration) -> List[Tuple[float, float]]:
    wells_cfg = config.wells_config
    assert wells_cfg is not None
    if wells_cfg.positions is not None:
        return wells_cfg.positions

    dims = _resolve_well_dims(config)
    span = dims if isinstance(dims, (int, float)) else max(dims)
    offset = span + span / 2.0
    return wells_pos_from_center_4(offset)


def _translate_geometry(
    geometry: solid.OpenSCADObject,
    x: float,
    y: float,
    z_offset: float,
    is_2d: bool,
) -> solid.OpenSCADObject:
    if is_2d:
        return solid.translate([x, y])(geometry)
    return solid.translate([x, y, z_offset])(geometry)


def _build_insert_hole_geometry(
    insert_holes: InsertHolesConfiguration,
    dxf: bool,
) -> solid.OpenSCADObject:
    base_hole = WellGeometryRequest.from_fields(
        dims=insert_holes.hole_dims,
        height=None,
        dxf=dxf,
    ).build()
    holes = []
    for x, y in insert_holes.well_positions:
        holes.append(solid.translate([x + insert_holes.offset, y])(base_hole))
    return union()(*holes)


def _build_wells(config: DeviceConfiguration) -> Optional[solid.OpenSCADObject]:
    if not config.add_wells or config.wells_config is None:
        return None

    wells_cfg = config.wells_config
    dims = _resolve_well_dims(config)
    positions = _default_well_positions(config)
    well_shape = WellGeometryRequest.from_fields(
        dims=dims,
        height=wells_cfg.height,
        dxf=config.dxf,
        segments=wells_cfg.segments,
    ).build()

    is_2d = config.dxf or wells_cfg.height is None
    z_offset = 0 if is_2d else (wells_cfg.height or 0) / 2.0
    wells = [
        _translate_geometry(well_shape, position[0], position[1], z_offset, is_2d)
        for position in positions
    ]
    wells_geometry = union()(*wells)

    if config.insert_holes is not None:
        insert_holes = _build_insert_hole_geometry(config.insert_holes, dxf=config.dxf)
        wells_geometry = solid.difference()(wells_geometry, insert_holes)

    return wells_geometry


def _center_in_casing(
    geometry: solid.OpenSCADObject,
    config: DeviceConfiguration,
    center_in_casing: bool,
) -> solid.OpenSCADObject:
    if config.rotation != 0:
        geometry = solid.rotate(config.rotation)(geometry)
    if center_in_casing:
        geometry = solid.translate([config.casing.x / 2.0, config.casing.y / 2.0, 0])(geometry)
    return geometry


def _build_component_geometries(config: DeviceConfiguration) -> Dict[str, solid.OpenSCADObject]:
    components: Dict[str, solid.OpenSCADObject] = {}
    channels, measurements = _build_channels(config)
    if channels is not None:
        components["channels"] = channels

    chambers = _build_chambers(config, measurements)
    if chambers is not None:
        components["chambers"] = chambers

    wells = _build_wells(config)
    if wells is not None:
        components["wells"] = wells

    return components


def assemble_device(
    config: DeviceConfiguration, center_in_casing: bool = True
) -> solid.OpenSCADObject:
    """Assemble a complete device from configuration.

    This function creates wells, channels, and chambers according to the
    configuration and combines them into a single device unit.

    Parameters
    ----------
    config : DeviceConfiguration
        Device configuration specifying all components.

    Returns
    -------
    solid.OpenSCADObject
        Assembled device geometry.

    Examples
    --------
    >>> from openmfd.devices.config import DeviceConfiguration, CasingConfiguration
    >>> from openmfd.geometry.wells import WellConfiguration
    >>> from openmfd.geometry.channels import ChannelConfiguration
    >>> from openmfd.geometry.chambers import ChamberConfiguration
    >>>
    >>> # Create configuration
    >>> config = DeviceConfiguration(
    ...     casing=CasingConfiguration(x=9.0, y=9.0),
    ...     wells_config=WellConfiguration(radius=1.5, height=0.3),
    ...     channels_config=ChannelConfiguration(length=1.0, width=0.01, height=0.01),
    ...     chambers_config=ChamberConfiguration(height=0.1),
    ...     dxf=True
    ... )
    >>>
    >>> # Assemble device
    >>> device = assemble_device(config)
    """
    components = _build_component_geometries(config)
    device_parts = list(components.values())
    if not device_parts:
        raise ValueError("No device parts to assemble")

    device = union()(*device_parts)
    return _center_in_casing(device, config, center_in_casing=center_in_casing)


def assemble_unit(
    config: DeviceConfiguration, position: Optional[List[float]] = None
) -> solid.OpenSCADObject:
    """Assemble a single device unit with optional positioning.

    Parameters
    ----------
    config : DeviceConfiguration
        Device configuration.
    position : list of float, optional
        [x, y, z] position for the unit. If None, uses default from config.

    Returns
    -------
    solid.OpenSCADObject
        Positioned device unit.

    Examples
    --------
    >>> # Create unit at specific position
    >>> unit = assemble_unit(config, position=[10.0, 20.0, 0])
    """
    device = assemble_device(config)

    if position is not None:
        device = solid.translate(position)(device)

    return device


def assemble_components_separately(config: DeviceConfiguration) -> dict:
    """Assemble device components separately (wells, channels, chambers).

    This is useful for creating separate output files for each component.

    Parameters
    ----------
    config : DeviceConfiguration
        Device configuration.

    Returns
    -------
    dict
        Dictionary with keys 'wells', 'channels', 'chambers', 'device',
        'chambers_wells' containing the respective geometries.

    Examples
    --------
    >>> components = assemble_components_separately(config)
    >>> wells = components['wells']
    >>> channels = components['channels']
    """
    base_components = _build_component_geometries(config)
    components = {
        name: _center_in_casing(geometry, config, center_in_casing=True)
        for name, geometry in base_components.items()
    }

    device_parts = [v for k, v in components.items() if k in ["wells", "channels", "chambers"]]
    if device_parts:
        components["device"] = union()(*device_parts)

    # Create chambers + wells combination
    chambers_wells_parts = []
    if "chambers" in components:
        chambers_wells_parts.append(components["chambers"])
    if "wells" in components:
        chambers_wells_parts.append(components["wells"])
    if chambers_wells_parts:
        components["chambers_wells"] = union()(*chambers_wells_parts)

    return components
