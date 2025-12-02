from typing import Dict


class Cylinder:
    """Represents a cylindrical container"""

    def __init__(self, id: int, diameter: float, weight: float):
        self.id = id
        self.diameter = diameter
        self.weight = weight
        self.radius = diameter / 2

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "diameter": self.diameter,
            "weight": self.weight
        }


class Container:
    """Represents the cargo container."""

    def __init__(self, width: float, depth: float, max_weight: float):
        self.width = width
        self.depth = depth
        self.max_weight = max_weight

    def to_dict(self) -> Dict:
        return {
            "width": self.width,
            "depth": self.depth,
            "max_weight": self.max_weight
        }


class PlacedCylinder:
    """A cylinder with its placed position."""

    def __init__(self, cylinder: Cylinder, x: float, y: float):
        self.cylinder = cylinder
        self.x = x
        self.y = y