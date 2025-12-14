# app.py
import sys
import os

# Add the parent directory to sys.path to allow importing mazespace
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pygame
from OpenGL.GL import *
from mazespace.ui.MenuManager import MenuManager
from mazespace.forest.forest_scene import ForestScene

# Screen configuration
WIDTH, HEIGHT = 1200, 800

def main():
    menu = MenuManager()
    menu.run()

    selected_shape = menu.selected_agent
    selected_algo = menu.selected_algo
    selected_theme = menu.selected_theme

    if not selected_shape or not selected_algo or not selected_theme:
        print("No selection made. Exiting...")
        return

    print(f"Selected Agent Shape: {selected_shape}")
    print(f"Selected Algorithm: {selected_algo}")
    print(f"Selected Theme: {selected_theme}")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption(f"3D Maze - {selected_theme} Edition")
    clock = pygame.time.Clock()

    current_scene = None
    
    # ✅ إضافة دعم LAVA theme
    if selected_theme == "FOREST":
        print("Initializing Forest Environment...")
        current_scene = ForestScene(WIDTH, HEIGHT)
        current_scene.initialize(agent_shape=selected_shape, algo_name=selected_algo)
        
    elif selected_theme == "LAVA":
        print("Initializing Lava Environment... 🌋")
        from mazespace.Lava.LavaMazeScene import LavaMazeScene
        current_scene = LavaMazeScene(WIDTH, HEIGHT)
        current_scene.initialize(agent_shape=selected_shape, algo_name=selected_algo)
        
    else:  # DEFAULT (Space)
        print("Initializing Standard Space Environment...")
        from mazespace.rendering.SpaceScene import SpaceScene
        current_scene = SpaceScene(selected_shape, selected_algo, WIDTH, HEIGHT)
        current_scene.initialize()

    running = True
    last_time = time.time()

    print("Maze initialized successfully!")

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
                if hasattr(current_scene, 'camera'):
                     current_scene.camera.distance -= event.y * 2
                     current_scene.camera.distance = max(3, min(60, current_scene.camera.distance))

        current_scene.update(dt)
        current_scene.render()

        pygame.display.flip()
        clock.tick(60)

    current_scene.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":

    main()
