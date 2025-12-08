"""
GridUtils.py - Grid Utilities
Provides helper functions for grid operations
"""

from typing import List, Tuple


class GridUtils:
    def __init__(self, grid: List[List[int]]):
        """
        Initialize grid utilities.
        
        Args:
            grid: 2D list representing the maze grid
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
    
    def in_bounds(self, x: int, y: int) -> bool:
        """
        Check if coordinates are within grid bounds.
        
        Args:
            x: X coordinate (column)
            y: Y coordinate (row)
        
        Returns:
            True if coordinates are valid
        """
        return 0 <= x < self.cols and 0 <= y < self.rows
    
    def free(self, x: int, y: int) -> bool:
        """
        Check if a cell is free (walkable).
        
        A cell is 'free' if it's 0 (normal) or 2 (slippery).
        It is NOT free if it's 1 (obstacle/ice block).
        
        Args:
            x: X coordinate (column)
            y: Y coordinate (row)
        
        Returns:
            True if cell is walkable
        """
        if not self.in_bounds(x, y):
            return False
        
        return self.grid[y][x] != 1  # 1 = obstacle
    
    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get all valid neighboring cells (4-directional).
        
        Args:
            x: X coordinate (column)
            y: Y coordinate (row)
        
        Returns:
            List of (x, y) tuples for valid neighbors
        """
        neighbors_list = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.free(nx, ny):
                neighbors_list.append((nx, ny))
        
        return neighbors_list
    
    def get_cell_type(self, x: int, y: int) -> int:
        """
        Get the type of cell at given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Cell type: 0 (free), 1 (obstacle), 2 (slippery), -1 (out of bounds)
        """
        if not self.in_bounds(x, y):
            return -1
        return self.grid[y][x]
    
    def set_cell_type(self, x: int, y: int, cell_type: int) -> bool:
        """
        Set the type of cell at given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            cell_type: New cell type
        
        Returns:
            True if successful, False if out of bounds
        """
        if not self.in_bounds(x, y):
            return False
        self.grid[y][x] = cell_type
        return True