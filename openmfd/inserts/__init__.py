"""3D printed insert generation for microfluidic devices.

This module provides functionality for generating 3D printed well inserts with
chamfered/tapered walls, alignment pins, and sealing skirts. These inserts enable
easier pipetting access, precise alignment, and better sealing for microfluidic devices.
"""

from openmfd.core import derive_public_exports

from .config import (
    CompleteInsertConfiguration,
    InsertConfiguration,
    PinConfiguration,
    SkirtConfiguration,
    TaperConfiguration,
)

from .chamfer import (
    deg_taper_len,
    chamfer_extrude_wrapper,
)

from .wells import (
    build_insert,
    create_well_insert,
    create_well_insert_array,
    assemble_well_inserts,
)

from .pins import (
    create_insert_pin,
    create_pin_array,
)

from .skirts import (
    create_skirt_layer,
    create_dual_skirt,
)

__all__ = derive_public_exports(globals())
