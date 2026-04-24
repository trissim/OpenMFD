import pytest
import solid

from openmfd.devices.alignment import (
    AlignmentMarkMode,
    AlignmentPatternType,
    create_alignment_marks,
    create_custom_alignment_pattern,
)
from openmfd.devices.text import DeviceLabelPosition, create_device_label
from openmfd.devices.text import TextLayoutContext


@pytest.mark.unit
def test_alignment_pattern_dispatch_accepts_nominal_enum_and_string() -> None:
    from_string = create_custom_alignment_pattern("corner", size=5.0)
    from_enum = create_custom_alignment_pattern(AlignmentPatternType.CORNER, size=5.0)

    assert isinstance(from_string, solid.OpenSCADObject)
    assert isinstance(from_enum, solid.OpenSCADObject)


@pytest.mark.unit
def test_alignment_pattern_dispatch_fails_loudly_for_unknown_pattern() -> None:
    with pytest.raises(ValueError, match="Unsupported pattern_type"):
        create_custom_alignment_pattern("bogus", size=5.0)


@pytest.mark.unit
def test_alignment_mode_dispatch_handles_none_nominally() -> None:
    array = solid.square([1, 1])

    result = create_alignment_marks(array, dims=[1, 1, 0], grid_size=[1, 1], alignment_mode=None)

    assert result is array
    assert AlignmentMarkMode.from_value(None) is AlignmentMarkMode.NONE


@pytest.mark.unit
def test_device_label_position_dispatch_accepts_nominal_enum() -> None:
    label = create_device_label(
        device_name="device",
        version="v1",
        context=TextLayoutContext.from_fields([6, 8], [9.0, 9.0, 0.0], size=1.5),
        position=DeviceLabelPosition.BOTTOM,
    )

    assert isinstance(label, solid.OpenSCADObject)


@pytest.mark.unit
def test_device_label_position_dispatch_fails_loudly() -> None:
    with pytest.raises(ValueError, match="Unsupported position"):
        create_device_label(
            device_name="device",
            version="v1",
            context=TextLayoutContext.from_fields([6, 8], [9.0, 9.0, 0.0], size=1.5),
            position="diagonal",
        )
