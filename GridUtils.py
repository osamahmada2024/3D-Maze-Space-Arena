from typing import List, Tuple

# ==============================
# Class: GridUtils
# Role: Provide safe access utilities for any grid. Does not modify the grid.
# Responsibilities:
#   • Validate coordinates.
#   • Check if a cell is traversable.
#   • Return the valid neighbors of a cell.
# Required Inputs:
#   • grid: List[List[int]]
# Provided Outputs:
#   • neighbors: List[Tuple[int,int]]
#   • free: bool
# Public Methods:
#   • in_bounds(x: int, y: int) -> bool
#   • free(x: int, y: int) -> bool
#   • neighbors(x: int, y: int) -> List[Tuple[int,int]]
# Internal State:
#   • self.grid: List[List[int]]
#   • self.rows: int
#   • self.cols: int
# ==============================

class GridUtils:
    def __init__(self, grid: List[List[int]]):
        """Initialize GridUtils with a 2D grid."""
        self.grid: List[List[int]] = grid
        self.rows: int = len(grid)
        self.cols: int = len(grid[0]) if grid else 0

    # ==============================
    # Public Method: in_bounds
    # ==============================
    def in_bounds(self, x: int, y: int) -> bool:
        """Check if (x, y) coordinates are inside the grid boundaries."""
        return 0 <= x < self.cols and 0 <= y < self.rows

    # ==============================
    # Public Method: free
    # ==============================
    def free(self, x: int, y: int) -> bool:
        """Check if a cell is free (0) and within grid bounds."""
        return self.in_bounds(x, y) and self.grid[y][x] == 0

    # ==============================
    # Public Method: neighbors
    # ==============================
    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Return a list of neighboring cells that are free.
        
        Only considers cardinal directions: up, down, left, right.
        """
        directions: List[Tuple[int, int]] = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        neighbors_list: List[Tuple[int, int]] = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.free(nx, ny):
                neighbors_list.append((nx, ny))

        return neighbors_list
