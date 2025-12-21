import heapq
from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Tuple[Optional[List[Tuple[int,int]]], int]:
    """Dijkstra's search algorithm. Returns (path, nodes_explored)."""
    open_set = []
    heapq.heappush(open_set, (0, start))
    parent = {start: None}
    g_score = {start: 0}

    while open_set:
        current_cost, current = heapq.heappop(open_set)
        
        if current == goal:
            # Reconstruct path
            path = []
            node = goal
            while node:
                path.append(node)
                node = parent[node]
            path.reverse()
            return path, len(g_score)

        for neighbor in grid_utils.neighbors(*current):
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                parent[neighbor] = current
                g_score[neighbor] = tentative_g_score
                heapq.heappush(open_set, (tentative_g_score, neighbor))
    
    return [], len(g_score)
