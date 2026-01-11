import random

from fitness import FitnessEvaluator
from greedy import greedy_placement

def random_ordering(num_cylinders):
    """Generate random orders"""
    random.seed()
    ordering = list(range(num_cylinders))
    random.shuffle(ordering)
    return ordering


def random_algorithm(container, cylinders, max_attempts):
    """Random baseline"""

    evaluator = FitnessEvaluator(container, cylinders, 100.0, 100.0, 50.0, 10.0)

    best_solution = None
    best_fitness = float('-inf')
    best_details = None

    for attempt in range(max_attempts):
        ordering = random_ordering(len(cylinders))

        #print(f"\nOrdering: {ordering}")
        solution = greedy_placement(ordering, cylinders, container)
        """print("Positions:")
        for p in solution.placed:
            print(f"  Cylinder {p.cylinder.id}: ({p.x:.2f}, {p.y:.2f})")"""

        fitness, is_feasible, details = evaluator.evaluate(solution)

        if fitness > best_fitness:
            best_solution = solution
            best_fitness = fitness
            best_details = details

    return best_solution, best_fitness, best_details