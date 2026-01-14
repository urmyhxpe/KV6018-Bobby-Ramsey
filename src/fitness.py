import math
from geometry import com_deviation


class FitnessEvaluator:

    def __init__(self, container, cylinders, overlap_penalty, bounds_penalty,
                 weight_penalty, com_penalty_base):
        self.container = container
        self.expected_count = len(cylinders)
        self.overlap_penalty = overlap_penalty
        self.bounds_penalty = bounds_penalty
        self.weight_penalty = weight_penalty
        self.com_penalty_base = com_penalty_base
        self.com_adaptive_coefficient = 1.0

    def evaluate(self, solution):
        """ Evaluate fitness """
        total_weight = solution.total_weight()
        com_dev = com_deviation(solution, self.container)
        total_placed = solution.num_placed()

        # Penalty for weight
        weight_excess = max(0, total_weight - self.container.max_weight)
        weight_pen = weight_excess * self.weight_penalty

        # Penalty for COM
        com_penalty = (
                self.com_penalty_base *
                self.com_adaptive_coefficient *
                (com_dev ** 2)
        )

        # Unplaced penalty
        unplaced_count = self.expected_count - total_placed
        unplaced_penalty = unplaced_count * 50.0

        total_penalty = weight_pen + com_penalty + unplaced_penalty

        fitness = 100 - total_penalty

        is_feasible = (
                weight_excess == 0 and
                com_dev == 0 and
                total_placed == self.expected_count
        )

        details = {
            'total_weight': total_weight,
            'weight_excess': weight_excess,
            'com_deviation': com_dev,
            'is_feasible': is_feasible
        }

        return fitness, is_feasible, details

    def adapt_penalty(self, feasibility_ratio):
        """Adapt COM coefficient"""
        if feasibility_ratio < 0.1:
            self.com_adaptive_coefficient *= 0.95
        elif feasibility_ratio > 0.5:
            self.com_adaptive_coefficient *= 1.05

        self.com_adaptive_coefficient = max(0.1, min(10.0, self.com_adaptive_coefficient))