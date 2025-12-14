import sys
import time
import math
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from mazespace.rendering.AgentRender import AgentRender

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
        
    def render(self):
        """Render a single frame. Must be called after init_window if managing loop manually."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Simple camera setup
        gluLookAt(10, 10, 10,  0, 0, 0,  0, 1, 0)
        
        # Draw all objects
        for obj in self.objects:
            self.agent_renderer.draw_agent(obj, obj.shape_type)
            
        pygame.display.flip()
        
    def show(self):
        """Opens a window and displays the scene (blocking)."""
        pygame.init()
        pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
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
        
        print("Controls: Arrow keys to rotate camera, Scroll to zoom.")
        
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
