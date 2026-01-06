import matplotlib.pyplot as plt

from models import load_instance
from instances.container_instances import create_basic_instances, create_challenging_instances
from random_baseline import random_algorithm
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

    results = run_random_baseline(basic_instances, max_attempts=5)
    visualise_results(results)

    results = run_random_baseline(challenging_instances, max_attempts=5)
    visualise_results(results)