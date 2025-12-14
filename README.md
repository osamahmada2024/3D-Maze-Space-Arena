# Mazespace Library

A professional Python library for easy 3D rendering of drones and sci-fi shapes.

## Installation

```bash
pip install .
```

## Quick Start

```python
from mazespace import Renderer

# Initialize renderer
renderer = Renderer()

# Draw some shapes
renderer.draw("drone", (0, 0, 0), color=(0, 1, 1))
renderer.draw("cube", (2, 0, 2), color=(1, 0, 0))
renderer.draw("crystal", (-2, 1, -2), color=(0.5, 0, 1))

# Show window
renderer.show()
```

## Running the Full Game

You can still run the original game:

```python
import mazespace
mazespace.run_game()
```
