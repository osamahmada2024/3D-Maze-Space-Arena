"""
PathRender.py - Path Rendering System
Renders the agent's path and movement trail
"""

from OpenGL.GL import *
from OpenGL.GLU import *


class PathRender:
    """
    Renders the agent's remaining path and the phosphorescent movement trail.
    """

    def __init__(self, cell_size=1.0, grid_size=25):
        """
        Initialize path renderer.
        
        Args:
            cell_size: Size of each grid cell
            grid_size: Size of the grid (N x N)
        """
        self.cell_size = cell_size
        self.grid_size = grid_size

    def draw_path(self, agent):
        """
        Draw the agent's remaining path as a bright line.
        
        Args:
            agent: Agent object with path and path_i attributes
        """
        if not agent.path or agent.path_i >= len(agent.path):
            return

        start_index = agent.path_i
        glLineWidth(6.0)
        glEnable(GL_LINE_SMOOTH)
        glColor3f(agent.color[0] * 0.8, agent.color[1] * 0.8, agent.color[2] * 0.8)

        glBegin(GL_LINE_STRIP)
        for i in range(start_index, len(agent.path)):
            pos = agent.path[i]
            x = (pos[0] - self.grid_size // 2) * self.cell_size
            z = (pos[1] - self.grid_size // 2) * self.cell_size
            glVertex3f(float(x), 0.01, float(z))
        glEnd()

    def draw_history(self, agent):
        """
        Draw the agent's recent positions with an alpha gradient glow.
        
        Args:
            agent: Agent object with history attribute
        """
        if not agent.history:
            return

        history_length = len(agent.history)
        glLineWidth(5.0)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBegin(GL_LINE_STRIP)
        for i, pos in enumerate(agent.history):
            # Fade older positions
            alpha = max(0.25, (i + 1) / history_length)
            glColor4f(agent.color[0], agent.color[1], agent.color[2], alpha)
            
            # Position is (x, y, z) in world coordinates
            sx = (pos[0] - self.grid_size // 2) * self.cell_size
            sz = (pos[2] - self.grid_size // 2) * self.cell_size
            glVertex3f(sx, 0.3, sz)
        glEnd()
        
        glDisable(GL_BLEND)

    def draw_waypoints(self, path, color=(1.0, 1.0, 0.0)):
        """
        Draw waypoints along the path as small spheres.
        
        Args:
            path: List of (x, y) grid coordinates
            color: RGB color for waypoints
        """
        if not path:
            return
        
        glColor3f(*color)
        
        for pos in path:
            x = (pos[0] - self.grid_size // 2) * self.cell_size
            z = (pos[1] - self.grid_size // 2) * self.cell_size
            
            glPushMatrix()
            glTranslatef(x, 0.1, z)
            
            quad = gluNewQuadric()
            gluSphere(quad, 0.1, 8, 8)
            gluDeleteQuadric(quad)
            
            glPopMatrix()

    def draw_full_path(self, path, color=(0.5, 0.5, 1.0), line_width=3.0):
        """
        Draw the complete path from start to goal.
        
        Args:
            path: List of (x, y) grid coordinates
            color: RGB color for the path
            line_width: Width of the path line
        """
        if not path or len(path) < 2:
            return
        
        glLineWidth(line_width)
        glEnable(GL_LINE_SMOOTH)
        glColor3f(*color)
        
        glBegin(GL_LINE_STRIP)
        for pos in path:
            x = (pos[0] - self.grid_size // 2) * self.cell_size
            z = (pos[1] - self.grid_size // 2) * self.cell_size
            glVertex3f(float(x), 0.05, float(z))
        glEnd()