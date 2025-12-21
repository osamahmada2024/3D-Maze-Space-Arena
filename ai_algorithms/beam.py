from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Tuple[Optional[List[Tuple[int,int]]], int]:
    """Beam Search algorithm. Returns (path, nodes_explored)."""
    
    beam_width = 10
    
    def heuristic(node):
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    current_layer = [(heuristic(start), start, [start])]
    
    visited = {start}
    
    while current_layer:
        next_layer_candidates = []
        
        for _, current_node, path in current_layer:
            if current_node == goal:
                return path, len(visited)
            
            neighbors = grid_utils.neighbors(*current_node)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    cost = heuristic(neighbor)
                    next_layer_candidates.append((cost, neighbor, path + [neighbor]))
        
        next_layer_candidates.sort(key=lambda x: x[0])
        current_layer = next_layer_candidates[:beam_width]
        
    return [], len(visited)
