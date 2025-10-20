"""Device assembly functions for combining geometric primitives.

This module provides functions for assembling complete microfluidic devices
from wells, channels, and chambers.
"""

from typing import Optional, List
import solid
from solid.utils import union

from openmfd.geometry.types import Measurements
from openmfd.geometry.wells import wells_top_bottom, four_corner
from openmfd.geometry.channels import make_channels
from openmfd.geometry.chambers import make_chambers

from .config import DeviceConfiguration, CasingConfiguration


def assemble_device(config: DeviceConfiguration) -> solid.OpenSCADObject:
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
    device_parts = []
    measurements = None
    
    # Create channels first (needed for chamber measurements)
    if config.add_channels and config.channels_config is not None:
        channels, measurements = make_channels(
            length=config.channels_config.length,
            width=config.channels_config.width,
            height=config.channels_config.height,
            num_chans=config.channels_config.num_channels,
            max_chans=config.channels_config.max_channels,
            spacing=config.channels_config.spacing,
            dxf=config.dxf,
            rotate_channels=config.channels_config.rotate
        )
        device_parts.append(channels)
    
    # Create chambers (requires channel measurements)
    if config.add_chambers and config.chambers_config is not None:
        if measurements is None:
            raise ValueError("Chambers require channels to be created first for measurements")
        
        chambers = make_chambers(
            msrs=measurements,
            height=config.chambers_config.height,
            extra=config.chambers_config.extra,
            len_until=config.chambers_config.len_until,
            width=config.chambers_config.width,
            dxf=config.dxf
        )
        device_parts.append(chambers)
    
    # Create wells
    if config.add_wells and config.wells_config is not None:
        wells_cfg = config.wells_config
        
        # Determine well creation function based on positions
        if wells_cfg.positions is not None:
            num_positions = len(wells_cfg.positions)
            if num_positions == 2:
                # Use wells_top_bottom for 2 wells
                wells = wells_top_bottom(
                    radius=wells_cfg.radius if wells_cfg.radius is not None else wells_cfg.dimensions,
                    height=wells_cfg.height,
                    positions=wells_cfg.positions,
                    dxf=config.dxf,
                    shape=wells_cfg.shape,
                    segments=wells_cfg.segments
                )
            elif num_positions == 4:
                # Use four_corner for 4 wells
                wells = four_corner(
                    radius=wells_cfg.radius if wells_cfg.radius is not None else wells_cfg.dimensions,
                    height=wells_cfg.height,
                    positions=wells_cfg.positions,
                    dxf=config.dxf,
                    square=(wells_cfg.shape == "square"),
                    segments=wells_cfg.segments
                )
            else:
                raise ValueError(f"Unsupported number of well positions: {num_positions}")
        else:
            # Default to 4-corner configuration
            wells = four_corner(
                radius=wells_cfg.radius if wells_cfg.radius is not None else wells_cfg.dimensions,
                height=wells_cfg.height,
                dxf=config.dxf,
                square=(wells_cfg.shape == "square"),
                segments=wells_cfg.segments
            )
        
        device_parts.append(wells)
    
    # Combine all parts
    if not device_parts:
        raise ValueError("No device parts to assemble")
    
    device = union()(*device_parts)
    
    # Apply rotation if specified
    if config.rotation != 0:
        device = solid.rotate(config.rotation)(device)
    
    # Translate to casing position (center device in casing)
    device = solid.translate([
        config.casing.x / 2.0,
        config.casing.y / 2.0,
        0
    ])(device)
    
    return device


def assemble_unit(
    config: DeviceConfiguration,
    position: Optional[List[float]] = None
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


def assemble_components_separately(
    config: DeviceConfiguration
) -> dict:
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
    components = {}
    measurements = None
    
    # Create and position channels
    if config.add_channels and config.channels_config is not None:
        channels, measurements = make_channels(
            length=config.channels_config.length,
            width=config.channels_config.width,
            height=config.channels_config.height,
            num_chans=config.channels_config.num_channels,
            max_chans=config.channels_config.max_channels,
            spacing=config.channels_config.spacing,
            dxf=config.dxf,
            rotate_channels=config.channels_config.rotate
        )
        
        if config.rotation != 0:
            channels = solid.rotate(config.rotation)(channels)
        channels = solid.translate([config.casing.x / 2, config.casing.y / 2, 0])(channels)
        components['channels'] = channels
    
    # Create and position chambers
    if config.add_chambers and config.chambers_config is not None and measurements is not None:
        chambers = make_chambers(
            msrs=measurements,
            height=config.chambers_config.height,
            extra=config.chambers_config.extra,
            len_until=config.chambers_config.len_until,
            width=config.chambers_config.width,
            dxf=config.dxf
        )
        
        if config.rotation != 0:
            chambers = solid.rotate(config.rotation)(chambers)
        chambers = solid.translate([config.casing.x / 2, config.casing.y / 2, 0])(chambers)
        components['chambers'] = chambers
    
    # Create and position wells
    if config.add_wells and config.wells_config is not None:
        wells_cfg = config.wells_config
        
        if wells_cfg.positions is not None and len(wells_cfg.positions) == 2:
            wells = wells_top_bottom(
                radius=wells_cfg.radius if wells_cfg.radius is not None else wells_cfg.dimensions,
                height=wells_cfg.height,
                positions=wells_cfg.positions,
                dxf=config.dxf,
                shape=wells_cfg.shape,
                segments=wells_cfg.segments
            )
        else:
            wells = four_corner(
                radius=wells_cfg.radius if wells_cfg.radius is not None else wells_cfg.dimensions,
                height=wells_cfg.height,
                positions=wells_cfg.positions,
                dxf=config.dxf,
                square=(wells_cfg.shape == "square"),
                segments=wells_cfg.segments
            )
        
        if config.rotation != 0:
            wells = solid.rotate(config.rotation)(wells)
        wells = solid.translate([config.casing.x / 2, config.casing.y / 2, 0])(wells)
        components['wells'] = wells
    
    # Create combined device
    device_parts = [v for k, v in components.items() if k in ['wells', 'channels', 'chambers']]
    if device_parts:
        components['device'] = union()(*device_parts)
    
    # Create chambers + wells combination
    chambers_wells_parts = []
    if 'chambers' in components:
        chambers_wells_parts.append(components['chambers'])
    if 'wells' in components:
        chambers_wells_parts.append(components['wells'])
    if chambers_wells_parts:
        components['chambers_wells'] = union()(*chambers_wells_parts)
    
    return components

