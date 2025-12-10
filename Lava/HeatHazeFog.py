"""
Heat Haze/Fog System
Creates a hellish red-orange fog for the lava maze.
"""

class HeatHazeFog:
    def __init__(self):
        self.fog_color = (0.3, 0.1, 0.05)
        self.fog_density = 0.25
        self.enabled = True
    
    def enable(self):
        if not self.enabled:
            return
        
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_EXP2)
        glFogf(GL_FOG_DENSITY, self.fog_density)
        glFogfv(GL_FOG_COLOR, (*self.fog_color, 1.0))
    
    def update_intensity(self, intensity: float):
        """Pulse the fog for breathing effect"""
        base_color = (0.3, 0.1, 0.05)
        self.fog_color = tuple(c * intensity for c in base_color)
        glFogfv(GL_FOG_COLOR, (*self.fog_color, 1.0))
