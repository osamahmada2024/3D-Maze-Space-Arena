# 🌟 PathRenderer Module README

## Overview

The **PathRenderer** is the visual component responsible for showing us exactly what the agents are thinking and doing. It doesn't handle the logic of _finding_ the path, but rather the art of **displaying** it.

Think of this class as the "painter" of the project. Its main job is to draw the planned route the agent is about to take and leave a **glowing, phosphorescent trail** behind the agent to show where it has been.

---

## 🎨 Key Features

- **Planned Path Visualization:** Draws a thin, dimmed line showing the remaining nodes the agent needs to visit to reach its goal.
- **Phosphorescent History Trail:** This is the cool visual effect. It draws a thick, glowing line representing the agent's movement history.
- **Neon/Glow Effect:** The trail isn't just a solid line; it uses **alpha blending** to fade out older points, creating a "neon" or "phosphorescent" look, similar to a light cycle.
- **3D Optimization:** The renderer automatically lifts the lines slightly above the floor (`y=0.05`) so the path doesn't glitch or clip into the ground tiles.

---

## 🛠️ Class Breakdown

### `PathRenderer`

**Role:** Render computed paths and movement trails.

#### Required Inputs

To do its job, this renderer needs access to a standard **Agent** object containing:

- `agent.path`: The list of future grid coordinates.
- `agent.history`: The list of past coordinates (where it has been).
- `agent.color`: The unique color assigned to that specific agent.

#### Public Methods

1.  **`draw_path(agent)`**

    - **What it does:** Iterates through the _remaining_ path indices (from `agent.path_i` to the end) and draws a simple line strip connecting them.
    - **Style:** Thin line width, slightly dimmed color.

2.  **`draw_history(agent)`**

    - **What it does:** Iterates through the `history` list to draw the trail.
    - **The "Glow" Logic:** It calculates transparency (`alpha`) based on the age of the point.
      - _Oldest points_ = High transparency (faded).
      - _Newest points_ = Low transparency (solid bright color).
    - **Style:** Thick line width (`glLineWidth(3)`), uses transparency blending.

---

## 🚀 How to Use

In your main simulation loop, you simply instantiate the renderer once, and then call its draw methods every frame for each agent.

```python
# 1. Initialization
path_renderer = PathRenderer()

# 2. Inside your Main Loop (The 'display' or 'render' function)
# Assuming 'agents' is a list of all your Agent objects
for agent in agents:
    # Draw the neon trail behind the agent (This is the required glowing line)
    path_renderer.draw_history(agent)

    # Draw the line showing where the agent is going next (The planned route)
    path_renderer.draw_path(agent)
```
