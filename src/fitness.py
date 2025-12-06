import math
from geometry import count_overlaps, count_out_of_bounds, com_deviation


class FitnessEvaluator:

    def __init__(self, container, overlap_penalty=100.0, bounds_penalty=100.0,
                 weight_penalty=50.0, com_penalty_base=10.0):
        self.container = container
        self.overlap_penalty = overlap_penalty
        self.bounds_penalty = bounds_penalty
        self.weight_penalty = weight_penalty
        self.com_penalty_base = com_penalty_base
        self.com_adaptive_coefficient = 1.0

    def evaluate(self, solution):
        """
        Evaluate a solution and compute fitness.

        Returns:
            (fitness, is_feasible, details_dict)
        """
        overlap_count = count_overlaps(solution)
        oob_count = count_out_of_bounds(solution, self.container)
        total_weight = solution.total_weight()
        com_dev = com_deviation(solution, self.container)

        # Penalty for geometry
        geometry_penalty = (
                overlap_count * self.overlap_penalty +
                oob_count * self.bounds_penalty
        )

        # Penalty for weight
        weight_excess = max(0, total_weight - self.container.max_weight)
        weight_pen = weight_excess * self.weight_penalty

        # Penalty for COM
        com_penalty = (
                self.com_penalty_base *
                self.com_adaptive_coefficient *
                (com_dev ** 2)
        )

        total_penalty = geometry_penalty + weight_pen + com_penalty

        # Incentivise good use of space
        area_covered = sum(math.pi * p.cylinder.diameter / 2 ** 2 for p in solution.placed)
        container_area = self.container.width * self.container.depth
        utilisation = area_covered / container_area if container_area > 0 else 0

        fitness = total_penalty - (utilisation * 100)

        is_feasible = (
                overlap_count == 0 and
                oob_count == 0 and
                weight_excess == 0 and
                com_dev == 0
        )

        details = {
            'overlap_count': overlap_count,
            'oob_count': oob_count,
            'total_weight': total_weight,
            'weight_excess': weight_excess,
            'com_deviation': com_dev,
            'utilisation': utilisation,
            'is_feasible': is_feasible
        }

        return fitness, is_feasible, details

    def adapt_penalty(self, feasibility_ratio):
        """Adapt COM coefficient"""
        if feasibility_ratio < 0.1:
            self.com_adaptive_coefficient *= 0.9
        elif feasibility_ratio > 0.5:
            self.com_adaptive_coefficient *= 1.1

        self.com_adaptive_coefficient = max(0.1, min(10.0, self.com_adaptive_coefficient))