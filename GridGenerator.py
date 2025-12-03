import random
from typing import List

class GridGenerator:
    """
    Class: GridGenerator
    Purpose:
        Generate a 2D grid environment with free cells and obstacles.

    Features:
        • Create a square grid of size grid_size x grid_size.
        • Populate obstacles randomly based on obstacle probability.
        • Provides a clean string representation for debugging.

    Parameters:
        grid_size (int): Size of the grid (number of rows/columns).
        obstacle_prob (float): Probability (0.0–1.0) that a cell is an obstacle.
    """

    def __init__(self, grid_size: int, obstacle_prob: float):
        self.grid_size: int = grid_size
        self.obstacle_prob: float = obstacle_prob
        self.grid: List[List[int]] = []

    # ------------------------------------------------------
    # Public Method: Generate Grid
    # ------------------------------------------------------
    def generate(self) -> List[List[int]]:
        """
        Generate a 2D grid.

        Returns:
            List[List[int]]: 0 = free cell, 1 = obstacle
        """
        self.grid = []

        for y in range(self.grid_size):
            row = []
            for x in range(self.grid_size):
                val = 1 if random.random() < self.obstacle_prob else 0
                row.append(val)
            self.grid.append(row)

        return self.grid

    # ------------------------------------------------------
    # Optional Helper: String Representation
    # ------------------------------------------------------
    def __str__(self) -> str:
        """
        Return a visual representation of the grid using symbols:
            □ = free cell
            ■ = obstacle
        """
        if not self.grid:
            return "Grid not generated yet"

        return '\n'.join(
            ' '.join('■' if cell == 1 else '□' for cell in row)
            for row in self.grid
        )
