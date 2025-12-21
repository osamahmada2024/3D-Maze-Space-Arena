# Pathfinding Algorithms: A Formal Comparative Analysis

**Document Version:** 1.0  
**Date:** December 21, 2025  
**Context:** 3D Grid-Based Maze Navigation in the 3D-Maze-Space-Arena Project  

---

## Executive Summary

This report provides a rigorous comparative analysis of nine pathfinding algorithms implemented for grid-based maze navigation. **A\* (A-Star) is the recommended algorithm** for general-purpose pathfinding in the 3D-Maze-Space-Arena project due to its optimal combination of guaranteed shortest-path discovery, efficient memory usage, and superior average-case performance when paired with an admissible heuristic. For specialized scenarios—such as memory-constrained environments—Iterative Deepening Search (IDS) offers a compelling alternative, while Bidirectional BFS provides significant speedups when the goal is known a priori. Greedy Best-First Search should be considered for real-time applications where speed is prioritized over path optimality.

---

## Table of Contents

1. [Summary Comparison Table](#1-summary-comparison-table)
2. [Algorithm Profiles](#2-algorithm-profiles)
   - [2.1 Breadth-First Search (BFS)](#21-breadth-first-search-bfs)
   - [2.2 Depth-First Search (DFS)](#22-depth-first-search-dfs)
   - [2.3 Dijkstra's Algorithm (Uniform Cost Search)](#23-dijkstras-algorithm-uniform-cost-search)
   - [2.4 A* (A-Star) Search](#24-a-a-star-search)
   - [2.5 Greedy Best-First Search](#25-greedy-best-first-search)
   - [2.6 Beam Search](#26-beam-search)
   - [2.7 Bidirectional BFS](#27-bidirectional-bfs)
   - [2.8 Iterative Deepening Search (IDS)](#28-iterative-deepening-search-ids)
   - [2.9 Genetic Algorithm](#29-genetic-algorithm)
3. [When to Use Which: Decision Guide](#3-when-to-use-which-decision-guide)
4. [Complexity Derivations](#4-complexity-derivations)
5. [References](#5-references)

---

## 1. Summary Comparison Table

| Algorithm | Time Complexity | Space Complexity | Complete | Optimal | Best Use Case |
|-----------|-----------------|------------------|:--------:|:-------:|---------------|
| **BFS** | O(V + E) | O(V) | ✓ | ✓* | Shortest path in unweighted graphs |
| **DFS** | O(V + E) | O(d) | ✗† | ✗ | Maze generation, connectivity checking |
| **Dijkstra** | O((V + E) log V) | O(V) | ✓ | ✓ | Shortest path in weighted graphs |
| **A\*** | O(E) avg, O(b^d) worst | O(b^d) | ✓ | ✓‡ | **General-purpose pathfinding** |
| **Greedy BFS** | O(b^m) | O(b^m) | ✗ | ✗ | Fast approximation, real-time systems |
| **Beam** | O(b × w × d) | O(w × d) | ✗ | ✗ | Memory-limited heuristic search |
| **Bidirectional** | O(b^(d/2)) | O(b^(d/2)) | ✓ | ✓* | Known start and goal positions |
| **IDS** | O(b^d) | O(d) | ✓ | ✓* | Memory-constrained optimal search |
| **Genetic** | O(G × P × L) | O(P × L) | ✗ | ✗ | Dynamic environments, exploration |

**Legend:**
- `V` = vertices, `E` = edges, `b` = branching factor, `d` = solution depth, `m` = max depth
- `w` = beam width, `G` = generations, `P` = population size, `L` = genome length
- `*` = optimal for unweighted graphs only
- `†` = complete for finite graphs, incomplete for infinite graphs
- `‡` = optimal when using an admissible heuristic

---

## 2. Algorithm Profiles

---

### 2.1 Breadth-First Search (BFS)

**Formal Name:** Breadth-First Search  
**Short Description:** A level-order graph traversal algorithm that explores all vertices at the current depth before proceeding to vertices at the next depth level.

#### Complexity Analysis

| Aspect | Complexity | Assumptions |
|--------|------------|-------------|
| **Time (Best)** | O(1) | Goal is the start node |
| **Time (Average)** | O(V + E) | Uniform distribution of goal position |
| **Time (Worst)** | O(V + E) | Goal is the last node explored |
| **Space** | O(V) | Queue and visited set storage |

**Memory Behavior:** BFS requires storing all nodes at the current frontier. In a 2D grid, the frontier can grow to O(√V) for a square grid, but the visited set reaches O(V) as search progresses.

#### Completeness
**Yes.** BFS will always find a solution if one exists in a finite graph. The algorithm systematically explores all reachable states in breadth-first order, guaranteeing discovery of any reachable goal.

#### Optimality
**Yes** (for unweighted graphs). BFS finds the shortest path in terms of number of edges. For weighted graphs, BFS is not optimal; Dijkstra's algorithm should be used instead.

#### Practical Performance Notes
- **Excels when:** Solution is shallow; graph is dense; all edges have equal weight.
- **Struggles when:** Solution is deep; memory is constrained; graph has many branches.

#### Implementation Hint
> **Parameter:** Use a `deque` (double-ended queue) for O(1) enqueue/dequeue operations.  
> **Speedup:** Mark nodes as visited when enqueued (not when dequeued) to avoid duplicate entries.  
> **Pitfall:** Using a list with `pop(0)` results in O(n) dequeue time—always use `collections.deque`.

#### Pseudocode

```
FUNCTION BFS(start, goal, neighbors):
    queue ← new FIFO Queue containing start
    visited ← {start}
    parent ← {start: NULL}
    
    WHILE queue is not empty:
        current ← queue.dequeue()
        
        IF current = goal:
            RETURN ReconstructPath(parent, goal)
        
        FOR EACH neighbor IN neighbors(current):
            IF neighbor ∉ visited:
                visited.add(neighbor)
                parent[neighbor] ← current
                queue.enqueue(neighbor)
    
    RETURN failure
```

**Invariant:** All nodes in the queue have distance from start ≤ current level, and all nodes at distance < current level have been fully processed.

---

### 2.2 Depth-First Search (DFS)

**Formal Name:** Depth-First Search  
**Short Description:** A graph traversal algorithm that explores as far as possible along each branch before backtracking.

#### Complexity Analysis

| Aspect | Complexity | Assumptions |
|--------|------------|-------------|
| **Time (Best)** | O(1) | Goal is the start node |
| **Time (Average)** | O(V + E) | Depends on goal location |
| **Time (Worst)** | O(V + E) | Must explore entire graph |
| **Space** | O(d) | Depth `d` of recursion/stack |

**Memory Behavior:** DFS only stores nodes along the current path, making it memory-efficient. For grids, maximum depth is O(V) in the worst case but often much smaller in practice.

#### Completeness
**No** (in general). DFS can loop infinitely in graphs with cycles unless a visited set is maintained. With cycle detection in finite graphs, DFS is complete.

#### Optimality
**No.** DFS finds *a* path, not necessarily the shortest path. The first solution found depends on the order of neighbor exploration.

#### Practical Performance Notes
- **Excels when:** Memory is severely limited; solution depth is predictable; exploring all paths.
- **Struggles when:** Optimal path is required; graph is very deep; solution is shallow but DFS goes deep first.

#### Implementation Hint
> **Parameter:** Use iterative implementation with explicit stack for large graphs (avoids stack overflow).  
> **Speedup:** Order neighbor exploration to check promising directions first.  
> **Pitfall:** Always maintain a visited set to prevent infinite loops in cyclic graphs.

#### Pseudocode

```
FUNCTION DFS(start, goal, neighbors):
    stack ← [start]
    visited ← {start}
    parent ← {start: NULL}
    
    WHILE stack is not empty:
        current ← stack.pop()
        
        IF current = goal:
            RETURN ReconstructPath(parent, goal)
        
        FOR EACH neighbor IN neighbors(current):
            IF neighbor ∉ visited:
                visited.add(neighbor)
                parent[neighbor] ← current
                stack.push(neighbor)
    
    RETURN failure
```

**Invariant:** The stack contains only unvisited nodes or nodes whose subtrees are not fully explored.

---

### 2.3 Dijkstra's Algorithm (Uniform Cost Search)

**Formal Name:** Dijkstra's Shortest Path Algorithm / Uniform Cost Search  
**Short Description:** A greedy algorithm that finds the shortest path from a source vertex to all other vertices in a weighted graph with non-negative edge weights.

#### Complexity Analysis

| Aspect | Complexity | Assumptions |
|--------|------------|-------------|
| **Time (Best)** | O(1) | Goal is the start node |
| **Time (Average)** | O((V + E) log V) | Using binary heap |
| **Time (Worst)** | O((V + E) log V) | Using binary heap |
| **Space** | O(V) | Priority queue + distance array |

**Memory Behavior:** Maintains a priority queue and distance dictionary. Memory usage is linear in the number of vertices.

#### Completeness
**Yes.** Dijkstra's algorithm will find a path if one exists, assuming finite edge weights and no negative-weight edges.

#### Optimality
**Yes.** Dijkstra's algorithm is guaranteed to find the shortest path in weighted graphs with non-negative edge weights.

#### Practical Performance Notes
- **Excels when:** Edge weights vary (terrain costs); optimality is required; weights are non-negative.
- **Struggles when:** All weights are equal (BFS is faster); graph has negative weights (use Bellman-Ford).

#### Implementation Hint
> **Parameter:** Choice of priority queue implementation significantly affects performance.  
> **Speedup:** Use a binary heap (`heapq`) for O(log V) operations. For very dense graphs, Fibonacci heaps offer O(1) amortized decrease-key.  
> **Pitfall:** Avoid re-processing nodes; track visited nodes in a separate set or use lazy deletion.

#### Pseudocode

```
FUNCTION Dijkstra(start, goal, neighbors, weight):
    pq ← new Priority Queue with (0, start)
    dist ← {start: 0}
    parent ← {start: NULL}
    
    WHILE pq is not empty:
        (cost, current) ← pq.extract_min()
        
        IF current = goal:
            RETURN ReconstructPath(parent, goal)
        
        IF cost > dist[current]:   // Already processed
            CONTINUE
        
        FOR EACH neighbor IN neighbors(current):
            new_cost ← dist[current] + weight(current, neighbor)
            IF neighbor ∉ dist OR new_cost < dist[neighbor]:
                dist[neighbor] ← new_cost
                parent[neighbor] ← current
                pq.insert((new_cost, neighbor))
    
    RETURN failure
```

**Invariant:** When a node is extracted from the priority queue, its distance value is the true shortest distance from the source.

---

### 2.4 A* (A-Star) Search

**Formal Name:** A* Search Algorithm  
**Short Description:** An informed best-first search algorithm that uses a heuristic function to estimate the cost to reach the goal, combining the actual cost from the start with the estimated cost to the goal.

#### Complexity Analysis

| Aspect | Complexity | Assumptions |
|--------|------------|-------------|
| **Time (Best)** | O(d) | Perfect heuristic (h = h*) |
| **Time (Average)** | O(E) | Good heuristic |
| **Time (Worst)** | O(b^d) | Poor heuristic (h = 0, degenerates to Dijkstra) |
| **Space** | O(b^d) | Must store all generated nodes |

**Memory Behavior:** A* stores all nodes in the open and closed sets. Memory is often the limiting factor for A* in large search spaces.

#### Completeness
**Yes.** A* is complete if the branching factor is finite and edge costs are bounded above zero.

#### Optimality
**Yes** (with conditions). A* finds the optimal path if and only if the heuristic function h(n) is **admissible** (never overestimates the true cost) and **consistent** (satisfies the triangle inequality).

#### Practical Performance Notes
- **Excels when:** Good heuristic is available; solution exists; graph has uniform structure.
- **Struggles when:** Heuristic is poor; memory is limited; problem has no clear path.

#### Implementation Hint
> **Parameter:** The heuristic function is critical. Manhattan distance is admissible for 4-connected grids; Euclidean for 8-connected.  
> **Speedup:** Add tie-breaking to the heuristic (e.g., cross-product) to reduce nodes explored. Use `heapq` with tuple comparison `(f, g, node)`.  
> **Pitfall:** An inadmissible heuristic can find suboptimal paths. Always verify admissibility.

#### Pseudocode

```
FUNCTION AStar(start, goal, neighbors, h):
    open_set ← Priority Queue with (h(start), 0, start)
    g_score ← {start: 0}
    parent ← {start: NULL}
    
    WHILE open_set is not empty:
        (f, g, current) ← open_set.extract_min()
        
        IF current = goal:
            RETURN ReconstructPath(parent, goal)
        
        FOR EACH neighbor IN neighbors(current):
            tentative_g ← g_score[current] + cost(current, neighbor)
            
            IF neighbor ∉ g_score OR tentative_g < g_score[neighbor]:
                g_score[neighbor] ← tentative_g
                f_score ← tentative_g + h(neighbor)
                parent[neighbor] ← current
                open_set.insert((f_score, tentative_g, neighbor))
    
    RETURN failure
```

**Invariant:** For any node n in the closed set, g(n) is the optimal cost from start to n.

---

### 2.5 Greedy Best-First Search

**Formal Name:** Greedy Best-First Search (Hill Climbing Variant)  
**Short Description:** An informed search algorithm that expands the node that appears to be closest to the goal according to a heuristic function, ignoring the cost to reach that node.

#### Complexity Analysis

| Aspect | Complexity | Assumptions |
|--------|------------|-------------|
| **Time (Best)** | O(d) | Heuristic leads directly to goal |
| **Time (Average)** | O(b^m) | Heuristic quality varies |
| **Time (Worst)** | O(b^m) | Explores most of the space |
| **Space** | O(b^m) | Stores frontier nodes |

**Memory Behavior:** Similar to BFS, but often explores fewer nodes due to heuristic guidance. Worst case matches BFS.

#### Completeness
**No.** Greedy search can get stuck in infinite loops in graphs with cycles (without a visited set) or fail to find a path that exists if the heuristic leads away from viable routes.

#### Optimality
**No.** Greedy search finds a path quickly but often not the shortest path. It prioritizes speed over quality.

#### Practical Performance Notes
- **Excels when:** Speed is critical; approximate solution is acceptable; obstacles are sparse.
- **Struggles when:** Optimal path is required; many dead-ends exist; heuristic is misleading.

#### Implementation Hint
> **Parameter:** Heuristic choice determines behavior. More aggressive heuristics are faster but less reliable.  
> **Speedup:** Combine with random restarts for escaping local minima.  
> **Pitfall:** Without a visited set, can loop infinitely. The path found may be very poor compared to optimal.

#### Pseudocode

```
FUNCTION GreedyBFS(start, goal, neighbors, h):
    open_set ← Priority Queue with (h(start), start)
    visited ← {start}
    parent ← {start: NULL}
    
    WHILE open_set is not empty:
        (_, current) ← open_set.extract_min()
        
        IF current = goal:
            RETURN ReconstructPath(parent, goal)
        
        FOR EACH neighbor IN neighbors(current):
            IF neighbor ∉ visited:
                visited.add(neighbor)
                parent[neighbor] ← current
                open_set.insert((h(neighbor), neighbor))
    
    RETURN failure
```

**Invariant:** The open set always contains nodes ordered by heuristic value (estimated distance to goal).

---

### 2.6 Beam Search

**Formal Name:** Beam Search  
**Short Description:** A bounded-width search algorithm that explores a limited number of the most promising nodes at each level, discarding others.

#### Complexity Analysis

| Aspect | Complexity | Assumptions |
|--------|------------|-------------|
| **Time (Best)** | O(w × d) | Goal found at depth d |
| **Time (Average)** | O(b × w × d) | Branching factor b, width w, depth d |
| **Time (Worst)** | O(b × w × d) | Full exploration within beam |
| **Space** | O(w × d) | Stores w nodes per level, depth d paths |

**Memory Behavior:** Memory is bounded by beam width × solution depth, making it predictable and controllable.

#### Completeness
**No.** Beam search may discard the path to the goal if it falls outside the beam width. Increasing beam width approaches BFS completeness.

#### Optimality
**No.** Beam search is not guaranteed to find the optimal path because it prunes potentially optimal branches.

#### Practical Performance Notes
- **Excels when:** Memory is limited; approximate solution is acceptable; beam width is well-tuned.
- **Struggles when:** Optimal path has poor intermediate heuristic values; goal is in a narrow corridor.

#### Implementation Hint
> **Parameter:** Beam width (w) controls the tradeoff between completeness and efficiency. Start with w = 10 and adjust.  
> **Speedup:** Use stable sorting to maintain consistent behavior across runs.  
> **Pitfall:** Too small beam width leads to failure on complex mazes; too large negates benefits.

#### Pseudocode

```
FUNCTION BeamSearch(start, goal, neighbors, h, beam_width):
    current_level ← [(h(start), start, [start])]
    visited ← {start}
    
    WHILE current_level is not empty:
        next_level ← []
        
        FOR EACH (cost, node, path) IN current_level:
            IF node = goal:
                RETURN path
            
            FOR EACH neighbor IN neighbors(node):
                IF neighbor ∉ visited:
                    visited.add(neighbor)
                    next_level.append((h(neighbor), neighbor, path + [neighbor]))
        
        next_level.sort(by cost)
        current_level ← next_level[0:beam_width]
    
    RETURN failure
```

**Invariant:** At each level, exactly min(beam_width, |candidates|) nodes are retained for expansion.

---

### 2.7 Bidirectional BFS

**Formal Name:** Bidirectional Breadth-First Search  
**Short Description:** A search strategy that runs two simultaneous BFS searches—one forward from the start and one backward from the goal—meeting in the middle.

#### Complexity Analysis

| Aspect | Complexity | Assumptions |
|--------|------------|-------------|
| **Time (Best)** | O(1) | Start equals goal |
| **Time (Average)** | O(b^(d/2)) | Solution at depth d |
| **Time (Worst)** | O(b^(d/2)) | Two searches meet at middle |
| **Space** | O(b^(d/2)) | Two frontiers stored |

**Memory Behavior:** Both frontiers must be stored. Total space is still less than unidirectional BFS (O(b^d)) for deep solutions.

#### Completeness
**Yes.** Like BFS, bidirectional search will find a solution if one exists in a finite graph.

#### Optimality
**Yes** (for unweighted graphs). The path found by bidirectional BFS is optimal when edge weights are uniform.

#### Practical Performance Notes
- **Excels when:** Goal position is known; solution depth is large; branching factor is uniform.
- **Struggles when:** Goal is unknown or multiple; reversing edges is expensive; graph is asymmetric.

#### Implementation Hint
> **Parameter:** Alternate between forward and backward searches for even exploration.  
> **Speedup:** Check for intersection after each expansion (not just after processing full frontiers).  
> **Pitfall:** Path reconstruction requires careful handling of both parent maps; the meeting point must be correctly identified.

#### Pseudocode

```
FUNCTION BidirectionalBFS(start, goal, neighbors):
    IF start = goal:
        RETURN [start]
    
    queue_fwd ← [start], queue_bwd ← [goal]
    parent_fwd ← {start: NULL}, parent_bwd ← {goal: NULL}
    
    WHILE queue_fwd and queue_bwd:
        // Expand forward frontier
        current ← queue_fwd.dequeue()
        FOR EACH neighbor IN neighbors(current):
            IF neighbor ∉ parent_fwd:
                parent_fwd[neighbor] ← current
                queue_fwd.enqueue(neighbor)
                IF neighbor ∈ parent_bwd:
                    RETURN ReconstructBidirectionalPath(neighbor, parent_fwd, parent_bwd)
        
        // Expand backward frontier
        current ← queue_bwd.dequeue()
        FOR EACH neighbor IN neighbors(current):
            IF neighbor ∉ parent_bwd:
                parent_bwd[neighbor] ← current
                queue_bwd.enqueue(neighbor)
                IF neighbor ∈ parent_fwd:
                    RETURN ReconstructBidirectionalPath(neighbor, parent_fwd, parent_bwd)
    
    RETURN failure
```

**Invariant:** At each step, both search frontiers have explored all nodes within distance `k` from their respective origins.

---

### 2.8 Iterative Deepening Search (IDS)

**Formal Name:** Iterative Deepening Depth-First Search (IDDFS)  
**Short Description:** A search strategy that combines the space efficiency of DFS with the completeness of BFS by performing repeated DFS with increasing depth limits.

#### Complexity Analysis

| Aspect | Complexity | Assumptions |
|--------|------------|-------------|
| **Time (Best)** | O(b) | Goal at depth 1 |
| **Time (Average)** | O(b^d) | Solution at depth d |
| **Time (Worst)** | O(b^d) | Goal at maximum depth |
| **Space** | O(d) | Only stores current path |

**Memory Behavior:** Exceptional memory efficiency—stores only the nodes on the current search path, making it suitable for memory-constrained environments.

#### Completeness
**Yes.** IDS is complete for finite branching factors and will find a solution if one exists.

#### Optimality
**Yes** (for unweighted graphs). IDS finds the shallowest goal, which corresponds to the optimal solution in unweighted graphs.

#### Practical Performance Notes
- **Excels when:** Memory is severely limited; solution depth is unknown; optimality required.
- **Struggles when:** Solution is deep; branching factor is high; repeated work is costly.

#### Implementation Hint
> **Parameter:** Use time limits to prevent hanging on unsolvable instances. Start max_depth relative to Manhattan distance.  
> **Speedup:** Implement transposition tables to avoid re-exploring the same states across iterations.  
> **Pitfall:** The repeated work factor is b/(b-1), which is small for large b (e.g., 1.25 for b=4).

#### Pseudocode

```
FUNCTION IDS(start, goal, neighbors, max_depth):
    FOR depth_limit FROM 0 TO max_depth:
        result ← DepthLimitedDFS(start, goal, neighbors, depth_limit)
        IF result ≠ cutoff:
            RETURN result
    RETURN failure

FUNCTION DepthLimitedDFS(node, goal, neighbors, limit):
    IF node = goal:
        RETURN [node]
    IF limit = 0:
        RETURN cutoff
    
    FOR EACH neighbor IN neighbors(node):
        result ← DepthLimitedDFS(neighbor, goal, neighbors, limit - 1)
        IF result ≠ cutoff:
            RETURN [node] + result
    
    RETURN cutoff
```

**Invariant:** At iteration k, all nodes at depth ≤ k have been fully explored.

---

### 2.9 Genetic Algorithm

**Formal Name:** Genetic Algorithm (Evolutionary Pathfinding)  
**Short Description:** A metaheuristic optimization algorithm inspired by natural selection that evolves a population of candidate solutions (paths) through selection, crossover, and mutation.

#### Complexity Analysis

| Aspect | Complexity | Assumptions |
|--------|------------|-------------|
| **Time (Best)** | O(P × L) | Solution in first generation |
| **Time (Average)** | O(G × P × L) | G generations, P population, L genome length |
| **Time (Worst)** | O(G × P × L) | No improvement across generations |
| **Space** | O(P × L) | Population storage |

**Memory Behavior:** Memory scales with population size and genome length. Each individual stores a complete solution candidate.

#### Completeness
**No.** Genetic algorithms are stochastic and may not find a valid path even if one exists. Success depends on parameter tuning and randomness.

#### Optimality
**No.** Genetic algorithms are not guaranteed to find optimal solutions. They approximate good solutions within computational constraints.

#### Practical Performance Notes
- **Excels when:** Search space is complex; analytical methods fail; exploring solution diversity matters; problem is dynamic.
- **Struggles when:** Optimal solution is required; search space is simple; time is critical.

#### Implementation Hint
> **Parameter:** Population size (50-200), generations (50-500), mutation rate (0.05-0.2), and crossover strategy significantly affect convergence.  
> **Speedup:** Use elitism to preserve best solutions; implement tournament selection for efficiency.  
> **Pitfall:** Premature convergence occurs when diversity is lost—maintain diversity through mutation and varied selection pressure.

#### Pseudocode

```
FUNCTION GeneticPathfinder(start, goal, grid, pop_size, generations, mutation_rate):
    population ← [RandomGenome() FOR i IN 1..pop_size]
    best_solution ← NULL
    
    FOR gen IN 1..generations:
        // Evaluate fitness
        scored ← [(Fitness(genome, start, goal), genome) FOR genome IN population]
        scored.sort(descending by fitness)
        
        IF scored[0].fitness > best_solution.fitness:
            best_solution ← scored[0].genome
            IF GoalReached(best_solution):
                RETURN DecodePath(best_solution)
        
        // Selection
        survivors ← top 50% of scored
        
        // Crossover and Mutation
        new_population ← []
        WHILE |new_population| < pop_size:
            parent1, parent2 ← random pair from survivors
            child ← Crossover(parent1, parent2)
            IF random() < mutation_rate:
                child ← Mutate(child)
            new_population.append(child)
        
        population ← new_population
    
    RETURN DecodePath(best_solution)
```

**Invariant:** The best individual in the population never decreases in fitness across generations (with elitism).

---

## 3. When to Use Which: Decision Guide

Use this decision guide to select the appropriate algorithm based on your requirements:

1. **If you need the shortest path and have adequate memory** → Use **A\*** with Manhattan distance heuristic. It balances optimality and efficiency, making it the gold standard for grid-based pathfinding.

2. **If you need the shortest path but memory is severely constrained** → Use **IDS**. It provides optimal unweighted paths with O(d) space complexity, trading time for memory.

3. **If you need any valid path as fast as possible (optimality not required)** → Use **Greedy Best-First Search** for maximum speed, or **Beam Search** if you want bounded memory usage with moderate path quality.

4. **If the graph has weighted edges (variable terrain costs)** → Use **Dijkstra** (if no heuristic available) or **A\*** (if a good heuristic exists). BFS and IDS assume uniform edge weights.

5. **If start and goal are both known and the graph is large** → Consider **Bidirectional BFS** for up to quadratic speedup. This is particularly effective when the solution depth is large.

---

## 4. Complexity Derivations

### 4.1 BFS Time Complexity: O(V + E)

**Derivation:** BFS visits each vertex exactly once and examines each edge exactly once. The queue operations (enqueue, dequeue) are O(1) using a proper deque. Total work is bounded by:

$$
T(n) = \sum_{v \in V} (1 + \deg(v)) = V + \sum_{v \in V} \deg(v) = V + 2E = O(V + E)
$$

For a 2D grid of size n×n: V = n², E = O(4n²) = O(V), so T(n) = O(V).

### 4.2 A* Time Complexity: O(b^d) worst case, O(E) average case

**Derivation:** In the worst case (h = 0), A* degenerates to Dijkstra's algorithm, exploring states proportional to b^d where b is the branching factor and d is the solution depth.

With a perfect heuristic (h = h*), A* expands only nodes on the optimal path: O(d).

With an admissible, consistent heuristic, A* typically expands O(E) nodes, where the constant factor depends on heuristic quality. The effectiveness of A* is characterized by:

$$
A^* \text{ expansion count} \approx O(b^{d \cdot (1 - \epsilon)})
$$

where ε measures heuristic accuracy.

### 4.3 Bidirectional BFS: O(b^(d/2)) vs O(b^d)

**Derivation:** Unidirectional BFS explores O(b^d) nodes. Bidirectional search runs two BFS instances, each exploring O(b^(d/2)) nodes before meeting:

$$
T_{bidir} = O(2 \cdot b^{d/2}) = O(b^{d/2})
$$

The speedup ratio is:

$$
\frac{b^d}{2 \cdot b^{d/2}} = \frac{b^d}{2 \cdot b^{d/2}} = \frac{b^{d/2}}{2} \approx O(b^{d/2})
$$

For b = 4, d = 20: Unidirectional explores 4²⁰ ≈ 10¹² nodes; Bidirectional explores 2 × 4¹⁰ ≈ 2 × 10⁶ nodes.

### 4.4 IDS Overhead Factor

**Derivation:** IDS repeats DFS at depths 0, 1, 2, ..., d. Total nodes expanded:

$$
N_{total} = \sum_{i=0}^{d} b^i = \frac{b^{d+1} - 1}{b - 1}
$$

Compared to BFS which expands b^d nodes at final level:

$$
\text{Overhead} = \frac{N_{total}}{b^d} = \frac{b^{d+1} - 1}{(b-1) \cdot b^d} \approx \frac{b}{b-1}
$$

For b = 4: overhead ≈ 4/3 ≈ 1.33×. This is minimal in practice.

---

*Document prepared for the 3D-Maze-Space-Arena Project*  
*© 2025 3D Maze Space Arena Team* 
