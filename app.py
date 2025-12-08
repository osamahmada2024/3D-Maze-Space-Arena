import sys
import time
import math
import pygame
import random
from OpenGL.GL import *
from OpenGL.GLU import *

# Import from organized packages
from core.Agent import Agent
from core.GridGenerator import GridGenerator
from core.PathfindingEngine import PathfindingEngine
from rendering.PathRender import PathRender
from rendering.GoalRender import GoalRender
from rendering.ParticleSystem import ParticleSystem
from ui.MenuManager import MenuManager
from ui.CameraController import CameraController

# Configuration
WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 1.0
GRID_SIZE = 25
OBSTACLE_PROB = 0.25

CELL_FREE = 0
CELL_OBSTACLE = 1
CELL_SLIPPERY = 2


def draw_cube(size):
    """Draw a cube."""
    s = size / 2.0
    glBegin(GL_QUADS)
    
    # All 6 faces
    faces = [
        ([0,0,1], [(-s,-s,s), (s,-s,s), (s,s,s), (-s,s,s)]),
        ([0,0,-1], [(-s,-s,-s), (-s,s,-s), (s,s,-s), (s,-s,-s)]),
        ([0,1,0], [(-s,s,-s), (-s,s,s), (s,s,s), (s,s,-s)]),
        ([0,-1,0], [(-s,-s,-s), (s,-s,-s), (s,-s,s), (-s,-s,s)]),
        ([1,0,0], [(s,-s,-s), (s,s,-s), (s,s,s), (s,-s,s)]),
        ([-1,0,0], [(-s,-s,-s), (-s,-s,s), (-s,s,s), (-s,s,-s)])
    ]
    
    for normal, vertices in faces:
        glNormal3f(*normal)
        for v in vertices:
            glVertex3f(*v)
    
    glEnd()


def init_opengl():
    """Initialize OpenGL settings."""
    glClearColor(0.02, 0.02, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearDepth(1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 5.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.5, 0.6, 0.8, 1.0])
    
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, [0.05, 0.1, 0.15, 1.0])
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, 0.08)


def setup_view(camera):
    """Setup camera view."""
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


def draw_floor(grid_size, grid):
    """Draw floor with slippery zones."""
    glDisable(GL_LIGHTING)
    grid_size_half = grid_size / 2 * CELL_SIZE
    
    glColor3f(0.15, 0.2, 0.25)
    glBegin(GL_QUADS)
    glVertex3f(-grid_size_half, 0, -grid_size_half)
    glVertex3f(grid_size_half, 0, -grid_size_half)
    glVertex3f(grid_size_half, 0, grid_size_half)
    glVertex3f(-grid_size_half, 0, grid_size_half)
    glEnd()

    # Slippery zones
    glColor3f(0.3, 0.35, 0.4)
    for y in range(grid_size):
        for x in range(grid_size):
            if grid[y][x] == CELL_SLIPPERY:
                wx = (x - grid_size//2) * CELL_SIZE
                wz = (y - grid_size//2) * CELL_SIZE
                
                glPushMatrix()
                glTranslatef(wx, 0.01, wz)
                glBegin(GL_QUADS)
                s = CELL_SIZE / 2
                glVertex3f(-s, 0, -s)
                glVertex3f(s, 0, -s)
                glVertex3f(s, 0, s)
                glVertex3f(-s, 0, s)
                glEnd()
                glPopMatrix()

    glEnable(GL_LIGHTING)


def draw_obstacles(grid):
    """Draw ice block obstacles."""
    glEnable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glColor4f(0.6, 0.8, 0.95, 0.6)
    
    grid_size = len(grid)
    for y in range(grid_size):
        for x in range(len(grid[0])):
            if grid[y][x] == CELL_OBSTACLE:
                wx = (x - grid_size//2) * CELL_SIZE
                wz = (y - grid_size//2) * CELL_SIZE
                
                glPushMatrix()
                glTranslatef(wx, 0.6, wz)
                draw_cube(CELL_SIZE * 1.1)
                glPopMatrix()

    glDisable(GL_BLEND)


def main():
    """Main application."""
    print("="*60)
    print("🎮 3D Maze Arena - Ice Maze")
    print("="*60)
    
    # Menu
    menu = MenuManager()
    menu.run()
    
    selected_agent = menu.selected_agent
    selected_algo = menu.selected_algo
    
    if not selected_agent or not selected_algo:
        print("No selection made. Exiting...")
        return
    
    print(f"Agent: {selected_agent}, Algorithm: {selected_algo}")
    
    # Initialize Pygame and OpenGL
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("3D Maze Arena - Ice Maze")
    clock = pygame.time.Clock()
    init_opengl()
    
    # Generate maze
    generator = GridGenerator(GRID_SIZE, OBSTACLE_PROB)
    grid = generator.generate()
    
    start = (0, 0)
    goal = (GRID_SIZE - 1, GRID_SIZE - 1)
    
    # Find path
    pathfinder = PathfindingEngine(grid)
    path = pathfinder.find_path(start, goal, selected_algo)
    
    if not path:
        print("No path found!")
        return
    
    # Create agent
    speed_map = {"AC": 1.5, "ACS": 2.5, "Hybrid": 3.0}
    color_map = {"AC": (1,0,0), "ACS": (0,1,0), "Hybrid": (0,0,1)}
    
    agent = Agent(
        start, goal, path,
        speed_map.get(selected_agent, 2.0),
        color_map.get(selected_agent, (1,1,1)),
        grid
    )
    
    # Rendering systems
    camera = CameraController(distance=20, angle_x=45, angle_y=60)
    goal_renderer = GoalRender(cellSize=CELL_SIZE, grid_size=GRID_SIZE)
    path_renderer = PathRender(cell_size=CELL_SIZE, grid_size=GRID_SIZE)
    particles = ParticleSystem()
    
    print("✅ Game ready!")
    
    # Main loop
    running = True
    last_time = time.time()
    
    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEWHEEL:
                camera.zoom(-event.y * 2)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            camera.rotate(-60 * dt, 0)
        if keys[pygame.K_RIGHT]:
            camera.rotate(60 * dt, 0)
        if keys[pygame.K_UP]:
            camera.rotate(0, 30 * dt)
        if keys[pygame.K_DOWN]:
            camera.rotate(0, -30 * dt)
        
        agent.update(dt)
        camera.follow_target(agent.position)
        particles.update(dt)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_view(camera)
        
        draw_floor(GRID_SIZE, grid)
        draw_obstacles(grid)
        
        glDisable(GL_LIGHTING)
        path_renderer.draw_history(agent)
        path_renderer.draw_path(agent)
        glEnable(GL_LIGHTING)
        
        if not agent.arrived:
            goal_renderer.draw_goal(agent)
        
        # Draw agent
        agent_x = agent.position[0] - GRID_SIZE//2
        agent_z = agent.position[2] - GRID_SIZE//2
        
        glPushMatrix()
        glTranslatef(agent_x, 0.3, agent_z)
        glEnable(GL_LIGHTING)
        glColor3f(*agent.color)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, 0.25, 24, 24)
        gluDeleteQuadric(quad)
        
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glColor4f(*agent.color, 0.15)
        quad_glow = gluNewQuadric()
        gluSphere(quad_glow, 0.4, 16, 16)
        gluDeleteQuadric(quad_glow)
        glDepthMask(GL_TRUE)
        glPopMatrix()
        
        pygame.display.flip()
        clock.tick(60)
        
        if agent.arrived:
            print("🎉 Goal reached!")
            time.sleep(2)
            running = False
    
    pygame.quit()
    print("✅ Game closed")


if __name__ == "__main__":
    main()