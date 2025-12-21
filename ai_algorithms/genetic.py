import random
from typing import List, Tuple, Optional

def run(start: Tuple[int,int], goal: Tuple[int,int], grid_utils) -> Tuple[Optional[List[Tuple[int,int]]], int]:
    """Genetic Search Algorithm. Returns (path, nodes_explored)."""
    
    cols = grid_utils.cols
    rows = grid_utils.rows
    grid = grid_utils.grid
    
    MOVES = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    max_moves = (abs(start[0] - goal[0]) + abs(start[1] - goal[1])) * 2
    max_moves = max(max_moves, 20)
    
    population_size = 50
    generations = 100
    mutation_rate = 0.1
    
    def random_genome():
        return [random.choice(MOVES) for _ in range(max_moves)]
    
    def get_path_from_genome(genome):
        path = [start]
        curr = start
        for move in genome:
            nx, ny = curr[0] + move[0], curr[1] + move[1]
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                curr = (nx, ny)
                path.append(curr)
                if curr == goal:
                    break
        return path
        
    def fitness(genome):
        path = get_path_from_genome(genome)
        end_node = path[-1]
        dist = abs(end_node[0] - goal[0]) + abs(end_node[1] - goal[1])
        score = 1000 - (dist * 10) - len(path)
        if end_node == goal:
            score += 2000 
        return score
    
    population = [random_genome() for _ in range(population_size)]
    best_overall_genome = None
    best_overall_score = -float('inf')
    
    actual_generations = 0
    
    for gen in range(generations):
        actual_generations = gen + 1
        scores = [(fitness(g), g) for g in population]
        scores.sort(key=lambda x: x[0], reverse=True)
        
        if scores[0][0] > best_overall_score:
            best_overall_score = scores[0][0]
            best_overall_genome = scores[0][1]
            path = get_path_from_genome(best_overall_genome)
            if path[-1] == goal and gen > generations // 2: 
                break 

        survivors = [g for s, g in scores[:population_size//2]]
        new_population = []
        while len(new_population) < population_size:
            p1 = random.choice(survivors)
            p2 = random.choice(survivors)
            split = random.randint(1, max_moves-1)
            child = p1[:split] + p2[split:]
            if random.random() < mutation_rate:
                mutate_idx = random.randint(0, max_moves-1)
                child[mutate_idx] = random.choice(MOVES)
            new_population.append(child)
        population = new_population

    # Nodes explored = number of fitness evaluations
    nodes_explored = actual_generations * population_size
    
    return get_path_from_genome(best_overall_genome), nodes_explored
