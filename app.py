# app.py
import sys
import time
import pygame
from OpenGL.GL import *
from ui.MenuManager import MenuManager
from forest.forest_scene import ForestScene

# Screen configuration
WIDTH, HEIGHT = 1024, 720

# Helper for robust GL setup
def create_opengl_display(w, h, title):
    """Attempts to create OpenGL display with fallback configs"""
    configs = [
        {"multisample": True, "samples": 4, "depth": 24}, # High End
        {"multisample": True, "samples": 2, "depth": 16}, # Mid Range
        {"multisample": False, "samples": 0, "depth": 16}, # Low End
        {"multisample": False, "samples": 0, "depth": 0},  # Potato / Safe (Let driver decide)
    ]
    
    for i, conf in enumerate(configs):
        try:
            # Full tear-down to clear any stuck states
            if pygame.get_init():
                pygame.quit()
            
            pygame.init()
            
            # Set attributes
            if conf["multisample"]:
                pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
                pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, conf["samples"])
            else:
                pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0)
                
            if conf["depth"] > 0:
                pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, conf["depth"])
            
            # Common stable attributes
            pygame.display.gl_set_attribute(pygame.GL_RED_SIZE, 8)
            pygame.display.gl_set_attribute(pygame.GL_GREEN_SIZE, 8)
            pygame.display.gl_set_attribute(pygame.GL_BLUE_SIZE, 8)
            pygame.display.gl_set_attribute(pygame.GL_ALPHA_SIZE, 8)
            pygame.display.gl_set_attribute(pygame.GL_BUFFER_SIZE, 32)
            
            screen = pygame.display.set_mode((w, h), pygame.DOUBLEBUF | pygame.OPENGL)
            pygame.display.set_caption(title)
            print(f"GL Context created with config: {conf}")
            return screen, pygame.time.Clock()
            
        except pygame.error as e:
            print(f"Config {i} failed: {e}")
            continue
            
    print("CRITICAL: Failed to create ANY OpenGL context.")
    sys.exit(1)

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
        
        # 🔥 Cleanup after 2D panels
        pygame.display.quit()
        
        if not config_data:
            print("Configuration cancelled. Exiting...")
            break
            
        print(f"Config: {config_data}")
        
        # Short pause
        time.sleep(0.5)

        # 3. Initialize Game (Robust)
        screen, clock = create_opengl_display(WIDTH, HEIGHT, f"3D Maze - {selected_theme} Edition")

        current_scene = None
        
        if selected_theme == "FOREST":
            current_scene = ForestScene(WIDTH, HEIGHT)
        elif selected_theme == "LAVA":
            from Lava.LavaMazeScene import LavaMazeScene
            current_scene = LavaMazeScene(WIDTH, HEIGHT)
        else:  # DEFAULT (Space)
            from rendering.SpaceScene import SpaceScene
            current_scene = SpaceScene("sphere_droid", "astar", WIDTH, HEIGHT)

        # Initialize Scene with Config
        if not config_data["agents"]:
            print("No active agents configured!")
            continue

        # Use first agent's config as default for the scene init logic
        first_agent_conf = config_data["agents"][0]
        current_scene.agent_shape = first_agent_conf["shape"]
        current_scene.algo_name = first_agent_conf["algo_name"]

        # 🟢 Inject Entropy Logic
        from config import settings
        settings.GRID_SETTINGS["obstacle_prob_space"] = config_data["entropy"]
        settings.GRID_SETTINGS["obstacle_prob_forest"] = config_data["entropy"]
        settings.GRID_SETTINGS["obstacle_prob_lava"] = config_data["entropy"]

        # Run initialize
        current_scene.initialize()
        
        # 🟡 CRITICAL FIX: Clear agents to prevent duplication and ensure config adherence
        current_scene.agents = [] 
        current_scene.agent = None
        
        # Re-create all agents from config
        start_pos = (0, 0)
        
        # Determine Goal Logic
        dist_setting = config_data.get("target_dist", "Far")
        grid_sz = current_scene.grid_size
        
        if dist_setting == "Near":
             # 25% across
             goal_pos = (grid_sz // 4, grid_sz // 4)
        elif dist_setting == "Medium":
             # 50% across (approx)
             goal_pos = (grid_sz // 2, grid_sz // 2)
        else: # Far
             goal_pos = (grid_sz - 1, grid_sz - 1)

        # Sanity check goal position
        current_scene.grid[goal_pos[1]][goal_pos[0]] = 0 # Ensure clear
        
        for i, conf in enumerate(config_data["agents"]):
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
                
                # Pass events to scene (e.g., zoom)
                if current_scene:
                    current_scene.handle_event(event)
            
            # Scene Update
            current_scene.update(dt)
            current_scene.render()
            pygame.display.flip()
            clock.tick(60)
            
            # Check completion
            if hasattr(current_scene, 'is_finished') and current_scene.is_finished:
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
            pygame.display.quit()
            
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