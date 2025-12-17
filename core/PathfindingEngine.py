import heapq
import random
from collections import deque
from .GridUtils import GridUtils
from typing import List, Tuple, Dict, Optional

class PathfindingEngine:
    """Pathfinding engine supporting A*, Dijkstra, BFS, and DFS algorithms."""
    
    def __init__(self, grid: List[List[int]]):
        """Initialize engine with grid"""
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.utils = GridUtils(grid)

    def heuristic(self, node: Tuple[int,int], goal: Tuple[int,int]) -> int:
        """Compute Manhattan distance"""
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    def astar(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """A* search algorithm"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        parent = {start: None}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == goal:
                return self.reconstruct(parent, start, goal)

            for neighbor in self.utils.neighbors(*current):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    parent[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
        
        return []

    def dijkstra(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """Dijkstra's algorithm (A* with zero heuristic)"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        parent = {start: None}
        g_score = {start: 0}

        while open_set:
            current_cost, current = heapq.heappop(open_set)
            
            if current == goal:
                return self.reconstruct(parent, start, goal)

            for neighbor in self.utils.neighbors(*current):
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    parent[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    heapq.heappush(open_set, (tentative_g_score, neighbor))
        
        return []

    def bfs(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """Breadth-First Search algorithm"""
        queue = deque([start])
        parent = {start: None}
        visited = {start}

        while queue:
            current = queue.popleft()
            
            if current == goal:
                return self.reconstruct(parent, start, goal)

            for neighbor in self.utils.neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        
        return []

    def dfs(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """Depth-First Search algorithm"""
        stack = [start]
        parent = {start: None}
        visited = {start}

        while stack:
            current = stack.pop()
            
            if current == goal:
                return self.reconstruct(parent, start, goal)

            for neighbor in self.utils.neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    stack.append(neighbor)
        
        return []

    def reconstruct(self, parent: Dict[Tuple[int,int], Tuple[int,int]], 
                   start: Tuple[int,int], goal: Tuple[int,int]) -> List[Tuple[int,int]]:
        """Reconstruct path from parent dictionary"""
        path = []
        current = goal
        
        while current is not None:
            path.append(current)
            current = parent.get(current)
        
        path.reverse()
        return path

    def genetic_algorithm(self, start: Tuple[int,int], goal: Tuple[int,int], 
                          population_size=50, generations=100, mutation_rate=0.1) -> Optional[List[Tuple[int,int]]]:
        """
        Genetic Search Algorithm for pathfinding.
        Genome: A list of moves (dx, dy).
        """
        
        # Possible execution moves
        MOVES = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        # Heuristic estimation for max path length (start to goal manhattan * 2 as buffer)
        max_moves = (abs(start[0] - goal[0]) + abs(start[1] - goal[1])) * 2
        max_moves = max(max_moves, 20) # Min buffer
        
        def random_genome():
            return [random.choice(MOVES) for _ in range(max_moves)]
        
        def get_path_from_genome(genome):
            path = [start]
            curr = start
            for move in genome:
                nx, ny = curr[0] + move[0], curr[1] + move[1]
                # Check bounds and obstacles
                if 0 <= nx < self.cols and 0 <= ny < self.rows and self.grid[ny][nx] == 0:
                    curr = (nx, ny)
                    path.append(curr)
                    if curr == goal:
                        break
                # If hit obstacle or wall, stay inplace (or logic to die, but staying is safer for path continuity)
            return path
            
        def fitness(genome):
            path = get_path_from_genome(genome)
            end_node = path[-1]
            dist = abs(end_node[0] - goal[0]) + abs(end_node[1] - goal[1])
            
            # Penalize distance to goal (lower is better, so 1/(dist+1) or similar, but here we likely want to minimize cost)
            # Let's return a score where Higher is Better.
            score = 1000 - (dist * 10) - len(path)
            
            if end_node == goal:
                score += 2000 # Big bonus for reaching goal
                
            return score
        
        # Initialize Population
        population = [random_genome() for _ in range(population_size)]
        
        best_overall_genome = None
        best_overall_score = -float('inf')
        
        for gen in range(generations):
            # Evaluate
            scores = [(fitness(g), g) for g in population]
            scores.sort(key=lambda x: x[0], reverse=True)
            
            # Check best
            if scores[0][0] > best_overall_score:
                best_overall_score = scores[0][0]
                best_overall_genome = scores[0][1]
                
                # Early exit if goal reached with good score? 
                # For now just let it evolve to optimize path length
                path = get_path_from_genome(best_overall_genome)
                if path[-1] == goal and gen > generations // 2: 
                    break 

            # Selection (Top 50%)
            survivors = [g for s, g in scores[:population_size//2]]
            
            new_population = []
            while len(new_population) < population_size:
                p1 = random.choice(survivors)
                p2 = random.choice(survivors)
                
                # Crossover
                split = random.randint(1, max_moves-1)
                child = p1[:split] + p2[split:]
                
                # Mutation
                if random.random() < mutation_rate:
                    mutate_idx = random.randint(0, max_moves-1)
                    child[mutate_idx] = random.choice(MOVES)
                    
                new_population.append(child)
            
            population = new_population

        return get_path_from_genome(best_overall_genome)

    def ucs(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """Uniform Cost Search (Alias for Dijkstra in unweighted grid)"""
        return self.dijkstra(start, goal)

    def hill_climbing(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """Hill Climbing (Implemented as Greedy Best-First Search)"""
        open_set = []
        heapq.heappush(open_set, (self.heuristic(start, goal), start))
        parent = {start: None}
        visited = {start}

        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == goal:
                return self.reconstruct(parent, start, goal)

            # Greedy: Only consider neighbors, pick best heuristic next
            # Standard Hill Climbing doesn't backtrack, but Best-First does.
            # User likely implies Informed Search -> Greedy Best First.
            for neighbor in self.utils.neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    h = self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (h, neighbor))
        
        return []

    def ids(self, start: Tuple[int,int], goal: Tuple[int,int]) -> Optional[List[Tuple[int,int]]]:
        """Iterative Deepening Search"""
        def dls(node, depth, path, visited_cycle):
            if depth == 0 and node == goal:
                return path
            if depth > 0:
                if node == goal:
                    return path
                
                for neighbor in self.utils.neighbors(*node):
                    if neighbor not in visited_cycle:
                        visited_cycle.add(neighbor)
                        res = dls(neighbor, depth-1, path + [neighbor], visited_cycle)
                        visited_cycle.remove(neighbor)
                        if res:
                            return res
            return None

        # Limit depth to avoid infinite loops if no path
        max_depth = self.rows * self.cols  # Worst case
        for d in range(max_depth):
            # Visited set for cycle prevention in current path branch
            res = dls(start, d, [start], {start})
            if res:
                return res
        return []

    def find_path(self, start: Tuple[int,int], goal: Tuple[int,int], algo: str) -> Optional[List[Tuple[int,int]]]:
        """Select algorithm and compute path"""
        algo_lower = algo.lower()
        
        if algo_lower in ("a*", "astar", "a* search"):
            return self.astar(start, goal)
        elif algo_lower in ("dijkstra", "ucs", "uniform-cost search"):
            return self.dijkstra(start, goal)
        elif algo_lower == "bfs":
            return self.bfs(start, goal)
        elif algo_lower == "dfs":
            return self.dfs(start, goal)
        elif algo_lower in ("ids", "iterative deepening"):
            return self.ids(start, goal)
        elif algo_lower in ("hill climbing", "greedy", "greedy bfs"):
            return self.hill_climbing(start, goal)
        elif algo_lower in ("genetic", "ga", "genetic algorithm"):
            print("🧬 Running Genetic Algorithm pathfinding...")
            return self.genetic_algorithm(start, goal)
        else:
            print(f"Warning: Unknown algorithm '{algo}', using A* as default")
            return self.astar(start, goal)