#!/usr/bin/env python3

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
from PIL import Image, ImageOps

from generate_openmfd_design_figure import (
    COLORS,
    DxfSources,
    StlSources,
    TwoCompartmentDeviceConfig,
    rotation_matrix,
    triangle_normals,
)
from openmfd.inserts.chamfer import deg_taper_len


FIGURE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = FIGURE_DIR / "final_drop" / "Fig2_insert_bonding"
PHOTO_DIR = FIGURE_DIR / "final_drop" / "Fig3_bonding_fixture"
PHOTO_TRANSFER = PHOTO_DIR / "clamp_assembly_seperated.jpg"
PHOTO_CLAMPED = PHOTO_DIR / "clamp_assembly.jpg"
PHOTO_GLUED = OUTPUT_DIR / "glued.png"
PHOTO_REAL_SUEX = OUTPUT_DIR / "real_suex.png"
SUBFIGURE_DPI = 600
SUEX_200_THICKNESS_MM = 0.20
LOCK_VIEW_Z_EXAGGERATION = 3.0


class TextRole(Enum):
    PANEL_BADGE = auto()
    PANEL_TITLE = auto()
    PHOTO_CAPTION = auto()
    LAYER_LABEL = auto()
    CALLOUT = auto()
    SMALL = auto()
    EMPHASIS = auto()
    LIGHT = auto()


class BoxRole(Enum):
    PANEL = auto()
    METAL = auto()
    WAFER = auto()
    SUEX = auto()
    INSERT = auto()
    EPOXY = auto()
    FOIL = auto()
    RUBBER = auto()
    MAGNET = auto()
    MAGNETIC_PLATE = auto()
    HOLE = auto()


@dataclass(frozen=True)
class TextStyle:
    size: float
    color: str
    ha: str = "center"
    va: str = "center"
    weight: str | None = None

    def kwargs(self) -> dict[str, object]:
        data: dict[str, object] = {
            "fontsize": self.size,
            "color": self.color,
            "ha": self.ha,
            "va": self.va,
        }
        if self.weight is not None:
            data["fontweight"] = self.weight
        return data


@dataclass(frozen=True, kw_only=True)
class FigureStyle(ABC):
    color: str
    edge: str
    linewidth: float = 1.0
    alpha: float = 1.0


@dataclass(frozen=True, kw_only=True)
class BoxStyle(FigureStyle):

    def kwargs(self) -> dict[str, object]:
        return {
            "facecolor": self.color,
            "edgecolor": self.edge,
            "linewidth": self.linewidth,
            "alpha": self.alpha,
        }


@dataclass(frozen=True)
class StackLayer:
    role: BoxRole
    label: str
    y: float
    height: float


@dataclass(frozen=True)
class InsertCrossSection:
    platform_x: tuple[float, float]
    base_x: tuple[float, float]
    contact_x: tuple[float, float]
    lock_x: tuple[float, float]
    pin_x: tuple[float, float]


@dataclass(frozen=True)
class SourceCrossSectionGeometry:
    inserts: tuple[InsertCrossSection, ...]
    source_x: tuple[float, float]
    suex_height: float
    pin_depth: float
    base_height: float
    taper_height: float


@dataclass(frozen=True, kw_only=True)
class SceneMesh(FigureStyle):
    triangles: np.ndarray


@dataclass(frozen=True, kw_only=True)
class SceneLineSet(FigureStyle):
    segments: np.ndarray


@dataclass(frozen=True)
class SceneTransform:
    center: np.ndarray
    scale: float
    offset: np.ndarray
    rotation: np.ndarray


TEXT = {
    TextRole.PANEL_BADGE: TextStyle(11.0, "white", ha="left", va="top", weight="bold"),
    TextRole.PANEL_TITLE: TextStyle(10.8, COLORS["ink"], ha="left", va="top", weight="bold"),
    TextRole.PHOTO_CAPTION: TextStyle(8.5, COLORS["muted"]),
    TextRole.LAYER_LABEL: TextStyle(6.7, COLORS["ink"], ha="left"),
    TextRole.CALLOUT: TextStyle(8.2, COLORS["ink"], ha="left"),
    TextRole.SMALL: TextStyle(7.5, COLORS["muted"]),
    TextRole.EMPHASIS: TextStyle(8.7, COLORS["ink"], weight="bold"),
    TextRole.LIGHT: TextStyle(8.0, "white", weight="bold"),
}


BOX = {
    BoxRole.PANEL: BoxStyle(color="white", edge=COLORS["grid"], linewidth=1.0),
    BoxRole.METAL: BoxStyle(color="#6f7680", edge="#4b535c", linewidth=1.0),
    BoxRole.WAFER: BoxStyle(color="#222a35", edge="#121820", linewidth=1.0),
    BoxRole.SUEX: BoxStyle(color="#46b486", edge="#1f8060", linewidth=1.0),
    BoxRole.INSERT: BoxStyle(color="#f4a037", edge="#cf7e10", linewidth=1.0),
    BoxRole.EPOXY: BoxStyle(color="#ffd166", edge="#d99b2b", linewidth=0.8, alpha=0.95),
    BoxRole.FOIL: BoxStyle(color="#d9dee5", edge="#a9b2bf", linewidth=0.8),
    BoxRole.RUBBER: BoxStyle(color="#6d5a8e", edge="#4e3f66", linewidth=1.0),
    BoxRole.MAGNET: BoxStyle(color="#547aa5", edge="#35577e", linewidth=1.0),
    BoxRole.MAGNETIC_PLATE: BoxStyle(color="#3c4654", edge="#1f2630", linewidth=1.0),
    BoxRole.HOLE: BoxStyle(color="#f7f9fb", edge="#1f8060", linewidth=1.2),
}


STACK_LAYERS = (
    StackLayer(BoxRole.METAL, "lower clamp build plate", 0.150, 0.045),
    StackLayer(BoxRole.WAFER, "silicon wafer", 0.205, 0.032),
    StackLayer(BoxRole.MAGNETIC_PLATE, "magnetic build plate", 0.443, 0.044),
    StackLayer(BoxRole.FOIL, "2-layer aluminum foil", 0.500, 0.010),
    StackLayer(BoxRole.FOIL, "", 0.515, 0.010),
    StackLayer(BoxRole.RUBBER, "rubber dampener", 0.541, 0.046),
    StackLayer(BoxRole.MAGNET, "magnetic build plate magnet", 0.601, 0.044),
    StackLayer(BoxRole.METAL, "top clamp build plate", 0.660, 0.050),
)
STACK_SOURCE_BOTTOM = min(layer.y for layer in STACK_LAYERS)
STACK_SOURCE_TOP = max(layer.y + layer.height for layer in STACK_LAYERS)
STACK_DRAW_BOTTOM = 0.110
STACK_DRAW_TOP = 0.830
STACK_DRAW_SCALE = (STACK_DRAW_TOP - STACK_DRAW_BOTTOM) / (STACK_SOURCE_TOP - STACK_SOURCE_BOTTOM)
STACK_LEFT = 0.205
STACK_WIDTH = 0.535
STACK_LABEL_X = 0.760
INSERT_DRAW_LEFT = 0.220
INSERT_DRAW_WIDTH = 0.520


def setup_axis(ax: plt.Axes) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def add_text(ax: plt.Axes, x: float, y: float, value: str, role: TextRole) -> None:
    kwargs = TEXT[role].kwargs()
    if role is TextRole.PANEL_BADGE:
        kwargs["clip_on"] = False
        kwargs["zorder"] = 100
    ax.text(x, y, value, **kwargs)


def add_rect(ax: plt.Axes, x: float, y: float, width: float, height: float, role: BoxRole) -> None:
    ax.add_patch(Rectangle((x, y), width, height, **BOX[role].kwargs()))


def rounded_panel(ax: plt.Axes, x: float, y: float, width: float, height: float) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.012,rounding_size=0.03",
            zorder=0.2,
            **BOX[BoxRole.PANEL].kwargs(),
        )
    )


def rounded_border(ax: plt.Axes, x: float, y: float, width: float, height: float) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.012,rounding_size=0.03",
            facecolor="none",
            edgecolor=BOX[BoxRole.PANEL].edge,
            linewidth=BOX[BoxRole.PANEL].linewidth,
            zorder=3,
        )
    )


def panel_label(ax: plt.Axes, label: str, title: str) -> None:
    panel_badge(ax, label)
    add_text(ax, 0.105, 0.965, title, TextRole.PANEL_TITLE)


def panel_badge(ax: plt.Axes, label: str) -> None:
    ax.text(
        0.02,
        0.97,
        label,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": COLORS["ink"], "edgecolor": "none"},
        clip_on=False,
        zorder=100,
        **TEXT[TextRole.PANEL_BADGE].kwargs(),
    )


def crop_to_aspect(image: Image.Image, aspect: float) -> Image.Image:
    width, height = image.size
    current = width / height
    if current > aspect:
        new_width = int(height * aspect)
        left = (width - new_width) // 2
        return image.crop((left, 0, left + new_width, height))
    new_height = int(width / aspect)
    top = max(0, (height - new_height) // 2)
    return image.crop((0, top, width, top + new_height))


def read_photo(path: Path, aspect: float) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image = crop_to_aspect(image, aspect)
    return ImageOps.autocontrast(image, cutoff=1)


def draw_photo_panel(ax: plt.Axes, path: Path) -> None:
    setup_axis(ax)
    photo_box = (0.02, 0.98, 0.025, 0.925)
    photo_aspect = (photo_box[1] - photo_box[0]) / (photo_box[3] - photo_box[2])
    image = read_photo(path, photo_aspect)
    ax.imshow(image, extent=photo_box, zorder=1)


def draw_labeled_photo_panel(ax: plt.Axes, path: Path, label: str, title: str) -> None:
    draw_photo_panel(ax, path)
    panel_badge(ax, label)


def draw_clamp_symbol(ax: plt.Axes) -> None:
    color = "#3b434f"
    x = 0.150
    y0 = 0.090
    y1 = 0.825
    arm = 0.055
    ax.plot([x, x], [y0, y1], color=color, lw=3.2, solid_capstyle="round", clip_on=False)
    ax.plot([x, x + arm], [y1, y1], color=color, lw=3.2, solid_capstyle="round", clip_on=False)
    ax.plot([x, x + arm], [y0, y0], color=color, lw=3.2, solid_capstyle="round", clip_on=False)
    ax.add_patch(
        FancyArrowPatch(
            (x + arm - 0.012, y1 - 0.008),
            (x + arm - 0.012, y1 - 0.090),
            arrowstyle="-|>",
            mutation_scale=11,
            color=color,
            lw=1.5,
            clip_on=False,
        )
    )


def draw_stack_layer(ax: plt.Axes, layer: StackLayer) -> None:
    draw_y = stack_draw_y(layer.y)
    draw_height = stack_draw_height(layer.height)
    add_rect(ax, STACK_LEFT, draw_y, STACK_WIDTH, draw_height, layer.role)
    if layer.label:
        add_text(ax, STACK_LABEL_X, draw_y + draw_height / 2, layer.label, TextRole.LAYER_LABEL)


def stack_draw_y(y: float) -> float:
    return STACK_DRAW_BOTTOM + (y - STACK_SOURCE_BOTTOM) * STACK_DRAW_SCALE


def stack_draw_height(height: float) -> float:
    return height * STACK_DRAW_SCALE


def stack_draw_layer(layer: StackLayer) -> StackLayer:
    return StackLayer(layer.role, layer.label, stack_draw_y(layer.y), stack_draw_height(layer.height))


def x_range(center: float, width: float) -> tuple[float, float]:
    return center - width / 2, center + width / 2


def source_cross_section_geometry(cfg: TwoCompartmentDeviceConfig) -> SourceCrossSectionGeometry:
    insert_cfg = cfg.insert_config()
    pins = insert_cfg.pins
    skirts = insert_cfg.skirts
    if pins is None or skirts is None:
        raise ValueError("The v27 cross-section requires insert pin and skirt configuration")

    wells = cfg.wells_config()
    channels = cfg.channels_config()
    unit_center_x = cfg.casing_x / 2
    taper_inset = deg_taper_len(insert_cfg.outer_taper.height, insert_cfg.outer_taper.degrees)
    base_inset = insert_cfg.outer_taper.extra_length
    pin_positions = sorted(insert_cfg.well_positions or [], key=lambda position: position[0])
    well_positions = sorted(wells.positions, key=lambda position: position[0])
    if len(pin_positions) != len(well_positions):
        raise ValueError("Insert pin positions must match well positions for the cross-section")

    inserts = []
    for well_position, pin_position in zip(well_positions, pin_positions):
        well_center_x = unit_center_x + well_position[0]
        pin_center_x = unit_center_x + pin_position[0]
        if well_position[0] < 0:
            platform_x = (well_center_x - wells.radius, unit_center_x - channels.length / 2)
        else:
            platform_x = (unit_center_x + channels.length / 2, well_center_x + wells.radius)
        base_x = (platform_x[0] + base_inset, platform_x[1] - base_inset)
        contact_x = (base_x[0] + taper_inset, base_x[1] - taper_inset)
        inserts.append(
            InsertCrossSection(
                platform_x=platform_x,
                base_x=base_x,
                contact_x=contact_x,
                lock_x=x_range(pin_center_x, pins.hole_dims[0]),
                pin_x=x_range(pin_center_x, pins.dims[0]),
            )
        )

    source_x = (
        min(insert.platform_x[0] for insert in inserts),
        max(insert.platform_x[1] for insert in inserts),
    )
    return SourceCrossSectionGeometry(
        inserts=tuple(inserts),
        source_x=source_x,
        suex_height=SUEX_200_THICKNESS_MM,
        pin_depth=pins.height,
        base_height=skirts.height1 + skirts.height2,
        taper_height=insert_cfg.outer_taper.height,
    )


def stack_layer(role: BoxRole) -> StackLayer:
    for layer in STACK_LAYERS:
        if layer.role is role:
            return layer
    raise ValueError(f"Missing stack layer for role: {role}")


def draw_insert_cross_section(ax: plt.Axes, cfg: TwoCompartmentDeviceConfig) -> None:
    geometry = source_cross_section_geometry(cfg)
    wafer = stack_draw_layer(stack_layer(BoxRole.WAFER))
    magnetic_plate = stack_draw_layer(stack_layer(BoxRole.MAGNETIC_PLATE))
    source_height = geometry.suex_height + geometry.base_height + geometry.taper_height
    x_min, x_max = geometry.source_x
    x_scale = INSERT_DRAW_WIDTH / (x_max - x_min)
    x_offset = INSERT_DRAW_LEFT - x_min * x_scale
    y_scale = (magnetic_plate.y - (wafer.y + wafer.height)) / source_height

    def draw_x(source_x: float) -> float:
        return x_offset + source_x * x_scale

    def draw_y(source_z: float) -> float:
        return wafer.y + wafer.height + source_z * y_scale

    suex_y = draw_y(0.0)
    suex_top_y = draw_y(geometry.suex_height)
    base_top_y = draw_y(geometry.suex_height + geometry.base_height)
    taper_top_y = draw_y(source_height)
    pin_bottom_y = draw_y(geometry.suex_height - geometry.pin_depth)

    for insert in geometry.inserts:
        platform_x0, platform_x1 = (draw_x(value) for value in insert.platform_x)
        lock_x0, lock_x1 = (draw_x(value) for value in insert.lock_x)
        pin_x0, pin_x1 = (draw_x(value) for value in insert.pin_x)
        base_x0, base_x1 = (draw_x(value) for value in insert.base_x)
        contact_x0, contact_x1 = (draw_x(value) for value in insert.contact_x)
        add_rect(ax, platform_x0, suex_y, platform_x1 - platform_x0, suex_top_y - suex_y, BoxRole.SUEX)
        add_rect(ax, lock_x0, suex_y, lock_x1 - lock_x0, suex_top_y - suex_y, BoxRole.HOLE)
        add_rect(ax, pin_x0, pin_bottom_y, pin_x1 - pin_x0, suex_top_y - pin_bottom_y, BoxRole.INSERT)
        add_rect(ax, base_x0, suex_top_y, base_x1 - base_x0, base_top_y - suex_top_y, BoxRole.INSERT)
        ax.add_patch(
            Polygon(
                [
                    (base_x0, base_top_y),
                    (base_x1, base_top_y),
                    (contact_x1, taper_top_y),
                    (contact_x0, taper_top_y),
                ],
                closed=True,
                **BOX[BoxRole.INSERT].kwargs(),
            )
        )

    add_text(ax, STACK_LABEL_X, (suex_y + suex_top_y) / 2 + 0.018, "SUEX lock platforms", TextRole.LAYER_LABEL)
    add_text(ax, STACK_LABEL_X, (suex_top_y + taper_top_y) / 2, "separate tapered inserts;\none pin each", TextRole.LAYER_LABEL)


def draw_side_stack(
    ax: plt.Axes,
    cfg: TwoCompartmentDeviceConfig,
    label: str = "C",
    title: str = "Bonding fixture cross-section",
) -> None:
    setup_axis(ax)
    panel_badge(ax, label)
    draw_clamp_symbol(ax)
    for layer in STACK_LAYERS:
        draw_stack_layer(ax, layer)
    draw_insert_cross_section(ax, cfg)


def cuboid_triangles(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> np.ndarray:
    vertices = np.array(
        [
            [x0, y0, z0],
            [x1, y0, z0],
            [x1, y1, z0],
            [x0, y1, z0],
            [x0, y0, z1],
            [x1, y0, z1],
            [x1, y1, z1],
            [x0, y1, z1],
        ],
        dtype=float,
    )
    faces = (
        (0, 1, 2),
        (0, 2, 3),
        (4, 7, 6),
        (4, 6, 5),
        (0, 4, 5),
        (0, 5, 1),
        (1, 5, 6),
        (1, 6, 2),
        (2, 6, 7),
        (2, 7, 3),
        (3, 7, 4),
        (3, 4, 0),
    )
    return np.array([[vertices[i], vertices[j], vertices[k]] for i, j, k in faces])


def rectangle_contains(rect: tuple[float, float, float, float], x: float, y: float) -> bool:
    x0, x1, y0, y1 = rect
    return x0 <= x <= x1 and y0 <= y <= y1


def slab_with_holes(
    bounds: tuple[float, float, float, float],
    holes: tuple[tuple[float, float, float, float], ...],
    z0: float,
    z1: float,
) -> np.ndarray:
    x0, x1, y0, y1 = bounds
    xs = sorted({x0, x1, *(value for hole in holes for value in hole[:2])})
    ys = sorted({y0, y1, *(value for hole in holes for value in hole[2:])})
    pieces = []
    for left, right in zip(xs[:-1], xs[1:]):
        for bottom, top in zip(ys[:-1], ys[1:]):
            center_x = (left + right) / 2
            center_y = (bottom + top) / 2
            if any(rectangle_contains(hole, center_x, center_y) for hole in holes):
                continue
            pieces.append(cuboid_triangles(left, right, bottom, top, z0, z1))
    return np.concatenate(pieces)


def scaled_insert_triangles(stl: StlSources, cfg: TwoCompartmentDeviceConfig) -> np.ndarray:
    triangles = stl.single_insert.triangles.copy()
    triangles[:, :, :2] /= cfg.pdms_config().scale_factor()
    return triangles


def contained_triangles(triangles: np.ndarray, bounds: tuple[float, float, float, float, float, float]) -> np.ndarray:
    x0, x1, y0, y1, z0, z1 = bounds
    mask = (
        (triangles[:, :, 0] >= x0)
        & (triangles[:, :, 0] <= x1)
        & (triangles[:, :, 1] >= y0)
        & (triangles[:, :, 1] <= y1)
        & (triangles[:, :, 2] >= z0)
        & (triangles[:, :, 2] <= z1)
    ).all(axis=1)
    return triangles[mask]


def centered_triangles(triangles: np.ndarray, bounds: tuple[float, float, float, float, float, float]) -> np.ndarray:
    x0, x1, y0, y1, z0, z1 = bounds
    centers = triangles.mean(axis=1)
    mask = (
        (centers[:, 0] >= x0)
        & (centers[:, 0] <= x1)
        & (centers[:, 1] >= y0)
        & (centers[:, 1] <= y1)
        & (centers[:, 2] >= z0)
        & (centers[:, 2] <= z1)
    )
    return triangles[mask]


def dxf_segments_at_z(
    dxf: DxfSources,
    z: float,
    bounds: tuple[float, float, float, float],
) -> np.ndarray:
    x0, x1, y0, y1 = bounds
    segments = []
    for start, end in dxf.single_top.segments:
        if not (
            max(start[0], end[0]) < x0
            or min(start[0], end[0]) > x1
            or max(start[1], end[1]) < y0
            or min(start[1], end[1]) > y1
        ):
            segments.append(((start[0], start[1], z), (end[0], end[1], z)))
    return np.array(segments, dtype=float)


def scaled_z_triangles(triangles: np.ndarray, scale: float) -> np.ndarray:
    scaled = triangles.copy()
    scaled[:, :, 2] *= scale
    return scaled


def scaled_z_segments(segments: np.ndarray, scale: float) -> np.ndarray:
    scaled = segments.copy()
    scaled[:, :, 2] *= scale
    return scaled


def make_scene_transform(
    meshes: tuple[SceneMesh, ...],
    line_sets: tuple[SceneLineSet, ...],
    frame: tuple[float, float, float, float],
) -> SceneTransform:
    points = [mesh.triangles.reshape((-1, 3)) for mesh in meshes]
    points.extend(line_set.segments.reshape((-1, 3)) for line_set in line_sets if len(line_set.segments))
    all_points = np.concatenate(points)
    center = (all_points.min(axis=0) + all_points.max(axis=0)) / 2
    rotation = rotation_matrix(-42.0, 18.0)
    rotated = (all_points - center) @ rotation
    min_xy = rotated[:, :2].min(axis=0)
    max_xy = rotated[:, :2].max(axis=0)
    size = max_xy - min_xy
    frame_x, frame_y, frame_w, frame_h = frame
    scale = min(frame_w / size[0], frame_h / size[1])
    offset = np.array([frame_x, frame_y]) + (np.array([frame_w, frame_h]) - size * scale) / 2 - min_xy * scale
    return SceneTransform(center=center, scale=scale, offset=offset, rotation=rotation)


def project_scene_points(points: np.ndarray, transform: SceneTransform) -> np.ndarray:
    rotated = (points - transform.center) @ transform.rotation
    return rotated[:, :2] * transform.scale + transform.offset


def scene_facecolors(mesh: SceneMesh, rotated_triangles: np.ndarray, depths: np.ndarray) -> list[tuple[float, float, float, float]]:
    normals = triangle_normals(rotated_triangles)
    light = np.array([-0.35, -0.50, 0.79])
    light = light / np.linalg.norm(light)
    illumination = np.abs(normals @ light)
    normalized_depth = (depths - depths.min()) / (depths.max() - depths.min() + 1e-9)
    shade = np.clip(0.28 + 0.46 * illumination + 0.16 * normalized_depth, 0, 1)
    base = np.array(mcolors.to_rgb(mesh.color))
    highlight = np.array(mcolors.to_rgb("white"))
    return [tuple(base * (1 - value) + highlight * value) + (mesh.alpha,) for value in shade]


def draw_scene(ax: plt.Axes, meshes: tuple[SceneMesh, ...], line_sets: tuple[SceneLineSet, ...], frame: tuple[float, float, float, float]) -> None:
    transform = make_scene_transform(meshes, line_sets, frame)
    polygons = []
    depths = []
    facecolors = []
    edgecolors = []
    linewidths = []
    for mesh in meshes:
        rotated = ((mesh.triangles.reshape((-1, 3)) - transform.center) @ transform.rotation).reshape((-1, 3, 3))
        projected = project_scene_points(mesh.triangles.reshape((-1, 3)), transform).reshape((-1, 3, 2))
        mesh_depths = rotated[:, :, 2].mean(axis=1)
        mesh_facecolors = scene_facecolors(mesh, rotated, mesh_depths)
        polygons.extend(projected)
        depths.extend(mesh_depths)
        facecolors.extend(mesh_facecolors)
        edgecolors.extend([mcolors.to_rgba(mesh.edge, mesh.alpha * 0.35)] * len(mesh_depths))
        linewidths.extend([mesh.linewidth] * len(mesh_depths))
    order = np.argsort(np.array(depths))
    ax.add_collection(
        PolyCollection(
            [polygons[index] for index in order],
            facecolors=[facecolors[index] for index in order],
            edgecolors=[edgecolors[index] for index in order],
            linewidths=[linewidths[index] for index in order],
            zorder=2,
        )
    )
    for line_set in line_sets:
        if not len(line_set.segments):
            continue
        projected = project_scene_points(line_set.segments.reshape((-1, 3)), transform).reshape((-1, 2, 2))
        ax.add_collection(
            LineCollection(projected, colors=mcolors.to_rgba(line_set.color, line_set.alpha), linewidths=line_set.linewidth, zorder=3)
        )


def source_rect(
    ax: plt.Axes,
    x_range_: tuple[float, float],
    y_range_: tuple[float, float],
    role: BoxRole,
    alpha: float = 1.0,
    zorder: float = 2.0,
) -> None:
    style = BOX[role].kwargs()
    style["alpha"] = alpha
    ax.add_patch(
        Rectangle(
            (x_range_[0], y_range_[0]),
            x_range_[1] - x_range_[0],
            y_range_[1] - y_range_[0],
            zorder=zorder,
            **style,
        )
    )


def dimension_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str,
    text_xy: tuple[float, float],
    rotation: float = 0.0,
    extension_points: tuple[tuple[float, float], tuple[float, float]] | None = None,
    text_background: bool = False,
) -> None:
    if extension_points is not None:
        for edge_point, arrow_point in zip(extension_points, (start, end), strict=True):
            ax.plot(
                [edge_point[0], arrow_point[0]],
                [edge_point[1], arrow_point[1]],
                color=COLORS["ink"],
                lw=0.65,
                linestyle=(0, (1.0, 2.0)),
                zorder=8,
            )
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="<->", mutation_scale=9, color=COLORS["ink"], lw=0.8))
    bbox = None
    if text_background:
        bbox = {"boxstyle": "round,pad=0.10", "facecolor": "white", "edgecolor": "none", "alpha": 0.92}
    ax.text(*text_xy, label, fontsize=7.6, color=COLORS["ink"], ha="center", va="center", rotation=rotation, bbox=bbox)


def convex_hull(points: np.ndarray) -> np.ndarray:
    ordered = sorted({tuple(point) for point in points})
    if len(ordered) <= 1:
        return np.array(ordered, dtype=float)

    def cross(origin: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
        return (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (b[0] - origin[0])

    lower: list[tuple[float, float]] = []
    for point in ordered:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper: list[tuple[float, float]] = []
    for point in reversed(ordered):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return np.array(lower[:-1] + upper[:-1], dtype=float)


def insert_projection_hull(
    stl: StlSources,
    cfg: TwoCompartmentDeviceConfig,
    right_side: bool,
    z_range: tuple[float, float] | None = None,
) -> np.ndarray:
    triangles = stl.single_insert.triangles.copy()
    triangles[:, :, :2] /= cfg.pdms_config().scale_factor()
    points = triangles.reshape((-1, 3))[:, :2]
    if z_range is not None:
        z_values = triangles.reshape((-1, 3))[:, 2]
        points = points[(z_values >= z_range[0]) & (z_values <= z_range[1])]
    if right_side:
        points = points[points[:, 0] >= cfg.casing_x / 2]
    else:
        points = points[points[:, 0] < cfg.casing_x / 2]
    if len(points) == 0:
        raise ValueError("No insert points found for requested side")
    return convex_hull(points)


def intersecting_segments(dxf: DxfSources, crop: tuple[float, float, float, float]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    x0, x1, y0, y1 = crop
    segments = []
    for start, end in dxf.single_top.segments:
        if start[0] < x0 or start[0] > x1 or end[0] < x0 or end[0] > x1:
            continue
        if start[1] < y0 or start[1] > y1 or end[1] < y0 or end[1] > y1:
            continue
        segments.append((start, end))
    return segments


def draw_lock_view(
    ax: plt.Axes,
    cfg: TwoCompartmentDeviceConfig,
    stl: StlSources,
    dxf: DxfSources,
    label: str = "B",
    title: str = "Equal-scale XY detail of insert lock",
) -> None:
    setup_axis(ax)
    panel_badge(ax, label)

    insert_cfg = cfg.insert_config()
    pins = insert_cfg.pins
    if pins is None:
        raise ValueError("The v27 XY projection requires pin configuration")
    geometry = source_cross_section_geometry(cfg)
    center_y = cfg.casing_y / 2
    wells = cfg.wells_config()
    platform_y = x_range(center_y, wells.radius * 2)
    lock_y = x_range(center_y, pins.hole_dims[1])
    pin_y = x_range(center_y, pins.dims[1])
    right_insert = geometry.inserts[-1]
    platform_x = right_insert.platform_x
    hull = insert_projection_hull(stl, cfg, right_side=True)
    skirt = insert_cfg.skirts
    if skirt is None:
        raise ValueError("The v27 XY projection requires skirt configuration")
    skirt_inner_z = (
        pins.height + skirt.height2 + 0.02,
        pins.height + skirt.height2 + skirt.height1 - 0.02,
    )
    skirt_inner_hull = insert_projection_hull(stl, cfg, right_side=True, z_range=skirt_inner_z)
    hull_min = hull.min(axis=0)
    hull_max = hull.max(axis=0)
    pad = 0.65
    crop = (
        hull_min[0] - 1.00,
        max(hull_max[0] + pad, platform_x[1] + 0.55),
        hull_min[1] - pad,
        max(hull_max[1] + pad, platform_y[1] + 0.82),
    )
    schematic_left = hull_min[0] - 0.55

    detail_ax = ax.inset_axes([0.025, 0.020, 0.95, 0.900])
    detail_ax.set_zorder(0)
    detail_ax.set_xlim(crop[0], crop[1])
    detail_ax.set_ylim(crop[2], crop[3])
    detail_ax.set_aspect("equal", adjustable="box")
    detail_ax.axis("off")
    detail_ax.add_patch(
        Rectangle(
            (schematic_left, crop[2]),
            crop[1] - schematic_left,
            crop[3] - crop[2],
            facecolor="#f1f4f8",
            edgecolor="none",
            linewidth=0.0,
            zorder=1,
        )
    )
    detail_ax.add_patch(
        Polygon(
            hull,
            closed=True,
            facecolor=mcolors.to_rgba(BOX[BoxRole.INSERT].color, 0.30),
            edgecolor=BOX[BoxRole.INSERT].edge,
            linewidth=1.2,
            zorder=2,
        )
    )
    detail_ax.add_patch(
        Polygon(
            skirt_inner_hull,
            closed=True,
            facecolor=mcolors.to_rgba("#f6dfbf", 0.94),
            edgecolor="#a46200",
            linewidth=1.1,
            linestyle="--",
            zorder=4,
        )
    )
    source_rect(detail_ax, right_insert.lock_x, lock_y, BoxRole.HOLE, 1.0, 5)
    source_rect(detail_ax, right_insert.pin_x, pin_y, BoxRole.INSERT, 0.85, 6)
    top_segments = intersecting_segments(dxf, (schematic_left, crop[1], crop[2], crop[3]))
    detail_ax.add_collection(LineCollection(top_segments, colors=BOX[BoxRole.SUEX].edge, linewidths=1.05, alpha=0.96, zorder=7))

    insert_arrow_y = hull_min[1] - 0.34
    p_insert_0 = (hull_min[0], insert_arrow_y)
    p_insert_1 = (hull_max[0], insert_arrow_y)
    dimension_arrow(
        detail_ax,
        p_insert_0,
        p_insert_1,
        f"{hull_max[0] - hull_min[0]:.2f} mm insert",
        ((p_insert_0[0] + p_insert_1[0]) / 2, p_insert_0[1] - 0.22),
        extension_points=((hull_min[0], hull_min[1]), (hull_max[0], hull_min[1])),
    )
    insert_arrow_x = hull_min[0] - 0.55
    p_insert_2 = (insert_arrow_x, hull_min[1])
    p_insert_3 = (insert_arrow_x, hull_max[1])
    dimension_arrow(
        detail_ax,
        p_insert_2,
        p_insert_3,
        f"{hull_max[1] - hull_min[1]:.2f} mm",
        (p_insert_2[0] - 0.24, (p_insert_2[1] + p_insert_3[1]) / 2),
        90.0,
        extension_points=((hull_min[0], hull_min[1]), (hull_min[0], hull_max[1])),
        text_background=True,
    )

    platform_arrow_y = platform_y[1] + 0.38
    platform_p0 = (platform_x[0], platform_arrow_y)
    platform_p1 = (platform_x[1], platform_arrow_y)
    dimension_arrow(
        detail_ax,
        platform_p0,
        platform_p1,
        f"{platform_x[1] - platform_x[0]:.2f} mm platform",
        (platform_p0[0] + 2.20, platform_p0[1] + 0.18),
        extension_points=((platform_x[0], platform_y[1]), (platform_x[1], platform_y[1])),
    )
    platform_arrow_x = platform_x[1] + 0.28
    platform_p2 = (platform_arrow_x, platform_y[0])
    platform_p3 = (platform_arrow_x, platform_y[1])
    dimension_arrow(
        detail_ax,
        platform_p2,
        platform_p3,
        f"{platform_y[1] - platform_y[0]:.2f} mm",
        (platform_p2[0] + 0.18, (platform_p2[1] + platform_p3[1]) / 2),
        90.0,
        extension_points=((platform_x[1], platform_y[0]), (platform_x[1], platform_y[1])),
    )

    lock_arrow_y = lock_y[1] + 0.62
    p0 = (right_insert.lock_x[0], lock_arrow_y)
    p1 = (right_insert.lock_x[1], lock_arrow_y)
    dimension_arrow(
        detail_ax,
        p0,
        p1,
        f"{pins.hole_dims[0]:.2f} mm SUEX lock",
        ((p0[0] + p1[0]) / 2, p0[1] + 0.22),
        extension_points=((right_insert.lock_x[0], lock_y[1]), (right_insert.lock_x[1], lock_y[1])),
    )
    pin_arrow_y = pin_y[0] - 0.50
    p2 = (right_insert.pin_x[0], pin_arrow_y)
    p3 = (right_insert.pin_x[1], pin_arrow_y)
    dimension_arrow(
        detail_ax,
        p2,
        p3,
        f"{pins.dims[0]:.2f} mm printed pin",
        ((p2[0] + p3[0]) / 2, p2[1] - 0.22),
        extension_points=((right_insert.pin_x[0], pin_y[0]), (right_insert.pin_x[1], pin_y[0])),
    )


def save_subfigure_images(fig: plt.Figure, axes: dict[str, plt.Axes]) -> None:
    subfigure_dir = OUTPUT_DIR / "subfigures"
    subfigure_dir.mkdir(parents=True, exist_ok=True)
    for path in subfigure_dir.glob("*.png"):
        path.unlink()

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for label, ax in axes.items():
        bbox = ax.get_tightbbox(renderer).expanded(1.03, 1.05)
        bbox_inches = bbox.transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(subfigure_dir / f"{label}.png", dpi=SUBFIGURE_DPI, bbox_inches=bbox_inches, pad_inches=0.02)


def build_figure() -> tuple[plt.Figure, dict[str, plt.Axes]]:
    cfg = TwoCompartmentDeviceConfig()
    stl = StlSources.from_generated_design()
    dxf = DxfSources.from_generated_design()
    fig, axes_grid = plt.subplots(3, 2, figsize=(7.15, 8.25))
    fig.patch.set_facecolor("white")
    for ax in axes_grid.ravel():
        ax.set_facecolor(COLORS["paper"])

    axes = {
        "A": axes_grid[0, 0],
        "B": axes_grid[0, 1],
        "C": axes_grid[1, 0],
        "D": axes_grid[1, 1],
        "E": axes_grid[2, 0],
        "F": axes_grid[2, 1],
    }

    draw_labeled_photo_panel(axes["A"], PHOTO_TRANSFER, "A", "Wafer and insert transfer plate")
    draw_lock_view(axes["B"], cfg, stl, dxf, "B", "Equal-scale XY detail of insert lock")
    draw_labeled_photo_panel(axes["C"], PHOTO_CLAMPED, "C", "Clamped fixture for acetone wash")
    draw_side_stack(axes["D"], cfg, "D", "Bonding fixture cross-section")
    draw_labeled_photo_panel(axes["E"], PHOTO_GLUED, "E", "Glued insert-wafer interface")
    draw_labeled_photo_panel(axes["F"], PHOTO_REAL_SUEX, "F", "Real SUEX lock micrograph")

    fig.suptitle(
        "Printed insert arrays register to SUEX locks before wafer bonding",
        fontsize=11.8,
        fontweight="bold",
        color=COLORS["ink"],
        y=0.985,
    )
    fig.subplots_adjust(left=0.035, right=0.985, bottom=0.040, top=0.920, wspace=-0.180, hspace=0.020)
    return fig, axes


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = build_figure()
    fig.savefig(OUTPUT_DIR / "draft_figure.pdf", bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "draft_figure.png", dpi=300, bbox_inches="tight")
    save_subfigure_images(fig, axes)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
