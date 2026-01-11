import random


class Individual:
    """ Represents a single solution in the population """

    def __init__(self, num_cylinders):
        # Order-based encoding
        self.chromosome = list(range(num_cylinders))
        random.shuffle(self.chromosome)
        self.fitness = None
        self.solution = None  # Stores the decoded Solution
        self.is_feasible = False
        self.details = None

    def copy(self):
        new_individual = Individual(len(self.chromosome))
        new_individual.chromosome = self.chromosome[:]
        new_individual.fitness = self.fitness
        new_individual.solution = self.solution
        new_individual.is_feasible = self.is_feasible
        new_individual.details = self.details
        return new_individual


class Population:
    """ Manages the population of individuals and evolutionary operations """

    def __init__(self, pop_size, num_cylinders, tournament_size):
        self.pop_size = pop_size
        self.num_cylinders = num_cylinders
        self.tournament_size = tournament_size
        self.individuals = []
        self.generation = 0
        self.best_ever = None

        # Initialise population with random individuals
        for _ in range(pop_size):
            self.individuals.append(Individual(num_cylinders))

    def evaluate_all(self, cylinders, container, placement_func, fitness_evaluator):
        """ Evaluate fitness for whole population """
        for individual in self.individuals:
            # Decode chromosome using placement algorithm
            individual.solution = placement_func(individual.chromosome, cylinders, container)

            # Calculate fitness
            fitness, is_feasible, details = fitness_evaluator.evaluate(individual.solution)
            individual.fitness = fitness
            individual.is_feasible = is_feasible
            individual.details = details

        # Tracking the best solution (higher is better)
        current_best = self.get_best()
        if self.best_ever is None or current_best.fitness > self.best_ever.fitness:
            self.best_ever = current_best.copy()

    def tournament_selection(self):
        """ Select one individual using tournament selection """
        tournament = random.sample(self.individuals, self.tournament_size)
        return max(tournament, key=lambda ind: ind.fitness)

    def ordered_crossover(self, parent1, parent2):
        """ Perform Ordered Crossover (OX) to create a child """
        size = len(parent1.chromosome)
        child = Individual(size)
        child.chromosome = [None] * size

        # Select random segment from parent1
        start = random.randint(0, size - 2)
        end = random.randint(start + 1, size - 1)

        # Copy segment from parent1 to child
        for i in range(start, end + 1):
            child.chromosome[i] = parent1.chromosome[i]

        # Fill remaining positions from parent2 in order
        parent2_genes = []
        for gene in parent2.chromosome:
            if gene not in child.chromosome:
                parent2_genes.append(gene)

        # Fill empty positions
        gene_index = 0
        for i in range(size):
            if child.chromosome[i] is None:
                child.chromosome[i] = parent2_genes[gene_index]
                gene_index += 1

        return child

    def swap_mutation(self, individual, mutation_rate):
        """ Apply swap mutation with given probability """
        if random.random() < mutation_rate:
            size = len(individual.chromosome)
            pos1 = random.randint(0, size - 1)
            pos2 = random.randint(0, size - 1)
            while pos2 == pos1:
                pos2 = random.randint(0, size - 1)

            # Swap the two positions
            individual.chromosome[pos1], individual.chromosome[pos2] = \
                individual.chromosome[pos2], individual.chromosome[pos1]

    def evolve(self, mutation_rate, elitism):
        """ Create next generation through selection, crossover, and mutation """
        new_population = []

        # Elitism: keep the best individual
        if elitism:
            best = self.get_best()
            new_population.append(best.copy())

        # Fill rest of population
        while len(new_population) < self.pop_size:
            # Select parents
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()

            # Create offspring through crossover
            child = self.ordered_crossover(parent1, parent2)

            # Apply mutation
            self.swap_mutation(child, mutation_rate)

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
                feasible_count = feasible_count + 1

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
                feasible_count = feasible_count + 1
        return feasible_count / len(self.individuals)


class EvolutionaryAlgorithm:
    """ Main class coordinating the evolutionary optimisation process """

    def __init__(self, container, cylinders, placement_func, fitness_evaluator,
                 pop_size, tournament_size, mutation_rate, elitism):
        self.container = container
        self.cylinders = cylinders
        self.placement_func = placement_func
        self.fitness_evaluator = fitness_evaluator
        self.pop_size = pop_size
        self.tournament_size = tournament_size
        self.mutation_rate = mutation_rate
        self.elitism = elitism
        self.num_cylinders = len(cylinders)

        # Initialise population
        self.population = Population(pop_size, self.num_cylinders, tournament_size)

        # History tracking
        self.history = []

    def run(self, max_generations, target_fitness, track_output):
        """ Run the evolutionary algorithm for specified generations """
        # Initial evaluation
        self.population.evaluate_all(
            self.cylinders, self.container,
            self.placement_func, self.fitness_evaluator
        )

        stats = self.population.get_stats(self.fitness_evaluator.com_adaptive_coefficient)
        feasibility_ratio = self.population.get_feasibility_ratio()

        self.history.append(stats)

        # Adapt penalty based on feasibility
        self.fitness_evaluator.adapt_penalty(feasibility_ratio)

        if track_output:
            best_feasible = self.population.best_ever.is_feasible
            print(f"Generation 0: Best={stats['best']:.3f}, "
                  f"Avg={stats['average']:.3f}, "
                  f"Feasible={stats['feasibility_ratio']:.0%}, "
                  f"Solution found={best_feasible}")

        # Main evolution loop
        for gen in range(1, max_generations + 1):
            # Create next generation
            self.population.evolve(self.mutation_rate, self.elitism)

            # Evaluate new population
            self.population.evaluate_all(
                self.cylinders, self.container,
                self.placement_func, self.fitness_evaluator
            )

            stats = self.population.get_stats(self.fitness_evaluator.com_adaptive_coefficient)
            self.history.append(stats)

            if track_output and gen % 10 == 0:
                best_feasible = self.population.best_ever.is_feasible
                print(f"Generation {gen}: Best={stats['best']:.4f}, "
                      f"Avg={stats['average']:.4f}, "
                      f"Feasible={stats['feasibility_ratio']:.0%}, "
                      f"Solution found={best_feasible}")

            # Check for early stopping
            if target_fitness is not None:
                if stats['best'] >= target_fitness:
                    if track_output:
                        print(f"Target fitness reached at generation {gen}")
                    break

        return self.get_best_solution()

    def get_best_solution(self):
        """ Return the best solution found """
        return self.population.best_ever.solution

    def get_best_chromosome(self):
        """ Return the best chromosome found """
        return self.population.best_ever.chromosome

    def get_history(self):
        """ Return the evolution history """
        return self.history