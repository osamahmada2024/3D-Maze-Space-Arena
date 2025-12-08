
import sys
import time
import math
import pygame
import random
from OpenGL.GL import *
from OpenGL.GLU import *

from Agent import Agent
from GridUtils import GridUtils
from PathRender import PathRender
from GoalRender import GoalRender
from MenuManager import MenuManager
from AgentRender import AgentRender
from GridGenerator import GridGenerator
from CameraController import CameraController
from PathfindingEngine import PathfindingEngine
from EnvironmentRender import EnvironmentRender

# NEW: Particle system
from ParticleSystem import ParticleSystem

# ==================== CONFIGURATION ====================
WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 1.0
GRID_SIZE = 25
OBSTACLE_PROB = 0.25

# Cell Types
CELL_FREE = 0
CELL_OBSTACLE = 1
CELL_SLIPPERY = 2

# ==================== HELPER FUNCTION (Cube) ====================
def draw_cube_manual(size):
    """Draws a cube centered at (0, 0, 0)."""
    glBegin(GL_QUADS)
    half = size / 2.0
    
    # Top Face
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-half, half, -half)
    glVertex3f(half, half, -half)
    glVertex3f(half, half, half)
    glVertex3f(-half, half, half)
    
    # Bottom Face
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-half, -half, half)
    glVertex3f(half, -half, half)
    glVertex3f(half, -half, -half)
    glVertex3f(-half, -half, -half)
    
    # Front Face
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-half, half, half)
    glVertex3f(half, half, half)
    glVertex3f(half, -half, half)
    glVertex3f(-half, -half, half)
    
    # Back Face
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-half, -half, -half)
    glVertex3f(half, -half, -half)
    glVertex3f(half, half, -half)
    glVertex3f(-half, half, -half)
    
    # Left Face
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-half, half, -half)
    glVertex3f(-half, half, half)
    glVertex3f(-half, -half, half)
    glVertex3f(-half, -half, -half)
    
    # Right Face
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(half, -half, -half)
    glVertex3f(half, -half, half)
    glVertex3f(half, half, half)
    glVertex3f(half, half, -half)
    
    glEnd()


# ==================== OPENGL INIT (Blizzard Zones) ====================
def init_opengl():
    # Realistic snowy colors: dark blue background
    glClearColor(0.02, 0.02, 0.1, 1.0) 
    
    # Enable depth testing PROPERLY
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearDepth(1.0)
    
    # Enable blending (transparency)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    
    # Cold blue lighting (Light Setup)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 5.0, 1.0])
    # Ambient light: light blue
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.2, 1.0])
    # Diffuse light: cold blue
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.5, 0.6, 0.8, 1.0])

    # Blizzard Zones reducing visibility (Cold Fog)
    glEnable(GL_FOG)
    fog_color = [0.05, 0.1, 0.15, 1.0] # Dark blue fog color
    glFogfv(GL_FOG_COLOR, fog_color)
    glFogi(GL_FOG_MODE, GL_EXP2) # Exponential fog density
    glFogf(GL_FOG_DENSITY, 0.08) # Fog density


def setup_view(camera):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WIDTH / HEIGHT, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    pos = camera.calculate_camera_position()
    target = camera.target
    up = camera._calculate_up_vector()

    gluLookAt(pos[0], pos[1], pos[2],
              target[0], target[1], target[2],
              up[0], up[1], up[2])


# ==================== GRID RENDERING ====================

def draw_grid_3d(grid_size):
    # Change grid lines color to reflect a snowy ground
    glDisable(GL_LIGHTING)
    
    glColor3f(0.2, 0.25, 0.3)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    half = grid_size / 2 * CELL_SIZE
    for i in range(-grid_size//2, grid_size//2 + 1):
        x = i * CELL_SIZE
        glVertex3f(x, 0, -half)
        glVertex3f(x, 0, half)
        glVertex3f(-half, 0, x)
        glVertex3f(half, 0, x)
    glEnd()

    # Draw outer frame
    glColor3f(0.4, 0.5, 0.6)
    glLineWidth(3.0)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-half, 0, -half)
    glVertex3f(half, 0, -half)
    glVertex3f(half, 0, half)
    glVertex3f(-half, 0, half)
    glEnd()
    
    glEnable(GL_LIGHTING)


def draw_obstacles(grid):
    """Draw obstacles as icy cubes (Ice blocks obstructing the path)."""
    glEnable(GL_LIGHTING)
    
    # Enable transparency (Light reflection effects on the ice)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Realistic materials for snow and ice: Ice color (light blue with transparency)
    glColor4f(0.6, 0.8, 0.95, 0.6) # Alpha = 0.6
    
    grid_size = len(grid)
    
    for y in range(grid_size):
        for x in range(len(grid[0])):
            if grid[y][x] == CELL_OBSTACLE:
                wx = (x - grid_size//2) * CELL_SIZE
                wz = (y - grid_size//2) * CELL_SIZE
                
                glPushMatrix()
                # Slightly lift the obstacle to look like an ice block
                glTranslatef(wx, 0.6, wz)
                # Use a slightly larger size (1.1)
                draw_cube_manual(CELL_SIZE * 1.1)
                glPopMatrix()

    # Disable transparency for obstacles
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    
def draw_floor(grid_size, grid):
    """Draw the floor plane. Note: now accepts grid for slippery cells."""
    glDisable(GL_LIGHTING)
    
    # Slippery floor color
    COLOR_SLIPPERY = (0.3, 0.35, 0.4) 
    
    grid_size_half = grid_size / 2 * CELL_SIZE
    
    # Draw floor for the entire area
    glColor3f(0.15, 0.2, 0.25)
    glBegin(GL_QUADS)
    glVertex3f(-grid_size_half, 0, -grid_size_half)
    glVertex3f(grid_size_half, 0, -grid_size_half)
    glVertex3f(grid_size_half, 0, grid_size_half)
    glVertex3f(-grid_size_half, 0, grid_size_half)
    glEnd()

    # Highlight slippery zones (CELL_SLIPPERY = 2)
    glColor3f(*COLOR_SLIPPERY)
    
    for y in range(grid_size):
        for x in range(grid_size):
            if grid[y][x] == CELL_SLIPPERY:
                wx = (x - grid_size//2) * CELL_SIZE
                wz = (y - grid_size//2) * CELL_SIZE
                
                glPushMatrix()
                glTranslatef(wx, 0.01, wz) # Slight lift to avoid Z-fighting
                glBegin(GL_QUADS)
                # Cell (x, z)
                glVertex3f(-CELL_SIZE/2, 0, -CELL_SIZE/2)
                glVertex3f(CELL_SIZE/2, 0, -CELL_SIZE/2)
                glVertex3f(CELL_SIZE/2, 0, CELL_SIZE/2)
                glVertex3f(-CELL_SIZE/2, 0, CELL_SIZE/2)
                glEnd()
                glPopMatrix()

    glEnable(GL_LIGHTING)


# ==================== MAIN LOOP (Agent & Render) ====================

def main():
    # Run menu to select agent and algorithm
    menu = MenuManager()
    menu.run()
    selected_agent = menu.selected_agent
    selected_algo = menu.selected_algo

    if not selected_agent or not selected_algo:
        print("No selection made. Exiting...")
        return
    print(f"Selected Agent: {selected_agent}")
    print(f"Selected Algorithm: {selected_algo}")

    # Initialize Pygame and OpenGL
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("3D Maze-𝕊pace Arena - The Ultimate Pathfinding Experience (ICE MAZE)")
    clock = pygame.time.Clock()
    init_opengl()

    # NEW: Particle system instance (melting + breath)
    particles = ParticleSystem()

    # Generate the maze
    generator = GridGenerator(GRID_SIZE, OBSTACLE_PROB)
    grid = generator.generate()

    # Find Start (0,0) and Goal (N-1, N-1)
    start = (0, 0)
    goal = (GRID_SIZE - 1, GRID_SIZE - 1)

    # Pathfinding
    pathfinder = PathfindingEngine(grid)
    path = pathfinder.find_path(start, goal, selected_algo)
    
    if not path:
        print("No path found! Cannot start simulation.")
        return

    # Create agent based on selection
    speed = 2.0
    color = (0.0, 1.0, 1.0)
    if selected_agent == "AC":
        speed = 1.5
        color = (1.0, 0.0, 0.0)
    elif selected_agent == "ACS":
        speed = 2.5
        color = (0.0, 1.0, 0.0)
    elif selected_agent == "Hybrid":
        speed = 3.0
        color = (0.0, 0.0, 1.0)

    agent = Agent(start, goal, path, speed, color)

    # Visualization systems
    agent_renderer = AgentRender(cell_size=CELL_SIZE)
    path_renderer = PathRender(cell_size=CELL_SIZE, grid_size=GRID_SIZE)
    goal_renderer = GoalRender(cellSize=CELL_SIZE, grid_size=GRID_SIZE)  # أضفت grid_size
    
    # ✨ الكاميرا أقرب ومتابعة أحسن ✨
    camera = CameraController(distance=15, angle_x=45, angle_y=45)

    # Control variables
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # ... (Camera control via mouse and keyboard)

        # 1. Update (Agent and Camera)
        agent.update(dt)
        camera.update(dt)

        # 2. Rendering
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_view(camera)

        # 3. Draw scene components
        draw_floor(GRID_SIZE, grid)
        draw_grid_3d(GRID_SIZE)
        draw_obstacles(grid)
        
        # 3.5 Emit melting particles occasionally from obstacles (to reduce cost, use small probability)
        # You can tune the probability (0.01) and count if needed.
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid[y][x] == CELL_OBSTACLE:
                    if random.random() < 0.01:  # 1% chance per frame per block
                        wx = (x - GRID_SIZE//2) * CELL_SIZE
                        wz = (y - GRID_SIZE//2) * CELL_SIZE
                        particles.emit(wx, 0.55, wz, count=2)

        # 4. Draw path and goal
        glDisable(GL_LIGHTING)
        path_renderer.draw_path(agent.history)
        
        if not agent.arrived:
            glDisable(GL_LIGHTING)
            goal_renderer.draw_goal(agent)
            glEnable(GL_LIGHTING)
        
        # 5. Draw agent
        agent_x = agent.position[0] - GRID_SIZE//2
        agent_z = agent.position[2] - GRID_SIZE//2
        
        glPushMatrix()
        glTranslatef(agent_x, 0.3, agent_z)
        
        # Main solid sphere
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        glColor3f(*agent.color)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, 0.25, 24, 24)
        gluDeleteQuadric(quad)
        
        # Glow effect (Snow Glow)
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*agent.color, 0.15)
        
        quad_glow = gluNewQuadric()
        gluSphere(quad_glow, 0.4, 16, 16)
        gluDeleteQuadric(quad_glow)
        
        # Restore states
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glPopMatrix()

        # Update and draw particles (melting + breath)
        particles.update(dt)
        particles.draw()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()