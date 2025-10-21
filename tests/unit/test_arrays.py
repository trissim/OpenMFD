"""Unit tests for device array generation."""
import pytest
import solid
from openmfd.devices.arrays import create_device_array


@pytest.mark.unit
class TestCreateDeviceArray:
    """Tests for create_device_array function."""
    
    @pytest.fixture
    def sample_unit(self):
        """Create a sample unit for testing."""
        return solid.square([5, 5])
    
    def test_creates_openscad_object(self, sample_unit, sample_dims, sample_grid_size):
        """Test that create_device_array returns an OpenSCAD object."""
        array = create_device_array(sample_unit, sample_dims, sample_grid_size)
        assert isinstance(array, solid.OpenSCADObject)
    
    def test_2d_array_creation(self, sample_unit, sample_dims, sample_grid_size):
        """Test 2D array creation for DXF export."""
        array = create_device_array(
            sample_unit, sample_dims, sample_grid_size, dxf=True
        )
        assert isinstance(array, solid.OpenSCADObject)
