import time
from typing import List, Optional, Tuple

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Optional[List[Tuple[int,int]]]:
    """Iterative Deepening Search (Optimized with Time Limit & Transposition Table)"""
    manhattan = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    # Increase cap to allow finding winding paths (e.g. 200)
    max_depth = min(manhattan * 10, 400) 
    
    start_time = time.time()
    time_limit = 3.0  # Increased to 3s for complex paths
    
    for depth_limit in range(max_depth):
        # Time check
        if time.time() - start_time > time_limit:
            print(f"[IDS] ⚠️ Timeout after {time.time() - start_time:.2f}s at depth {depth_limit}")
            return []

        # Graph Search DLS using Stack
        # Stack: (node, path) - we derive depth from len(path)-1
        stack = [(start, [start])]
        
        # Optimization: Track minimum depth we reached each node at during THIS iteration.
        # If we reach a node again with >= cost, we skip it.
        visited_min_depth = {start: 0}
        
        while stack:
            # Periodic time check in inner loop
            if (len(stack) % 200 == 0) and (time.time() - start_time > time_limit):
                print(f"[IDS] ⚠️ Timeout in inner loop")
                return []
                
            current, path = stack.pop()
            depth = len(path) - 1
            
            if current == goal:
                return path
            
            if depth < depth_limit:
                # Neighbors
                neighbors = grid_utils.neighbors(*current)
                
                for neighbor in neighbors:
                    new_depth = depth + 1
                    # Cycle check in current path is implicitly handled by generic graph search logic 
                    # if we only expand if we found a better path, BUT for raw DFS without costs 
                    # we must ensure we don't loop in the branch.
                    # With visited_min_depth, we avoid cycles too! 
                    # (Current branch would have equal or lower depth).
                    
                    if neighbor not in visited_min_depth or new_depth < visited_min_depth[neighbor]:
                        visited_min_depth[neighbor] = new_depth
                        stack.append((neighbor, path + [neighbor]))
    
    return []
