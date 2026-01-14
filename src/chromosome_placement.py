import math

from models import Solution, PlacedCylinder
from geometry import is_within_bounds, circles_overlap


def chromosome_placement(ordering, position_choices, cylinders, container):
    """ Placement using chromosome positions"""
    solution = Solution()

    for step, idx in enumerate(ordering):
        current_cyl = cylinders[idx]
        valid_positions = find_valid_positions(current_cyl, solution.placed, container)

        if valid_positions:
            # Use position_choice from chromosome to select from candidates
            choice_idx = position_choices[step] % len(valid_positions)
            chosen_pos = valid_positions[choice_idx]

            placed = PlacedCylinder(cylinder=current_cyl, x=chosen_pos[0], y=chosen_pos[1])
            solution.placed.append(placed)

    return solution


def find_valid_positions(cylinder, placed, container):
    """ Get a list of valid positions """
    r = cylinder.diameter / 2

    if len(placed) == 0:
        corners = get_corner_positions(r, container)
        return [pos for pos in corners if check_position_valid(pos, cylinder, placed, container)]

    # Get all possible positions
    all_positions = (
            find_wall_tangent_positions(cylinder, placed, container) +
            find_cylinder_tangent_positions(cylinder, placed) +
            get_corner_positions(r, container)
    )

    positions = []
    for x, y in all_positions:
        if check_position_valid((x, y), cylinder, placed, container):
            if is_loadable_from_rear(x, y, r, placed):
                positions.append((x, y))

    return positions


def get_corner_positions(r, container):
    """Return corner positions for cylinder"""
    return [
        (r, r),
        (container.width - r, r),
        (r, container.depth - r),
        (container.width - r, container.depth - r)
    ]


def check_position_valid(position, cylinder, placed, container):
    """Check if position is in bounds with no overlaps"""
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


def is_loadable_from_rear(x, y, radius, placed):
    """ Check if there is a straight line from rear door to cylinder """
    for p in placed:
        pr = p.cylinder.diameter / 2

        if p.y >= y:
            if abs(p.x - x) < radius + pr:
                return False

    return True