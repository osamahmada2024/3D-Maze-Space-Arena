import heapq
from typing import List, Tuple, Optional
from .algorithm_utils import reconstruct_path

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Optional[List[Tuple[int,int]]]:
    """Hill Climbing (Greedy Best-First Search)"""
    def heuristic(node, goal):
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), start))
    parent = {start: None}
    visited = {start}

    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            return reconstruct_path(parent, start, goal)

        for neighbor in grid_utils.neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                h = heuristic(neighbor, goal)
                heapq.heappush(open_set, (h, neighbor))
    
    return []
