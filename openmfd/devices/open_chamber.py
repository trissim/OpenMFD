"""Reusable open-chamber compartment unit shared across device layouts.

An *open chamber* is the canonical OpenMFD compartment unit: two reservoir
wells bridged by a central array of microchannels, with diffusion chambers
that fan out from the channel array toward each well.

The same unit is composed into the higher-order legacy layouts:

- two-compartment    : a single unit (the primary platform design)
- three-compartment  : a linear chain of units sharing a central hub well
  (:func:`linear_chain`)
- myelination /
  axon-guidance      : two units crossed at 90 degrees and rotated 45 degrees
  to form a four-well diamond with a crossing microchannel X
  (:func:`crossed_diamond`)

This module mirrors the geometry contract of the legacy ``make_open_chamber``
recipe so the ported layouts reproduce the validated originals:

- the chamber bridges from the channel array out to ``chamber_len_until``
  (defaulting to the channel length ``chan_l``), and
- the chamber spans the channel-array width unless ``chamber_width`` is given.

Keeping ``chamber_width`` at the (narrow) channel-array width is what keeps the
reservoir wells round and distinct - overriding it to the full well diameter
instead merges neighbouring wells into a single open pool.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import solid
from solid.utils import union

from openmfd.geometry import (
    make_chambers,
    make_channels,
    wells_pos_from_center_2,
    wells_top_bottom,
)
from openmfd.geometry.types import Measurements
from openmfd.geometry.wells import WellPatternContext


@dataclass(frozen=True)
class OpenChamberSpec:
    """Parameters describing a single open-chamber compartment unit.

    The two wells sit at ``(+/- well_gap, 0)``. A central array of
    ``num_chans`` microchannels (each ``chan_w`` wide, separated by
    ``chan_gap``) connects them, and two diffusion chambers fan out from the
    channel array toward each well.

    Attributes
    ----------
    well_gap : float
        Distance from the origin to each well centre.
    well_rad : float
        Well radius.
    chan_l : float
        Microchannel length (along the well-to-well axis).
    chan_w : float
        Width of an individual microchannel.
    chan_gap : float
        Gap between adjacent microchannels.
    num_chans : int
        Number of microchannels in the central array.
    chamber_len_until : float, optional
        Absolute distance from the origin the chamber extends to. If ``None``
        the chamber reaches ``chan_l`` (the legacy default).
    chamber_width : float, optional
        Override the chamber width. If ``None`` the chamber spans the
        channel-array width (which keeps the wells round and distinct).
    """

    well_gap: float
    well_rad: float
    chan_l: float
    chan_w: float = 0.01
    chan_gap: float = 0.01
    num_chans: int = 1
    chamber_len_until: Optional[float] = None
    chamber_width: Optional[float] = None

    @property
    def resolved_chamber_len_until(self) -> float:
        """Absolute distance the chamber bridges to from the origin."""
        if self.chamber_len_until is not None:
            return self.chamber_len_until
        return self.chan_l


def build_open_chamber(
    spec: OpenChamberSpec,
    *,
    add_wells: bool = True,
    add_channels: bool = True,
    add_chambers: bool = True,
) -> solid.OpenSCADObject:
    """Build a single two-well open-chamber unit centred on the origin.

    The channel array is always evaluated (it provides the measurements that
    size the chambers) but is only included in the returned geometry when
    ``add_channels`` is true. This mirrors the legacy ``make_open_chamber``
    contract where the bottom (channel) layer enables channels and the top
    (well/feature) layer disables them.

    Parameters
    ----------
    spec : OpenChamberSpec
        Geometry parameters for the unit.
    add_wells : bool, default=True
        Include the two reservoir wells.
    add_channels : bool, default=True
        Include the central microchannel array.
    add_chambers : bool, default=True
        Include the diffusion chambers bridging channels to wells.

    Returns
    -------
    solid.OpenSCADObject
        Union of the enabled components, a single connected body.
    """
    if spec.chan_l > 0:
        channels, msrs = make_channels(
            length=spec.chan_l,
            width=spec.chan_w,
            height=None,
            num_chans=spec.num_chans,
            spacing=spec.chan_gap,
            dxf=True,
        )
    else:
        # A zero-length channel (e.g. the myelination "oligo" arm) carries no
        # channel geometry; the chamber alone forms the thin bridge. Synthesise
        # the measurements the chamber needs (a zero-length array at the
        # channel-array width).
        channels = union()()
        total_width = (spec.chan_w * spec.num_chans) + (spec.chan_gap * max(spec.num_chans - 1, 0))
        msrs = Measurements(
            x=(0.0, 0.0),
            y=(total_width / 2.0, -total_width / 2.0),
            z=(0.0, 0.0),
        )
    chambers = make_chambers(
        msrs=msrs,
        height=None,
        extra=0,
        len_until=spec.resolved_chamber_len_until,
        width=spec.chamber_width,
        dxf=True,
    )

    parts: list[solid.OpenSCADObject] = []
    if add_channels:
        parts.append(channels)
    if add_wells:
        parts.append(
            wells_top_bottom(
                WellPatternContext.from_fields(
                    dims=spec.well_rad,
                    positions=wells_pos_from_center_2(spec.well_gap),
                    height=None,
                    dxf=True,
                )
            )
        )
    if add_chambers:
        parts.append(chambers)

    if not parts:
        raise ValueError("open chamber unit has no enabled components")

    return union()(*parts)


def linear_chain(
    unit: solid.OpenSCADObject,
    well_gap: float,
    count: int = 2,
) -> solid.OpenSCADObject:
    """Compose a shared-hub linear chain from a two-well unit.

    The unit (wells at ``+/- well_gap``) is shifted so its left well lands on
    the origin, then replicated by ``count`` evenly-spaced rotations about the
    origin. ``count = 2`` (rotations of 0 and 180 degrees) yields a three-well
    chain in which the central hub well is shared.

    Parameters
    ----------
    unit : solid.OpenSCADObject
        A two-well open-chamber unit centred on the origin.
    well_gap : float
        The well gap used to build ``unit``.
    count : int, default=2
        Number of rotational copies.

    Returns
    -------
    solid.OpenSCADObject
        The composed chain.
    """
    shifted = solid.translate([well_gap, 0, 0])(unit)
    angle = 360.0 / float(count)
    return union()(*(solid.rotate([0, 0, angle * idx])(shifted) for idx in range(count)))


def crossed_diamond(
    primary: solid.OpenSCADObject,
    secondary: solid.OpenSCADObject,
    *,
    center: Optional[solid.OpenSCADObject] = None,
    rotation: float = 45.0,
) -> solid.OpenSCADObject:
    """Compose a four-well diamond from two crossed two-well units.

    ``secondary`` is rotated 90 degrees so the two units cross at the origin,
    then the whole assembly is rotated by ``rotation`` (45 degrees by default)
    so the four wells sit at the corners of a square with a crossing
    microchannel X between them.

    An optional ``center`` geometry (e.g. the axon-guidance central closed
    chamber) is unioned in at the origin *before* the final rotation, so an
    axis-aligned square becomes a diamond whose flat edges face the four
    diagonal chamber arms.

    Parameters
    ----------
    primary : solid.OpenSCADObject
        The first two-well unit (placed along the x-axis).
    secondary : solid.OpenSCADObject
        The second two-well unit (rotated 90 degrees onto the y-axis).
    center : solid.OpenSCADObject, optional
        A central feature added at the origin before the final rotation.
    rotation : float, default=45.0
        Final rotation applied to the crossed assembly, in degrees.

    Returns
    -------
    solid.OpenSCADObject
        The composed four-well diamond.
    """
    parts = [primary, solid.rotate([0, 0, 90])(secondary)]
    if center is not None:
        parts.append(center)
    crossed = union()(*parts)
    return solid.rotate([0, 0, rotation])(crossed)
