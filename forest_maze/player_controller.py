"""
Player Controller for Forest Maze
Extends the existing Agent class with forest-specific features.
"""

import math
from typing import Tuple, List

class ForestPlayerController:
    """
    Extended player controller for forest maze.
    Handles smooth movement, slow zones, collisions with environment.
    """
    
    def __init__(self, start: Tuple[int, int], goal: Tuple[int, int], 
                 path: List[Tuple[int, int]], speed: float = 2.0, 
                 color: Tuple[float, float, float] = (0.0, 1.0, 1.0)):
        """
        Initialize forest player controller.
        
        Args:
            start: Starting grid position
            goal: Goal grid position
            path: Computed path from start to goal
            speed: Base movement speed
            color: Player color for rendering
        """
        self.start = start
        self.goal = goal
        self.path = path
        self.base_speed = speed
        self.current_speed = speed
        self.color = color
        
        # Position (world coordinates)
        self.position = (float(start[0]), 0.3, float(start[1]))
        
        # Path tracking
        self.path_index = 0
        self.history = []
        self.arrived = False
        
        # Effects
        self.is_in_slow_zone = False
        self.speed_multiplier = 1.0
        self.collision_radius = 0.1  # Reduced from 0.25 to minimize collision issues
    
    def update(self, dt: float, environment_manager=None, slow_zone_manager=None):
        """
        Update player state.
        
        Args:
            dt: Delta time in seconds
            environment_manager: Optional EnvironmentObjectManager for collision
            slow_zone_manager: Optional SlowZoneManager for slow zones
        """
        if self.arrived:
            return
        
        # Update speed multiplier based on slow zones
        if slow_zone_manager:
            self.speed_multiplier = slow_zone_manager.get_speed_multiplier(self.position)
            self.current_speed = self.base_speed * self.speed_multiplier
        else:
            self.current_speed = self.base_speed
            self.speed_multiplier = 1.0
        
        # Move towards next target
        self.move(dt, environment_manager)
        
        # Record history
        self.history.append(self.position)
        if len(self.history) > 200:
            self.history.pop(0)
    
    def move(self, dt: float, environment_manager=None):
        """
        Move player along path (no collision checks - trees are visual only).
        
        Args:
            dt: Delta time in seconds
            environment_manager: Not used (environment objects are decorative)
        """
        if self.reached_goal():
            self.arrived = True
            return
        
        # Get target position
        target_x, target_y = self.next_target()
        
        # Current position
        x, y, z = self.position
        
        # Calculate direction
        dx = target_x - x
        dz = target_y - z
        distance = math.sqrt(dx*dx + dz*dz)
        
        # Reached waypoint
        if distance < 0.1:
            self.position = (target_x, 0.3, target_y)
            self.path_index += 1
            
            if self.reached_goal():
                self.arrived = True
            return
        
        # Calculate movement
        step = self.current_speed * dt
        move_x = (dx / distance) * step
        move_z = (dz / distance) * step
        
        new_position = (x + move_x, 0.3, z + move_z)
        
        # Move freely (no collision checks with trees)
        self.position = new_position
    
    def next_target(self) -> Tuple[int, int]:
        """
        Get the next waypoint on the path.
        
        Returns:
            (x, y) target grid position
        """
        if self.path_index >= len(self.path):
            return self.goal
        
        return self.path[self.path_index]
    
    def reached_goal(self) -> bool:
        """Check if player has reached the goal"""
        return self.path_index >= len(self.path)
    
    def get_position(self) -> Tuple[float, float, float]:
        """Get current world position"""
        return self.position
    
    def set_speed(self, speed: float):
        """Set base movement speed"""
        self.base_speed = max(0.1, speed)
        self.current_speed = self.base_speed * self.speed_multiplier
    
    def get_speed(self) -> float:
        """Get current effective speed"""
        return self.current_speed
    
    def reset(self):
        """Reset player to start position"""
        self.position = (float(self.start[0]), 0.3, float(self.start[1]))
        self.path_index = 0
        self.history = []
        self.arrived = False
