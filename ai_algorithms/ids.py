from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Optional[List[Tuple[int,int]]]:
    """Iterative Deepening Search (Optimized)"""
    manhattan = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    max_depth = min(manhattan * 3, 100)  # Cap at 100 to prevent freezing
    
    for depth_limit in range(max_depth):
        # Depth-limited DFS using stack (iterative)
        stack = [(start, [start], 0)]  # (node, path, depth)
        visited_at_depth = set() # To avoid cycles in current path is tricky in IDS iterative without full state. 
        # Standard DFS handles visited per path branch, but simpler: use visited but reset?
        # In this implementation, we simply store path.
        
        # Optimization: Global visited set for THIS iteration
        # Note: In standard IDS, we can revisit nodes if we find a shorter path, but for uniform grid DFS, 
        # simply avoiding cycles in current recursion stack is efficient. 
        # But here we use a stack of states.
        
        while stack:
            current, path, depth = stack.pop()
            
            if current == goal:
                return path
            
            if depth < depth_limit:
                # Get neighbors
                current_neighbors = grid_utils.neighbors(*current)
                # Sort to ensure deterministic or smart order? Nah.
                for neighbor in current_neighbors:
                     if neighbor not in path: # Avoid cycles in current path
                        stack.append((neighbor, path + [neighbor], depth + 1))
    
    return []
