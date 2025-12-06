"""
Firefly Particle System
Generates flickering lights in the forest using OpenGL point sprites and billboards.
"""

import random
import math
import time
from typing import List, Tuple
from OpenGL.GL import *
from OpenGL.GLU import *

class Firefly:
    """Single firefly particle with position, brightness, and flicker"""
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.brightness = random.uniform(0.3, 1.0)
        self.flicker_speed = random.uniform(2.0, 6.0)
        self.flicker_offset = random.uniform(0, math.pi * 2)
        self.lifetime = random.uniform(5.0, 20.0)
        self.age = 0.0
        self.color = (1.0, 0.95, 0.5)  # Warm yellow
        self.radius = 0.08
    
    def update(self, dt: float):
        """Update firefly state"""
        self.age += dt
        
        # Calculate flicker using sine wave
        flicker = (math.sin(self.age * self.flicker_speed + self.flicker_offset) + 1.0) / 2.0
        self.brightness = flicker * 0.8 + 0.2  # Range from 0.2 to 1.0
    
    def is_alive(self) -> bool:
        """Check if firefly is still alive"""
        return self.age < self.lifetime
    
    def get_position(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


class FireflyParticleSystem:
    """Manages a swarm of fireflies with physics and rendering"""
    
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0, 
                 num_fireflies: int = 50, height_range: Tuple[float, float] = (1.0, 3.0)):
        """
        Initialize firefly particle system.
        
        Args:
            grid_size: Size of the grid
            cell_size: Size of each cell
            num_fireflies: Number of fireflies to spawn
            height_range: (min_height, max_height) for firefly spawning
        """
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.num_fireflies = num_fireflies
        self.height_min, self.height_max = height_range
        self.fireflies: List[Firefly] = []
        self.spawn_timer = 0.0
        self.spawn_delay = 0.1  # Spawn new fireflies every 0.1 seconds
        
        # Initial spawn
        self._spawn_fireflies(num_fireflies)
    
    def _spawn_fireflies(self, count: int):
        """Spawn new fireflies at random positions"""
        half_grid = self.grid_size / 2 * self.cell_size
        
        for _ in range(count):
            x = random.uniform(-half_grid, half_grid)
            z = random.uniform(-half_grid, half_grid)
            y = random.uniform(self.height_min, self.height_max)
            
            firefly = Firefly(x, y, z)
            self.fireflies.append(firefly)
    
    def update(self, dt: float):
        """
        Update all fireflies and remove dead ones.
        Respawn fireflies as needed to maintain count.
        """
        # Update existing fireflies
        alive_fireflies = []
        for firefly in self.fireflies:
            firefly.update(dt)
            if firefly.is_alive():
                alive_fireflies.append(firefly)
        
        self.fireflies = alive_fireflies
        
        # Spawn new fireflies if needed
        self.spawn_timer += dt
        if self.spawn_timer > self.spawn_delay:
            deficit = self.num_fireflies - len(self.fireflies)
            if deficit > 0:
                self._spawn_fireflies(deficit)
            self.spawn_timer = 0.0
    
    def render(self):
        """
        Render fireflies using textured quads (billboards).
        Creates a glow effect around each firefly.
        """
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Inner bright core
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for firefly in self.fireflies:
            r, g, b = firefly.color
            glColor4f(r, g, b, firefly.brightness)
            x, y, z = firefly.get_position()
            glVertex3f(x, y, z)
        glEnd()
        
        # Outer glow sphere
        for firefly in self.fireflies:
            glPushMatrix()
            x, y, z = firefly.get_position()
            glTranslatef(x, y, z)
            
            r, g, b = firefly.color
            glColor4f(r, g, b, firefly.brightness * 0.4)
            
            quad = gluNewQuadric()
            gluQuadricNormals(quad, GLU_SMOOTH)
            gluSphere(quad, firefly.radius, 8, 8)
            gluDeleteQuadric(quad)
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
    
    def get_light_positions(self) -> List[Tuple[float, float, float]]:
        """
        Get positions of all fireflies for light simulation.
        Useful for dynamic lighting calculations.
        """
        return [firefly.get_position() for firefly in self.fireflies]
    
    def get_light_colors(self) -> List[Tuple[float, float, float]]:
        """
        Get brightness-adjusted colors for each firefly.
        """
        colors = []
        for firefly in self.fireflies:
            r, g, b = firefly.color
            brightness = firefly.brightness
            colors.append((r * brightness, g * brightness, b * brightness))
        return colors
