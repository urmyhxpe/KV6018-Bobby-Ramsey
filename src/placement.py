from models import PlacedCylinder, Solution
from geometry import circles_overlap


def find_placement_position(cylinder, placed_list, container):
    """ Find a position for the cylinder"""
    r = cylinder.diameter / 2
    step = min(r / 2, 0.5)

    best_y = float('inf')
    best_x = r

    # Scan from rear (y=r) to front
    y = r
    while y + r <= container.depth:
        x = r
        while x + r <= container.width:
            # Check if position is valid
            valid = True
            test_placed = PlacedCylinder(cylinder, x, y)
            for p in placed_list:
                if circles_overlap(test_placed, p):
                    valid = False
                    break

            if valid and y < best_y:
                best_y = y
                best_x = x
                break

            x += step

        if best_y < float('inf'):
            break
        y += step

    # Default
    if best_y == float('inf'):
        best_y = r
        best_x = r

    return best_x, best_y


def place_cylinders(ordering, cylinders, container):
    """Place cylinders in order"""
    solution = Solution()

    for idx in ordering:
        cyl = cylinders[idx]
        x, y = find_placement_position(cyl, solution.placed, container)
        solution.placed.append(PlacedCylinder(cyl, x, y))

    return solution