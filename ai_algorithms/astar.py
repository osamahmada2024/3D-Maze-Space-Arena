import heapq
from typing import List, Tuple, Optional
from .algorithm_utils import reconstruct_path

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Optional[List[Tuple[int,int]]]:
    """A* search algorithm"""
    def heuristic(node, goal):
        # Manhattan distance
        h = abs(node[0] - goal[0]) + abs(node[1] - goal[1])
        
        # Tie-breaker: Cross-product to prefer paths along the straight line
        # This breaks ties between multiple equal-length paths
        dx1 = node[0] - goal[0]
        dy1 = node[1] - goal[1]
        dx2 = start[0] - goal[0]
        dy2 = start[1] - goal[1]
        cross = abs(dx1*dy2 - dx2*dy1)
        
        return h + (cross * 0.001)

    open_set = []
    heapq.heappush(open_set, (0, start))
    parent = {start: None}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            return reconstruct_path(parent, start, goal)

        for neighbor in grid_utils.neighbors(*current):
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                parent[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
    
    return []
