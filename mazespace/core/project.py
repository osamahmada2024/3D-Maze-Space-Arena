from mazespace.config.definitions import GlobalConfig
from mazespace.config.loader import load_defaults
from mazespace.ui.MenuManager import MenuManager
from mazespace.api import Renderer # Reuse existing Renderer logic for now
# Ideally we move Renderer to mazespace.core or similar

class Project:
    def __init__(self, config: GlobalConfig = None, headless: bool = False):
        self.config = config if config else load_defaults()
        self.headless = headless

    def run(self):
        if self.headless:
            print("Running in headless mode. Config loaded.")
            print(f"Theme: {self.config.app.default_theme}")
            return

        # 1. Run Menu to finalize config
        menu = MenuManager(self.config)
        final_config = menu.run()
        
        # 2. Run Game Renderer
        # Find selected theme/agent definitions
        theme_cfg = next((t for t in final_config.themes if t.key == final_config.app.default_theme), final_config.themes[0])
        agent_cfg = next((a for a in final_config.agents if a.key == final_config.app.default_agent), final_config.agents[0])
        
        print(f"Starting Game with Theme: {theme_cfg.name}, Agent: {agent_cfg.name}")
        
        # Initialize Renderer with Config Values
        r = Renderer(
            width=final_config.app.width,
            height=final_config.app.height,
            bg_color=theme_cfg.background_color
        )
        
        # Add Agent
        r.draw(
            shape=agent_cfg.shape, 
            position=(0, 0, 0), 
            color=agent_cfg.color
        )
        
        # Add Environment Props (Based on theme density/damage?)
        # For demo, just static
        if theme_cfg.key == "LAVA":
             r.draw("cube", (5, 0, 5), (1, 0, 0)) # Hazards
             
        r.show()
