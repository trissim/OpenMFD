"""Device-specific implementations and templates."""

from .alignment import (
    create_alignment_marks,
    create_alignment_target,
    create_crosshair_mark,
    create_custom_alignment_pattern,
    create_full_alignment_mark,
    create_single_L_mark,
    create_vernier_scale,
)
from .arrays import (
    center_array,
    compute_array_dimensions,
    create_device_array,
    create_device_array_from_config,
    create_hollow_array,
    create_partial_array,
)
from .assembly import (
    assemble_components_separately,
    assemble_device,
    assemble_unit,
)
from .config import (
    ArrayConfiguration,
    CasingConfiguration,
    CompleteDeviceConfiguration,
    DeviceConfiguration,
    OutlineConfiguration,
    WallConfiguration,
)
from .outline import (
    compute_outline_dimensions,
    create_custom_outline,
    create_device_outline,
    create_glass_outline,
    create_outline,
    create_solid_outline,
)
from .text import (
    create_centered_text,
    create_cure_temperature_text,
    create_date_stamp,
    create_device_label,
    create_multiline_text,
)
from .wafer import (
    compute_wafer_center,
    create_wafer,
    create_wafer_calibration_rings,
    create_wafer_holder,
    create_wafer_mask,
)
from .walls import (
    create_device_walls,
    create_wafer_walls,
    create_wall,
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
    "create_glass_outline",
    # Walls
    "create_wall",
    "create_wafer_walls",
    "create_device_walls",
    # Wafer
    "compute_wafer_center",
    "create_wafer",
    "create_wafer_mask",
    "create_wafer_holder",
    "create_wafer_calibration_rings",
    # Alignment
    "create_single_L_mark",
    "create_full_alignment_mark",
    "create_alignment_marks",
    "create_crosshair_mark",
    "create_vernier_scale",
    "create_alignment_target",
    "create_custom_alignment_pattern",
    # Text
    "create_centered_text",
    "create_multiline_text",
    "create_cure_temperature_text",
    "create_device_label",
    "create_date_stamp",
]
