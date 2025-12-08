from typing import List, Tuple

class GridUtils:
    def _init_(self, grid: List[List[int]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows
    
    def free(self, x: int, y: int) -> bool:
        """
        A cell is 'free' if it's 0 (normal) or 2 (slippery).
        It is NOT free if it's 1 (obstacle/ice block).
        """
        if not self.in_bounds(x, y):
            return False
        
        return self.grid[y][x] != 1   # 1 = obstacle
    
    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        neighbors_list = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.free(nx, ny):
                neighbors_list.append((nx, ny))
        
        return neighbors_list