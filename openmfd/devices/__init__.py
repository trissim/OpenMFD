"""Device-specific implementations and templates."""

from .config import (
    CasingConfiguration,
    ArrayConfiguration,
    OutlineConfiguration,
    WallConfiguration,
    DeviceConfiguration,
    CompleteDeviceConfiguration,
)

from .assembly import (
    assemble_device,
    assemble_unit,
    assemble_components_separately,
)

from .arrays import (
    create_device_array,
    create_device_array_from_config,
    compute_array_dimensions,
    center_array,
    create_partial_array,
    create_hollow_array,
)

from .outline import (
    create_outline,
    create_device_outline,
    compute_outline_dimensions,
    create_solid_outline,
    create_custom_outline,
)

from .walls import (
    create_wall,
    create_wafer_walls,
    create_device_walls,
)

__all__ = [
    # Config
    "CasingConfiguration",
    "ArrayConfiguration",
    "OutlineConfiguration",
    "WallConfiguration",
    "DeviceConfiguration",
    "CompleteDeviceConfiguration",
    # Assembly
    "assemble_device",
    "assemble_unit",
    "assemble_components_separately",
    # Arrays
    "create_device_array",
    "create_device_array_from_config",
    "compute_array_dimensions",
    "center_array",
    "create_partial_array",
    "create_hollow_array",
    # Outline
    "create_outline",
    "create_device_outline",
    "compute_outline_dimensions",
    "create_solid_outline",
    "create_custom_outline",
    # Walls
    "create_wall",
    "create_wafer_walls",
    "create_device_walls",
]

