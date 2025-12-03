from OpenGL.GL import *
from Agent import Agent
from OpenGL.GLU import *
from OpenGL.GLUT import *

class AgentRender:
    def __init__(self, cell_size=60):
        self.cell_size = cell_size
    
    def draw(self, agent: Agent):
        screen_x = (agent.x * self.cell_size) + (self.cell_size / 2)
        screen_y = (agent.y * self.cell_size) + (self.cell_size / 2)
        
        glPushMatrix()
        glTranslatef(screen_x, screen_y, 0)
        glColor3f(*agent.color)
        glutSolidSphere(self.cell_size / 3, 20, 20)
        glPopMatrix()
    
    def draw_grid(self, width, height):
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_LINES)
        for i in range(0, width + 1, self.cell_size):
            glVertex2f(i, 0)
            glVertex2f(i, height)
        for j in range(0, height + 1, self.cell_size):
            glVertex2f(0, j)
            glVertex2f(width, j)
        glEnd()
