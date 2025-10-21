"""Unit tests for alignment mark generation."""
import pytest
import solid
from openmfd.devices.alignment import (
    create_single_L_mark,
    create_full_alignment_mark,
    create_alignment_marks,
)


@pytest.mark.unit
class TestSingleLMark:
    """Tests for create_single_L_mark function."""
    
    def test_creates_openscad_object(self):
        """Test that create_single_L_mark returns an OpenSCAD object."""
        mark = create_single_L_mark(corner_length=2.0, thickness_divisor=3.0)
        assert isinstance(mark, solid.OpenSCADObject)
    
    def test_default_thickness_divisor(self):
        """Test that default thickness divisor is used."""
        mark = create_single_L_mark(corner_length=2.0)
        assert isinstance(mark, solid.OpenSCADObject)


@pytest.mark.unit
class TestFullAlignmentMark:
    """Tests for create_full_alignment_mark function."""
    
    def test_creates_openscad_object(self):
        """Test that create_full_alignment_mark returns an OpenSCAD object."""
        mark = create_full_alignment_mark(corner_length=2.0, thickness_divisor=8.0)
        assert isinstance(mark, solid.OpenSCADObject)


@pytest.mark.unit
class TestAlignmentMarks:
    """Tests for create_alignment_marks function."""
    
    @pytest.fixture
    def sample_array(self):
        """Create a sample array for testing."""
        return solid.square([10, 10])
    
    def test_creates_openscad_object(self, sample_array, sample_dims, sample_grid_size):
        """Test that create_alignment_marks returns an OpenSCAD object."""
        result = create_alignment_marks(
            sample_array, sample_dims, sample_grid_size,
            alignment_mode="full"
        )
        assert isinstance(result, solid.OpenSCADObject)
    
    def test_full_alignment_mode(self, sample_array, sample_dims, sample_grid_size):
        """Test full alignment mode (solid marks)."""
        result = create_alignment_marks(
            sample_array, sample_dims, sample_grid_size,
            alignment_mode="full",
            units_from_center=(3, 4)
        )
        assert isinstance(result, solid.OpenSCADObject)
