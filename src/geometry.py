import math


def circles_overlap(c1, c2):
    """Check if cylinders overlap"""
    dx = c1.x - c2.x
    dy = c1.y - c2.y
    dist = math.sqrt(dx * dx + dy * dy)
    return dist < (c1.cylinder.diameter / 2 + c2.cylinder.diameter / 2)


def is_within_bounds(placed, container):
    """Check if a placed cylinder is in bounds"""
    r = placed.cylinder.diameter / 2
    return (placed.x - r >= 0 and
            placed.x + r <= container.width and
            placed.y - r >= 0 and
            placed.y + r <= container.depth)


def com_deviation(solution, container):
    """ Calculate how far the centre of mass is from the valid zone"""
    if not solution.placed:
        return 0.0

    cx, cy = solution.center_of_mass()
    min_x, max_x, min_y, max_y = container.centre_zone_bounds()

    dev_x = 0.0
    if cx < min_x:
        dev_x = min_x - cx
    elif cx > max_x:
        dev_x = cx - max_x

    dev_y = 0.0
    if cy < min_y:
        dev_y = min_y - cy
    elif cy > max_y:
        dev_y = cy - max_y

    return math.sqrt(dev_x * dev_x + dev_y * dev_y)


def count_overlaps(solution):
    """Count overlapping cylinders"""
    count = 0
    placed = solution.placed
    n = len(placed)
    for i in range(n):
        for j in range(i + 1, n):
            if circles_overlap(placed[i], placed[j]):
                count += 1
    return count


def count_out_of_bounds(solution, container):
    """Count cylinders that are out of bounds"""
    count = 0
    for p in solution.placed:
        if not is_within_bounds(p, container):
            count += 1
    return count