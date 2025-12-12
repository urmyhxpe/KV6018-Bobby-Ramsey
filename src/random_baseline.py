import random

from models import load_instance
from fitness import FitnessEvaluator
from placement import place_cylinders


def random_ordering(num_cylinders):
    """Generate random orders"""
    random.seed()
    ordering = list(range(num_cylinders))
    random.shuffle(ordering)
    return ordering


def random_algorithm(problem, max_attempts):
    """Random baseline"""

    container, cylinders = load_instance(problem)

    evaluator = FitnessEvaluator(container)

    best_solution = None
    best_fitness = float('inf')
    best_details = None

    for attempt in range(max_attempts):
        ordering = random_ordering(len(cylinders))

        #print(f"\nOrdering: {ordering}")
        solution = place_cylinders(ordering, cylinders, container)
        """print("Positions:")
        for p in solution.placed:
            print(f"  Cylinder {p.cylinder.id}: ({p.x:.2f}, {p.y:.2f})")"""

        fitness, is_feasible, details = evaluator.evaluate(solution)

        if fitness < best_fitness:
            best_solution = solution
            best_fitness = fitness
            best_details = details

    return best_solution, best_fitness, best_details