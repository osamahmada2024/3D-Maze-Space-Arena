import heapq
from typing import List, Tuple, Optional
from .algorithm_utils import reconstruct_path

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Optional[List[Tuple[int,int]]]:
    """Beam Search algorithm (Breadth-First with limited beam width)"""
    
    beam_width = 10  # K parameter
    
    # Priority Queue: (heuristic_cost, node)
    # We use path length + heuristic like A* but strictly cull queue
    
    def heuristic(node):
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    # Initial layer
    current_layer = [(heuristic(start), start, [start])] # cost, node, path
    
    visited = {start}
    
    while current_layer:
        next_layer_candidates = []
        
        for _, current_node, path in current_layer:
            if current_node == goal:
                return path
            
            neighbors = grid_utils.neighbors(*current_node)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    cost = heuristic(neighbor)
                    # For beam search, we often just want the node and its path
                    # We store (cost, neighbor, new_path)
                    next_layer_candidates.append((cost, neighbor, path + [neighbor]))
        
        # Sort by best heuristic and keep only top K
        next_layer_candidates.sort(key=lambda x: x[0])
        current_layer = next_layer_candidates[:beam_width]
        
    return []
