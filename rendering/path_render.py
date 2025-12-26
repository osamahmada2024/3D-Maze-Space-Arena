from OpenGL.GL import *
from OpenGL.GLU import *

class PathRender:
    """
    Role: Renders the agent's remaining path and the Flash-style movement trail.
    Optimized for smooth performance.
    """

    def __init__(self, cell_size=1.0, grid_size=25, ground_sampler=None):
        self.cell_size = cell_size
        self.grid_size = grid_size
        self.ground_sampler = ground_sampler

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
            
            x = (pos[0] - self.grid_size//2) * self.cell_size
            z = (pos[1] - self.grid_size//2) * self.cell_size

            if self.ground_sampler is not None:
                y = self.ground_sampler(x, z) + 0.1
            else:
                y = 0.01

            glVertex3f(float(x), float(y), float(z))
        glEnd()

    def draw_history(self, agent):
        """
        ✨ Optimized Flash-style trail - single draw call
        """
        if not agent.history or len(agent.history) < 2:
            return

        history_list = list(agent.history)
        history_length = len(history_list)
        half_grid = self.grid_size // 2
        
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glLineWidth(3.0)
        glBegin(GL_LINE_STRIP)
        
        for i, pos in enumerate(history_list):
            if history_length > 1:
                norm = float(i) / float(history_length - 1)
            else:
                norm = 1.0
            
            alpha = norm ** 0.5
            glow = 0.5 + (norm * 0.5)
            
            glColor4f(
                agent.color[0] * glow,
                agent.color[1] * glow,
                agent.color[2] * glow,
                alpha
            )
            
            glVertex3f(
                pos[0] - half_grid,
                0.3,
                pos[2] - half_grid
            )
        
        glEnd()
        
        glDisable(GL_BLEND)
        glLineWidth(1.0)

    def draw_coverage(self, agents):
        """
        Draws highlighted squares for every cell visited by the agents.
        """
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Lift slightly above floor to avoid z-fighting
        y_height = 0.05
        
        half_grid = self.grid_size // 2
        
        glBegin(GL_QUADS)
        
        for agent in agents:
            r, g, b = agent.color
            # Use low alpha for coverage to not be overwhelming
            glColor4f(r, g, b, 0.3)
            
            for (gx, gy) in agent.visited_cells:
                # Convert grid to world
                x = (gx - half_grid) * self.cell_size
                z = (gy - half_grid) * self.cell_size
                
                half_cell = self.cell_size * 0.45 # Slightly smaller than full cell
                
                glVertex3f(x - half_cell, y_height, z - half_cell)
                glVertex3f(x + half_cell, y_height, z - half_cell)
                glVertex3f(x + half_cell, y_height, z + half_cell)
                glVertex3f(x - half_cell, y_height, z + half_cell)
                
        glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)