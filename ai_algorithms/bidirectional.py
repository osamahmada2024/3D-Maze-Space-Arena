import collections
from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Optional[List[Tuple[int,int]]]:
    """Bidirectional Breadth-First Search"""
    
    if start == goal:
        return [start]
        
    # Frontiers
    q_start = collections.deque([start])
    q_goal = collections.deque([goal])
    
    # Visited dictionaries map node -> parent
    parent_start = {start: None}
    parent_goal = {goal: None}
    
    def reconstruct_bidirectional_path(meet_node):
        # Reconstruct path from start to meeting point
        path_start = []
        curr = meet_node
        while curr:
            path_start.append(curr)
            curr = parent_start[curr]
        path_start.reverse()
        
        # Reconstruct path from meeting point to goal
        path_goal = []
        curr = parent_goal[meet_node] # parent of meet_node in goal tree
        while curr:
            path_goal.append(curr)
            curr = parent_goal[curr]
            
        return path_start + path_goal
        
    while q_start and q_goal:
        # 1. Expand from Start
        if q_start:
            curr = q_start.popleft()
            neighbors = grid_utils.neighbors(*curr)
            for n in neighbors:
                if n not in parent_start:
                    parent_start[n] = curr
                    q_start.append(n)
                    # Check connection
                    if n in parent_goal:
                        return reconstruct_bidirectional_path(n)
                        
        # 2. Expand from Goal
        if q_goal:
            curr = q_goal.popleft()
            neighbors = grid_utils.neighbors(*curr)
            for n in neighbors:
                if n not in parent_goal:
                    parent_goal[n] = curr
                    q_goal.append(n)
                    # Check connection
                    if n in parent_start:
                        return reconstruct_bidirectional_path(n)
                        
    return []
