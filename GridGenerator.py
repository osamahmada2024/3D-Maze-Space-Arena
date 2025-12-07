import random
from typing import List, Tuple, Set

class GridGenerator:
    """
    Role: Produce a complete 2D grid environment. 
    
    Generates a matrix with: 0 = free cell (normal), 1 = obstacle (Ice Block), 2 = slippery cell
    """
    
    def _init_(self, grid_size: int, obstacle_prob: float):
        self.grid_size: int = grid_size
        self.obstacle_prob: float = obstacle_prob
        self.grid: List[List[int]] = []
        # Constants for clarity
        self.CELL_FREE = 0
        self.CELL_OBSTACLE = 1
        self.CELL_SLIPPERY = 2
    
    def generate(self) -> List[List[int]]:
        """
        Generate a 2D grid with obstacles and slippery zones.
        """
        # Initialize empty grid (all free)
        self.grid = [[self.CELL_FREE for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Generate PRIMARY guaranteed path (simple and direct)
        primary_path = self._generate_simple_path()
        
        # Generate 1-2 additional alternative paths for variety
        num_alt_paths = random.randint(1, 2)
        alternative_paths = []
        for _ in range(num_alt_paths):
            alt_path = self._generate_random_walk_path()
            alternative_paths.append(alt_path)
        
        # Combine all protected cells
        protected_cells: Set[Tuple[int, int]] = set(primary_path)
        for alt_path in alternative_paths:
            # Protect path cells
            protected_cells.update(alt_path)
            # Protect a safe zone around the path
            for cell in alt_path:
                protected_cells.update(self._get_safe_zone(cell, radius=1))
        
        # 1. Fill grid with obstacles (1) - Ice Blocks
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if (x, y) not in protected_cells:
                    val = self.CELL_OBSTACLE if random.random() < self.obstacle_prob else self.CELL_FREE
                    self.grid[y][x] = val
        
        # 2. Add Slippery Zones (2) - Ultra-Slippery
        SLIPPERY_PROB = 0.15 # 15% of free cells become slippery
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # If the cell is free (0) and we have a chance to add a slippery floor
                if self.grid[y][x] == self.CELL_FREE and random.random() < SLIPPERY_PROB:
                    # Ensure it's not the start or goal point
                    if (x, y) != (0, 0) and (x, y) != (self.grid_size - 1, self.grid_size - 1):
                        self.grid[y][x] = self.CELL_SLIPPERY 
                        
        # Ensure Start (0,0) and Goal (N-1, N-1) are always normal free cells (0)
        self.grid[0][0] = self.CELL_FREE
        self.grid[self.grid_size - 1][self.grid_size - 1] = self.CELL_FREE
                    
        return self.grid
    
    def _generate_simple_path(self) -> List[Tuple[int, int]]:
        """
        Generate a SIMPLE guaranteed path from (0,0) to (grid_size-1, grid_size-1).
        This path only moves RIGHT or DOWN, ensuring it ALWAYS reaches the goal.
        
        Returns:
            List[Tuple[int, int]]: List of (x, y) coordinates forming the path
        """
        x, y = 0, 0
        target_x, target_y = self.grid_size - 1, self.grid_size - 1
        path = [(x, y)]
        
        # Move right and down only (guaranteed to reach target)
        while x < target_x or y < target_y:
            if x < target_x and y < target_y:
                # Both directions available - choose randomly
                if random.random() < 0.5:
                    x += 1
                else:
                    y += 1
            elif x < target_x:
                # Can only move right
                x += 1
            else:
                # Can only move down
                y += 1
            
            path.append((x, y))
        
        return path
    
    def _generate_random_walk_path(self) -> List[Tuple[int, int]]:
        """
        Generate a random walk path that eventually reaches the goal.
        Can move in all 4 directions, but biased towards the goal.
        
        Returns:
            List[Tuple[int, int]]: List of (x, y) coordinates forming the path
        """
        x, y = 0, 0
        target_x, target_y = self.grid_size - 1, self.grid_size - 1
        path = [(x, y)]
        visited = {(x, y)}
        
        max_steps = self.grid_size * self.grid_size  # Prevent infinite loops
        steps = 0
        
        while (x != target_x or y != target_y) and steps < max_steps:
            # Calculate direction to goal
            dx = 1 if x < target_x else (-1 if x > target_x else 0)
            dy = 1 if y < target_y else (-1 if y > target_y else 0)
            
            # Possible moves (4-directional)
            possible_moves = []
            
            # Bias towards goal (70% chance)
            if random.random() < 0.7:
                if dx != 0:
                    nx, ny = x + dx, y
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        possible_moves.append((nx, ny))
                
                if dy != 0:
                    nx, ny = x, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        possible_moves.append((nx, ny))
            
            # Also consider other directions (for variety)
            for move_dx, move_dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + move_dx, y + move_dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    if (nx, ny) not in visited:
                        possible_moves.append((nx, ny))
            
            if possible_moves:
                x, y = random.choice(possible_moves)
                path.append((x, y))
                visited.add((x, y))
            else:
                # If stuck, move towards goal directly
                if x < target_x:
                    x += 1
                elif x > target_x:
                    x -= 1
                elif y < target_y:
                    y += 1
                elif y > target_y:
                    y -= 1
                
                path.append((x, y))
                visited.add((x, y))
            
            steps += 1
        
        return path
    
    def _get_safe_zone(self, center: Tuple[int, int], radius: int = 1) -> Set[Tuple[int, int]]:
        """
        Get all cells within a radius around a center point.
        
        Args:
            center: (x, y) center coordinate
            radius: radius around center
            
        Returns:
            Set of (x, y) coordinates in the safe zone
        """
        cx, cy = center
        safe_zone = set()
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    safe_zone.add((x, y))
        
        return safe_zone
    
    def _str_(self) -> str:
        """String representation of the grid for visualization."""
        if not self.grid:
            return "Grid not generated yet"
        
        result = []
        for row in self.grid:
            result.append(' '.join([
                '□' if cell == self.CELL_FREE else 
                '■' if cell == self.CELL_OBSTACLE else 
                '~' for cell in row  # Assuming ~ for slippery
            ]))
        return '\n'.join(result)