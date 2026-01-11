import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from models import load_instance
from instances.container_instances import create_basic_instances, create_challenging_instances
from random_baseline import random_algorithm
from evolutionary import EvolutionaryAlgorithm
from greedy import greedy_placement
from fitness import FitnessEvaluator
from visualisations import ContainerVisualiser


def run_random_baseline(instances, max_attempts):
    """Run random baseline on all instances."""
    print("Random Baseline Algorithm")
    print("=" * 60)

    results = []

    for instance in instances:
        container, cylinders = load_instance(instance)
        solution, fitness, details = random_algorithm(container, cylinders, max_attempts)

        print(f"{instance.name}: fitness={fitness:.3f}, feasible={details['is_feasible']}")

        results.append({
            'name': instance.name,
            'container': container,
            'expected_count': len(cylinders),
            'solution': solution,
            'fitness': fitness,
            'details': details
        })

    return results


def run_evolutionary(instances, placement_func):
    """Run evolutionary algorithm on all instances."""
    print("Evolutionary Algorithm")
    print("=" * 60)

    results = []

    for instance in instances:
        print(f"\n{instance.name}")
        print("-" * 40)

        container, cylinders = load_instance(instance)
        evaluator = FitnessEvaluator(container, cylinders)

        ea = EvolutionaryAlgorithm(
            container=container,
            cylinders=cylinders,
            placement_func=placement_func,
            fitness_evaluator=evaluator,
            pop_size=100,
            tournament_size=5,
            mutation_rate=0.02,
            elitism=True
        )

        solution = ea.run(
            max_generations=100,
            target_fitness=None,
            verbose=True
        )

        # Get final fitness from best individual
        best = ea.population.best_ever
        fitness = best.fitness
        details = best.details

        print(f"Result: fitness={fitness:.3f}, feasible={details['is_feasible']}")

        results.append({
            'name': instance.name,
            'container': container,
            'expected_count': len(cylinders),
            'solution': solution,
            'fitness': fitness,
            'details': details,
            'history': ea.get_history()
        })

    return results


def visualise_results(results):
    """Visualise all results."""
    for result in results:
        display = ContainerVisualiser(result['container'])
        display.set_solution(result['solution'], result['fitness'], result['details'],
                             expected_count=result['expected_count'])
        display.draw(
            title=f"{result['name']}\nFitness: {result['fitness']:.3f}, Feasible: {result['details']['is_feasible']}")
        plt.show()


if __name__ == "__main__":
    basic_instances = create_basic_instances()
    challenging_instances = create_challenging_instances()

    # Random baseline
    base_results = run_random_baseline(basic_instances, max_attempts=5)
    visualise_results(base_results)

    # Evolutionary algorithm
    results = run_evolutionary(basic_instances, greedy_placement)
    visualise_results(results)
