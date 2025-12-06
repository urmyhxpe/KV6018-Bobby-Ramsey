from typing import Dict


class Cylinder:
    """Represents a cylindrical container"""

    def __init__(self, id: int, diameter: float, weight: float):
        self.id = id
        self.diameter = diameter
        self.weight = weight

    def to_dict(self):
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

    def centre_zone_bounds(self):
        """ Returns (min_x, max_x, min_y, max_y) for the centre of mass zone """
        margin_x = self.width * 0.2
        margin_y = self.depth * 0.2
        return (margin_x, self.width - margin_x,
                margin_y, self.depth - margin_y)

    def to_dict(self):
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


class Solution:
    """ A potential solution """

    def __init__(self):
        self.placed = []

    def total_weight(self):
        """Total weight of all placed cylinders"""
        return sum(p.cylinder.weight for p in self.placed)

    def num_placed(self):
        """Count of successfully placed cylinders"""
        return len(self.placed)

    def center_of_mass(self):
        """ Calculate centre of mass """
        if not self.placed:
            return 0.0, 0.0

        total_w = self.total_weight()
        cx = sum(p.x * p.cylinder.weight for p in self.placed) / total_w
        cy = sum(p.y * p.cylinder.weight for p in self.placed) / total_w
        return cx, cy

    def is_balanced(self, container):
        """ Check if centre of mass is in the right zone """
        if not self.placed:
            return True

        cx, cy = self.center_of_mass()
        min_x, max_x, min_y, max_y = container.centre_zone_bounds()
        return min_x <= cx <= max_x and min_y <= cy <= max_y

def load_instance(instance):
    """load instances into above structure """
    container = Container(
        width=instance.container.width,
        depth=instance.container.depth,
        max_weight=instance.container.max_weight
    )

    cylinders = [
        Cylinder(id=c.id, diameter=c.diameter, weight=c.weight)
        for c in instance.cylinders
    ]

    return container, cylinders