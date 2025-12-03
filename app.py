import sys
import time
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
from EnvironmentRender import EnvironmentRender  # Imported for consistency; minimal usage in 3D

# Screen configuration
WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 1.0

def init_opengl():
    glClearColor(0.05, 0.05, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

def setup_view(camera: CameraController):
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

def draw_grid_3d(grid_size):
    glColor3f(0.15, 0.15, 0.2)
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
    glColor3f(0.3, 0.3, 0.4)
    glLineWidth(3.0)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-half, 0, -half)
    glVertex3f(half, 0, -half)
    glVertex3f(half, 0, half)
    glVertex3f(-half, 0, half)
    glEnd()

def draw_obstacles(grid, utils):
    glColor3f(0.2, 0.2, 0.3)
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == 1:
                wx = (x - len(grid)//2) * CELL_SIZE
                wz = (y - len(grid)//2) * CELL_SIZE
                glPushMatrix()
                glTranslatef(wx, 0.5, wz)
                glutSolidCube(CELL_SIZE * 0.9)
                glPopMatrix()

def main():
    # Run menu to select agent and algorithm
    menu = MenuManager()
    menu.run()  # Continues until user makes a selection

    selected_agent = menu.selected_agent
    selected_algo = menu.selected_algo

    if not selected_agent or not selected_algo:
        print("No selection made. Exiting...")
        return

    print(f"Selected Agent: {selected_agent}")
    print(f"Selected Algorithm: {selected_algo}")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("3D Maze-𝕊pace Arena - The Ultimate Pathfinding Experience")
    clock = pygame.time.Clock()

    init_opengl()

    # Generate the maze
    GRID_SIZE = 25
    OBSTACLE_PROB = 0.25
    generator = GridGenerator(GRID_SIZE, OBSTACLE_PROB)
    grid = generator.generate()
    utils = GridUtils(grid)

    # Ensure start and goal positions are free
    start = (0, 0)
    goal = (GRID_SIZE-1, GRID_SIZE-1)
    while not utils.free(*start):
        start = (random.randint(0, GRID_SIZE//3), random.randint(0, GRID_SIZE//3))
    while not utils.free(*goal):
        goal = (random.randint(GRID_SIZE//2, GRID_SIZE-1), random.randint(GRID_SIZE//2, GRID_SIZE-1))

    # Compute path using the selected algorithm
    engine = PathfindingEngine(grid)
    path = engine.find_path(start, goal, selected_algo)
    if not path:
        print("No path could be found!")
        return

    # Create agent based on selection
    speed = 2.0  # Default
    color = (0.0, 1.0, 1.0)  # Default cyan
    if selected_agent == "AC":
        speed = 1.5
        color = (1.0, 0.0, 0.0)  # Red
    elif selected_agent == "ACS":
        speed = 2.5
        color = (0.0, 1.0, 0.0)  # Green
    elif selected_agent == "Hybrid":
        speed = 3.0
        color = (0.0, 0.0, 1.0)  # Blue

    agent = Agent(start, goal, path, speed, color)

    # Visualization systems
    agent_renderer = AgentRender(cell_size=CELL_SIZE)
    path_renderer = PathRender(cell_size=CELL_SIZE)
    goal_renderer = GoalRender(cellSize=CELL_SIZE)
    camera = CameraController(distance=30, angle_x=45, angle_y=35)

    # Control variables
    running = True
    last_time = time.time()

    print("3D Maze-𝕊pace Arena initialized successfully!")
    print(f"Start: {start} | Goal: {goal} | Path length: {len(path)} steps")

    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                camera.distance -= event.y * 2
                camera.distance = max(5, min(60, camera.distance))

        # Camera control via keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  camera.angle_x -= 60 * dt
        if keys[pygame.K_RIGHT]: camera.angle_x += 60 * dt
        if keys[pygame.K_UP]:    camera.angle_y += 60 * dt
        if keys[pygame.K_DOWN]:  camera.angle_y -= 60 * dt
        camera.angle_y = max(-89, min(89, camera.angle_y))

        # Update agent
        agent.update(dt)

        # Center camera on agent
        wx = (agent.position[0] - GRID_SIZE//2) * CELL_SIZE
        wz = (agent.position[2] - GRID_SIZE//2) * CELL_SIZE
        camera.target = [wx, 0, wz]

        # Rendering
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_view(camera)

        # Floor and grid
        draw_grid_3d(GRID_SIZE)
        draw_obstacles(grid, utils)

        # Draw remaining path and phosphorescent trail
        path_renderer.draw_path(agent)
        path_renderer.draw_history(agent)

        # Draw glowing goal
        goal_renderer.draw_goal(agent)

        # Draw agent (glowing sphere)
        glPushMatrix()
        glTranslatef(agent.position[0] - GRID_SIZE//2, 0.3, agent.position[2] - GRID_SIZE//2)
        glColor3f(*agent.color)
        quad = gluNewQuadric()
        gluSphere(quad, 0.25, 24, 24)
        gluDeleteQuadric(quad)

        # External glow effect
        glDisable(GL_DEPTH_TEST)
        glColor4f(*agent.color, 0.15)
        gluSphere(quad, 0.4, 16, 16)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()

        # Display victory message
        if agent.arrived:
            print("Goal reached! Congratulations!")
            # Optional: draw on-screen text

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        from OpenGL.GLUT import glutSolidCube, glutInit
        glutInit()
    except:
        print("Warning: GLUT not available. Obstacles will be rendered as spheres instead of cubes.")
    main()
