"""
core/Agent.py - Agent Movement System
Handles agent movement, pathfinding, and slippery surfaces
"""

import math
from typing import List, Tuple, Optional


class Agent:
    def __init__(
        self,
        start: Tuple[float, float],
        goal: Tuple[float, float],
        path: List[Tuple[float, float]],
        speed: float,
        color: Tuple[float, float, float] = (1, 1, 1),
        grid: Optional[List[List[int]]] = None,
    ) -> None:
        """
        Initialize agent.
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
            path: List of waypoints from start to goal
            speed: Movement speed
            color: RGB color tuple
            grid: Optional grid for slippery cell detection
        """
        self.start = start
        self.goal = goal
        self.path = path

        self.base_speed = speed
        self.speed = speed

        self.path_i = 0
        # Position stored in grid units (x, y_height, z)
        self.position = (start[0], 0.05, start[1])
        self.color = color
        self.history: List[Tuple[float, float, float]] = []
        self.arrived = False

        # Grid for slippery surface detection
        self.grid = grid
        self.is_slipping = False
        self.SLIP_BOOST = 2.5
        self.CELL_SLIPPERY = 2

    def next_target(self) -> Tuple[float, float]:
        """
        Get next waypoint in world coordinates.
        
        Returns:
            (x, z) coordinates of next target
        """
        if self.path_i < len(self.path):
            tx, ty = self.path[self.path_i]
            # Path stores grid coordinates (0..N-1). Return them directly
            return tx, ty

        # If no more path entries, return goal as grid coordinates
        return self.goal

    def reached_goal(self) -> bool:
        """Check if agent has reached the goal."""
        return self.path_i >= len(self.path)

    def update(self, dt: float) -> None:
        """
        Update agent state.
        
        Args:
            dt: Delta time in seconds
        """
        if self.arrived:
            return

        self.move(dt)

        # Record history in grid units
        self.history.append(self.position)
        if len(self.history) > 200:
            self.history.pop(0)

    def move(self, dt: float) -> None:
        """
        Move agent towards next waypoint.
        
        Args:
            dt: Delta time in seconds
        """
        if self.reached_goal():
            self.arrived = True
            return

        tx, ty = self.next_target()

        x, _, z = self.position
        dx = tx - x
        dz = ty - z

        # Adjust speed based on current cell type (if grid provided)
        cell_type = 0
        if self.grid:
            grid_size = len(self.grid)
            # Position is stored in grid coordinates (0..N-1)
            current_grid_x = int(round(x))
            current_grid_y = int(round(z))
            if 0 <= current_grid_y < grid_size and 0 <= current_grid_x < grid_size:
                cell_type = self.grid[current_grid_y][current_grid_x]
            
            # Apply slippery boost
            if cell_type == self.CELL_SLIPPERY and not self.is_slipping:
                self.is_slipping = True
                self.speed = self.base_speed * self.SLIP_BOOST
            elif cell_type != self.CELL_SLIPPERY and self.is_slipping:
                self.is_slipping = False
                self.speed = self.base_speed

        dist = math.sqrt(dx * dx + dz * dz)

        # Snap to target if very close
        snap_threshold = 0.01

        if dist <= snap_threshold:
            # Snap exactly and advance path index
            self.position = (tx, 0.05, ty)
            
            # Reset slipping if needed
            if self.is_slipping and (not self.grid or cell_type != self.CELL_SLIPPERY):
                self.is_slipping = False
                self.speed = self.base_speed
            
            self.path_i += 1
            if self.reached_goal():
                self.arrived = True
            return

        # Move up to step, but don't overshoot
        step = min(self.speed * dt, dist)
        if dist > 0:
            nx = x + (dx / dist) * step
            nz = z + (dz / dist) * step
            self.position = (nx, 0.05, nz)