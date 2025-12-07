"""
Fog System
Implements atmospheric fog effect for forest using depth-based blending.
"""

import math
from typing import Tuple
from OpenGL.GL import *

class FogSystem:
    """
    Manages fog effect for the forest scene.
    Uses OpenGL fog or custom depth-based rendering.
    """
    
    def __init__(self, fog_color: Tuple[float, float, float] = (0.2, 0.5, 0.3),
                 fog_density: float = 0.15, fog_start: float = 5.0, fog_end: float = 50.0):
        """
        Initialize fog system.
        
        Args:
            fog_color: RGB color of fog (greenish default)
            fog_density: Density of fog (0.0 to 1.0)
            fog_start: Near distance for fog
            fog_end: Far distance for fog
        """
        self.fog_color = fog_color
        self.fog_density = fog_density
        self.fog_start = fog_start
        self.fog_end = fog_end
        self.enabled = True
    
    def enable(self):
        """Enable fog in OpenGL"""
        if not self.enabled:
            return
        
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_DENSITY, self.fog_density)
        glFogf(GL_FOG_START, self.fog_start)
        glFogf(GL_FOG_END, self.fog_end)
        glFogfv(GL_FOG_COLOR, (*self.fog_color, 1.0))
    
    def disable(self):
        """Disable fog in OpenGL"""
        glDisable(GL_FOG)
    
    def set_density(self, density: float):
        """
        Change fog density dynamically.
        
        Args:
            density: New fog density (0.0 to 1.0)
        """
        self.fog_density = max(0.0, min(1.0, density))
        glFogf(GL_FOG_DENSITY, self.fog_density)
    
    def set_color(self, color: Tuple[float, float, float]):
        """
        Change fog color.
        
        Args:
            color: RGB color tuple
        """
        self.fog_color = color
        glFogfv(GL_FOG_COLOR, (*color, 1.0))
    
    def set_range(self, fog_start: float, fog_end: float):
        """
        Set fog near/far range.
        
        Args:
            fog_start: Near distance
            fog_end: Far distance
        """
        self.fog_start = fog_start
        self.fog_end = fog_end
        glFogf(GL_FOG_START, fog_start)
        glFogf(GL_FOG_END, fog_end)
    
    def update_time_of_day(self, time_factor: float):
        """
        Update fog based on time of day (0.0 to 1.0 cycle).
        Creates dynamic fog changes throughout a "day".
        
        Args:
            time_factor: Time factor from 0.0 to 1.0
        """
        # Fog is denser at night/early morning
        density = self.fog_density * (0.5 + 0.5 * math.sin(time_factor * math.pi * 2))
        self.set_density(density)
        
        # Fog color shifts from greenish (day) to blue-grey (night)
        day_color = (0.2, 0.5, 0.3)    # Green fog (day)
        night_color = (0.3, 0.3, 0.4)  # Blue-grey fog (night)
        
        # Interpolate between day and night colors
        ratio = (math.sin(time_factor * math.pi * 2) + 1) / 2
        color = tuple(
            day_color[i] * ratio + night_color[i] * (1 - ratio)
            for i in range(3)
        )
        self.set_color(color)
    
    def render_fog_quad(self, camera_distance: float = 50.0, fog_alpha: float = 0.3):
        """
        Render fog as a large quad surrounding the camera for additional visual effect.
        (Optional: for enhanced fog appearance)
        
        Args:
            camera_distance: Distance of fog quad from camera
            fog_alpha: Alpha transparency of fog
        """
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor4f(*self.fog_color, fog_alpha)
        
        glBegin(GL_QUADS)
        # Draw a large cube around the scene
        size = camera_distance
        # Front face
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(-size, size, -size)
        glEnd()
        
        glEnable(GL_LIGHTING)
