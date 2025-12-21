import collections
from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Tuple[Optional[List[Tuple[int,int]]], int]:
    """Bidirectional Breadth-First Search. Returns (path, nodes_explored)."""
    
    if start == goal:
        return [start], 1
        
    q_start = collections.deque([start])
    q_goal = collections.deque([goal])
    
    parent_start = {start: None}
    parent_goal = {goal: None}
    
    def reconstruct_bidirectional_path(meet_node):
        path_start = []
        curr = meet_node
        while curr:
            path_start.append(curr)
            curr = parent_start[curr]
        path_start.reverse()
        
        path_goal = []
        curr = parent_goal[meet_node]
        while curr:
            path_goal.append(curr)
            curr = parent_goal[curr]
            
        return path_start + path_goal
        
    while q_start and q_goal:
        if q_start:
            curr = q_start.popleft()
            neighbors = grid_utils.neighbors(*curr)
            for n in neighbors:
                if n not in parent_start:
                    parent_start[n] = curr
                    q_start.append(n)
                    if n in parent_goal:
                        nodes_explored = len(parent_start) + len(parent_goal)
                        return reconstruct_bidirectional_path(n), nodes_explored
                        
        if q_goal:
            curr = q_goal.popleft()
            neighbors = grid_utils.neighbors(*curr)
            for n in neighbors:
                if n not in parent_goal:
                    parent_goal[n] = curr
                    q_goal.append(n)
                    if n in parent_start:
                        nodes_explored = len(parent_start) + len(parent_goal)
                        return reconstruct_bidirectional_path(n), nodes_explored
                        
    nodes_explored = len(parent_start) + len(parent_goal)
    return [], nodes_explored
