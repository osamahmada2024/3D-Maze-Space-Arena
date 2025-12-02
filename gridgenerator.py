import random
from typing import List

class GridGenerator:
    """
    **Role:** Produce a complete 2D grid environment. No external dependencies.
    
    Creates a matrix representing free cells and obstacles with uniform obstacle probability.
    """
    
    def __init__(self, grid_size: int, obstacle_prob: float):
        """
        Initialize the GridGenerator.
        
        Args:
            grid_size (int): The size of the grid (grid_size x grid_size)
            obstacle_prob (float): Probability of a cell being an obstacle (0.0 to 1.0)
        """
        self.grid_size: int = grid_size
        self.obstacle_prob: float = obstacle_prob
        self.grid: List[List[int]] = []
    
    def generate(self) -> List[List[int]]:
        """
        Generate a 2D grid with obstacles placed according to obstacle_prob.
        
        Returns:
            List[List[int]]: 2D grid where 0 = free cell, 1 = obstacle
        """
        # Initialize empty grid
        self.grid = []
        
        # Create grid_size x grid_size matrix
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                # Apply obstacle probability uniformly
                if random.random() < self.obstacle_prob:
                    row.append(1)  # Obstacle
                else:
                    row.append(0)  # Free cell
            self.grid.append(row)
        
        return self.grid
    
    def __str__(self) -> str:
        """String representation of the grid for visualization."""
        if not self.grid:
            return "Grid not generated yet"
        
        result = []
        for row in self.grid:
            result.append(' '.join(['■' if cell == 1 else '□' for cell in row]))
        return '\n'.join(result)
