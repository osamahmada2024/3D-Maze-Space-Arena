"""
core/PathfindingEngine.py - Pathfinding Algorithms
Supports A*, Dijkstra, BFS, and DFS algorithms
"""

import heapq
from collections import deque
from typing import List, Tuple, Dict, Optional

# Try to import GridUtils from same package
try:
    from .GridUtils import GridUtils
except ImportError:
    from GridUtils import GridUtils


class PathfindingEngine:
    """Pathfinding engine supporting A*, Dijkstra, BFS, and DFS algorithms."""
    
    def __init__(self, grid: List[List[int]]):
        """
        Initialize engine with grid.
        
        Args:
            grid: 2D grid where 0=free, 1=obstacle, 2=slippery
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.utils = GridUtils(grid)

    def heuristic(self, node: Tuple[int, int], goal: Tuple[int, int]) -> int:
        """
        Compute Manhattan distance heuristic.
        
        Args:
            node: Current position
            goal: Goal position
        
        Returns:
            Manhattan distance
        """
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    def astar(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        A* search algorithm.
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
        
        Returns:
            List of positions from start to goal, or empty list if no path
        """
        open_set = []
        heapq.heappush(open_set, (0, start))
        parent = {start: None}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == goal:
                return self.reconstruct(parent, start, goal)

            for neighbor in self.utils.neighbors(*current):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    parent[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
        
        return []

    def dijkstra(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Dijkstra's algorithm (A* with zero heuristic).
        
        Args:
            start: Starting position
            goal: Goal position
        
        Returns:
            List of positions from start to goal
        """
        open_set = []
        heapq.heappush(open_set, (0, start))
        parent = {start: None}
        g_score = {start: 0}

        while open_set:
            current_cost, current = heapq.heappop(open_set)
            
            if current == goal:
                return self.reconstruct(parent, start, goal)

            for neighbor in self.utils.neighbors(*current):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    parent[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    heapq.heappush(open_set, (tentative_g_score, neighbor))
        
        return []

    def bfs(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Breadth-First Search algorithm.
        
        Args:
            start: Starting position
            goal: Goal position
        
        Returns:
            List of positions from start to goal
        """
        queue = deque([start])
        parent = {start: None}
        visited = {start}

        while queue:
            current = queue.popleft()
            
            if current == goal:
                return self.reconstruct(parent, start, goal)

            for neighbor in self.utils.neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        
        return []

    def dfs(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Depth-First Search algorithm.
        
        Args:
            start: Starting position
            goal: Goal position
        
        Returns:
            List of positions from start to goal
        """
        stack = [start]
        parent = {start: None}
        visited = {start}

        while stack:
            current = stack.pop()
            
            if current == goal:
                return self.reconstruct(parent, start, goal)

            for neighbor in self.utils.neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    stack.append(neighbor)
        
        return []

    def reconstruct(self, parent: Dict[Tuple[int, int], Tuple[int, int]], 
                   start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Reconstruct path from parent dictionary.
        
        Args:
            parent: Dictionary mapping each node to its parent
            start: Starting position
            goal: Goal position
        
        Returns:
            List of positions from start to goal
        """
        path = []
        current = goal
        
        while current is not None:
            path.append(current)
            current = parent.get(current)
        
        path.reverse()
        return path

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], algo: str) -> Optional[List[Tuple[int, int]]]:
        """
        Select algorithm and compute path.
        
        Args:
            start: Starting position
            goal: Goal position
            algo: Algorithm name ("astar", "dijkstra", "bfs", "dfs")
        
        Returns:
            List of positions from start to goal
        """
        algo_lower = algo.lower()
        
        if algo_lower in ("a*", "astar", "a* search"):
            return self.astar(start, goal)
        elif algo_lower == "dijkstra":
            return self.dijkstra(start, goal)
        elif algo_lower == "bfs":
            return self.bfs(start, goal)
        elif algo_lower == "dfs":
            return self.dfs(start, goal)
        else:
            print(f"Warning: Unknown algorithm '{algo}', using A* as default")
            return self.astar(start, goal)