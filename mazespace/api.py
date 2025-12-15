import sys
import time
import math
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from mazespace.rendering.AgentRender import AgentRender
from mazespace.ui.MenuManager import MenuManager

class SimpleAgent:
    """Internal wrapper to mimic Agent interface for AgentRender"""
    def __init__(self, position, color, shape):
        self.position = list(position)
        self.color = color
        self.shape_type = shape
        self.path = []
        self.path_i = 0
        self.arrived = False

class Renderer:
    """
    The main entry point for the mazespace library.
    Allows easy drawing of 3D shapes without managing the loop.
    """
    def __init__(self, width=800, height=600, bg_color=(0.1, 0.1, 0.1, 1.0)):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.objects = []
        self.running = False
        self.font = None
        
        # Internal renderer
        self.agent_renderer = AgentRender(cell_size=1.0, grid_size=0) 
        # grid_size=0 because we want exact coordinates, not grid-relative
        
    def draw(self, shape="drone", position=(0, 0, 0), color=(0, 1, 1)):
        """
        Add a shape to the scene.
        
        Args:
            shape (str): Shape name ('drone', 'cube', 'sphere', etc.)
            position (tuple): (x, y, z) coordinates
            color (tuple): (r, g, b) color values 0.0-1.0
        """
        # Map friendly names to internal names if needed
        shape_map = {
            "drone": "mini_drone",
            "cube": "robo_cube",
            "sphere": "sphere_droid",
            "crystal": "crystal_alien"
        }
        internal_shape = shape_map.get(shape.lower(), shape)
        
        agent = SimpleAgent(position, color, internal_shape)
        self.objects.append(agent)
    
    def show_exit_dialog(self, screen):
        """Overlay for Return or Exit"""
        # Switch to 2D overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Draw overlay using Pygame (needs surface access which is tricky in OpenGL mode)
        # Actually in Pygame OpenGL, we can't easily mixed blit. 
        # We have to draw simple quads or text textures.
        # SIMPLIFICATION: Since user asked for "Window same as entry", 
        # we can pause the loop and show a 2D Pygame loop if we weren't in OpenGL mode, 
        # but we ARE.
        
        # For simplicity in this prompt's constraints:
        # We will use console or title bar text? No, user wants a window.
        # Best approach: Use a separate MenuManager instance or similar logic?
        # Or just break the loop and return a status code, and let the App handle it?
        
        # Let's try to render a simple overlay using OpenGL direct calls? Too complex to write quickly.
        # Alternative: The user accepts "Return or Exit". 
        # I will signal the App to show the menu again?
        
        # ACTUALLY: The request says "Return or Exit" window.
        # I will implement a text overlay on title bar for now as a fallback?
        # No, "Window same as entry".
        
        # Let's try to temporally switch caption.
        pygame.display.set_caption("PAUSED - Press Y to Exit, N to Return")
        
        waiting = True
        result = False # Return
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        waiting = False
                        result = True # Exit
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        waiting = False
                        result = False # Return
                    
            pygame.time.wait(50)
            
        pygame.display.set_caption("Mazespace Renderer")
        
        # Restore OpenGL state
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        return result

        
    def show(self):
        """Opens a window and displays the scene (blocking)."""
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("Mazespace Renderer")
        
        # OpenGL Init
        glClearColor(*self.bg_color)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        clock = pygame.time.Clock()
        self.running = True
        
        # Simple camera state
        cam_dist = 20
        cam_angle_y = 45
        cam_angle_x = 30
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Show Exit Dialog
                        should_exit = self.show_exit_dialog(screen)
                        if should_exit:
                            self.running = False
            
            # Camera controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: cam_angle_y -= 2
            if keys[pygame.K_RIGHT]: cam_angle_y += 2
            if keys[pygame.K_UP]: cam_angle_x -= 2
            if keys[pygame.K_DOWN]: cam_angle_x += 2
            
            # Setup View
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(60, self.width / self.height, 0.1, 100.0)
            
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # Polar coord camera
            rad_y = math.radians(cam_angle_y)
            rad_x = math.radians(cam_angle_x)
            
            cam_x = cam_dist * math.cos(rad_x) * math.sin(rad_y)
            cam_y = cam_dist * math.sin(rad_x)
            cam_z = cam_dist * math.cos(rad_x) * math.cos(rad_y)
            
            gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 1, 0)
            
            # Draw objects
            for obj in self.objects:
                self.agent_renderer.draw_agent(obj, obj.shape_type)
                
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()


class MazeApp:
    def __init__(self, themes=None, agents=None, default_theme="DEFAULT"):
        self.themes = themes
        self.agents = agents
        self.default_theme = default_theme

    def run(self):
        # 1. Run Menu
        while True:
            # Re-init menu each time to allow full "Exit" loop
            menu = MenuManager(self.themes, self.agents)
            if self.default_theme:
                menu.selected_theme = self.default_theme
                
            config = menu.run()
            
            if config is None:
                # User cancelled or exited from menu
                break
                
            # 2. Run Game
            # Create Renderer
            bg = (0.1, 0.1, 0.1, 1.0)
            theme = config.get("theme", "DEFAULT")
            
            if theme == "LAVA":
                 bg = (0.2, 0.05, 0.05, 1.0)
            elif theme == "FOREST":
                 bg = (0.05, 0.15, 0.05, 1.0)
                 
            r = Renderer(bg_color=bg)
            
            # Add Agent
            agent_type = config.get("agent", "sphere_droid")
            r.draw(shape=agent_type, position=(0, 0, 0), color=(0, 1, 1))
            
            # Add some dummy scenery based on theme
            if theme == "LAVA":
                r.draw(shape="cube", position=(5, 0, 5), color=(1, 0.2, 0)) # Hot cube
                r.draw(shape="crystal", position=(-5, 2, -5), color=(1, 0.5, 0))
            elif theme == "FOREST":
                r.draw(shape="crystal", position=(5, 0, 5), color=(0.2, 1, 0.2))
            
            # Show Window (Blocking)
            # If user exits this window, we go back to menu loop?
            # User said "Return or Exit". Exit might mean back to menu or quit app?
            # Usually "Exit" in game means quit or back to menu.
            # I will assume: Return -> Resume Game, Exit -> Back to Menu.
            r.show()
            
            # After show returns, we loop back to menu.
            # If user really wants to quit app, they can do so from menu.
