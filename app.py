
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
from EnvironmentRender import EnvironmentRender

# Screen configuration
WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 1.0

def init_opengl():
    glClearColor(0.05, 0.05, 0.1, 1.0)
    
    # Enable depth testing PROPERLY
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearDepth(1.0)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    
    # Enable lighting for better 3D appearance
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set up light
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 5.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])

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

def draw_grid_3d(grid_size):
    # Disable lighting for grid lines
    glDisable(GL_LIGHTING)
    
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
    
    glEnable(GL_LIGHTING)

def draw_cube_manual(size):
    """Draw a cube using GL_QUADS (no GLUT dependency)"""
    s = size / 2.0
    
    glBegin(GL_QUADS)
    
    # Front face
    glNormal3f(0, 0, 1)
    glVertex3f(-s, -s, s)
    glVertex3f(s, -s, s)
    glVertex3f(s, s, s)
    glVertex3f(-s, s, s)
    
    # Back face
    glNormal3f(0, 0, -1)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s, s, -s)
    glVertex3f(s, s, -s)
    glVertex3f(s, -s, -s)
    
    # Top face
    glNormal3f(0, 1, 0)
    glVertex3f(-s, s, -s)
    glVertex3f(-s, s, s)
    glVertex3f(s, s, s)
    glVertex3f(s, s, -s)
    
    # Bottom face
    glNormal3f(0, -1, 0)
    glVertex3f(-s, -s, -s)
    glVertex3f(s, -s, -s)
    glVertex3f(s, -s, s)
    glVertex3f(-s, -s, s)
    
    # Right face
    glNormal3f(1, 0, 0)
    glVertex3f(s, -s, -s)
    glVertex3f(s, s, -s)
    glVertex3f(s, s, s)
    glVertex3f(s, -s, s)
    
    # Left face
    glNormal3f(-1, 0, 0)
    glVertex3f(-s, -s, -s)
    glVertex3f(-s, -s, s)
    glVertex3f(-s, s, s)
    glVertex3f(-s, s, -s)
    
    glEnd()

def draw_obstacles(grid):
    """Draw obstacles as cubes WITH proper depth"""
    glEnable(GL_LIGHTING)
    glColor3f(0.2, 0.2, 0.3)
    grid_size = len(grid)
    
    for y in range(grid_size):
        for x in range(len(grid[0])):
            if grid[y][x] == 1:
                wx = (x - grid_size//2) * CELL_SIZE
                wz = (y - grid_size//2) * CELL_SIZE
                
                glPushMatrix()
                glTranslatef(wx, 0.5, wz)
                draw_cube_manual(CELL_SIZE * 0.9)
                glPopMatrix()

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
    
    # Make sure start and goal are free
    grid[start[1]][start[0]] = 0
    grid[goal[1]][goal[0]] = 0

    # Compute path using the selected algorithm
    engine = PathfindingEngine(grid)
    
    # Map algorithm names
    algo_map = {
        "A* search": "astar",
        "Dijkstra": "dijkstra",
        "DFS": "dfs",
        "BFS": "bfs"
    }
    algo_name = algo_map.get(selected_algo, selected_algo.lower())
    
    path = engine.find_path(start, goal, algo_name)
    if not path:
        print("No path could be found!")
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEWHEEL:
                camera.distance -= event.y * 2
                # ✨ Range أصغر للـ zoom (3-40 بدل 5-60) ✨
                camera.distance = max(3, min(40, camera.distance))

        # Camera control via keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  
            camera.angle_x -= 60 * dt
        if keys[pygame.K_RIGHT]: 
            camera.angle_x += 60 * dt
        if keys[pygame.K_UP]:    
            camera.angle_y += 60 * dt
        if keys[pygame.K_DOWN]:  
            camera.angle_y -= 60 * dt
        camera.angle_y = max(-89, min(89, camera.angle_y))

        # Update agent
        agent.update(dt)

        # ✨ Center camera on agent position (including Y height!) ✨
        wx = (agent.position[0]) * CELL_SIZE
        wy = agent.position[1]  # ارتفاع الـ Agent (0.3)
        wz = (agent.position[2]) * CELL_SIZE
        camera.target = [wx, wy, wz]

        # === RENDERING - ORDER MATTERS FOR DEPTH! ===
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_view(camera)

        # 1. Draw floor and grid
        draw_grid_3d(GRID_SIZE)
        
        # 2. Draw obstacles
        draw_obstacles(grid)
        
        # 3. Draw paths
        glDisable(GL_LIGHTING)
        path_renderer.draw_path(agent)
        path_renderer.draw_history(agent)
        glEnable(GL_LIGHTING)
        
        # 4. ✨ Draw goal بس لو الـ Agent لسه مواصلش ✨
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
        
        # Glow effect
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
        glEnable(GL_LIGHTING)
        
        glPopMatrix()

        # Display victory message
        if agent.arrived:
            if not hasattr(agent, '_victory_printed'):
                print("🎉 Goal reached! Congratulations!")
                agent._victory_printed = True

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()