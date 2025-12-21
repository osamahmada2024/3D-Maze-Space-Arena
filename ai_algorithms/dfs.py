from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Tuple[Optional[List[Tuple[int,int]]], int]:
    """Depth-First Search algorithm. Returns (path, nodes_explored)."""
    stack = [start]
    parent = {start: None}
    visited = {start}

    while stack:
        current = stack.pop()
        
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
                stack.append(neighbor)
    
    return [], len(visited)
