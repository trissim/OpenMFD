"""High-level device builder for config-driven device generation.

This module provides a high-level builder function that encapsulates all the
low-level operations (arrays, decorations, scaling, wafer masks) into a single
config-driven interface.
"""

from typing import Dict
import solid
import numpy as np

from .config import CompleteDeviceConfiguration, TextConfiguration
from .assembly import assemble_device
from .arrays import create_device_array
from .wafer import create_wafer_mask
from .outline import create_glass_outline


def _array_grid_size(config: CompleteDeviceConfiguration) -> list[int]:
    if config.has_array():
        assert config.array is not None
        return config.array.grid_size()
    return [1, 1]


def _build_wafer_mask_kwargs(
    config: CompleteDeviceConfiguration,
    mask: solid.OpenSCADObject,
) -> dict:
    assert config.wafer_mask is not None

    kwargs = {
        "wafer_size": config.wafer_mask.wafer_size,
        "flat_length": config.wafer_mask.flat_length,
        "mask": mask,
        "grid_size": _array_grid_size(config),
        "dims": config.device.casing.as_list(),
        "wafer_line_thickness": config.wafer_mask.wafer_line_thickness,
        "outer_mask_thickness": config.wafer_mask.outer_mask_thickness,
    }
    if config.alignment_offset:
        kwargs["alignment_offset"] = config.alignment_offset
    if config.has_pdms_scaling():
        assert config.pdms is not None
        kwargs["shrinkage_scale"] = config.pdms.scale_factor()
    return kwargs


def _build_text_annotation_geometry(text_config: TextConfiguration) -> solid.OpenSCADObject:
    return solid.translate(list(text_config.position))(
        solid.text(
            text_config.text,
            halign=text_config.halign,
            valign=text_config.valign,
            size=text_config.size,
        )
    )


def _build_array_kwargs(config: CompleteDeviceConfiguration, alignment: str) -> dict:
    assert config.array is not None
    return {
        "dims": config.device.casing.as_list(),
        "grid_size": config.array.grid_size(),
        "dxf": config.device.dxf,
        "alignment": alignment,
        "units_from_center": config.array.units_from_center,
        "alignment_offset": config.alignment_offset,
        "alignment_mark_size": config.alignment_mark_size,
    }


def _build_outline_geometry(config: CompleteDeviceConfiguration) -> solid.OpenSCADObject:
    assert config.outline is not None
    assert config.outline.glass_size is not None
    assert config.outline.wall_thickness is not None
    return create_glass_outline(
        glass_size=(np.array(config.outline.glass_size) - config.outline.wall_thickness).tolist(),
        wall_thickness=config.outline.wall_thickness,
        grid_size=_array_grid_size(config),
        dims=config.device.casing.as_list(),
        alignment_groove_thickness=config.outline.alignment_groove_thickness,
    )


def build_device_layer(
    config: CompleteDeviceConfiguration, alignment: str = "full"
) -> Dict[str, solid.OpenSCADObject]:
    """Build complete device layer with arrays, decorations, and wafer masks.

    This is the main high-level function for generating device layers from
    a CompleteDeviceConfiguration. It encapsulates all the array generation,
    decoration addition, PDMS scaling, and wafer mask creation.

    Parameters
    ----------
    config : CompleteDeviceConfiguration
        Complete device configuration including device, array, decorations, etc.
    alignment : str, default='full'
        Alignment mark type: 'full' (solid), 'hollow' (ring), or 'partial'.

    Returns
    -------
    Dict[str, solid.OpenSCADObject]
        Dictionary containing:
        - 'device': Single device unit
        - 'array': Device array (if array config provided)
        - 'decorated': Array with decorations (if decorations provided)
        - 'scaled': Decorated array with PDMS scaling (if PDMS config provided)
        - 'wafer_mask': Final wafer mask (if wafer mask config provided)

    Examples
    --------
    >>> from openmfd.devices import (
    ...     CompleteDeviceConfiguration,
    ...     DeviceConfiguration,
    ...     CasingConfiguration,
    ...     ArrayConfiguration,
    ...     PDMSConfiguration,
    ...     WaferMaskConfiguration,
    ...     build_device_layer
    ... )
    >>> from openmfd.geometry import WellConfiguration, ChannelConfiguration
    >>>
    >>> # Create complete configuration
    >>> config = CompleteDeviceConfiguration(
    ...     device=DeviceConfiguration(
    ...         casing=CasingConfiguration(x=18, y=9),
    ...         wells_config=WellConfiguration(radius=2.5, positions=[(4.5, 0), (-4.5, 0)]),
    ...         channels_config=ChannelConfiguration(length=6.3, width=0.01, num_channels=83),
    ...         dxf=True
    ...     ),
    ...     array=ArrayConfiguration(rows=6, columns=8),
    ...     pdms=PDMSConfiguration(cure_temp=100),
    ...     wafer_mask=WaferMaskConfiguration(wafer_size=150, flat_length=57.5)
    ... )
    >>>
    >>> # Build complete device layer
    >>> result = build_device_layer(config, alignment='full')
    >>> wafer_mask = result['wafer_mask']
    """
    result = {}

    # Step 1: Assemble single device unit
    # Device is centered at origin (not in casing) for use with create_device_array
    device = assemble_device(config.device, center_in_casing=False)
    result["device"] = device

    # Step 2: Create array if configured
    if config.has_array():
        array = create_device_array(device, **_build_array_kwargs(config, alignment))
        result["array"] = array
    else:
        # No array, just use single device (center it in casing for standalone use)
        array = assemble_device(config.device, center_in_casing=True)
        result["array"] = array

    # Step 3: Add decorations (text, outline)
    decorated = array

    # Add text annotations
    if config.text_annotations:
        text_parts = [
            _build_text_annotation_geometry(text_config) for text_config in config.text_annotations
        ]

        if text_parts:
            decorated = solid.union()(decorated, *text_parts)

    # Add outline
    if config.has_outline():
        outline = _build_outline_geometry(config)
        decorated = solid.union()(decorated, outline)

    result["decorated"] = decorated

    # Step 4: Apply PDMS scaling if configured
    if config.has_pdms_scaling():
        assert config.pdms is not None
        scale_factor = config.pdms.scale_factor()
        scaled = solid.scale([scale_factor, scale_factor])(decorated)
        result["scaled"] = scaled
    else:
        scaled = decorated
        result["scaled"] = scaled

    # Step 5: Create wafer mask if configured
    if config.has_wafer_mask():
        wafer_mask = create_wafer_mask(**_build_wafer_mask_kwargs(config, scaled))
        result["wafer_mask"] = wafer_mask
    else:
        result["wafer_mask"] = scaled

    return result


def build_device_stack(
    bottom_config: CompleteDeviceConfiguration,
    top_config: CompleteDeviceConfiguration,
) -> Dict[str, solid.OpenSCADObject]:
    """Build complete device stack (bottom + top layers) with all features.

    This function builds both bottom and top layers and creates an aligned
    layer combining both.

    Parameters
    ----------
    bottom_config : CompleteDeviceConfiguration
        Configuration for bottom layer (typically channels only).
    top_config : CompleteDeviceConfiguration
        Configuration for top layer (typically wells + chambers).

    Returns
    -------
    Dict[str, solid.OpenSCADObject]
        Dictionary containing:
        - 'bottom': Bottom layer wafer mask
        - 'top': Top layer wafer mask
        - 'aligned': Aligned layer (top + bottom)
        - 'single_bottom': Single bottom device
        - 'single_top': Single top device
        - 'single_aligned': Single aligned device

    Examples
    --------
    >>> # Build complete device stack
    >>> result = build_device_stack(bottom_config, top_config)
    >>> bottom_mask = result['bottom']
    >>> top_mask = result['top']
    >>> aligned_mask = result['aligned']
    """
    # Build bottom layer (solid alignment marks)
    bottom_result = build_device_layer(bottom_config, alignment="full")

    # Build top layer (hollow alignment marks)
    top_result = build_device_layer(top_config, alignment="hollow")

    # Create aligned layer (before wafer mask)
    bottom_array = bottom_result.get("array", bottom_result["device"])
    top_array = top_result.get("array", top_result["device"])
    aligned_array = solid.union()(top_array, bottom_array)

    # Apply PDMS scaling to aligned if configured
    if bottom_config.has_pdms_scaling():
        assert bottom_config.pdms is not None
        scale_factor = bottom_config.pdms.scale_factor()
        aligned_array = solid.scale([scale_factor, scale_factor])(aligned_array)

    # Create aligned wafer mask
    if bottom_config.has_wafer_mask():
        aligned_mask = create_wafer_mask(**_build_wafer_mask_kwargs(bottom_config, aligned_array))
    else:
        aligned_mask = aligned_array

    return {
        "bottom": bottom_result["wafer_mask"],
        "top": top_result["wafer_mask"],
        "aligned": aligned_mask,
        "single_bottom": bottom_result["device"],
        "single_top": top_result["device"],
        "single_aligned": solid.union()(top_result["device"], bottom_result["device"]),
    }
