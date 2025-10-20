"""Type definitions for geometry module."""

from typing import Tuple, Union, List
from dataclasses import dataclass

# Position types
Position2D = Tuple[float, float]
Position3D = Tuple[float, float, float]
Position = Union[Position2D, Position3D]

# Dimension types
Dimensions2D = Tuple[float, float]
Dimensions3D = Tuple[float, float, float]
Dimensions = Union[float, Dimensions2D, Dimensions3D]

# Measurement types
MeasurementRange = Tuple[float, float]  # (positive, negative) from center


@dataclass
class Measurements:
    """Measurements of a geometry component.
    
    Attributes:
        x: X-dimension range (positive, negative) from center
        y: Y-dimension range (positive, negative) from center
        z: Z-dimension range (positive, negative) from center (optional for 2D)
    """
    x: MeasurementRange
    y: MeasurementRange
    z: MeasurementRange = (0.0, 0.0)
    
    def total_x(self) -> float:
        """Total X dimension."""
        return abs(self.x[0]) + abs(self.x[1])
    
    def total_y(self) -> float:
        """Total Y dimension."""
        return abs(self.y[0]) + abs(self.y[1])
    
    def total_z(self) -> float:
        """Total Z dimension."""
        return abs(self.z[0]) + abs(self.z[1])
    
    def to_dict(self) -> dict:
        """Convert to dictionary format (for backward compatibility)."""
        return {'x': self.x, 'y': self.y, 'z': self.z}

