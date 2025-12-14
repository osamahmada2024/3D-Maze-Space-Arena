# Mazespace API Reference & Usage Guide

This document provides a complete reference for the `mazespace` library, including supported commands, parameters, and configuration options.

## Table of Contents
1. [Core API](#core-api) (`mazespace.Renderer`)
2. [Game Launcher](#game-launcher)
3. [Configuration](#configuration)

---

## Core API

### `mazespace.Renderer`

The main class for creating custom 3D scenes.

```python
from mazespace import Renderer
r = Renderer(width=800, height=600, bg_color=(0.1, 0.1, 0.1, 1.0))
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | `int` | `800` | Window width in pixels. |
| `height` | `int` | `600` | Window height in pixels. |
| `bg_color` | `tuple` | `(0.1, 0.1, 0.1, 1.0)` | Background color (R, G, B, A) values from 0.0 to 1.0. |

---

### Methods

#### `draw(shape, position, color)`

Adds a 3D object to the scene.

```python
r.draw(shape="drone", position=(0, 0, 0), color=(1, 0, 0))
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `shape` | `str` | `"drone"` | The type of object to draw. Supported values below. |
| `position` | `tuple` | `(0, 0, 0)` | (x, y, z) coordinates for the object. |
| `color` | `tuple` | `(0, 1, 1)` | (r, g, b) color tuple, values 0.0 to 1.0. |

**Supported Shapes:**
- `"drone"` (or `"mini_drone"`)
- `"cube"` (or `"robo_cube"`)
- `"sphere"` (or `"sphere_droid"`)
- `"crystal"` (or `"crystal_alien"`)

#### `show()`

Opens the window and starts the event loop. **This is a blocking call.**
Navigate with Arrow Keys, Zoom with Mouse Wheel.

```python
r.show()
```

#### `render()`

Renders a single frame. Use this ONLY if you are managing your own PyGame loop.

```python
r.render()
```

---

## Game Launcher

Run the full interactive maze game.

```python
import mazespace
mazespace.run_game()
```

The game behavior is controlled by the interactive menu that appears on launch.

---

## Configuration

You can customize advanced settings by modifying `mazespace/config/settings.py`.

### Theme Settings (`THEME_SETTINGS`)
- **`FOREST`**: Dark, foggy environment with particles.
- **`LAVA`**: Volcanic environment (red/orange) with heat haze and lava damage.
- **`DEFAULT`**: Classic space theme.

### Agent Settings (`AGENT_SETTINGS`)
- **`speed`**: Movement speed of the agent.
- **`trail_length`**: Length of the movement trail.
- **`colors`**: Default colors for each agent type.

### Grid Settings (`GRID_SETTINGS`)
- **`size`**: Size of the maze grid (default: 25).
- **`obstacle_prob_...`**: Probability of obstacles generation per theme.
