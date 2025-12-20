# Lava/heat_haze_fog.py
"""
Heat Haze/Fog System
Creates a hellish red-orange fog for the lava maze.
"""

from OpenGL.GL import *


class HeatHazeFog:
    """نظام الضباب الحراري للمتاهة البركانية"""
    
    def __init__(self):
        self.fog_color = (0.3, 0.1, 0.05)
        self.fog_density = 0.025
        self.enabled = True
        self._initialized = False
    
    def enable(self):
        """تفعيل الضباب"""
        if not self.enabled:
            return
        
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_EXP2)
        glFogf(GL_FOG_DENSITY, self.fog_density)
        glFogfv(GL_FOG_COLOR, [*self.fog_color, 1.0])
        self._initialized = True
    
    def disable(self):
        """إيقاف الضباب"""
        glDisable(GL_FOG)
        self._initialized = False
    
    def update_intensity(self, intensity: float):
        """تحديث شدة الضباب للتأثير النابض"""
        if not self._initialized:
            return
            
        base_color = (0.3, 0.1, 0.05)
        self.fog_color = tuple(c * intensity for c in base_color)
        glFogfv(GL_FOG_COLOR, [*self.fog_color, 1.0])
    
    def set_density(self, density: float):
        """تعيين كثافة الضباب"""
        self.fog_density = max(0.0, min(1.0, density))
        if self._initialized:
            glFogf(GL_FOG_DENSITY, self.fog_density)