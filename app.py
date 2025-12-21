# app.py
import sys
import time
import pygame
from OpenGL.GL import *
from ui.menu_manager import MenuManager
from environments.forest.forest_scene import ForestScene

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

def find_clear_goal_position(grid, preferred_pos, search_radius=3):
    """
    Find a clear position near the preferred goal position.
    Searches in expanding squares around the preferred position.
    
    Args:
        grid: 2D grid where 0 = free, 1 = obstacle
        preferred_pos: (x, y) tuple of desired goal position
        search_radius: Maximum radius to search
        
    Returns:
        (x, y) tuple of a clear position, or preferred_pos if already clear
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    px, py = preferred_pos
    
    # Validate preferred position is within bounds
    if not (0 <= px < cols and 0 <= py < rows):
        print(f"Warning: Preferred goal position {preferred_pos} is out of bounds, using (0,0)")
        return (0, 0)
    
    # Check if preferred position is already clear
    if grid[py][px] == 0:
        return preferred_pos
    
    # Search in expanding squares around preferred position
    for radius in range(1, search_radius + 1):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                # Only check perimeter of current radius
                if abs(dx) == radius or abs(dy) == radius:
                    nx, ny = px + dx, py + dy
                    if (0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0):
                        return (nx, ny)
    
    # If no clear position found, return preferred (algorithms should handle unreachable goals)
    print(f"Warning: No clear goal position found near {preferred_pos}, using as-is")
    return preferred_pos

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
        from ui.sim_config_panel import SimConfigPanel
        config_panel = SimConfigPanel()
        config_data = config_panel.run()
        
        # 🔥 Cleanup after 2D panels
        pygame.display.quit()
        
        # Handle back navigation
        if config_data is None:
            # User clicked "Back" - return to theme selection
            continue
        
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
            from environments.lava.lava_maze_scene import LavaMazeScene
            current_scene = LavaMazeScene(WIDTH, HEIGHT)
        else:  # DEFAULT (Space)
            from rendering.space_scene import SpaceScene
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
        
        # Ensure start position is clear (should be protected by grid generator, but double-check)
        if current_scene.grid[start_pos[1]][start_pos[0]] != 0:
            print(f"Warning: Start position {start_pos} is blocked, clearing it")
            current_scene.grid[start_pos[1]][start_pos[0]] = 0
        
        # Determine Goal Logic
        dist_setting = config_data.get("target_dist", "Far")
        grid_sz = current_scene.grid_size
        
        if dist_setting == "Near":
             # 25% across
             preferred_goal = (grid_sz // 4, grid_sz // 4)
        elif dist_setting == "Medium":
             # 50% across (approx)
             preferred_goal = (grid_sz // 2, grid_sz // 2)
        else: # Far
             preferred_goal = (grid_sz - 1, grid_sz - 1)

        # Find a clear goal position near the preferred location
        goal_pos = find_clear_goal_position(current_scene.grid, preferred_goal)
        
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
            from ui.results_dashboard import ResultsDashboard
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