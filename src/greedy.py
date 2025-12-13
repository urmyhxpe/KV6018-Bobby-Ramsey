import math

from models import Solution, PlacedCylinder
from geometry import is_within_bounds, circles_overlap


def greedy_placement(ordering, cylinders, container):
    """ Greedy placement algorithm"""

    solution = Solution()

    center_x = container.width / 2
    center_y = container.depth / 2

    for idx in ordering:
        current_cyl = cylinders[idx]
        valid_positions = find_valid_positions(current_cyl, solution.placed, container)
        if valid_positions:
            best_position = min(valid_positions,key=lambda p: score_position(p, current_cyl, solution, center_x, center_y))

            placed = PlacedCylinder(cylinder=current_cyl, x=best_position[0], y=best_position[1])
            solution.placed.append(placed)

    return solution



def find_valid_positions(cylinder, placed, container):
    """ Get a list of valid positions """
    r = cylinder.diameter / 2

    if len(placed) == 0:
        #print("First placed cylinder")
        corners = get_corner_positions(r, container)
        return [position for position in corners if check_position_valid(position, cylinder, placed, container)]

    #print("min 1 position found")
    # Get all possible positions
    all_positions = (
            find_wall_tangent_positions(cylinder, placed, container) +
            find_cylinder_tangent_positions(cylinder, placed) +
            get_corner_positions(r, container)
    )

    return [position for position in all_positions if check_position_valid(position, cylinder, placed, container)]



def get_corner_positions(r, container):
    """Return corner positions for cylinder"""
    return [(r, r), (container.width - r, r), (r, container.depth - r), (container.width - r, container.depth - r)]


def check_position_valid(position, cylinder, placed, container):
    """Check if position is in bounds with no overlaps to previously placed cylinders"""
    x, y = position
    temp = PlacedCylinder(cylinder=cylinder, x=x, y=y)

    if not is_within_bounds(temp, container):
        return False

    for p in placed:
        if circles_overlap(temp, p):
            return False

    return True


def find_wall_tangent_positions(cylinder, placed, container):
    """Find positions touching one wall and one existing cylinder"""
    positions = []
    r = cylinder.diameter / 2

    for p in placed:
        pr = p.cylinder.diameter / 2
        touch_distance = r + pr

        # Bottom wall
        if touch_distance >= abs(p.y - r):
            dx = math.sqrt(max(0, touch_distance ** 2 - (p.y - r) ** 2))
            positions.append((p.x - dx, r))
            positions.append((p.x + dx, r))

        # Top wall
        top_y = container.depth - r
        if touch_distance >= abs(p.y - top_y):
            dx = math.sqrt(max(0, touch_distance ** 2 - (p.y - top_y) ** 2))
            positions.append((p.x - dx, top_y))
            positions.append((p.x + dx, top_y))

        # Left wall
        if touch_distance >= abs(p.x - r):
            dy = math.sqrt(max(0, touch_distance ** 2 - (p.x - r) ** 2))
            positions.append((r, p.y - dy))
            positions.append((r, p.y + dy))

        # Right wall
        right_x = container.width - r
        if touch_distance >= abs(p.x - right_x):
            dy = math.sqrt(max(0, touch_distance ** 2 - (p.x - right_x) ** 2))
            positions.append((right_x, p.y - dy))
            positions.append((right_x, p.y + dy))

    return positions


def find_cylinder_tangent_positions(cylinder, placed):
    """Find positions tangent to two existing cylinders"""
    positions = []
    r = cylinder.diameter / 2

    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            c1, c2 = placed[i], placed[j]

            r1 = r + c1.cylinder.diameter / 2
            r2 = r + c2.cylinder.diameter / 2

            dx = c2.x - c1.x
            dy = c2.y - c1.y
            d = math.sqrt(dx ** 2 + dy ** 2)

            if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
                continue

            a = (r1 ** 2 - r2 ** 2 + d ** 2) / (2 * d)
            h_sq = r1 ** 2 - a ** 2
            if h_sq < 0:
                continue
            h = math.sqrt(h_sq)

            px = c1.x + a * dx / d
            py = c1.y + a * dy / d

            positions.append((px + h * dy / d, py - h * dx / d))
            positions.append((px - h * dy / d, py + h * dx / d))

    return positions


def score_position(position, cylinder, solution, center_x, center_y):
    """ Measure position distance from COM so the best positions disrupt the COM the least"""
    x, y = position

    # Temporarily add cylinder
    temp = PlacedCylinder(cylinder=cylinder, x=x, y=y)
    solution.placed.append(temp)

    # Get position distance from current COM
    com_x, com_y = solution.center_of_mass()
    score = math.sqrt((com_x - center_x) ** 2 + (com_y - center_y) ** 2)

    # Remove placement
    solution.placed.pop()

    return score