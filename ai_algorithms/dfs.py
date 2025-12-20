from typing import List, Tuple, Optional
from .algorithm_utils import reconstruct_path

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Optional[List[Tuple[int,int]]]:
    """Depth-First Search algorithm"""
    stack = [start]
    parent = {start: None}
    visited = {start}

    while stack:
        current = stack.pop()
        
        if current == goal:
            return reconstruct_path(parent, start, goal)

        for neighbor in grid_utils.neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)
    
    return []
