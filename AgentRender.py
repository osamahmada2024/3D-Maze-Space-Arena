from OpenGL.GL import *
from Agent import Agent
from OpenGL.GLU import *
from OpenGL.GLUT import *
from typing import Optional


class AgentRender:
    """
    Handles rendering of the agent and arena grid.
    """

    def __init__(self, cell_size: int = 60):
        self.cell_size = cell_size

    # ---------------------------------------------------------

    def draw(self, agent: Agent) -> None:
        """Draw the agent at its world position."""
        x, _, z = agent.position
        sx = (x * self.cell_size) + (self.cell_size / 2)
        sy = (z * self.cell_size) + (self.cell_size / 2)

        glPushMatrix()
        glTranslatef(sx, sy, 0)
        glColor3f(*agent.color)
        glutSolidSphere(self.cell_size / 3, 20, 20)
        glPopMatrix()

    # ---------------------------------------------------------

    def draw_grid(self, width: int, height: int) -> None:
        """Draw grid lines for the arena."""
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_LINES)

        # Vertical
        for i in range(0, width + 1, self.cell_size):
            glVertex2f(i, 0)
            glVertex2f(i, height)

        # Horizontal
        for j in range(0, height + 1, self.cell_size):
            glVertex2f(0, j)
            glVertex2f(width, j)

        glEnd()
