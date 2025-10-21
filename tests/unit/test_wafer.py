"""Unit tests for wafer mask generation."""
import pytest
import solid
from openmfd.devices.wafer import (
    compute_wafer_center,
    create_wafer,
    create_wafer_mask,
)


@pytest.mark.unit
class TestComputeWaferCenter:
    """Tests for compute_wafer_center function."""
    
    def test_basic_computation(self, sample_dims, sample_grid_size):
        """Test basic wafer center computation."""
        cx, cy = compute_wafer_center(sample_grid_size, sample_dims)
        assert isinstance(cx, (int, float))
        assert isinstance(cy, (int, float))
        assert cx > 0
        assert cy > 0
    
    def test_center_calculation_accuracy(self):
        """Test that center calculation is accurate."""
        # For a 6x8 grid of 18x9mm devices
        grid_size = [6, 8]
        dims = [18.0, 9.0, 0.2]
        cx, cy = compute_wafer_center(grid_size, dims)
        
        # Expected: (6 * 18) / 2 = 54, (8 * 9) / 2 = 36
        assert cx == 54.0
        assert cy == 36.0


@pytest.mark.unit
class TestCreateWafer:
    """Tests for create_wafer function."""
    
    def test_creates_openscad_object(self, sample_wafer_size, sample_flat_length):
        """Test that create_wafer returns an OpenSCAD object."""
        wafer = create_wafer(sample_wafer_size, sample_flat_length)
        assert isinstance(wafer, solid.OpenSCADObject)
