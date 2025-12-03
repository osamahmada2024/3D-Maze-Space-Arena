from OpenGL.GL import *
from OpenGL.GLU import *

# ==============================
# Class: PathRender
# Role: Render the computed path and the agent's movement trail.
# Responsibilities:
#   • Show the agent's planned remaining path.
#   • Show the glowing movement history (phosphorescent trail).
# Required Inputs:
#   • agent.path: List of remaining path coordinates.
#   • agent.history: List of past positions.
#   • agent.color: Tuple[float, float, float] RGB color.
# Public Methods:
#   • draw_path(agent) -> None
#   • draw_history(agent) -> None
# Internal State:
#   • self.cell_size: float
# ==============================

class PathRender:
    def __init__(self, cell_size: float = 1.0):
        """
        Initialize PathRenderer.
        
        Args:
            cell_size (float): Scale to convert grid coordinates to world coordinates.
        """
        self.cell_size: float = cell_size

    # ==============================
    # Public Method: draw_path
    # ==============================
    def draw_path(self, agent):
        """
        Draw the agent's planned remaining path as a thin line.
        """
        if not agent.path or agent.path_i >= len(agent.path):
            return

        start_index = agent.path_i
        glLineWidth(1.0)
        glEnable(GL_LINE_SMOOTH)
        glColor3f(agent.color[0] * 0.5, agent.color[1] * 0.5, agent.color[2] * 0.5)

        glBegin(GL_LINE_STRIP)
        for i in range(start_index, len(agent.path)):
            x = agent.path[i][0] * self.cell_size
            z = agent.path[i][1] * self.cell_size
            glVertex3f(float(x), 0.01, float(z))
        glEnd()

    # ==============================
    # Public Method: draw_history
    # ==============================
    def draw_history(self, agent):
        """
        Draw the agent's historical movement trail with a glow/fade effect.
        """
        if not agent.history:
            return

        history_length = len(agent.history)
        glLineWidth(3.0)
        glEnable(GL_LINE_SMOOTH)
        glBegin(GL_LINE_STRIP)

        for i, pos in enumerate(agent.history):
            alpha = max(0.2, i / history_length)
            glColor4f(agent.color[0], agent.color[1], agent.color[2], alpha)
            glVertex3f(pos[0], 0.05, pos[2])
        glEnd()
