"""
Lava Zones Manager
Handles deadly lava pools that damage and slow the player.
"""

import math
import random
from typing import List, Tuple
from OpenGL.GL import *
from OpenGL.GLU import *

class LavaZone:
    """Represents a single lava pool"""
    
    def __init__(self, x: float, y: float, z: float, radius: float = 0.6, 
                 damage_rate: float = 10.0):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.damage_rate = damage_rate
        self.glow_intensity = random.uniform(0.8, 1.0)
        self.animation_offset = random.uniform(0, math.pi * 2)
        self.bubble_timer = 0.0
    
    def get_position(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def contains_point(self, pos: Tuple[float, float, float]) -> bool:
        px, py, pz = pos
        dx = px - self.x
        dz = pz - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        return distance <= self.radius
    
    def update(self, dt: float):
        """Animate the lava"""
        self.bubble_timer += dt
        self.glow_intensity = 0.8 + 0.2 * math.sin(self.bubble_timer * 3.0 + self.animation_offset)


class LavaZoneManager:
    """Manages all lava zones in the maze"""
    
    def __init__(self):
        self.zones: List[LavaZone] = []
    
    def add_zone(self, x: float, y: float, z: float, 
                 radius: float = 0.6, damage_rate: float = 10.0):
        zone = LavaZone(x, y, z, radius, damage_rate)
        self.zones.append(zone)
    
    def create_from_grid_positions(self, grid_positions: List[Tuple[int, int]], 
                                   grid_size: int = 25, cell_size: float = 1.0,
                                   radius: float = 0.5):
        for gx, gy in grid_positions:
            wx = (gx - grid_size // 2) * cell_size
            wz = (gy - grid_size // 2) * cell_size
            self.add_zone(wx, -0.05, wz, radius)
    
    def get_damage_rate(self, position: Tuple[float, float, float]) -> float:
        """Get damage rate for a position"""
        damage = 0.0
        for zone in self.zones:
            if zone.contains_point(position):
                damage += zone.damage_rate
        return damage
    
    def is_in_lava(self, position: Tuple[float, float, float]) -> bool:
        """Check if position is in any lava zone"""
        for zone in self.zones:
            if zone.contains_point(position):
                return True
        return False
    
    def update(self, dt: float):
        """Update all lava zones"""
        for zone in self.zones:
            zone.update(dt)
    
    def render_zones(self):
        """Render all lava zones with animated glow"""
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for zone in self.zones:
            glPushMatrix()
            x, y, z = zone.get_position()
            glTranslatef(x, y, z)
            
            # Glowing lava surface
            glColor4f(1.0, 0.3, 0.0, 0.9 * zone.glow_intensity)
            
            # Draw as filled circle
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0.02, 0)
            segments = 20
            for i in range(segments + 1):
                angle = 2.0 * math.pi * i / segments
                glVertex3f(
                    zone.radius * math.cos(angle),
                    0.02,
                    zone.radius * math.sin(angle)
                )
            glEnd()
            
            # Bright center glow
            glColor4f(1.0, 1.0, 0.0, 0.7 * zone.glow_intensity)
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0.03, 0)
            for i in range(segments + 1):
                angle = 2.0 * math.pi * i / segments
                glVertex3f(
                    zone.radius * 0.3 * math.cos(angle),
                    0.03,
                    zone.radius * 0.3 * math.sin(angle)
                )
            glEnd()
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
