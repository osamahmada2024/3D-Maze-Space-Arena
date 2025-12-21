import heapq
from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Tuple[Optional[List[Tuple[int,int]]], int]:
    """Hill Climbing (Greedy Best-First Search). Returns (path, nodes_explored)."""
    def heuristic(node, goal):
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), start))
    parent = {start: None}
    visited = {start}

    while open_set:
        _, current = heapq.heappop(open_set)
        
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
                h = heuristic(neighbor, goal)
                heapq.heappush(open_set, (h, neighbor))
    
    return [], len(visited)
