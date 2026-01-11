import matplotlib.pyplot as plt
import matplotlib.patches as patches


def _apply_style(ax, fig, title, xlabel, ylabel):
    ax.set_facecolor('#01364C')
    fig.patch.set_facecolor('#01364C')
    ax.tick_params(colors='#F7F8F9')

    for spine in ax.spines.values():
        spine.set_color('#F7F8F9')

    ax.set_xlabel(xlabel, color='#F7F8F9', fontsize=12)
    ax.set_ylabel(ylabel, color='#F7F8F9', fontsize=12)
    ax.set_title(title, color='#F7F8F9', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', facecolor='#01364C', edgecolor='#F7F8F9',
              labelcolor='#F7F8F9', framealpha=0.9)
    ax.grid(True, alpha=0.3, color='#F7F8F9')


class ContainerVisualiser:
    """Visualiser"""

    def __init__(self, container):
        self.container = container
        self.solution = None
        self.fitness = None
        self.details = None
        self.expected_count = None

    def set_solution(self, solution, fitness=None, details=None, expected_count=None):
        """Set the solution to visualise."""
        self.solution = solution
        self.fitness = fitness
        self.details = details
        self.expected_count = expected_count

    def draw(self, title="Container Packing Solution"):
        """Draw the current solution"""
        fig, ax = plt.subplots(figsize=(12, 10))

        # Set up plot area
        margin = max(self.container.width, self.container.depth) * 0.1
        ax.set_xlim(-margin, self.container.width + margin)
        ax.set_ylim(-margin, self.container.depth + margin)
        ax.set_aspect('equal')

        # Draw container boundary
        container_rect = patches.Rectangle(
            (0, 0), self.container.width, self.container.depth,
            fill=False, edgecolor='#F4BA02', linewidth=3,
            label='Container boundary'
        )
        ax.add_patch(container_rect)

        # Label rear door (y = depth)
        ax.text(self.container.width / 2, self.container.depth + margin * 0.4,
                'REAR DOOR',
                ha='center', va='center', color='#F4BA02',
                fontsize=11, fontweight='bold')

        # Draw centre of mass valid zone (central 60%)
        min_x, max_x, min_y, max_y = self.container.centre_zone_bounds()
        zone_width = max_x - min_x
        zone_height = max_y - min_y
        com_zone = patches.Rectangle(
            (min_x, min_y), zone_width, zone_height,
            fill=True, facecolor='#2E7D32', alpha=0.2,
            edgecolor='#2E7D32', linewidth=2, linestyle='--',
            label='Valid CoM zone (60%)'
        )
        ax.add_patch(com_zone)

        # Draw placed cylinders
        placed_count = 0
        if self.solution and self.solution.placed:
            placed_count = len(self.solution.placed)
            for order, placed in enumerate(self.solution.placed, start=1):
                radius = placed.cylinder.diameter / 2
                circle = patches.Circle(
                    (placed.x, placed.y), radius,
                    fill=True, facecolor='#99D9DD', alpha=0.7,
                    edgecolor='#01364C', linewidth=2
                )
                ax.add_patch(circle)

                # Label orders
                ax.text(placed.x, placed.y, str(order), fontsize=10,
                        ha='center', va='center',
                        color='#01364C', fontweight='bold')

            # Draw centre of mass marker
            com_x, com_y = self.solution.center_of_mass()
            ax.plot(com_x, com_y, 'x', color='#D32F2F', markersize=15,
                    markeredgewidth=3, label=f'Centre of Mass ({com_x:.1f}, {com_y:.1f})')

        # Placement count annotation
        if self.expected_count is not None:
            status = "✓" if placed_count == self.expected_count else "✗"
            colour = '#2E7D32' if placed_count == self.expected_count else '#D32F2F'
            count_text = f"Placed: {placed_count} / {self.expected_count} {status}"
        else:
            colour = '#F7F8F9'
            count_text = f"Placed: {placed_count}"

        ax.text(self.container.width, -margin * 0.5, count_text,
                ha='right', va='center', color=colour,
                fontsize=11, fontweight='bold')

        _apply_style(ax, fig, title, 'Width (m)', 'Depth (m)')
        plt.tight_layout()

        return fig, ax


class EvolutionVisualiser:
    """ Visualiser for EA progress across generations """

    def __init__(self, history):
        self.history = history

    def draw(self, title="Evolutionary Algorithm Progress"):
        """ Draw fitness and feasibility progress """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        generations = [stats['generation'] for stats in self.history]
        best_fitness = [stats['best'] for stats in self.history]
        avg_fitness = [stats['average'] for stats in self.history]
        feasibility = [stats['feasibility_ratio'] * 100 for stats in self.history]

        # Top plot: Fitness over generations
        ax1.plot(generations, best_fitness, color='#2E7D32', linewidth=2, label='Best Fitness')
        ax1.plot(generations, avg_fitness, color='#F4BA02', linewidth=2, label='Average Fitness')
        _apply_style(ax1, fig, 'Fitness Progress', 'Generation', 'Fitness (lower is better)')

        # Bottom plot: Feasibility ratio over generations
        ax2.plot(generations, feasibility, color='#99D9DD', linewidth=2, label='Feasibility %')
        ax2.axhline(y=100, color='#2E7D32', linestyle='--', linewidth=1, label='100% Target')
        ax2.set_ylim(0, 105)
        _apply_style(ax2, fig, 'Population Feasibility', 'Generation', 'Feasibility (%)')
        ax2.legend(loc='lower right', facecolor='#01364C', edgecolor='#F7F8F9',
                   labelcolor='#F7F8F9', framealpha=0.9)

        fig.suptitle(title, color='#F7F8F9', fontsize=16, fontweight='bold')
        plt.tight_layout()

        return fig, (ax1, ax2)