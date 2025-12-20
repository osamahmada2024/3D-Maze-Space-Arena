import time
from typing import List, Optional, Tuple

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Optional[List[Tuple[int,int]]]:
    """Iterative Deepening Search (Optimized with Time Limit)"""
    manhattan = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    # Lower cap to prevent insane searches on large open grids
    max_depth = min(manhattan * 4, 80) 
    
    start_time = time.time()
    time_limit = 2.0  # 2 seconds max
    
    for depth_limit in range(max_depth):
        # Time check inside the depth loop
        if time.time() - start_time > time_limit:
            print(f"[IDS] ⚠️ Timeout after {time.time() - start_time:.2f}s at depth {depth_limit}")
            return []

        # Depth-limited DFS (iterative) with 'visited in current path' optimization
        # Stack: (node, path, depth)
        stack = [(start, [start], 0)]
        
        # Optimization: We can't use a global visited set for standard DLS 
        # because we might reach a node via a deeper path first which is bad,
        # or a shallower path which is good.
        # But for 'tree' search behavior in a grid, we need to be careful.
        # 
        # Standard optimization: 
        # Track 'visited' as (node, depth) -> if we visited this node at <= depth, skip.
        # BUT this requires storage.
        # For simple IDS to work without freezing:
        
        while stack:
            # Check timeout periodically inside the inner loop too
            if (len(stack) % 100 == 0) and (time.time() - start_time > time_limit):
                print(f"[IDS] ⚠️ Timeout in inner loop")
                return []
                
            current, path, depth = stack.pop()
            
            if current == goal:
                return path
            
            if depth < depth_limit:
                # Neighbors
                neighbors = grid_utils.neighbors(*current)
                
                # Check neighbors
                for neighbor in neighbors:
                    if neighbor not in path: # Cycle check
                        stack.append((neighbor, path + [neighbor], depth + 1))
    
    return []
