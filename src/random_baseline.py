import random

from models import load_instance
from placement import place_cylinders
from fitness import FitnessEvaluator



def random_ordering(num_cylinders):
    """Generate random orders"""
    ordering = list(range(num_cylinders))
    random.shuffle(ordering)
    return ordering


def random_algorithm(problem, max_attempts=100, seed=None):
    """Random baseline"""
    if seed is not None:
        random.seed(seed)

    container, cylinders = load_instance(problem)

    evaluator = FitnessEvaluator(container)

    best_solution = None
    best_fitness = float('inf')
    best_details = None

    for attempt in range(max_attempts):
        ordering = random_ordering(len(cylinders))
        solution = place_cylinders(ordering, cylinders, container)

        fitness, is_feasible, details = evaluator.evaluate(solution)

        if fitness < best_fitness:
            best_solution = solution
            best_fitness = fitness
            best_details = details

    return best_solution, best_fitness, best_details