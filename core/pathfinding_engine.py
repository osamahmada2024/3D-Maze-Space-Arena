import heapq
import random
from collections import deque
from .grid_utils import GridUtils
from typing import List, Tuple, Dict, Optional

# Import Algorithms
import ai_algorithms.astar as AStarAlgo
import ai_algorithms.dijkstra as DijkstraAlgo
import ai_algorithms.bfs as BFSAlgo
import ai_algorithms.dfs as DFSAlgo
import ai_algorithms.ids as IDSAlgo
import ai_algorithms.greedy as GreedyAlgo
import ai_algorithms.genetic as GeneticAlgo

class PathfindingEngine:
    """Pathfinding engine as a Facade for ai_algorithms."""
    
    def __init__(self, grid: List[List[int]]):
        """Initialize engine with grid"""
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.utils = GridUtils(grid)

    def find_path(self, start: Tuple[int,int], goal: Tuple[int,int], algo: str) -> Optional[List[Tuple[int,int]]]:
        """Select algorithm and compute path"""
        algo_lower = algo.lower()
        
        # Dispatcher
        if algo_lower in ("a*", "astar", "a* search"):
            return AStarAlgo.run(start, goal, self.utils)
            
        elif algo_lower in ("dijkstra", "ucs", "uniform-cost search"):
            return DijkstraAlgo.run(start, goal, self.utils)
            
        elif algo_lower == "bfs":
            return BFSAlgo.run(start, goal, self.utils)
            
        elif algo_lower == "dfs":
            return DFSAlgo.run(start, goal, self.utils)
            
        elif algo_lower in ("ids", "iterative deepening"):
            return IDSAlgo.run(start, goal, self.utils)
            
        elif algo_lower in ("hill climbing", "greedy", "greedy bfs"):
            return GreedyAlgo.run(start, goal, self.utils)
            
        elif algo_lower in ("genetic", "ga", "genetic algorithm"):
            print("🧬 Running Genetic Algorithm pathfinding...")
            # Genetic needs the utils or grid properly. 
            # Our Genetic.run takes (start, goal, grid_utils)
            return GeneticAlgo.run(start, goal, self.utils)
            
        else:
            print(f"Warning: Unknown algorithm '{algo}', using A* as default")
            return AStarAlgo.run(start, goal, self.utils)