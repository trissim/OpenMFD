"""Integration tests for complete device generation workflow."""
import pytest
import solid
from openmfd.devices import (
    create_device_array,
    create_wafer_mask,
    compute_wafer_center,
)


@pytest.mark.integration
class TestDeviceGenerationWorkflow:
    """Integration tests for complete device generation."""
    
    @pytest.fixture
    def simple_device_unit(self):
        """Create a simple device unit for testing."""
        return solid.square([8, 8])
    
    def test_basic_device_array_generation(self, simple_device_unit):
        """Test basic device array generation."""
        dims = [9.0, 9.0, 0.2]
        grid_size = [4, 4]
        
        array = create_device_array(
            simple_device_unit, dims, grid_size, dxf=True
        )
        
        assert isinstance(array, solid.OpenSCADObject)
    
    def test_device_array_with_alignment_marks(self, simple_device_unit):
        """Test device array with alignment marks."""
        dims = [18.0, 9.0, 0.2]
        grid_size = [6, 8]
        
        # Bottom layer with full marks
        bottom_array = create_device_array(
            simple_device_unit, dims, grid_size,
            dxf=True,
            alignment="full",
            units_from_center=(3, 4),
            alignment_mark_size=1.0
        )
        
        assert isinstance(bottom_array, solid.OpenSCADObject)
