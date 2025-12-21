from collections import deque
from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Tuple[Optional[List[Tuple[int,int]]], int]:
    """Breadth-First Search algorithm. Returns (path, nodes_explored)."""
    queue = deque([start])
    parent = {start: None}
    visited = {start}

    while queue:
        current = queue.popleft()
        
        if current == goal:
            # Reconstruct path
            path = []
            node = goal
            while node:
                path.append(node)
                node = parent[node]
            path.reverse()
            return path, len(visited)

        for neighbor in grid_utils.neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
    
    return [], len(visited)
