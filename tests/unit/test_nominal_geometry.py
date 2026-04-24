import pytest
import solid

from openmfd.geometry.primitives import make_well
from openmfd.geometry.wells import WellPatternContext, four_corner, well_array, wells_top_bottom


@pytest.mark.unit
@pytest.mark.parametrize(
    ("dims", "kwargs"),
    [
        (2.0, {"dxf": True}),
        ((2.0,), {"height": 0.3}),
        ((2.0, 2.0), {"dxf": True}),
        ((2.0, 2.0, 0.3), {"height": 0.3}),
    ],
)
def test_make_well_handles_nominal_dimension_families(dims, kwargs) -> None:
    well = make_well(dims, **kwargs)

    assert isinstance(well, solid.OpenSCADObject)


@pytest.mark.unit
def test_make_well_rejects_unknown_dimension_rank() -> None:
    with pytest.raises(ValueError, match="dims tuple must have 1, 2, or 3 elements"):
        make_well((1.0, 2.0, 3.0, 4.0), dxf=True)


@pytest.mark.unit
def test_well_pattern_helpers_still_build_geometry_after_context_refactor() -> None:
    top_bottom = wells_top_bottom(
        WellPatternContext.from_fields(2.0, positions=[(3.0, 0.0), (-3.0, 0.0)], dxf=True)
    )
    corners = four_corner(
        WellPatternContext.from_fields(
            (2.0, 2.0),
            positions=[(3.0, 3.0), (-3.0, 3.0), (-3.0, -3.0), (3.0, -3.0)],
            dxf=True,
        )
    )
    array = well_array(
        WellPatternContext.from_fields(2.0, positions=[], dxf=True),
        rows=2,
        cols=3,
        spacing_x=5.0,
    )

    assert isinstance(top_bottom, solid.OpenSCADObject)
    assert isinstance(corners, solid.OpenSCADObject)
    assert isinstance(array, solid.OpenSCADObject)
