
from OpenGL.GL import *
from OpenGL.GLU import *

class PathRender:
    """
    Role: Renders the agent's remaining path and the phosphorescent movement trail.
    """

    def __init__(self, cell_size=1.0, grid_size=25):
        self.cell_size = cell_size
        self.grid_size = grid_size

    def draw_path(self, agent):
        """
        Draws the agent's planned remaining path.
        """
        if not agent.path or agent.path_i >= len(agent.path):
            return

        start_index = agent.path_i
        
        glLineWidth(1.0)
        glEnable(GL_LINE_SMOOTH)
        
        glColor3f(agent.color[0] * 0.5, agent.color[1] * 0.5, agent.color[2] * 0.5)

        glBegin(GL_LINE_STRIP)
        for i in range(start_index, len(agent.path)):
            pos = agent.path[i]
            
            # Convert grid coordinates to world coordinates
            x = (pos[0] - self.grid_size//2) * self.cell_size
            z = (pos[1] - self.grid_size//2) * self.cell_size
            
            glVertex3f(float(x), 0.01, float(z))
        glEnd()

    def draw_history(self, agent):
        """
        Draws the agent's historical movement trail with a glow effect.
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
            
            # pos is already in world coordinates from Agent.update()
            glVertex3f(pos[0] - self.grid_size//2, 0.3, pos[2] - self.grid_size//2)
            
        glEnd()