import matplotlib.pyplot as plt
import matplotlib.patches as patches


def _apply_style(ax, fig, title):
    ax.set_facecolor('#01364C')
    fig.patch.set_facecolor('#01364C')
    ax.tick_params(colors='#F7F8F9')

    for spine in ax.spines.values():
        spine.set_color('#F7F8F9')

    ax.set_xlabel('Width (m)', color='#F7F8F9', fontsize=12)
    ax.set_ylabel('Depth (m)', color='#F7F8F9', fontsize=12)
    ax.set_title(title, color='#F7F8F9', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', facecolor='#01364C', edgecolor='#F7F8F9',
              labelcolor='#F7F8F9', framealpha=0.9)
    ax.grid(True, alpha=0.3, color='#F7F8F9')

    plt.tight_layout()


class ContainerVisualiser:
    """Visualiser"""

    def __init__(self, container):
        self.container = container
        self.solution = None
        self.fitness = None
        self.details = None

    def set_solution(self, solution, fitness=None, details=None):
        """Set the solution to visualise."""
        self.solution = solution
        self.fitness = fitness
        self.details = details

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

        # Label rear door (at y=0)
        ax.text(self.container.width / 2, -margin * 0.4, 'REAR DOOR',
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
        if self.solution and self.solution.placed:
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

        _apply_style(ax, fig, title)

        return fig, ax

