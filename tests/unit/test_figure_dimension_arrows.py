import importlib
from pathlib import Path

import numpy as np
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


@pytest.fixture
def dimension_arrow(monkeypatch):
    figure_dir = Path(__file__).resolve().parents[2] / "papers/mfd_platform/figures"
    monkeypatch.syspath_prepend(str(figure_dir))
    return importlib.import_module("generate_bonding_fixture_figure").dimension_arrow


@pytest.mark.unit
@pytest.mark.parametrize("dpi", [100, 300, 600])
@pytest.mark.parametrize("vertical", [False, True])
@pytest.mark.parametrize("side", [-1, 1])
def test_dimension_tips_meet_extension_lines(dimension_arrow, dpi, vertical, side):
    points = np.array([[0.0, 0.4 * side], [2.0, 0.4 * side]])
    edges = np.array([[0.0, 0.0], [2.0, 0.0]])
    if vertical:
        points = points[:, ::-1]
        edges = edges[:, ::-1]

    fig = Figure(figsize=(4, 4), dpi=dpi)
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    ax.set(xlim=(-1, 3), ylim=(-1, 3), aspect="equal")
    dimension_arrow(ax, *points, "test", (1, 1), extension_points=edges)
    fig.canvas.draw()

    arrow = ax.patches[0]
    assert arrow.shrinkA == arrow.shrinkB == 0
    display_points = ax.transData.transform(points)
    direction = display_points[1] - display_points[0]
    direction /= np.linalg.norm(direction)
    vertices = arrow.get_transform().transform(arrow.get_path().vertices)
    projected = (vertices - display_points[0]) @ direction
    span = np.linalg.norm(display_points[1] - display_points[0])
    # Stroke-cap correction can move the path tip by less than one point.
    tolerance = dpi / 72
    assert abs(projected.min()) < tolerance
    assert abs(projected.max() - span) < tolerance

    for line, edge, tip in zip(ax.lines, edges, points, strict=True):
        extension = line.get_xydata()
        np.testing.assert_allclose(extension[0], edge)
        outward = (tip - edge) / np.linalg.norm(tip - edge)
        np.testing.assert_allclose(extension[1], tip + 0.08 * outward)


@pytest.mark.unit
def test_extension_lines_reach_outline_instead_of_empty_bounding_corners(dimension_arrow):
    module = importlib.import_module("generate_bonding_fixture_figure")
    outline = np.array([[0., 0.], [2., 0.], [3., 1.], [2., 2.], [0., 2.]])
    top = module.dimension_extension_points(outline, (0., 2.4), (3., 2.4))
    right = module.dimension_extension_points(outline, (3.4, 0.), (3.4, 2.))
    np.testing.assert_allclose(top, [(0., 2.), (3., 1.)])
    np.testing.assert_allclose(right, [(2., 0.), (2., 2.)])
    assert top[0] == (0., 2.)  # The connected top-left vertical stays unchanged.


@pytest.mark.unit
def test_clamp_jaws_clear_stack_and_arrows_press_inward(dimension_arrow):
    module = importlib.import_module("generate_bonding_fixture_figure")
    fig = Figure()
    ax = fig.subplots()
    module.draw_clamp_symbol(ax)
    top_arm, bottom_arm = ax.lines[1:]
    assert top_arm.get_ydata()[0] > module.STACK_DRAW_TOP
    assert bottom_arm.get_ydata()[0] < module.STACK_DRAW_BOTTOM
    assert top_arm.get_xdata()[1] > module.STACK_LEFT
    assert bottom_arm.get_xdata()[1] == top_arm.get_xdata()[1]
    top, bottom = [np.asarray(arrow._posA_posB) for arrow in ax.patches]
    assert top[0, 1] > top[1, 1] > module.STACK_DRAW_TOP
    assert bottom[0, 1] < bottom[1, 1] < module.STACK_DRAW_BOTTOM
    np.testing.assert_allclose(top[:, 0], bottom[:, 0])
    assert module.STACK_LEFT < top[0, 0] < top_arm.get_xdata()[1]


@pytest.mark.unit
def test_subfigure_exports_hide_neighbors_and_restore_visibility(dimension_arrow, monkeypatch, tmp_path):
    module = importlib.import_module("generate_bonding_fixture_figure")
    monkeypatch.setattr(module, "OUTPUT_DIR", tmp_path)
    fig = Figure()
    FigureCanvasAgg(fig)
    panels = dict(zip(("A", "B"), fig.subplots(1, 2), strict=True))
    exports = []

    def record_export(path, **kwargs):
        exports.append((path.stem, [label for label, ax in panels.items() if ax.get_visible()]))

    monkeypatch.setattr(fig, "savefig", record_export)
    module.save_subfigure_images(fig, panels)
    assert exports == [("A", ["A"]), ("B", ["B"])]
    assert all(ax.get_visible() for ax in panels.values())
