import random
from models import PlacedCylinder, Solution
from geometry import circles_overlap, is_within_bounds

#  another placement algorithm for testing/experiments, now defunct. used to be the simple right-left program

def find_random_position(cylinder, placed_list, container):
    """ Find a random valid position """
    r = cylinder.diameter / 2

    for attempt in range(1000):
        # Generate random position within bounds
        x = random.uniform(r, container.width - r)
        y = random.uniform(r, container.depth - r)

        # Check if  valid
        test_placed = PlacedCylinder(cylinder, x, y)

        valid = True
        for p in placed_list:
            if circles_overlap(test_placed, p):
                valid = False
                break

        if valid:
            return x, y

    return None, None


def place_cylinders_random(ordering, cylinders, container):
    """Place cylinders randomly"""
    solution = Solution()

    for idx in ordering:
        cyl = cylinders[idx]
        x, y = find_random_position(cyl, solution.placed, container)

        # Only add if valid position found
        if x is not None:
            solution.placed.append(PlacedCylinder(cyl, x, y))

    return solution