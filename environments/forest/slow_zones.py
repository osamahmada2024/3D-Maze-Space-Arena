"""
Slow Zones Manager
Handles mud/sand areas that reduce player movement speed.
"""

import math
from typing import List, Tuple
from OpenGL.GL import *
from OpenGL.GLU import *

class SlowZone:
    """Represents a single slow zone (mud or sand area)"""
    
    def __init__(self, x: float, y: float, z: float, radius: float = 0.5, 
                 slow_factor: float = 0.5):
        """
        Initialize a slow zone.
        
        Args:
            x, y, z: Center position
            radius: Radius of the slow zone
            slow_factor: Speed multiplier (0.5 = 50% speed)
        """
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.slow_factor = max(0.0, min(1.0, slow_factor))
        self.color = (0.8, 0.6, 0.4)  # Brown/sand color
    
    def get_position(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def contains_point(self, pos: Tuple[float, float, float]) -> bool:
        """
        Check if a position is within this slow zone.
        
        Args:
            pos: (x, y, z) position to check
        
        Returns:
            True if position is inside slow zone
        """
        px, py, pz = pos
        dx = px - self.x
        dz = pz - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        return distance <= self.radius


class SlowZoneManager:
    """Manages all slow zones in the forest"""
    
    def __init__(self):
        """Initialize slow zone manager"""
        self.zones: List[SlowZone] = []
    
    def add_zone(self, x: float, y: float, z: float, 
                 radius: float = 0.5, slow_factor: float = 0.5):
        """
        Add a slow zone to the manager.
        
        Args:
            x, y, z: Center position
            radius: Radius of the zone
            slow_factor: Speed reduction factor
        """
        zone = SlowZone(x, y, z, radius, slow_factor)
        self.zones.append(zone)
    
    def create_from_grid_positions(self, grid_positions: List[Tuple[int, int]], 
                                   grid_size: int = 25, cell_size: float = 1.0,
                                   radius: float = 0.3, slow_factor: float = 0.5):
        """
        Create slow zones from grid positions (from maze generator).
        
        Args:
            grid_positions: List of (grid_x, grid_y) positions
            grid_size: Size of the grid
            cell_size: Size of each cell
            radius: Radius of each zone
            slow_factor: Speed reduction factor
        """
        for gx, gy in grid_positions:
            # Convert grid coordinates to world coordinates
            wx = (gx - grid_size // 2) * cell_size
            wz = (gy - grid_size // 2) * cell_size
            
            self.add_zone(wx, 0, wz, radius, slow_factor)
    
    def get_speed_multiplier(self, position: Tuple[float, float, float]) -> float:
        """
        Get speed multiplier for a position.
        If in multiple zones, returns the most restrictive multiplier.
        
        Args:
            position: (x, y, z) position to check
        
        Returns:
            Speed multiplier (0.0 to 1.0)
        """
        multiplier = 1.0
        
        for zone in self.zones:
            if zone.contains_point(position):
                # Apply the most restrictive factor
                multiplier = min(multiplier, zone.slow_factor)
        
        return multiplier
    
    def get_active_zones(self, position: Tuple[float, float, float]) -> List[SlowZone]:
        """
        Get all active slow zones at a position.
        
        Args:
            position: (x, y, z) position to check
        
        Returns:
            List of slow zones containing the position
        """
        active = []
        
        for zone in self.zones:
            if zone.contains_point(position):
                active.append(zone)
        
        return active
    
    def render_zones(self):
        """Render all slow zones for debugging"""
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for zone in self.zones:
            glPushMatrix()
            x, y, z = zone.get_position()
            glTranslatef(x, y, z)
            
            # Draw zone as semi-transparent cylinder
            glColor4f(zone.color[0], zone.color[1], zone.color[2], 0.3)
            
            quad = gluNewQuadric()
            gluQuadricNormals(quad, GLU_SMOOTH)
            gluCylinder(quad, zone.radius, zone.radius, 0.1, 16, 4)
            gluDeleteQuadric(quad)
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
