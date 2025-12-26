# 3D Maze-𝕊pace Arena

A high-performance 3D maze simulation featuring multiple AI pathfinding algorithms, real-time OpenGL visualization, and multi-agent navigation.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-green.svg)](https://www.python.org/)

---

## Why This Project

Pathfinding is a fundamental challenge in robotics, game development, and autonomous systems. The 3D Maze-Space Arena provides an interactive platform for visualizing and comparing AI algorithms in real time. Whether you are a student learning about search algorithms, a researcher benchmarking navigation strategies, or a developer prototyping agent behavior, this project offers a hands-on environment to explore and experiment.

---

## Key Features

- **9 Pathfinding Algorithms**: A*, BFS, DFS, Dijkstra, Greedy Best-First, IDS, Bidirectional Search, Beam Search, and Genetic Algorithm
- **Real-Time 3D Visualization**: Smooth OpenGL rendering with dynamic camera controls
- **Multi-Agent Simulation**: Deploy multiple agents simultaneously, each with configurable algorithms
- **Environment Themes**: Choose between Forest and Space scenes with distinct visual styles
- **Performance Metrics**: Compare algorithm efficiency with nodes explored, path length, and execution time
- **Interactive Configuration**: Adjust grid size, obstacle density, and agent settings through an intuitive UI

---

## Getting Started

### Prerequisites

- Python 3.12 or higher
- OpenGL-compatible graphics driver

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/osamahmada2024/3D-Maze-Space-Arena.git
   cd 3D-Maze-Space-Arena
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python app.py
   ```

---

## Usage

Launch the application and use the configuration panel to set up your simulation:

```bash
python app.py
```

**Example workflow:**

1. Select an environment theme (Forest or Lava)
2. Configure grid dimensions and obstacle density
3. Add one or more agents and assign pathfinding algorithms
4. Click **Start Simulation** to watch agents navigate the maze
5. Review performance metrics in the results dashboard

**Expected output:**

The application opens a 1024x720 window displaying a 3D maze. Agents visualized as distinct models navigate from start to goal positions, with their paths rendered in real time.

---

## Algorithm Comparison

| Algorithm       | Time Complexity   | Optimal | Best Use Case                          |
|-----------------|-------------------|---------|----------------------------------------|
| A*              | O(E)              | Yes     | Shortest path with heuristic guidance  |
| BFS             | O(V + E)          | Yes     | Unweighted shortest path               |
| Dijkstra        | O(E + V log V)    | Yes     | Weighted graphs                        |
| DFS             | O(V + E)          | No      | Maze exploration                       |
| Greedy BFS      | O(V)              | No      | Fast approximate paths                 |
| IDS             | O(b^d)            | Yes     | Memory-constrained environments        |
| Bidirectional   | O(b^(d/2))        | Yes     | Large search spaces                    |
| Beam Search     | O(b * w)          | No      | Constrained memory search              |
| Genetic         | Variable          | No      | Dynamic or complex environments        |

For detailed analysis, see [Algorithm Comparison Report](ai_algorithms/Algorithm_Comparison_Report.md).

---

## Project Structure

```
3D-Maze-Space-Arena/
├── app.py                 # Application entry point
├── ai_algorithms/         # Pathfinding algorithm implementations
├── core/                  # Grid generation, agent logic, scene management
├── rendering/             # OpenGL rendering modules
├── ui/                    # Menu manager and configuration panel
├── environments/          # Environment themes (Forest, Space)
├── assets/                # Textures and 3D models
└── config/                # Configuration files
```

---

## Dependencies

- **pygame** 2.6.1 — Window management and input handling
- **PyOpenGL** 3.1.10 — 3D graphics rendering
- **NumPy** 1.26.4 — Numerical computations
- **noise** 1.2.2 — Procedural terrain generation
- **Pillow** 10.1.0 — Image processing

See [requirements.txt](requirements.txt) for the complete list.

---

## Release Notes

**Current Version:** v2.0.0 

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
