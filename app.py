"""
app.py - Main Ice Maze Application (FIXED VERSION)
✅ Fixed camera distance
✅ Fixed agent colors
✅ Fixed obstacle colors
✅ Fixed agent path following
✅ Stable rendering
"""

import sys
import time
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

# Import from organized packages
from core.Agent import Agent
from ui.MenuManager import MenuManager
from rendering.PathRender import PathRender
from rendering.GoalRender import GoalRender
from core.GridGenerator import GridGenerator
from rendering.AgentRender import AgentRender
from ui.CameraController import CameraController
from rendering.ParticleSystem import ParticleSystem
from core.PathfindingEngine import PathfindingEngine

# Configuration
WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 1.0
GRID_SIZE = 25
OBSTACLE_PROB = 0.25

CELL_FREE = 0
CELL_OBSTACLE = 1
CELL_SLIPPERY = 2


def draw_cube(size):
    """Draw a cube for obstacles - FIXED COLORS."""
    s = size / 2.0
    glBegin(GL_QUADS)
    
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
    """Initialize OpenGL settings - STABLE."""
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
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.4, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 1.0, 1.0])
    
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, [0.05, 0.1, 0.15, 1.0])
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, 0.08)


def setup_view(camera):
    """Setup camera view - FIXED DISTANCE."""
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
    """Draw floor with slippery zones - FIXED COLORS."""
    glDisable(GL_LIGHTING)
    grid_size_half = grid_size / 2 * CELL_SIZE
    
    # Base floor - dark blue
    glColor3f(0.1, 0.15, 0.25)
    glBegin(GL_QUADS)
    glVertex3f(-grid_size_half, 0, -grid_size_half)
    glVertex3f(grid_size_half, 0, -grid_size_half)
    glVertex3f(grid_size_half, 0, grid_size_half)
    glVertex3f(-grid_size_half, 0, grid_size_half)
    glEnd()

    # Slippery zones - lighter blue
    glColor3f(0.2, 0.3, 0.45)
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
    """Draw ice block obstacles - FIXED COLORS (STABLE)."""
    glEnable(GL_LIGHTING)
    glEnable(GL_BLEND)
    
    # ثابت - لون ثلج أزرق فاتح شفاف
    glColor4f(0.5, 0.7, 0.95, 0.7)
    
    grid_size = len(grid)
    for y in range(grid_size):
        for x in range(len(grid[0])):
            if grid[y][x] == CELL_OBSTACLE:
                wx = (x - grid_size//2) * CELL_SIZE
                wz = (y - grid_size//2) * CELL_SIZE
                
                glPushMatrix()
                glTranslatef(wx, 0.6, wz)
                draw_cube(CELL_SIZE * 1.0)
                glPopMatrix()

    glDisable(GL_BLEND)


def main():
    """Main application - FULLY FIXED."""
    print("="*70)
    print("🎮 3D Maze Arena - Ice Maze (FIXED VERSION)")
    print("="*70)
    
    # Menu - Agent shape selection
    menu = MenuManager()
    menu.run()
    
    selected_agent_shape = menu.selected_agent
    selected_algo = menu.selected_algo
    
    if not selected_agent_shape or not selected_algo:
        print("No selection made. Exiting...")
        return
    
    print(f"✅ Agent Shape: {selected_agent_shape}")
    print(f"✅ Algorithm: {selected_algo}")
    
    # Initialize Pygame and OpenGL
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("3D Maze Arena - Ice Maze (FIXED)")
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
        print("❌ No path found!")
        return
    
    print(f"✅ Path found: {len(path)} steps")
    
    # Agent colors - FIXED AND STABLE
    color_map = {
        "sphere_droid": (0.0, 1.0, 1.0),    # Cyan
        "robo_cube": (1.0, 0.6, 0.0),       # Orange
        "mini_drone": (0.0, 1.0, 0.5),      # Green-cyan
        "crystal_alien": (1.0, 0.2, 1.0)    # Magenta
    }
    
    agent_color = color_map.get(selected_agent_shape, (0.0, 1.0, 1.0))
    
    # Create agent with FIXED parameters
    agent = Agent(
        start, goal, path,
        speed=2.5,  # قليلاً أسرع
        color=agent_color,
        grid=grid
    )
    
    # Rendering systems
    agent_renderer = AgentRender(cell_size=CELL_SIZE, grid_size=GRID_SIZE)
    
    # FIXED CAMERA - closer and better angle
    camera = CameraController(
        angle_x=0.0,
        angle_y=60.0,  # زاوية أفضل
        angle_z=0.0,
        distance=12.0  # أقرب كتير!
    )
    
    goal_renderer = GoalRender(cellSize=CELL_SIZE, grid_size=GRID_SIZE)
    path_renderer = PathRender(cell_size=CELL_SIZE, grid_size=GRID_SIZE)
    particles = ParticleSystem()
    
    print("\n" + "="*70)
    print("🎮 Controls:")
    print("  Arrow Keys  - Rotate camera")
    print("  Mouse Wheel - Zoom")
    print("  ESC         - Exit")
    print("="*70 + "\n")
    print("✅ Game ready!")
    
    # Main loop
    running = True
    last_time = time.time()
    
    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEWHEEL:
                camera.zoom(-event.y * 1.5)
        
        # Camera controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            camera.rotate(-45 * dt, 0)
        if keys[pygame.K_RIGHT]:
            camera.rotate(45 * dt, 0)
        if keys[pygame.K_UP]:
            camera.rotate(0, 25 * dt)
        if keys[pygame.K_DOWN]:
            camera.rotate(0, -25 * dt)
        
        # Update agent
        agent.update(dt)
        
        # Camera follows agent SMOOTHLY
        agent_world_x = (agent.position[0] - GRID_SIZE//2) * CELL_SIZE
        agent_world_z = (agent.position[2] - GRID_SIZE//2) * CELL_SIZE
        camera.follow_target([agent_world_x, 0.0, agent_world_z])
        
        # Update particles
        particles.update(dt)
        
        # Rendering
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_view(camera)
        
        # Draw scene
        draw_floor(GRID_SIZE, grid)
        draw_obstacles(grid)
        
        # Draw path (lighting off for lines)
        glDisable(GL_LIGHTING)
        path_renderer.draw_history(agent)
        path_renderer.draw_path(agent)
        glEnable(GL_LIGHTING)
        
        # Draw goal
        if not agent.arrived:
            goal_renderer.draw_goal(agent)
        
        # Draw agent with selected shape - world coordinates
        glPushMatrix()
        glTranslatef(agent_world_x, agent.position[1], agent_world_z)
        agent_renderer.draw_agent(agent, shape_type=selected_agent_shape)
        glPopMatrix()
        
        pygame.display.flip()
        clock.tick(60)
        
        # Victory check
        if agent.arrived:
            print("\n" + "="*70)
            print("🎉 VICTORY! You reached the goal!")
            print("="*70)
            time.sleep(2)
            running = False
    
    pygame.quit()
    print("\n✅ Game closed successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()