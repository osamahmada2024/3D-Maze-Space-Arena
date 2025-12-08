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
        self.start = start
        self.goal = goal
        self.path = path

        self.base_speed = speed
        self.speed = speed

        self.path_i = 0
        # position stored in grid units (x, yheight, z)
        self.position = (start[0], 0.05, start[1])
        self.color = color
        self.history: List[Tuple[float, float, float]] = []
        self.arrived = False

        self.grid = grid
        self.is_slipping = False
        self.SLIP_BOOST = 2.5
        self.CELL_SLIPPERY = 2

    def next_target(self) -> Tuple[float, float]:
        # convert path grid coordinates to world coordinates (centered)
        if self.path_i < len(self.path):
            tx, ty = self.path[self.path_i]
            GRID_SIZE = len(self.grid) if self.grid else 0
            if GRID_SIZE:
                wx = tx - GRID_SIZE // 2
                wz = ty - GRID_SIZE // 2
                return wx, wz
            return tx, ty

        GRID_SIZE = len(self.grid) if self.grid else 0
        if GRID_SIZE:
            return self.goal[0] - GRID_SIZE // 2, self.goal[1] - GRID_SIZE // 2
        return self.goal

    def reached_goal(self) -> bool:
        return self.path_i >= len(self.path)

    def update(self, dt: float) -> None:
        if self.arrived:
            return

        self.move(dt)

        # record history in grid units
        self.history.append(self.position)
        if len(self.history) > 200:
            self.history.pop(0)

    def move(self, dt: float) -> None:
        if self.reached_goal():
            self.arrived = True
            return

        tx, ty = self.next_target()

        x, _, z = self.position
        dx = tx - x
        dz = ty - z

        # adjust speed based on current cell type (if grid provided)
        cell_type = 0
        if self.grid:
            grid_size = len(self.grid)
            current_grid_x = round(x) + grid_size // 2
            current_grid_y = round(z) + grid_size // 2
            if 0 <= current_grid_y < grid_size and 0 <= current_grid_x < grid_size:
                cell_type = self.grid[current_grid_y][current_grid_x]
            if cell_type == self.CELL_SLIPPERY and not self.is_slipping:
                self.is_slipping = True
                self.speed = self.base_speed * self.SLIP_BOOST
            elif cell_type != self.CELL_SLIPPERY and self.is_slipping:
                self.is_slipping = False
                self.speed = self.base_speed

        dist = math.sqrt(dx * dx + dz * dz)

        # if distance is extremely small, snap to target and advance
        snap_threshold = 0.01

        if dist <= snap_threshold:
            # snap exactly and advance path index
            self.position = (tx, 0.05, ty)
            # if slipping ended because we moved off a slippery cell, reset
            if self.is_slipping and (not self.grid or cell_type != self.CELL_SLIPPERY):
                self.is_slipping = False
                self.speed = self.base_speed
            self.path_i += 1
            if self.reached_goal():
                self.arrived = True
            return

        # move up to step, but don't overshoot
        step = min(self.speed * dt, dist)
        if dist > 0:
            nx = x + (dx / dist) * step
            nz = z + (dz / dist) * step
            self.position = (nx, 0.05, nz)

