import time
from typing import List, Optional, Tuple

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Tuple[Optional[List[Tuple[int,int]]], int]:
    """Iterative Deepening Search. Returns (path, nodes_explored)."""
    manhattan = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    max_depth = min(manhattan * 10, 400) 
    
    start_time = time.time()
    time_limit = 3.0
    
    total_nodes_explored = 0
    
    for depth_limit in range(max_depth):
        if time.time() - start_time > time_limit:
            print(f"[IDS] ⚠️ Timeout after {time.time() - start_time:.2f}s at depth {depth_limit}")
            return [], total_nodes_explored

        stack = [(start, [start])]
        visited_min_depth = {start: 0}
        
        while stack:
            if (len(stack) % 200 == 0) and (time.time() - start_time > time_limit):
                print(f"[IDS] ⚠️ Timeout in inner loop")
                return [], total_nodes_explored
                
            current, path = stack.pop()
            depth = len(path) - 1
            
            if current == goal:
                total_nodes_explored += len(visited_min_depth)
                return path, total_nodes_explored
            
            if depth < depth_limit:
                neighbors = grid_utils.neighbors(*current)
                
                for neighbor in neighbors:
                    new_depth = depth + 1
                    if neighbor not in visited_min_depth or new_depth < visited_min_depth[neighbor]:
                        visited_min_depth[neighbor] = new_depth
                        stack.append((neighbor, path + [neighbor]))
        
        # Add nodes explored in this iteration
        total_nodes_explored += len(visited_min_depth)
    
    return [], total_nodes_explored
