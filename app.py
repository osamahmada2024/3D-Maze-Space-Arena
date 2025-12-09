import sys
import time
import pygame
import random
from OpenGL.GL import *
from OpenGL.GLU import *

# from Agent import Agent
# from GridUtils import GridUtils
# from PathRender import PathRender
# from GoalRender import GoalRender
# from MenuManager import MenuManager
# from AgentRender import AgentRender
# from GridGenerator import GridGenerator
# from CameraController import CameraController
# from PathfindingEngine import PathfindingEngine
# from EnvironmentRender import EnvironmentRender3D

# import ui
# import core
# import forest
# import gestures
# import features
# import rendering    
from core.Agent import Agent
from core.Player import Player
from core.Player import GameMode
from core.Player import PowerUpType
from core.Player import MatchManager
from core.GridUtils import GridUtils
from core.GridGenerator import GridGenerator
from core.PathfindingEngine import PathfindingEngine

from rendering.GoalRender import GoalRender
from rendering.PathRender import PathRender
from rendering.AgentRender import AgentRender
from rendering.MenuManager import MenuManager
from rendering.EnvironmentRender import EnvironmentRender3D


from features.Feature_Valcon_Maze import Audio
from features.Feature_Valcon_Maze import BurnTile
from features.Feature_Valcon_Maze import Particle
from features.Feature_Valcon_Maze import Obstacles
from features.Feature_Valcon_Maze import MovingLava
from features.Feature_Valcon_Maze import Obstacles  
from features.Feature_Valcon_Maze import FallingStone
# from features.Feature_Valcon_Maze import ParticleSystem # THIS FILE IS Named in rendering/__init__.py
from features.Feature_Valcon_Maze import LavaEnvironment
from features.lucky_blocks import (
        LuckyBlock,
        EffectType,
        ActiveEffect,
        TeleportPoint,
        GameFlowIntegration,
        LuckyBlockTeleportSystem,
    )





from ui.MenuManager import MenuManager
from ui.CameraController import CameraController

# Screen configuration
WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 1.0

def init_opengl():
    glClearColor(0.05, 0.05, 0.1, 1.0)
    
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

def main():
    menu = MenuManager()
    menu.run()

    selected_shape = menu.selected_agent
    selected_algo = menu.selected_algo

    if not selected_shape or not selected_algo:
        print("No selection made. Exiting...")
        return

    print(f"Selected Agent Shape: {selected_shape}")
    print(f"Selected Algorithm: {selected_algo}")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("3D Maze-𝕊pace Arena - The Ultimate Pathfinding Experience")
    clock = pygame.time.Clock()

    init_opengl()

    GRID_SIZE = 25
    OBSTACLE_PROB = 0.25
    generator = GridGenerator(GRID_SIZE, OBSTACLE_PROB)
    grid = generator.generate()
    utils = GridUtils(grid)

    start = (0, 0)
    goal = (GRID_SIZE-1, GRID_SIZE-1)
    
    grid[start[1]][start[0]] = 0
    grid[goal[1]][goal[0]] = 0

    engine = PathfindingEngine(grid)
    
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

    shape_colors = {
        "sphere_droid": (0.0, 1.0, 1.0),
        "robo_cube": (1.0, 0.3, 0.3),
        "mini_drone": (0.2, 0.7, 0.3),
        "crystal_alien": (0.8, 0.3, 1.0)
    }
    
    agent_color = shape_colors.get(selected_shape, (0.0, 1.0, 1.0))
    agent_speed = 2.5

    # ✨ التعديل هنا - إضافة trail_length للتحكم بطول الذيل
    # يمكنك تغيير القيمة: 20 = قصير، 40 = متوسط، 60 = طويل
    TRAIL_LENGTH = 15  # طول ذيل مثل Flash
    
    agent = Agent(
        start, 
        goal, 
        path, 
        agent_speed, 
        agent_color, 
        selected_shape, 
        trail_length=TRAIL_LENGTH  # ✨ هذا الـ parameter الجديد
    )

    environment_renderer = EnvironmentRender3D(grid, cell_size=CELL_SIZE)
    agent_renderer = AgentRender(cell_size=CELL_SIZE, grid_size=GRID_SIZE)
    path_renderer = PathRender(cell_size=CELL_SIZE, grid_size=GRID_SIZE, ground_sampler=environment_renderer.get_ground_height)
    goal_renderer = GoalRender(cellSize=CELL_SIZE, grid_size=GRID_SIZE)
    
    camera = CameraController(distance=15, angle_x=45, angle_y=45)

    running = True
    last_time = time.time()
    start_time = time.time()

    print("3D Maze-Space Arena initialized successfully!")
    print(f"Start: {start} | Goal: {goal} | Path length: {len(path)} steps")
    print(f"Agent Shape: {selected_shape}")
    print(f"Trail Length: {TRAIL_LENGTH}")  # ✨ طباعة طول الذيل

    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        elapsed_time = current_time - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEWHEEL:
                camera.distance -= event.y * 2
                camera.distance = max(3, min(40, camera.distance))

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

        agent.update(dt)

        agent_renderer.update_time(dt)

        wx = (agent.position[0]) * CELL_SIZE
        wy = agent.position[1]
        wz = (agent.position[2]) * CELL_SIZE
        camera.target = [wx, wy, wz]

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_view(camera)

        environment_renderer.draw(elapsed_time)
        
        glDisable(GL_LIGHTING)
        path_renderer.draw_path(agent)
        path_renderer.draw_history(agent)
        glEnable(GL_LIGHTING)
        
        if not agent.arrived:
            glDisable(GL_LIGHTING)
            goal_renderer.draw_goal(agent)
            glEnable(GL_LIGHTING)
        
        agent_renderer.draw_agent(agent, agent.shape_type)

        if agent.arrived:
            if not hasattr(agent, '_victory_printed'):
                print("Goal reached! Congratulations!")
                agent._victory_printed = True

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()