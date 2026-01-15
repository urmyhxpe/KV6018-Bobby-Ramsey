import random


class Individual2:
    """ Extended chromosome: ordering + position_choices """

    def __init__(self, num_cylinders, max_positions=20):
        # Order-based encoding for placement sequence
        self.ordering = list(range(num_cylinders))
        random.shuffle(self.ordering)

        # Position selection for each placement step
        #self.position_choices = [
         #   random.randint(0, max_positions - 1)
         #   for _ in range(num_cylinders)
        #]
        self.position_choices = [0] * num_cylinders

        self.max_positions = max_positions
        self.fitness = None
        self.solution = None
        self.is_feasible = False
        self.details = None

    def copy(self):
        new_individual = Individual2(len(self.ordering), self.max_positions)
        new_individual.ordering = self.ordering[:]
        new_individual.position_choices = self.position_choices[:]
        new_individual.fitness = self.fitness
        new_individual.solution = self.solution
        new_individual.is_feasible = self.is_feasible
        new_individual.details = self.details
        return new_individual


class Population2:
    """ Manages the population with extended chromosome """

    def __init__(self, pop_size, num_cylinders, tournament_size, max_positions=20):
        self.pop_size = pop_size
        self.num_cylinders = num_cylinders
        self.tournament_size = tournament_size
        self.max_positions = max_positions
        self.individuals = []
        self.generation = 0
        self.best_ever = None

        for _ in range(pop_size):
            self.individuals.append(Individual2(num_cylinders, max_positions))

    def evaluate_all(self, cylinders, container, placement_func, fitness_evaluator):
        """ Evaluate fitness for whole population """
        for individual in self.individuals:
            # Pass both ordering AND position_choices to placement
            individual.solution = placement_func(
                individual.ordering,
                individual.position_choices,
                cylinders,
                container
            )
            fitness, is_feasible, details = fitness_evaluator.evaluate(individual.solution)
            individual.fitness = fitness
            individual.is_feasible = is_feasible
            individual.details = details

        # Track best solution (higher is better)
        current_best = self.get_best()
        if self.best_ever is None or current_best.fitness > self.best_ever.fitness:
            self.best_ever = current_best.copy()

    def tournament_selection(self):
        """ Select one individual using tournament selection """
        tournament = random.sample(self.individuals, self.tournament_size)
        return max(tournament, key=lambda ind: ind.fitness)

    def ordered_crossover(self, parent1, parent2):
        """ Perform Ordered Crossover (OX) for ordering part """
        size = len(parent1.ordering)
        child_ordering = [None] * size

        start = random.randint(0, size - 2)
        end = random.randint(start + 1, size - 1)

        for i in range(start, end + 1):
            child_ordering[i] = parent1.ordering[i]

        parent2_genes = []
        for gene in parent2.ordering:
            if gene not in child_ordering:
                parent2_genes.append(gene)

        gene_index = 0
        for i in range(size):
            if child_ordering[i] is None:
                child_ordering[i] = parent2_genes[gene_index]
                gene_index += 1

        return child_ordering

    def uniform_crossover_positions(self, parent1, parent2):
        """ Uniform crossover for position_choices """
        child_positions = []
        for i in range(len(parent1.position_choices)):
            if random.random() < 0.5:
                child_positions.append(parent1.position_choices[i])
            else:
                child_positions.append(parent2.position_choices[i])
        return child_positions

    def crossover(self, parent1, parent2):
        """ Combined crossover for extended chromosome """
        child = Individual2(self.num_cylinders, self.max_positions)
        child.ordering = self.ordered_crossover(parent1, parent2)
        child.position_choices = self.uniform_crossover_positions(parent1, parent2)
        return child

    def mutate(self, individual, ordering_rate, position_rate):
        """Mutation for positions determined by the probability parameters"""
        # Swap mutation for ordering
        if random.random() < ordering_rate:
            size = len(individual.ordering)
            pos1 = random.randint(0, size - 1)
            pos2 = random.randint(0, size - 1)
            while pos2 == pos1:
                pos2 = random.randint(0, size - 1)
            individual.ordering[pos1], individual.ordering[pos2] = \
                individual.ordering[pos2], individual.ordering[pos1]

        # Random reset mutation for position choices
        for i in range(len(individual.position_choices)):
            if random.random() < position_rate:
                individual.position_choices[i] = random.randint(0, self.max_positions - 1)

    def evolve(self, ordering_mutation_rate, position_mutation_rate, elitism):
        """ Create next generation """
        new_population = []

        if elitism:
            best = self.get_best()
            new_population.append(best.copy())

        while len(new_population) < self.pop_size:
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()

            child = self.crossover(parent1, parent2)
            self.mutate(child, ordering_mutation_rate, position_mutation_rate)

            new_population.append(child)

        self.individuals = new_population
        self.generation += 1

    def get_best(self):
        """ Return the individual with the highest fitness """
        return max(self.individuals, key=lambda ind: ind.fitness)

    def get_stats(self, adaptive_coefficient):
        """ Calculate population statistics """
        every_fitness = [ind.fitness for ind in self.individuals if ind.fitness is not None]
        if not every_fitness:
            return {"best": None, "worst": None, "average": None}

        feasible_count = 0
        for ind in self.individuals:
            if ind.is_feasible:
                feasible_count += 1

        return {
            "best": max(every_fitness),
            "worst": min(every_fitness),
            "average": sum(every_fitness) / len(every_fitness),
            "generation": self.generation,
            "feasibility_ratio": feasible_count / len(self.individuals),
            "adaptive_coefficient": adaptive_coefficient
        }

    def get_feasibility_ratio(self):
        """ Calculate proportion of feasible individuals """
        feasible_count = 0
        for ind in self.individuals:
            if ind.is_feasible:
                feasible_count += 1
        return feasible_count / len(self.individuals)


class EvolutionaryAlgorithm2:
    """ EA with extended chromosome (ordering + position_choices) """

    def __init__(self, container, cylinders, placement_func, fitness_evaluator,
                 pop_size, tournament_size, ordering_mutation_rate,
                 position_mutation_rate, elitism, max_positions=20):
        self.container = container
        self.cylinders = cylinders
        self.placement_func = placement_func
        self.fitness_evaluator = fitness_evaluator
        self.pop_size = pop_size
        self.tournament_size = tournament_size
        self.ordering_mutation_rate = ordering_mutation_rate
        self.position_mutation_rate = position_mutation_rate
        self.elitism = elitism
        self.max_positions = max_positions
        self.num_cylinders = len(cylinders)

        # Initialise population with extended chromosome
        self.population = Population2(
            pop_size,
            self.num_cylinders,
            tournament_size,
            max_positions
        )

        self.history = []

    def run(self, max_generations, target_fitness, track_output):
        """ Run the evolutionary algorithm """
        # Initial evaluation
        self.population.evaluate_all(
            self.cylinders, self.container,
            self.placement_func, self.fitness_evaluator
        )

        stats = self.population.get_stats(self.fitness_evaluator.com_adaptive_coefficient)
        feasibility_ratio = self.population.get_feasibility_ratio()
        self.history.append(stats)

        self.fitness_evaluator.adapt_penalty(feasibility_ratio)

        if track_output:
            best_feasible = self.population.best_ever.is_feasible
            print(f"Generation 0: Best={stats['best']:.3f}, "
                  f"Avg={stats['average']:.3f}, "
                  f"Feasible={stats['feasibility_ratio']:.0%}, "
                  f"Solution found={best_feasible}")

        # Main evolution loop
        for gen in range(1, max_generations + 1):
            self.population.evolve(
                self.ordering_mutation_rate,
                self.position_mutation_rate,
                self.elitism
            )

            self.population.evaluate_all(
                self.cylinders, self.container,
                self.placement_func, self.fitness_evaluator
            )

            feasibility_ratio = self.population.get_feasibility_ratio()
            self.fitness_evaluator.adapt_penalty(feasibility_ratio)
            stats = self.population.get_stats(self.fitness_evaluator.com_adaptive_coefficient)
            self.history.append(stats)

            if track_output and gen % 10 == 0:
                best_feasible = self.population.best_ever.is_feasible
                print(f"Generation {gen}: Best={stats['best']:.4f}, "
                      f"Avg={stats['average']:.4f}, "
                      f"Feasible={stats['feasibility_ratio']:.0%}, "
                      f"Solution found={best_feasible}")

            if target_fitness is not None:
                if stats['best'] >= target_fitness:
                    if track_output:
                        print(f"Target fitness reached at generation {gen}")
                    break

        return self.get_best_solution()

    def get_best_solution(self):
        """ Return the best solution found """
        return self.population.best_ever.solution

    def get_best_individual(self):
        """ Return the best individual found """
        return self.population.best_ever

    def get_history(self):
        """ Return the evolution history """
        return self.history