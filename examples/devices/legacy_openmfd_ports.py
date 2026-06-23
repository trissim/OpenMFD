"""Rebuild legacy open-chamber designs with the OpenMFD API.

This script recreates the legacy 3-compartment, axon-guidance, and
myelination layouts using the refactored OpenMFD primitives. It emits:

- single/multi layer stacks
- wafer masks and wall outlines
- 3D insert assemblies using the same pin/skirt system as the newer
  2-compartment example

The output lands under ``designs/open_chamber/openmfd_legacy_ports``.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Callable

import solid
from solid.utils import union

from openmfd.devices import (
    OpenChamberSpec,
    PDMSConfiguration,
    build_open_chamber,
    create_device_array,
    create_glass_outline,
    create_multiline_text,
    create_wafer_mask,
    create_wafer_walls,
    crossed_diamond,
    linear_chain,
)
from openmfd.devices.text import TextLayoutContext
from openmfd.export import export_scad, render_stl_with_viewscad, scad_to_dxf
from openmfd.geometry import wells_pos_from_center_4
from openmfd.inserts import assemble_well_inserts
from openmfd.inserts.chamfer import deg_taper_len
from openmfd.inserts.config import (
    InsertConfiguration,
    PinConfiguration,
    SkirtConfiguration,
    TaperConfiguration,
)
from openmfd.inserts.pins import create_insert_holes

OUTPUT_ROOT = Path("./designs/open_chamber/openmfd_legacy_ports")

CURE_TEMP = 100
PDMS_SCALE = PDMSConfiguration(cure_temp=CURE_TEMP).scale_factor()
SHORT_CHANNEL_LENGTH = 0.3

WAFER_SIZE = 150
WAFER_FLAT_LEN = 57.5
WAFER_LINE_THICKNESS = 0.3
OUTER_MASK_THICKNESS = 3

WALL_HEIGHT = 10
WALL_THICKNESS = 7
WALL_PADX = 9
WALL_PADY = 9

GLASS_SIZE = [110, 74]
GLASS_ERROR = 4
OUTLINE_ALIGNMENT_THICKNESS = 1

INSERT_PIN_OFFSET = -0.5
CHAMBER_HOLE_DIMS = (2.0, 2.0)
PIN_DIMS = (1.85, 1.85)
PIN_HEIGHT = 0.14
PIN_INNER_HEIGHT = 2.0
INSERT_OUTER_TAPER = TaperConfiguration(height=3.8, degrees=16, extra_length=0.3, segments=20)
AXON_INSERT_OUTER_TAPER = TaperConfiguration(height=2.0, degrees=16, extra_length=0.3, segments=20)
INSERT_INNER_TAPER = None
INSERT_PERIMETER_GAP = INSERT_OUTER_TAPER.extra_length

# Lock-and-key squares are axis-aligned by default (channels run along the
# x-axis for the linear three-compartment chain). The crossed-diamond devices
# (myelination, axon guidance) get a final 45 deg rotation, so their channels
# run diagonally - the square holes and matching pins must be rotated 45 deg to
# stay aligned with those channels.
DIAMOND_PIN_ROTATION = 45.0


def make_pin_config(rotation: float = 0.0) -> PinConfiguration:
    """Build the shared pin configuration with an optional square rotation."""
    return PinConfiguration(
        dims=PIN_DIMS,
        height=PIN_HEIGHT,
        inner_height=PIN_INNER_HEIGHT,
        offset=0.0,
        hole_dims=CHAMBER_HOLE_DIMS,
        rotation=rotation,
    )


SKIRT_CONFIG = SkirtConfiguration(
    thickness1=0.75,
    height1=0.66,
    empty1=0.3,
    thickness2=0.8,
    height2=0.04,
)


def save_geometry(
    geometry: solid.OpenSCADObject,
    output_dir: Path,
    name: str,
    *,
    make_dxf: bool = True,
    make_stl: bool = False,
) -> Path:
    """Export a geometry to SCAD and optional DXF/STL."""
    output_dir.mkdir(parents=True, exist_ok=True)
    scad_path = output_dir / f"{name}.scad"
    export_scad(geometry, scad_path)
    if make_dxf:
        scad_to_dxf(scad_path)
    if make_stl:
        render_stl_with_viewscad(geometry, output_dir / f"{name}.stl")
    return scad_path


def scale_xy(geometry: solid.OpenSCADObject, scale: float) -> solid.OpenSCADObject:
    if scale == 1.0:
        return geometry
    return solid.scale([scale, scale])(geometry)


def inset_toward_origin(
    position: tuple[float, float] | list[float],
    inset: float = INSERT_PIN_OFFSET,
) -> tuple[float, float]:
    """Move a lock/pin position along its radial device arm.

    The current two-compartment preset stores already-offset lock positions
    rather than relying on the older scalar x/y offset. This helper generalizes
    that convention to diagonal layouts.
    """
    x, y = float(position[0]), float(position[1])
    radius = math.hypot(x, y)
    if radius == 0.0:
        return (x, y)
    adjusted_radius = radius + inset
    if adjusted_radius <= 0.0:
        raise ValueError(f"pin inset {inset} collapses position {(x, y)}")
    scale = adjusted_radius / radius
    return (x * scale, y * scale)


def inset_positions_toward_origin(
    positions: list[tuple[float, float]] | list[list[float]],
) -> list[tuple[float, float]]:
    return [inset_toward_origin(position) for position in positions]


def unit_center_offsets(
    dims: list[float],
    grid_size: list[int],
) -> list[tuple[float, float]]:
    rows, cols = grid_size
    return [
        (row * dims[0] + dims[0] / 2.0, col * dims[1] + dims[1] / 2.0)
        for col in range(cols)
        for row in range(rows)
    ]


def absolute_pin_positions(
    local_positions: list[tuple[float, float]],
    dims: list[float],
    grid_size: list[int],
) -> list[tuple[float, float]]:
    return [
        (center_x + local_x, center_y + local_y)
        for center_x, center_y in unit_center_offsets(dims, grid_size)
        for local_x, local_y in local_positions
    ]


def make_cure_text(
    grid_size: list[int],
    dims: list[float],
    *,
    offset_y: float | None = None,
) -> solid.OpenSCADObject:
    """Create a standardized cure-temperature note."""
    if offset_y is None:
        offset_y = -(grid_size[1] + 3) * dims[1] / 2.0
    context = TextLayoutContext.from_fields(
        grid_size=grid_size,
        dims=dims,
        size=2.0,
        offset_y=offset_y,
    )
    return create_multiline_text(
        [f"Cure at {CURE_TEMP}C", "Use 60mL of Sylgard 184 in 1:10 ratio"],
        context,
    )


def build_device_function(
    footprint_builder: Callable[..., solid.OpenSCADObject],
    *,
    well_gap: float,
    chan_l: float,
    chan_w: float,
    chan_gap: float,
    num_chans: int,
    chamber_width: float,
    add_channels: bool = False,
) -> Callable[..., tuple[tuple[solid.OpenSCADObject, None], None, None]]:
    """Wrap a footprint builder so it matches the insert API contract."""

    def _device_function(
        *,
        well_rad: float,
        chan_l: float,
        chamber_width: float,
        add_chambers: bool,
    ) -> tuple[tuple[solid.OpenSCADObject, None], None, None]:
        geometry = footprint_builder(
            well_gap=well_gap,
            well_rad=well_rad,
            chan_l=chan_l,
            chan_w=chan_w,
            chan_gap=chan_gap,
            num_chans=num_chans,
            chamber_width=chamber_width,
            add_channels=add_channels,
            add_chambers=add_chambers,
        )
        return (geometry, None), None, None

    return _device_function


def build_insert_config(
    *,
    well_rad: float,
    chan_l: float,
    chamber_width: float,
    outer_taper: TaperConfiguration = INSERT_OUTER_TAPER,
) -> InsertConfiguration:
    """Create the common insert configuration used by all three designs."""
    return InsertConfiguration(
        outer_taper=outer_taper,
        inner_taper=INSERT_INNER_TAPER,
        well_radius=well_rad,
        channel_length=chan_l,
        chamber_width=chamber_width,
        add_chambers=True,
    )


def constant_gap_insert_surface(
    surface: solid.OpenSCADObject,
    *,
    outer_taper: TaperConfiguration = INSERT_OUTER_TAPER,
) -> solid.OpenSCADObject:
    """Create an insert top footprint that chamfers to a constant perimeter gap."""
    taper_spread = deg_taper_len(outer_taper.height, outer_taper.degrees)
    top_inset = taper_spread + INSERT_PERIMETER_GAP
    return solid.offset(r=-top_inset, segments=64)(surface)


def constant_gap_insert_device_function(
    surface: solid.OpenSCADObject,
    *,
    outer_taper: TaperConfiguration = INSERT_OUTER_TAPER,
) -> Callable[..., tuple[tuple[solid.OpenSCADObject, None], None, None]]:
    """Wrap a precomputed insert support surface for chamfered insert generation."""

    def _device_function(
        *,
        well_rad: float,
        chan_l: float,
        chamber_width: float,
        add_chambers: bool,
    ) -> tuple[tuple[solid.OpenSCADObject, None], None, None]:
        return (constant_gap_insert_surface(surface, outer_taper=outer_taper), None), None, None

    return _device_function


def save_regular_layer_stack(
    *,
    output_dir: Path,
    base_name: str,
    single_bottom: solid.OpenSCADObject,
    single_top: solid.OpenSCADObject,
    multi_bottom: solid.OpenSCADObject,
    multi_top: solid.OpenSCADObject,
    grid_size: list[int],
    dims: list[float],
    text_offset: float | None = None,
) -> None:
    """Save a feature stack for a regular rectangular array."""
    single_aligned = union()(single_top, single_bottom)
    multi_aligned = union()(multi_top, multi_bottom)

    outline = create_glass_outline(
        [g - GLASS_ERROR for g in GLASS_SIZE],
        WALL_THICKNESS,
        grid_size,
        dims,
        alignment_offset=None,
        alignment_groove_thickness=OUTLINE_ALIGNMENT_THICKNESS,
    )
    text = make_cure_text(grid_size, dims, offset_y=text_offset)

    multi_bottom_feature = union()(multi_bottom, text)
    multi_top_feature = union()(multi_top, outline)
    multi_aligned_feature = union()(multi_top_feature, multi_bottom_feature)

    multi_bottom_feature = scale_xy(multi_bottom_feature, PDMS_SCALE)
    multi_top_feature = scale_xy(multi_top_feature, PDMS_SCALE)
    multi_aligned_feature = scale_xy(multi_aligned_feature, PDMS_SCALE)

    multi_bottom_final = create_wafer_mask(
        WAFER_SIZE,
        WAFER_FLAT_LEN,
        multi_bottom_feature,
        grid_size,
        dims,
        wafer_line_thickness=WAFER_LINE_THICKNESS,
        outer_mask_thickness=OUTER_MASK_THICKNESS,
        alignment_offset=None,
        shrinkage_scale=PDMS_SCALE,
    )
    multi_top_final = create_wafer_mask(
        WAFER_SIZE,
        WAFER_FLAT_LEN,
        multi_top_feature,
        grid_size,
        dims,
        wafer_line_thickness=WAFER_LINE_THICKNESS,
        outer_mask_thickness=OUTER_MASK_THICKNESS,
        alignment_offset=None,
        shrinkage_scale=PDMS_SCALE,
    )
    multi_aligned_final = create_wafer_mask(
        WAFER_SIZE,
        WAFER_FLAT_LEN,
        multi_aligned_feature,
        grid_size,
        dims,
        wafer_line_thickness=WAFER_LINE_THICKNESS,
        outer_mask_thickness=OUTER_MASK_THICKNESS,
        alignment_offset=None,
        shrinkage_scale=PDMS_SCALE,
    )

    save_geometry(single_bottom, output_dir, f"{base_name}_single_bottom")
    save_geometry(single_top, output_dir, f"{base_name}_single_top")
    save_geometry(single_aligned, output_dir, f"{base_name}_single_aligned")
    save_geometry(multi_bottom, output_dir, f"{base_name}_multi_bottom")
    save_geometry(multi_top, output_dir, f"{base_name}_multi_top")
    save_geometry(multi_aligned, output_dir, f"{base_name}_multi_aligned")
    save_geometry(multi_bottom_final, output_dir, f"{base_name}_bottom")
    save_geometry(multi_top_final, output_dir, f"{base_name}_top")
    save_geometry(multi_aligned_final, output_dir, f"{base_name}_aligned")


def build_three_compartment(
    output_dir: Path,
    *,
    make_stl: bool = False,
    base_name: str = "three_compartment",
    microchannel_length: float | None = None,
) -> None:
    well_gap = 4.5
    well_rad = 6.94 / 2.0
    legacy_chamber_len_until = (well_gap - well_rad) * 2.0
    chan_l = microchannel_length if microchannel_length is not None else legacy_chamber_len_until
    chan_gap = 0.01
    chan_w = 0.01
    num_chans = int(well_rad / (chan_gap + chan_w))
    use_fixed_chamber_reach = microchannel_length is not None

    dims = [9 * 3, 9, 0]
    grid_size = [4, 8]
    # Lock-and-key holes/pins sit at every reservoir well. The linear chain
    # produces three wells along the x-axis: the two outer wells at
    # +/- 2 * well_gap and the shared central hub well at the origin.
    insert_positions = inset_positions_toward_origin(
        [
            (-2.0 * well_gap, 0.0),
            (0.0, 0.0),
            (2.0 * well_gap, 0.0),
        ]
    )
    single_pin_positions = absolute_pin_positions(insert_positions, dims, [1, 1])
    multi_pin_positions = absolute_pin_positions(insert_positions, dims, grid_size)
    # Linear chain: channels run along x, so axis-aligned squares already
    # align with the channels.
    pin_rotation = 0.0
    pin_config = make_pin_config(pin_rotation)

    def footprint_builder(
        *,
        well_gap: float,
        well_rad: float,
        chan_l: float,
        chan_w: float,
        chan_gap: float,
        num_chans: int,
        chamber_width: float,
        add_channels: bool,
        add_chambers: bool,
    ) -> solid.OpenSCADObject:
        # Narrow chamber (channel-array width) + chamber reaching only to
        # the legacy reach keeps the three reservoir wells round and distinct,
        # while allowing 300 um channel variants to keep chambers at the wells.
        chamber_len_until = legacy_chamber_len_until if use_fixed_chamber_reach else chan_l
        spec = OpenChamberSpec(
            well_gap=well_gap,
            well_rad=well_rad,
            chan_l=chan_l,
            chan_w=chan_w,
            chan_gap=chan_gap,
            num_chans=num_chans,
            chamber_len_until=chamber_len_until,
        )
        unit = build_open_chamber(
            spec,
            add_wells=True,
            add_channels=add_channels,
            add_chambers=add_chambers,
        )
        return linear_chain(unit, well_gap, count=2)

    single_bottom = footprint_builder(
        well_gap=well_gap,
        well_rad=well_rad,
        chan_l=chan_l,
        chan_w=chan_w,
        chan_gap=chan_gap,
        num_chans=num_chans,
        chamber_width=well_rad * 2,
        add_channels=True,
        add_chambers=True,
    )
    single_top = solid.difference()(
        footprint_builder(
            well_gap=well_gap,
            well_rad=well_rad,
            chan_l=chan_l,
            chan_w=chan_w,
            chan_gap=chan_gap,
            num_chans=num_chans,
            chamber_width=well_rad * 2,
            add_channels=False,
            add_chambers=True,
        ),
        create_insert_holes(
            insert_positions,
            CHAMBER_HOLE_DIMS,
            offset=0.0,
            rotation=pin_rotation,
        ),
    )

    multi_bottom = create_device_array(
        single_bottom,
        dims,
        grid_size,
        dxf=True,
        alignment="full",
        units_from_center=None,
        alignment_offset=None,
        alignment_mark_size=1.0,
    )
    multi_top = create_device_array(
        single_top,
        dims,
        grid_size,
        dxf=True,
        alignment="hollow",
        units_from_center=None,
        alignment_offset=None,
        alignment_mark_size=1.0,
    )

    save_regular_layer_stack(
        output_dir=output_dir,
        base_name=base_name,
        single_bottom=single_bottom,
        single_top=single_top,
        multi_bottom=multi_bottom,
        multi_top=multi_top,
        grid_size=grid_size,
        dims=dims,
    )

    insert_surface = footprint_builder(
        well_gap=well_gap,
        well_rad=well_rad,
        chan_l=chan_l,
        chan_w=chan_w,
        chan_gap=chan_gap,
        num_chans=num_chans,
        chamber_width=well_rad * 2,
        add_channels=False,
        add_chambers=True,
    )
    insert_device_function = constant_gap_insert_device_function(insert_surface)
    insert_config = build_insert_config(
        well_rad=well_rad,
        chan_l=chan_l,
        chamber_width=well_rad * 2,
    )
    single_insert = assemble_well_inserts(
        device_function=insert_device_function,
        insert_config=insert_config,
        pin_config=pin_config,
        skirt_config=SKIRT_CONFIG,
        dims=dims,
        grid_size=[1, 1],
        well_positions=single_pin_positions,
        alignment_offset=None,
        pdms_scale=PDMS_SCALE,
    )
    multi_insert = assemble_well_inserts(
        device_function=insert_device_function,
        insert_config=insert_config,
        pin_config=pin_config,
        skirt_config=SKIRT_CONFIG,
        dims=dims,
        grid_size=grid_size,
        well_positions=multi_pin_positions,
        alignment_offset=None,
        pdms_scale=PDMS_SCALE,
    )

    save_geometry(
        single_insert, output_dir, f"{base_name}_single_insert", make_dxf=False, make_stl=make_stl
    )
    save_geometry(
        multi_insert, output_dir, f"{base_name}_wells_insert", make_dxf=False, make_stl=make_stl
    )

    _, _, wall_single = create_wafer_walls(
        WAFER_SIZE,
        WALL_THICKNESS,
        [1, 1],
        dims,
        height=WALL_HEIGHT,
        segments=256,
        make_inner=False,
        padx=WALL_PADX,
        pady=WALL_PADY,
    )
    _, _, wall_multi = create_wafer_walls(
        WAFER_SIZE,
        WALL_THICKNESS,
        grid_size,
        dims,
        height=WALL_HEIGHT,
        segments=256,
        make_inner=False,
        padx=WALL_PADX,
        pady=WALL_PADY,
    )
    save_geometry(
        wall_single, output_dir, f"wall_single_{base_name}", make_dxf=False, make_stl=make_stl
    )
    save_geometry(wall_multi, output_dir, f"wall_{base_name}", make_dxf=False, make_stl=make_stl)


def build_myelination(
    output_dir: Path,
    *,
    make_stl: bool = False,
    base_name: str = "myelination",
    microchannel_length: float | None = None,
) -> None:
    well_gap = 6.36
    well_rad = 6.94 / 2.0
    legacy_chamber_len_until = (well_gap - well_rad) * 2.0
    chan_l = microchannel_length if microchannel_length is not None else legacy_chamber_len_until
    chan_gap = 0.01
    chan_w = 0.01
    num_chans = int(well_rad / (chan_gap + chan_w))
    oligo_channel_width = 0.1
    use_fixed_chamber_reach = microchannel_length is not None

    dims = [9 * 2, 9 * 2, 0]
    grid_size = [6, 4]
    # The crossed-diamond composition places the four wells on the diagonals
    # at distance ``well_gap`` from the origin, i.e. at
    # (+/- well_gap / sqrt(2), +/- well_gap / sqrt(2)). Put a lock-and-key
    # hole/pin at each of those four wells.
    insert_positions = inset_positions_toward_origin(
        wells_pos_from_center_4(well_gap / math.sqrt(2.0))
    )
    single_pin_positions = absolute_pin_positions(insert_positions, dims, [1, 1])
    multi_pin_positions = absolute_pin_positions(insert_positions, dims, grid_size)
    # Crossed-diamond: the whole unit is rotated 45 deg, so the channels run
    # diagonally. Rotate the square holes/pins 45 deg to align with them.
    pin_rotation = DIAMOND_PIN_ROTATION
    pin_config = make_pin_config(pin_rotation)

    def footprint_builder(
        *,
        well_gap: float,
        well_rad: float,
        chan_l: float,
        chan_w: float,
        chan_gap: float,
        num_chans: int,
        chamber_width: float,
        add_channels: bool,
        add_chambers: bool,
    ) -> solid.OpenSCADObject:
        # Primary arm: full microchannel array bridging two wells. The chamber
        # reaches the legacy reservoir span. For the legacy reconstruction the
        # channel array is half that reach; for 300 um variants, ``chan_l`` is
        # the actual microchannel-array length.
        primary_chan_l = chan_l if use_fixed_chamber_reach else chan_l / 2.0
        chamber_len_until = legacy_chamber_len_until if use_fixed_chamber_reach else chan_l
        open_chamber = build_open_chamber(
            OpenChamberSpec(
                well_gap=well_gap,
                well_rad=well_rad,
                chan_l=primary_chan_l,
                chan_w=chan_w,
                chan_gap=chan_gap,
                num_chans=num_chans,
                chamber_len_until=chamber_len_until,
            ),
            add_wells=True,
            add_channels=add_channels,
            add_chambers=add_chambers,
        )
        # Perpendicular arm: a single thin "oligo" channel between two wells,
        # represented by a narrow chamber that bridges centre to well.
        oligo_chamber = build_open_chamber(
            OpenChamberSpec(
                well_gap=well_gap,
                well_rad=well_rad,
                chan_l=0.0,
                chan_w=oligo_channel_width,
                chan_gap=oligo_channel_width / 2.0,
                num_chans=1,
                chamber_len_until=chamber_len_until,
            ),
            add_wells=True,
            add_channels=add_channels,
            add_chambers=add_chambers,
        )
        return crossed_diamond(open_chamber, oligo_chamber)

    single_bottom = footprint_builder(
        well_gap=well_gap,
        well_rad=well_rad,
        chan_l=chan_l,
        chan_w=chan_w,
        chan_gap=chan_gap,
        num_chans=num_chans,
        chamber_width=well_rad * 2,
        add_channels=True,
        add_chambers=True,
    )
    single_top = solid.difference()(
        footprint_builder(
            well_gap=well_gap,
            well_rad=well_rad,
            chan_l=chan_l,
            chan_w=chan_w,
            chan_gap=chan_gap,
            num_chans=num_chans,
            chamber_width=well_rad * 2,
            add_channels=False,
            add_chambers=True,
        ),
        create_insert_holes(
            insert_positions,
            CHAMBER_HOLE_DIMS,
            offset=0.0,
            rotation=pin_rotation,
        ),
    )

    multi_bottom = create_device_array(
        single_bottom,
        dims,
        grid_size,
        dxf=True,
        alignment="full",
        units_from_center=None,
        alignment_offset=None,
        alignment_mark_size=1.0,
    )
    multi_top = create_device_array(
        single_top,
        dims,
        grid_size,
        dxf=True,
        alignment="hollow",
        units_from_center=None,
        alignment_offset=None,
        alignment_mark_size=1.0,
    )

    save_regular_layer_stack(
        output_dir=output_dir,
        base_name=base_name,
        single_bottom=single_bottom,
        single_top=single_top,
        multi_bottom=multi_bottom,
        multi_top=multi_top,
        grid_size=grid_size,
        dims=dims,
    )

    def insert_surface_builder() -> solid.OpenSCADObject:
        primary_chan_l = chan_l if use_fixed_chamber_reach else chan_l / 2.0
        chamber_len_until = legacy_chamber_len_until if use_fixed_chamber_reach else chan_l
        primary = build_open_chamber(
            OpenChamberSpec(
                well_gap=well_gap,
                well_rad=well_rad,
                chan_l=primary_chan_l,
                chan_w=chan_w,
                chan_gap=chan_gap,
                num_chans=num_chans,
                chamber_len_until=chamber_len_until,
            ),
            add_wells=True,
            add_channels=False,
            add_chambers=True,
        )
        oligo_wells = build_open_chamber(
            OpenChamberSpec(
                well_gap=well_gap,
                well_rad=well_rad,
                chan_l=0.0,
                chan_w=oligo_channel_width,
                chan_gap=oligo_channel_width / 2.0,
                num_chans=1,
                chamber_len_until=chamber_len_until,
            ),
            add_wells=True,
            add_channels=False,
            add_chambers=False,
        )
        return crossed_diamond(primary, oligo_wells)

    insert_device_function = constant_gap_insert_device_function(insert_surface_builder())
    insert_config = build_insert_config(
        well_rad=well_rad,
        chan_l=chan_l,
        chamber_width=well_rad * 2,
    )
    single_insert = assemble_well_inserts(
        device_function=insert_device_function,
        insert_config=insert_config,
        pin_config=pin_config,
        skirt_config=SKIRT_CONFIG,
        dims=dims,
        grid_size=[1, 1],
        well_positions=single_pin_positions,
        alignment_offset=None,
        pdms_scale=PDMS_SCALE,
    )
    multi_insert = assemble_well_inserts(
        device_function=insert_device_function,
        insert_config=insert_config,
        pin_config=pin_config,
        skirt_config=SKIRT_CONFIG,
        dims=dims,
        grid_size=grid_size,
        well_positions=multi_pin_positions,
        alignment_offset=None,
        pdms_scale=PDMS_SCALE,
    )

    save_geometry(
        single_insert, output_dir, f"{base_name}_single_insert", make_dxf=False, make_stl=make_stl
    )
    save_geometry(
        multi_insert, output_dir, f"{base_name}_wells_insert", make_dxf=False, make_stl=make_stl
    )

    _, _, wall_single = create_wafer_walls(
        WAFER_SIZE,
        WALL_THICKNESS,
        [1, 1],
        dims,
        height=WALL_HEIGHT,
        segments=256,
        make_inner=False,
        padx=WALL_PADX,
        pady=WALL_PADY,
    )
    _, _, wall_multi = create_wafer_walls(
        WAFER_SIZE,
        WALL_THICKNESS,
        grid_size,
        dims,
        height=WALL_HEIGHT,
        segments=256,
        make_inner=False,
        padx=WALL_PADX,
        pady=WALL_PADY,
    )
    save_geometry(
        wall_single, output_dir, f"wall_single_{base_name}", make_dxf=False, make_stl=make_stl
    )
    save_geometry(wall_multi, output_dir, f"wall_{base_name}", make_dxf=False, make_stl=make_stl)


def build_axon_guidance(
    output_dir: Path,
    *,
    make_stl: bool = False,
    base_name: str = "axon_guidance",
    exposed_channel_length: float | None = None,
) -> None:
    # Faithful port of the legacy ``closed_gradient.py`` device.
    well_gap = 6.36
    well_rad = 6.94 / 2.0
    # The crossing channels span the full well gap (not (well_gap-well_rad)*2),
    # and the array is deliberately thinned (well_rad / 1.5) so the central
    # closed chamber stays small and the four microchannel arms remain exposed.
    chan_gap = 0.01
    chan_w = 0.01
    num_chans = int((well_rad / 1.5) / (chan_gap + chan_w))
    width_all_channels = num_chans * chan_w + (num_chans - 1) * chan_gap
    chan_l = well_gap
    if exposed_channel_length is not None:
        chan_l = width_all_channels + exposed_channel_length * 2.0
    use_fixed_chamber_reach = exposed_channel_length is not None

    dims = [9 * 2, 9 * 2, 0]
    grid_size = [6, 4]
    # The crossed-diamond composition places the four wells on the diagonals
    # at distance ``well_gap`` from the origin, i.e. at
    # (+/- well_gap / sqrt(2), +/- well_gap / sqrt(2)). Put a lock-and-key
    # hole/pin at each of those four wells.
    insert_positions = inset_positions_toward_origin(
        wells_pos_from_center_4(well_gap / math.sqrt(2.0))
    )
    single_pin_positions = absolute_pin_positions(insert_positions, dims, [1, 1])
    multi_pin_positions = absolute_pin_positions(insert_positions, dims, grid_size)
    # Crossed-diamond: the whole unit is rotated 45 deg, so the channels run
    # diagonally. Rotate the square holes/pins 45 deg to align with them.
    pin_rotation = DIAMOND_PIN_ROTATION
    pin_config = make_pin_config(pin_rotation)

    def footprint_builder(
        *,
        well_gap: float,
        well_rad: float,
        chan_l: float,
        chan_w: float,
        chan_gap: float,
        num_chans: int,
        chamber_width: float,
        add_channels: bool,
        add_chambers: bool,
        add_center_chamber: bool = True,
    ) -> solid.OpenSCADObject:
        # Axon guidance: a symmetric four-well diamond - both crossing arms
        # carry a full microchannel array so axons can be guided between any
        # pair of compartments. The (narrow) channel-array chamber width keeps
        # all four wells round and distinct.
        arm_chan_l = chan_l if use_fixed_chamber_reach else chan_l * 0.9
        chamber_len_until = well_gap if use_fixed_chamber_reach else chan_l
        arm = build_open_chamber(
            OpenChamberSpec(
                well_gap=well_gap,
                well_rad=well_rad,
                chan_l=arm_chan_l,
                chan_w=chan_w,
                chan_gap=chan_gap,
                num_chans=num_chans,
                chamber_len_until=chamber_len_until,
            ),
            add_wells=True,
            add_channels=add_channels,
            add_chambers=add_chambers,
        )
        # Central closed chamber: the small reservoir at the middle of the four
        # wells where guided axons converge. Its side equals the width of the
        # microchannel array (num_chans channels + gaps), so it is deliberately
        # small - the long (chan_l * 0.9) channel arms remain exposed between
        # this central square and each well. Treated as a chamber feature so it
        # appears wherever the diffusion chambers do.
        central_chamber = None
        if add_chambers and add_center_chamber:
            central_chamber = solid.square([width_all_channels, width_all_channels], center=True)
        return crossed_diamond(arm, arm, center=central_chamber)

    single_bottom = footprint_builder(
        well_gap=well_gap,
        well_rad=well_rad,
        chan_l=chan_l,
        chan_w=chan_w,
        chan_gap=chan_gap,
        num_chans=num_chans,
        chamber_width=well_rad * 2,
        add_channels=True,
        add_chambers=True,
    )
    single_top = solid.difference()(
        footprint_builder(
            well_gap=well_gap,
            well_rad=well_rad,
            chan_l=chan_l,
            chan_w=chan_w,
            chan_gap=chan_gap,
            num_chans=num_chans,
            chamber_width=well_rad * 2,
            add_channels=False,
            add_chambers=True,
        ),
        create_insert_holes(
            insert_positions,
            CHAMBER_HOLE_DIMS,
            offset=0.0,
            rotation=pin_rotation,
        ),
    )

    multi_bottom = create_device_array(
        single_bottom,
        dims,
        grid_size,
        dxf=True,
        alignment="full",
        units_from_center=None,
        alignment_offset=None,
        alignment_mark_size=1.0,
    )
    multi_top = create_device_array(
        single_top,
        dims,
        grid_size,
        dxf=True,
        alignment="hollow",
        units_from_center=None,
        alignment_offset=None,
        alignment_mark_size=1.0,
    )

    save_regular_layer_stack(
        output_dir=output_dir,
        base_name=base_name,
        single_bottom=single_bottom,
        single_top=single_top,
        multi_bottom=multi_bottom,
        multi_top=multi_top,
        grid_size=grid_size,
        dims=dims,
    )

    insert_surface = footprint_builder(
        well_gap=well_gap,
        well_rad=well_rad,
        chan_l=chan_l,
        chan_w=chan_w,
        chan_gap=chan_gap,
        num_chans=num_chans,
        chamber_width=well_rad * 2,
        add_channels=False,
        add_chambers=True,
        add_center_chamber=False,
    )
    insert_device_function = constant_gap_insert_device_function(
        insert_surface,
        outer_taper=AXON_INSERT_OUTER_TAPER,
    )
    insert_config = build_insert_config(
        well_rad=well_rad,
        chan_l=chan_l,
        chamber_width=well_rad * 2,
        outer_taper=AXON_INSERT_OUTER_TAPER,
    )
    single_insert = assemble_well_inserts(
        device_function=insert_device_function,
        insert_config=insert_config,
        pin_config=pin_config,
        skirt_config=SKIRT_CONFIG,
        dims=dims,
        grid_size=[1, 1],
        well_positions=single_pin_positions,
        alignment_offset=None,
        pdms_scale=PDMS_SCALE,
    )
    multi_insert = assemble_well_inserts(
        device_function=insert_device_function,
        insert_config=insert_config,
        pin_config=pin_config,
        skirt_config=SKIRT_CONFIG,
        dims=dims,
        grid_size=grid_size,
        well_positions=multi_pin_positions,
        alignment_offset=None,
        pdms_scale=PDMS_SCALE,
    )
    save_geometry(
        single_insert, output_dir, f"{base_name}_single_insert", make_dxf=False, make_stl=make_stl
    )
    save_geometry(
        multi_insert, output_dir, f"{base_name}_wells_insert", make_dxf=False, make_stl=make_stl
    )

    _, _, wall_single = create_wafer_walls(
        WAFER_SIZE,
        WALL_THICKNESS,
        [1, 1],
        dims,
        height=WALL_HEIGHT,
        segments=256,
        make_inner=False,
        padx=WALL_PADX,
        pady=WALL_PADY,
    )
    _, _, wall_multi = create_wafer_walls(
        WAFER_SIZE,
        WALL_THICKNESS,
        grid_size,
        dims,
        height=WALL_HEIGHT,
        segments=256,
        make_inner=False,
        padx=WALL_PADX,
        pady=WALL_PADY,
    )
    save_geometry(
        wall_single, output_dir, f"wall_single_{base_name}", make_dxf=False, make_stl=make_stl
    )
    save_geometry(wall_multi, output_dir, f"wall_{base_name}", make_dxf=False, make_stl=make_stl)


def build_three_compartment_300um(output_dir: Path, *, make_stl: bool = False) -> None:
    build_three_compartment(
        output_dir,
        make_stl=make_stl,
        base_name="three_compartment_300um",
        microchannel_length=SHORT_CHANNEL_LENGTH,
    )


def build_myelination_300um(output_dir: Path, *, make_stl: bool = False) -> None:
    build_myelination(
        output_dir,
        make_stl=make_stl,
        base_name="myelination_300um",
        microchannel_length=SHORT_CHANNEL_LENGTH,
    )


def build_axon_guidance_300um(output_dir: Path, *, make_stl: bool = False) -> None:
    build_axon_guidance(
        output_dir,
        make_stl=make_stl,
        base_name="axon_guidance_300um",
        exposed_channel_length=SHORT_CHANNEL_LENGTH,
    )


DESIGN_BUILDERS: dict[str, Callable[..., None]] = {
    "three_compartment": build_three_compartment,
    "three_compartment_300um": build_three_compartment_300um,
    "axon_guidance": build_axon_guidance,
    "axon_guidance_300um": build_axon_guidance_300um,
    "myelination": build_myelination,
    "myelination_300um": build_myelination_300um,
}


def run_generation(*, design: str = "all", make_stl: bool = False) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    if design != "all" and design not in DESIGN_BUILDERS:
        raise ValueError(f"Unknown design {design!r}")

    for key, builder in DESIGN_BUILDERS.items():
        if design != "all" and design != key:
            continue
        output_dir = OUTPUT_ROOT / key
        builder(output_dir, make_stl=make_stl)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild legacy open-chamber layouts with the OpenMFD API"
    )
    parser.add_argument(
        "--design",
        choices=[*DESIGN_BUILDERS, "all"],
        default="all",
    )
    parser.add_argument(
        "--stl",
        action="store_true",
        help="Also render STL files for inserts and walls",
    )
    args = parser.parse_args()
    run_generation(design=args.design, make_stl=args.stl)


if __name__ == "__main__":
    main()
