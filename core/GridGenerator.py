"""
GridGenerator.py - Maze Grid Generator
Generates 2D grids with obstacles and optional slippery cells
"""

import random
from typing import List, Tuple, Set


class GridGenerator:
    """
    Produce a 2D grid environment with obstacles and optional slippery cells.

    Cells:
      - 0: free (walkable)
      - 1: obstacle (wall)
      - 2: slippery (ice/mud)
    """

    def __init__(self, grid_size: int, obstacle_prob: float) -> None:
        """
        Initialize grid generator.
        
        Args:
            grid_size: Size of the grid (N x N)
            obstacle_prob: Probability of obstacles (0.0 to 1.0)
        """
        self.grid_size: int = grid_size
        self.obstacle_prob: float = obstacle_prob
        self.grid: List[List[int]] = []

        # Cell type constants
        self.CELL_FREE = 0
        self.CELL_OBSTACLE = 1
        self.CELL_SLIPPERY = 2

    def generate(self) -> List[List[int]]:
        """
        Generate the grid, guaranteeing at least one path from start to goal.
        
        The generator creates a guaranteed monotonic primary path (right/down moves)
        and 1-2 alternative random-walk paths. Protected cells around those paths
        are not filled with obstacles. Some remaining free cells may become slippery.
        
        Returns:
            2D grid where 0=path, 1=obstacle, 2=slippery
        """
        # Start with all free cells
        self.grid = [[self.CELL_FREE for _ in range(self.grid_size)] 
                     for _ in range(self.grid_size)]

        # Generate primary guaranteed path and some alternatives
        primary_path = self._generate_simple_path()
        num_alt_paths = random.randint(1, 2)
        alternative_paths = [self._generate_random_walk_path() 
                           for _ in range(num_alt_paths)]

        # Protected cells (do not place obstacles here)
        protected_cells: Set[Tuple[int, int]] = set(primary_path)
        
        for alt in alternative_paths:
            protected_cells.update(alt)
            # Protect area around alternative paths
            for cell in alt:
                protected_cells.update(self._get_safe_zone(cell, radius=1))

        # Also protect small zones around start and goal
        protected_cells.update(self._get_safe_zone((0, 0), radius=1))
        protected_cells.update(
            self._get_safe_zone((self.grid_size - 1, self.grid_size - 1), radius=1)
        )

        # Fill obstacles in non-protected areas
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if (x, y) not in protected_cells and random.random() < self.obstacle_prob:
                    self.grid[y][x] = self.CELL_OBSTACLE

        # Add slippery zones on some remaining free cells (but not on protected path)
        SLIPPERY_PROB = 0.15
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x] == self.CELL_FREE and (x, y) not in protected_cells:
                    if random.random() < SLIPPERY_PROB:
                        # Avoid start/goal
                        if (x, y) not in [(0, 0), (self.grid_size - 1, self.grid_size - 1)]:
                            self.grid[y][x] = self.CELL_SLIPPERY

        # Ensure start and goal are free
        self.grid[0][0] = self.CELL_FREE
        self.grid[self.grid_size - 1][self.grid_size - 1] = self.CELL_FREE

        return self.grid

    def _generate_simple_path(self) -> List[Tuple[int, int]]:
        """
        Generate a simple path that only moves right or down.
        Guarantees reaching the goal.
        
        Returns:
            List of (x, y) coordinates forming the path
        """
        x, y = 0, 0
        tx, ty = self.grid_size - 1, self.grid_size - 1
        path = [(x, y)]
        
        while x < tx or y < ty:
            if x < tx and y < ty:
                # Randomly choose right or down
                if random.random() < 0.5:
                    x += 1
                else:
                    y += 1
            elif x < tx:
                x += 1
            else:
                y += 1
            path.append((x, y))
        
        return path

    def _generate_random_walk_path(self) -> List[Tuple[int, int]]:
        """
        Generate a random walk path from start to goal.
        May take indirect routes but eventually reaches the goal.
        
        Returns:
            List of (x, y) coordinates forming the path
        """
        x, y = 0, 0
        tx, ty = self.grid_size - 1, self.grid_size - 1
        path = [(x, y)]
        visited = {(x, y)}
        max_steps = self.grid_size * self.grid_size
        steps = 0
        
        while (x != tx or y != ty) and steps < max_steps:
            # Prefer moving towards goal
            dx = 1 if x < tx else (-1 if x > tx else 0)
            dy = 1 if y < ty else (-1 if y > ty else 0)
            
            possible_moves = []
            
            # 70% chance to move towards goal
            if random.random() < 0.7:
                if dx != 0:
                    nx, ny = x + dx, y
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        possible_moves.append((nx, ny))
                if dy != 0:
                    nx, ny = x, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        possible_moves.append((nx, ny))
            
            # Add all unvisited neighbors
            for mdx, mdy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + mdx, y + mdy
                if (0 <= nx < self.grid_size and 0 <= ny < self.grid_size 
                    and (nx, ny) not in visited):
                    possible_moves.append((nx, ny))
            
            if possible_moves:
                x, y = random.choice(possible_moves)
            else:
                # Fallback: move towards goal
                if x < tx:
                    x += 1
                elif x > tx:
                    x -= 1
                elif y < ty:
                    y += 1
                elif y > ty:
                    y -= 1
            
            path.append((x, y))
            visited.add((x, y))
            steps += 1
        
        return path

    def _get_safe_zone(self, center: Tuple[int, int], radius: int = 1) -> Set[Tuple[int, int]]:
        """
        Get all cells within radius of center cell.
        
        Args:
            center: (x, y) center cell
            radius: Radius around center
        
        Returns:
            Set of (x, y) cells in safe zone
        """
        cx, cy = center
        safe_zone: Set[Tuple[int, int]] = set()
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    safe_zone.add((x, y))
        
        return safe_zone

    def __str__(self) -> str:
        """
        Return string representation of the grid.
        
        Returns:
            Grid visualization using Unicode characters
        """
        if not self.grid:
            return "Grid not generated yet"
        
        result = []
        for row in self.grid:
            result.append(' '.join([
                '□' if cell == self.CELL_FREE else
                '■' if cell == self.CELL_OBSTACLE else
                '~' for cell in row
            ]))
        return '\n'.join(result)