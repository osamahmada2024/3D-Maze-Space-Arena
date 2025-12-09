import sys
import time
import pygame
from OpenGL.GL import *
from ui.MenuManager import MenuManager
from forest.forest_scene import ForestScene

# Screen configuration
WIDTH, HEIGHT = 1200, 800

def main():
    # Show menu to select Agent and Algo (but Theme is Forest implicitly)
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
    if selected_theme == "FOREST":
        print("Initializing Forest Environment...")
        current_scene = ForestScene(WIDTH, HEIGHT)
        current_scene.initialize(agent_shape=selected_shape, algo_name=selected_algo)
    else:
        print("Initializing Standard Space Environment...")
        from rendering.SpaceScene import SpaceScene
        current_scene = SpaceScene(selected_shape, selected_algo, WIDTH, HEIGHT)
        current_scene.initialize()

    running = True
    last_time = time.time()

    print("Forest Maze initialized successfully!")

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