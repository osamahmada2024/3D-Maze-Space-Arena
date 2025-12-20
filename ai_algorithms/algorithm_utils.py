from typing import List, Tuple, Dict, Optional

def reconstruct_path(parent: Dict[Tuple[int,int], Tuple[int,int]], 
                     start: Tuple[int,int], goal: Tuple[int,int]) -> List[Tuple[int,int]]:
    """Reconstruct path from parent dictionary"""
    path = []
    current = goal
    
    while current is not None:
        path.append(current)
        current = parent.get(current)
    
    path.reverse()
    return path
