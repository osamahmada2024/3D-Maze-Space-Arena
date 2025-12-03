
import random
from typing import List, Tuple, Set

class GridGenerator:
    """
    **Role:** Produce a complete 2D grid environment. No external dependencies.
    
    Creates a matrix representing free cells and obstacles with uniform obstacle probability,
    ensuring there's always a path from top-left to bottom-right.
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
        Generate a 2D grid with obstacles placed according to obstacle_prob,
        while ensuring a valid path exists from (0,0) to (grid_size-1, grid_size-1).
        
        Returns:
            List[List[int]]: 2D grid where 0 = free cell, 1 = obstacle
        """
        # Initialize empty grid (all free)
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Generate 2-3 guaranteed paths to make it more interesting
        num_paths = random.randint(2, 3)
        protected_cells: Set[Tuple[int, int]] = set()
        
        for _ in range(num_paths):
            path = self._generate_random_path()
            protected_cells.update(path)
        
        # Fill remaining cells with obstacles according to obstacle_prob
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Don't place obstacles on protected path cells
                if (x, y) not in protected_cells:
                    if random.random() < self.obstacle_prob:
                        self.grid[y][x] = 1
        
        return self.grid
    
    def _generate_random_path(self) -> List[Tuple[int, int]]:
        """
        Generate a random path from (0,0) to (grid_size-1, grid_size-1).
        Can move right, down, or diagonally.
        
        Returns:
            List[Tuple[int, int]]: List of (x, y) coordinates forming the path
        """
        x, y = 0, 0
        target_x, target_y = self.grid_size - 1, self.grid_size - 1
        path = [(x, y)]
        
        while x < target_x or y < target_y:
            # Possible moves: right, down, diagonal
            possible_moves = []
            
            if x < target_x:
                possible_moves.append((1, 0))  # Right
            if y < target_y:
                possible_moves.append((0, 1))  # Down
            if x < target_x and y < target_y:
                possible_moves.append((1, 1))  # Diagonal
            
            # Choose random move
            dx, dy = random.choice(possible_moves)
            x += dx
            y += dy
            path.append((x, y))
        
        return path
    
    def __str__(self) -> str:
        """String representation of the grid for visualization."""
        if not self.grid:
            return "Grid not generated yet"
        
        result = []
        for row in self.grid:
            result.append(' '.join(['■' if cell == 1 else '□' for cell in row]))
        return '\n'.join(result)