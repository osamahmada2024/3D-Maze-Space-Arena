
import heapq
from collections import deque
from GridUtils import GridUtils
from typing import List, Tuple, Dict, Optional

class PathfindingEngine:
    """Pathfinding engine supporting A*, Dijkstra, BFS, and DFS algorithms."""
    
    def __init__(self, grid: List[List[int]]):
        """Initialize engine with grid"""
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.utils = GridUtils(grid)

    def heuristic(self, node: Tuple[int,int], goal: Tuple[int,int]) -> int:
        """Compute Manhattan distance"""
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    def astar(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """A* search algorithm"""
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

    def dijkstra(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """Dijkstra's algorithm (A* with zero heuristic)"""
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

    def bfs(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """Breadth-First Search algorithm"""
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

    def dfs(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """Depth-First Search algorithm"""
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

    def reconstruct(self, parent: Dict[Tuple[int,int], Tuple[int,int]], 
                   start: Tuple[int,int], goal: Tuple[int,int]) -> List[Tuple[int,int]]:
        """Reconstruct path from parent dictionary"""
        path = []
        current = goal
        
        while current is not None:
            path.append(current)
            current = parent.get(current)
        
        path.reverse()
        return path

    def find_path(self, start: Tuple[int,int], goal: Tuple[int,int], algo: str) -> Optional[List[Tuple[int,int]]]:
        """Select algorithm and compute path"""
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