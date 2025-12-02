from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Agent:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

class AgentRenderer:
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

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

renderer = AgentRenderer()
agents = [
    Agent(5, 5, (0.0, 1.0, 0.0)),
    Agent(10, 10, (1.0, 0.0, 0.0))
]

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    renderer.draw_grid(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    for agent in agents:
        renderer.draw(agent)
    
    glutSwapBuffers()

def main():
    try:
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        glutCreateWindow("Agent Renderer - Improved Version")
        init()
        glutDisplayFunc(display)
        glutMainLoop()
    except Exception as e:
        print(f"Error initializing GLUT: {e}. Ensure PyOpenGL is installed and the system supports OpenGL.")

if __name__ == "__main__":
    main()
