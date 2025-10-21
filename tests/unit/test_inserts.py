"""Unit tests for insert generation module."""

import pytest
import solid

from openmfd.inserts.config import (
    TaperConfiguration,
    InsertConfiguration,
    PinConfiguration,
    SkirtConfiguration,
)
from openmfd.inserts.chamfer import deg_taper_len, linear_extrude_if_flat
from openmfd.inserts.pins import create_insert_pin, create_pin_array, create_insert_holes
from openmfd.inserts.skirts import create_skirt_layer, create_dual_skirt


class TestTaperCalculation:
    """Test taper length calculation."""

    def test_deg_taper_len_basic(self):
        """Test basic taper length calculation."""
        # 45° angle should give taper_len = height
        taper_len = deg_taper_len(height=1.0, degrees=45)
        assert abs(taper_len - 1.0) < 0.01

    def test_deg_taper_len_zero_angle(self):
        """Test zero angle returns zero taper."""
        taper_len = deg_taper_len(height=5.0, degrees=0)
        assert taper_len == 0.0

    def test_deg_taper_len_realistic(self):
        """Test realistic taper angles."""
        # 16° taper over 3.8mm
        taper_len = deg_taper_len(height=3.8, degrees=16)
        assert 1.0 < taper_len < 1.2

        # 35° taper over 0.4mm
        taper_len = deg_taper_len(height=0.4, degrees=35)
        assert 0.25 < taper_len < 0.35


class TestPinGeneration:
    """Test alignment pin generation."""

    def test_create_insert_pin(self):
        """Test single pin creation."""
        pin = create_insert_pin(
            position=(10.0, 20.0),
            dims=(1.85, 1.85),
            height=2.0,
            offset=-0.5,
        )
        assert isinstance(pin, solid.OpenSCADObject)

    def test_create_pin_array(self):
        """Test pin array creation."""
        well_positions = [(0, -4.5), (0, 4.5)]
        pins = create_pin_array(
            well_positions=well_positions,
            dims=(1.85, 1.85),
            height=2.06,
            offset=-0.5,
        )
        assert isinstance(pins, solid.OpenSCADObject)

    def test_create_insert_holes(self):
        """Test insert hole creation."""
        well_positions = [(0, -4.5), (0, 4.5)]
        holes = create_insert_holes(
            well_positions=well_positions,
            hole_dims=(2.0, 2.0),
            offset=-0.5,
        )
        assert isinstance(holes, solid.OpenSCADObject)


class TestSkirtGeneration:
    """Test sealing skirt generation."""

    def test_create_skirt_layer(self):
        """Test single skirt layer creation."""
        # Create simple 2D geometry
        insert_2d = solid.circle(r=5.0)

        skirt = create_skirt_layer(
            insert_geometry=insert_2d,
            thickness=-0.75,
            height=0.66,
        )
        assert isinstance(skirt, solid.OpenSCADObject)

    def test_create_dual_skirt(self):
        """Test dual skirt creation."""
        # Create simple 2D geometry
        insert_2d = solid.circle(r=5.0)

        skirts = create_dual_skirt(
            insert_geometry=insert_2d,
            thickness1=-0.75,
            height1=0.66,
            empty1=0.3,
            thickness2=-0.8,
            height2=0.04,
            pin_height=0.06,
        )
        assert isinstance(skirts, solid.OpenSCADObject)


class TestConfiguration:
    """Test configuration dataclasses."""

    def test_taper_configuration(self):
        """Test TaperConfiguration creation."""
        config = TaperConfiguration(
            height=3.8,
            degrees=16,
            extra_length=0.3,
            segments=20,
        )
        assert config.height == 3.8
        assert config.degrees == 16
        assert config.extra_length == 0.3
        assert config.segments == 20

    def test_insert_configuration(self):
        """Test InsertConfiguration creation."""
        outer_taper = TaperConfiguration(height=3.8, degrees=16)
        inner_taper = TaperConfiguration(height=0.4, degrees=35)

        config = InsertConfiguration(
            outer_taper=outer_taper,
            inner_taper=inner_taper,
            well_radius=3.2,
            channel_length=1.0,
        )
        assert config.outer_taper == outer_taper
        assert config.inner_taper == inner_taper
        assert config.well_radius == 3.2
        assert config.channel_length == 1.0

    def test_pin_configuration(self):
        """Test PinConfiguration creation."""
        config = PinConfiguration(
            dims=(1.85, 1.85),
            height=0.06,
            inner_height=2.0,
            offset=-0.5,
            hole_dims=(2.0, 2.0),
        )
        assert config.dims == (1.85, 1.85)
        assert config.height == 0.06
        assert config.inner_height == 2.0
        assert config.offset == -0.5
        assert config.hole_dims == (2.0, 2.0)

    def test_skirt_configuration(self):
        """Test SkirtConfiguration creation."""
        config = SkirtConfiguration(
            thickness1=0.75,
            height1=0.66,
            empty1=0.3,
            thickness2=0.8,
            height2=0.04,
        )
        assert config.thickness1 == 0.75
        assert config.height1 == 0.66
        assert config.empty1 == 0.3
        assert config.thickness2 == 0.8
        assert config.height2 == 0.04


class TestExtrusion:
    """Test extrusion functions."""

    def test_linear_extrude_if_flat_zero_angle(self):
        """Test linear extrusion with zero angle."""
        obj = solid.circle(r=3.0)
        result = linear_extrude_if_flat(obj, height=5.0, degrees=0)
        assert isinstance(result, solid.OpenSCADObject)

    def test_linear_extrude_if_flat_with_angle(self):
        """Test chamfered extrusion with non-zero angle."""
        obj = solid.circle(r=3.0)
        result = linear_extrude_if_flat(obj, height=5.0, degrees=15, segments=20)
        assert isinstance(result, solid.OpenSCADObject)
