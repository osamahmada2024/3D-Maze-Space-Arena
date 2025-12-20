# AI Algorithms Comparison

This document compares the 7 pathfinding algorithms implementing in this project. The comparison is based on the context of a 2D Grid Maze.

| Algorithm | Time Complexity | Space Complexity | Complete? | Optimal? | Best Use Case |
|-----------|-----------------|------------------|-----------|----------|---------------|
| **BFS** | O(V + E) | O(V) | Yes | Yes (unweighted) | Shortest path in unweighted mazes. Guarantees shortest path. |
| **DFS** | O(V + E) | O(V) | No (in infinite) / Yes (finite) | No | Exploring maze structure, maze generation. Not good for pathfinding. |
| **UCS / Dijkstra** | O(E + V log V) | O(V) | Yes | Yes | Shortest path in **weighted** graphs (e.g. mud/lava costs). |
| **A* (A-Star)** | O(E) (depends on heuristic) | O(V) | Yes | Yes (admissible heuristic) | **The Standard**. Best for finding shortest path efficiently using heuristics. |
| **Greedy BFS** | O(V) (worst case) | O(V) | No (can loop) | No | Fast but not guaranteed to be shortest. Good for "good enough" paths. |
| **IDS** | O(b^d) | O(bd) | Yes | Yes (unweighted) | Memory-constrained environments where BFS is too heavy. |
| **Genetic** | Variable (Generations * Pop) | O(Pop Size) | No (Probabilistic) | No | Complex or dynamic environments where analytical solution is hard. Cool to watch! |

## Hints & Details

### 1. BFS (Breadth-First Search)
- **Hint:** Imagining pouring water into the maze; it spreads evenly in all directions.
- **Pros:** ALWAYS finds the shortest path in an unweighted grid.
- **Cons:** Slow. It explores everything.

### 2. DFS (Depth-First Search)
- **Hint:** Imagine a robot that keeps going forward until it hits a wall, then backtracks.
- **Pros:** Memory efficient (O(depth)).
- **Cons:** Can find terrible, long, winding paths.

### 3. Dijkstra (Uniform Cost Search)
- **Hint:** Like BFS, but prioritizes cheaper paths (if movement costs vary).
- **Pros:** Handles different terrain costs (e.g., walking on road vs sand).
- **Cons:** Slower than A* because it has no sense of direction (no heuristic).

### 4. A* (A-Star)
- **Hint:** Smart BFS. It uses a "Heuristic" (guess) to focus search towards the goal.
- **Pros:** The Gold Standard. Fast and Optimal.
- **Best For This Problem:** Yes. This is the recommended choice for the Agent.

### 5. IDS (Iterative Deepening Search)
- **Hint:** Tries DFS with depth 1, then depth 2, then 3...
- **Pros:** Combines BFS optimality with DFS space efficiency.
- **Cons:** Re-visits states many times. Slower in practice for simple grids.

### 6. Greedy Best-First Search (Hill Climbing)
- **Hint:** Always moves to the neighbor closest to the goal.
- **Pros:** extremely fast.
- **Cons:** Can get stuck in dead-ends (local optima) or find non-optimal paths.

### 7. Genetic Algorithm
- **Hint:** Evolution! Random paths breed and mutate to find better paths.
- **Pros:** Robust in very dynamic/weird environments.
- **Cons:** Slow, not guaranteed to reach the goal, and path is usually wiggly (not optimal).

## Recommendation
For this 3D Maze Arena, **A*** is the best choice. It is efficient, optimal, and handles the grid structure perfectly.
