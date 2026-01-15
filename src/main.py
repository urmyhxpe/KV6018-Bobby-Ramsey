import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from models import load_instance
from instances.container_instances import create_basic_instances, create_challenging_instances
from random_baseline import random_algorithm
from evolutionary import EvolutionaryAlgorithm
from greedy_placement import greedy_placement

from evolutionary2 import EvolutionaryAlgorithm2
from chromosome_placement import chromosome_placement

from fitness import FitnessEvaluator
from visualisations import ContainerVisualiser, EvolutionVisualiser, SolutionComparer


def run_random_baseline(instances, max_attempts):
    """Run random baseline on instances."""
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


def run_evolutionary(instances, greedy_placement):
    """Run evolutionary algorithm on all instances."""
    print("=" * 60)
    print("Evolutionary Algorithm")

    results = []

    for instance in instances:
        print(f"\n{instance.name}")
        print("-" * 40)

        container, cylinders = load_instance(instance)
        # Edit fitness defaults
        evaluator = FitnessEvaluator(container, cylinders, 100.0, 100.0, 50.0, 50.0)

        # Note: change testing parameters here
        ea = EvolutionaryAlgorithm(
            container=container,
            cylinders=cylinders,
            placement_func=greedy_placement,
            fitness_evaluator=evaluator,
            pop_size=100,
            tournament_size=3,
            mutation_rate=0.02,
            elitism=True
        )

        solution = ea.run(
            max_generations=100,
            target_fitness=None,
            track_output=True
        )

        best = ea.population.best_ever
        fitness = best.fitness
        details = best.details if best.details else {'is_feasible': best.is_feasible}

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


def run_evolutionary2(instances, placement_func):
    """Run EA with extended chromosome on all instances."""
    print("=" * 60)
    print("Evolutionary Algorithm 2 (Extended Chromosome)")
    print("=" * 60)

    results = []

    for instance in instances:
        print(f"\n{instance.name}")
        print("-" * 40)

        container, cylinders = load_instance(instance)

        # Edit fitness defaults
        evaluator = FitnessEvaluator(container, cylinders, 100.0, 100.0, 50.0, 50.0)

        # Note: change testing parameters here
        # max positions is just an estimate for the number valid positions found by the placement algorithm at a given point
        # so there are enough spots in the chromosome
        ea = EvolutionaryAlgorithm2(
            container=container,
            cylinders=cylinders,
            placement_func=placement_func,
            fitness_evaluator=evaluator,
            pop_size=10,
            tournament_size=3,
            ordering_mutation_rate=0.1,
            position_mutation_rate=0.05,
            elitism=True,
            max_positions=20
        )

        solution = ea.run(
            max_generations=2,
            target_fitness=None,
            track_output=True
        )

        best = ea.get_best_individual()
        fitness = best.fitness
        details = best.details if best.details else {'is_feasible': best.is_feasible}

        print(f"Result: fitness={fitness:.3f}, feasible={details['is_feasible']}")
        print(f"  Ordering: {best.ordering}")
        print(f"  Position choices: {best.position_choices}")

        results.append({
            'name': instance.name,
            'container': container,
            'expected_count': len(cylinders),
            'solution': solution,
            'fitness': fitness,
            'details': details,
            'history': ea.get_history(),
            'best_individual': best
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


def visualise_ea_results(results):
    """Visualise EA results including evolution progress."""
    for result in results:
        display = ContainerVisualiser(result['container'])
        display.set_solution(result['solution'], result['fitness'], result['details'],
                             expected_count=result['expected_count'])
        display.draw(
            title=f"{result['name']}\nFitness: {result['fitness']:.3f}, Feasible: {result['details']['is_feasible']}")
        plt.show()

        progress = EvolutionVisualiser(result['history'])
        progress.draw(title=f"{result['name']} - Evolution Progress")
        plt.show()


def compare_algorithms_by_instance(instance_name, algorithm_results):

    comparer = SolutionComparer()

    for algo_name, results in algorithm_results:
        for result in results:
            if result['name'] == instance_name:
                comparer.add_solution(algo_name, result)
                break

    if comparer.solutions:
        comparer.show()
    else:
        print(f"No results found for instance: {instance_name}")


def compare_all_instances(algorithm_results):
    # Collect all unique instance names
    instance_names = set()
    for _, results in algorithm_results:
        for result in results:
            instance_names.add(result['name'])

    # Sort for consistent ordering
    instance_names = sorted(instance_names)

    print("\nSolution Comparison Mode")
    print("=" * 60)
    print("Controls: ← → to flip between algorithms, Q for next instance")
    print("=" * 60)

    for instance_name in instance_names:
        print(f"\nComparing: {instance_name}")
        compare_algorithms_by_instance(instance_name, algorithm_results)


if __name__ == "__main__":
    basic_instances = create_basic_instances()
    challenging_instances = create_challenging_instances()


    # Random baseline
    random_basic = run_random_baseline(basic_instances, max_attempts=4)
    random_challenging = run_random_baseline(challenging_instances, max_attempts=4)

    # Evolutionary algorithm
    ea_basic = run_evolutionary(basic_instances, greedy_placement)
    ea_challenging = run_evolutionary(challenging_instances, greedy_placement)

    # Evolutionary algorithm 2 (extended chromosome)
    ea2_basic = run_evolutionary2(basic_instances, chromosome_placement)
    ea2_challenging = run_evolutionary2(challenging_instances, chromosome_placement)

    # Combine results for comparison
    basic_algorithm_results = [
        ("Random Baseline", random_basic),
        ("EA (Order-based)", ea_basic),
        ("EA2 (Extended)", ea2_basic)
    ]

    challenging_algorithm_results = [
        ("Random Baseline", random_challenging),
        ("EA (Order only)", ea_challenging),
        ("EA2 (Order + positions)", ea2_challenging)
    ]

    compare_all_instances(basic_algorithm_results)

    compare_all_instances(challenging_algorithm_results)

    visualise_ea_results(ea_basic)
    visualise_ea_results(ea_challenging)