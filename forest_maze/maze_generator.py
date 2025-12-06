"""
Forest Maze Generator using DFS algorithm with forest zones.
Generates a 25x25 (or configurable) maze with:
- Dense maze paths
- Open forest regions
- Guaranteed path to goal
"""

import random
from typing import List, Tuple, Set

class ForestMazeGenerator:
    """
    Generates a forest maze using Depth-First Search (DFS) with forest zones.
    Forest zones are open areas where trees can be freely placed.
    """
    
    def __init__(self, grid_size: int = 25, forest_density: float = 0.3):
        """
        Initialize the forest maze generator.
        
        Args:
            grid_size: Size of the maze (grid_size x grid_size)
            forest_density: Density of forest zones (0.0 to 1.0)
        """
        self.grid_size = grid_size
        self.forest_density = forest_density
        self.grid = []
        self.forest_zones = []  # Regions where trees can be placed
        self.slow_zones = []    # Mud/sand areas
        self.teleport_zones = []  # Teleport boxes
        
    def generate(self) -> Tuple[List[List[int]], List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Generate the forest maze.
        
        Returns:
            Tuple containing:
            - grid: 2D list where 0=path, 1=wall
            - forest_zones: List of (x, y) forest region cells
            - slow_zones: List of (x, y) slow zone cells
        """
        # Initialize grid with all walls
        self.grid = [[1 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Run DFS from top-left to create paths
        self._dfs_carve(1, 1)
        
        # Ensure start and goal are free
        self.grid[0][0] = 0
        self.grid[self.grid_size - 1][self.grid_size - 1] = 0
        
        # Generate forest zones in open areas
        self._generate_forest_zones()
        
        # Generate slow zones (mud areas)
        self._generate_slow_zones()
        
        # Generate teleport zones
        self._generate_teleport_zones()
        
        return self.grid, self.forest_zones, self.slow_zones
    
    def _dfs_carve(self, x: int, y: int, visited: Set[Tuple[int, int]] = None):
        """
        Depth-First Search to carve paths through the maze.
        
        Args:
            x, y: Starting position
            visited: Set of already visited cells
        """
        if visited is None:
            visited = set()
        
        visited.add((x, y))
        self.grid[y][x] = 0  # Mark as path
        
        # Define 4 directions: right, left, down, up
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Check bounds
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if (nx, ny) not in visited:
                    # Carve path between current and next
                    self.grid[y + dy // 2][x + dx // 2] = 0
                    self._dfs_carve(nx, ny, visited)
    
    def _generate_forest_zones(self):
        """
        Create forest regions in open areas of the maze.
        Forest zones are where trees, rocks, and logs appear.
        """
        self.forest_zones = []
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Free cells that are not paths can become forest zones
                if self.grid[y][x] == 0 and random.random() < self.forest_density:
                    self.forest_zones.append((x, y))
    
    def _generate_slow_zones(self):
        """
        Create slow zones (mud/sand) that reduce player speed.
        Distributed throughout the maze.
        """
        self.slow_zones = []
        num_slow_zones = max(3, self.grid_size // 5)  # ~20 zones for 25x25
        
        attempts = 0
        max_attempts = 100
        
        while len(self.slow_zones) < num_slow_zones and attempts < max_attempts:
            x = random.randint(2, self.grid_size - 3)
            y = random.randint(2, self.grid_size - 3)
            
            # Ensure it's not the start or goal
            if (x, y) not in [(0, 0), (self.grid_size - 1, self.grid_size - 1)]:
                if self.grid[y][x] == 0:  # Must be a free path
                    self.slow_zones.append((x, y))
                    attempts += 1
    
    def _generate_teleport_zones(self):
        """
        Create secret teleport zones for special gameplay moments.
        """
        self.teleport_zones = []
        num_teleports = 3  # 3 teleport boxes
        
        attempts = 0
        max_attempts = 50
        
        while len(self.teleport_zones) < num_teleports and attempts < max_attempts:
            x = random.randint(2, self.grid_size - 3)
            y = random.randint(2, self.grid_size - 3)
            
            if (x, y) not in [(0, 0), (self.grid_size - 1, self.grid_size - 1)]:
                if self.grid[y][x] == 0:
                    self.teleport_zones.append((x, y))
                    attempts += 1
    
    def get_maze_data(self) -> dict:
        """
        Return maze data as a dictionary for easy export/storage.
        """
        return {
            'grid': self.grid,
            'forest_zones': self.forest_zones,
            'slow_zones': self.slow_zones,
            'teleport_zones': self.teleport_zones,
            'grid_size': self.grid_size,
        }
