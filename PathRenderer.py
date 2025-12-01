from OpenGL.GL import *
from OpenGL.GLU import *

class PathRenderer:
    """
    Role: Renders the agent's remaining path and the phosphorescent movement trail.
    """

    def __init__(self, cell_size=1.0):
        # cell_size is used to convert grid coordinates to world scale.
        self.cell_size = cell_size 
        pass

    def draw_path(self, agent):
        """
        Draws the agent's planned remaining path.
        """
        if not agent.path or agent.path_i >= len(agent.path):
            return

        start_index = agent.path_i
        
        # (Path drawing settings)
        glLineWidth(1.0) # Thin line for the planned path 
        glEnable(GL_LINE_SMOOTH) # Makes lines look smoother/better quality
        
        # (Dimmed color for the path)
        glColor3f(agent.color[0] * 0.5, agent.color[1] * 0.5, agent.color[2] * 0.5) 

        # GL_LINE_STRIP (Draw the line using GL_LINE_STRIP)
        glBegin(GL_LINE_STRIP)
        for i in range(start_index, len(agent.path)):
            pos = agent.path[i]
            
            # Multiply by cell_size to ensure grid coordinates map to world space
            x = pos[0] * self.cell_size
            z = pos[1] * self.cell_size
            
            # Use (x, 0.01, z) to lift the path slightly 
            glVertex3f(float(x), 0.01, float(z)) 
        glEnd()

    def draw_history(self, agent):
        """
        (Glowing Movement Trail): Draws the agent's historical movement trail with a glow effect.
        """
        if not agent.history:
            return

        history_length = len(agent.history)
        
        # 1. (Neon/Glow effect settings)
        glLineWidth(3.0)
        glEnable(GL_LINE_SMOOTH) 
        
        glBegin(GL_LINE_STRIP) 

        for i, pos in enumerate(agent.history):
            # Calculate Alpha based on the point's age in history (Fade-out effect)
            alpha = max(0.2, i / history_length) 

            # (Setting Color and Transparency)
            glColor4f(agent.color[0], agent.color[1], agent.color[2], alpha) 

            # (Setting the 3D World Position)
            glVertex3f(pos[0], 0.05, pos[2]) 
            
        glEnd()