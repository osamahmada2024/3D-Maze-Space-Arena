# app.py
import sys
import time
import pygame
from OpenGL.GL import *
from ui.MenuManager import MenuManager
from forest.forest_scene import ForestScene

# Screen configuration
WIDTH, HEIGHT = 1200, 800

def main():
    while True: # Restart loop
        # 1. Main Menu (Theme Selection)
        menu = MenuManager()
        menu.run()
        
        selected_theme = menu.selected_theme
        if not selected_theme:
            print("No selection made. Exiting...")
            break
            
        print(f"Selected Theme: {selected_theme}")
        
        # 2. Advanced Configuration
        from ui.SimConfigPanel import SimConfigPanel
        config_panel = SimConfigPanel()
        config_data = config_panel.run()
        
        # 🔥 Ensure cleanup after 2D panels
        pygame.quit()
        
        if not config_data:
            print("Configuration cancelled. Exiting...")
            break
            
        print(f"Config: {config_data}")

        # 3. Initialize Game
        pygame.init() # Re-init for OpenGL
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption(f"3D Maze - {selected_theme} Edition")
        clock = pygame.time.Clock()

        current_scene = None
        
        if selected_theme == "FOREST":
            current_scene = ForestScene(WIDTH, HEIGHT)
        elif selected_theme == "LAVA":
            from Lava.LavaMazeScene import LavaMazeScene
            current_scene = LavaMazeScene(WIDTH, HEIGHT)
        else:  # DEFAULT (Space)
            from rendering.SpaceScene import SpaceScene
            # SpaceScene init requires shape/algo but we will override with add_agent loops
            # We pass defaults to satisfy constructor
            current_scene = SpaceScene("sphere_droid", "astar", WIDTH, HEIGHT)

        # Initialize Scene with Config
        # First, standard init (might create default agent, we can clear it or ignore it)
        # Actually initialize returns the agent.
        # We need a clean way to inject our agents.
        
        # Call initialize, passing the first agent's config as 'default' if needed, 
        # or rely on add_agent iteration.
        # But initialize calls _create_agent.
        # Let's call initialize with first agent params (legacy compat)
        first_agent_conf = config_data["agents"][0]
        
        # Monkey patch or modify args
        # But initialize takes (agent_shape, algo_name)
        # We can just call it.
        # SpaceScene.initialize() no args? 
        # SpaceScene.initialize() takes no args but uses self.agent_shape
        
        # Let's update the scene properties before init
        current_scene.agent_shape = first_agent_conf["shape"]
        current_scene.algo_name = first_agent_conf["algo_name"]

        # Run initialize
        current_scene.initialize()
        
        # NOW, clear if we want, or use the one created.
        # The one created used the properties of agent[0].
        # We need to create the rest.
        
        # agent[0] is already created (as self.agent and self.agents[0]).
        # Let's create the others.
        
        # Note: SpaceScene.initialize calls _create_agent -> add_agent.
        # So agent[0] is in self.agents[0].
        
        start_pos = current_scene.agents[0].start
        goal_pos = current_scene.agents[0].goal
        
        for i in range(1, len(config_data["agents"])):
            conf = config_data["agents"][i]
            current_scene.add_agent(start_pos, goal_pos, agent_config={
                "algo_name": conf["algo_name"],
                "shape": conf["shape"],
                "color": None # Will auto-pick based on shape
            })
            
        # 4. Game Loop
        running = True
        simulation_complete = False
        last_time = time.time()

        while running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit() # Hard exit
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Scene Update
            current_scene.update(dt)
            current_scene.render()
            pygame.display.flip()
            clock.tick(60)
            
            # Check completion
            if hasattr(current_scene, 'is_finished') and current_scene.is_finished:
                # Wait a bit or prompt?
                # Just exit game loop to show results
                # Give it a second or just break?
                # Let's break after 2 seconds?
                # For now break immediate to show Dashboard
                simulation_complete = True
                running = False
                
        # Cleanup
        current_scene.cleanup()
        
        if simulation_complete:
            # 5. Results Dashboard
            from ui.ResultsDashboard import ResultsDashboard
            # Need to pass agents from the scene
            dashboard = ResultsDashboard(current_scene.agents)
            res = dashboard.run()
            
            # 🔥 Cleanup after dashboard
            pygame.quit()
            
            if res == "QUIT":
                break
            elif res == "EXIT":
                break
            elif res == "RESTART":
                continue
        else:
            break
            
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()