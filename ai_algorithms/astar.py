import heapq
from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Tuple[Optional[List[Tuple[int,int]]], int]:
    """A* search algorithm. Returns (path, nodes_explored)."""
    def heuristic(node, goal):
        # Manhattan distance
        h = abs(node[0] - goal[0]) + abs(node[1] - goal[1])
        
        # Tie-breaker: Cross-product to prefer paths along the straight line
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
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
    
    return [], len(g_score)
