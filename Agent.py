import math
from typing import List, Tuple, Optional

class Agent:
    def _init_(
        self, 
        start: Tuple[float, float], 
        goal: Tuple[float, float], 
        path: List[Tuple[float, float]], 
        speed: float, 
        color: Tuple[float, float, float]=(1,1,1),
        grid: Optional[List[List[int]]] = None
    ):
        self.start = start
        self.goal = goal
        self.path = path
        
        self.base_speed = speed
        self.speed = speed

        self.path_i = 0
        self.position = (start[0], 0.05, start[1])
        self.color = color
        self.history: List[Tuple[float, float, float]] = []
        self.arrived = False

        self.grid = grid
        self.is_slipping = False
        self.SLIP_BOOST = 2.5
        self.CELL_SLIPPERY = 2

    def next_target(self) -> Tuple[float, float]:
        if self.path_i < len(self.path):
            tx, ty = self.path[self.path_i]
            GRID_SIZE = len(self.grid) if self.grid else 0
            wx = tx - GRID_SIZE // 2
            wz = ty - GRID_SIZE // 2
            return wx, wz
        GRID_SIZE = len(self.grid) if self.grid else 0
        return self.goal[0] - GRID_SIZE // 2, self.goal[1] - GRID_SIZE // 2

    def reached_goal(self) -> bool:
        return self.path_i >= len(self.path)

    def update(self, dt: float) -> None:
        if self.arrived:
            return
        self.move(dt)
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

        if self.grid:
            current_grid_x = round(x) + len(self.grid) // 2
            current_grid_y = round(z) + len(self.grid) // 2
            cell_type = 0
            grid_size = len(self.grid)
            if 0 <= current_grid_y < grid_size and 0 <= current_grid_x < grid_size:
                cell_type = self.grid[current_grid_y][current_grid_x]
            if cell_type == self.CELL_SLIPPERY and not self.is_slipping:
                self.is_slipping = True
                self.speed = self.base_speed * self.SLIP_BOOST
            elif cell_type != self.CELL_SLIPPERY and self.is_slipping:
                self.is_slipping = False
                self.speed = self.base_speed

        dist = math.sqrt(dx*dx + dz*dz)

        if dist < 0.01:
            self.position = (tx, 0.05, ty)
            if self.is_slipping and (not self.grid or cell_type != self.CELL_SLIPPERY):
                self.is_slipping = False
                self.speed = self.base_speed
            self.path_i += 1
            if self.reached_goal():
                self.arrived = True
            return

        step = min(self.speed * dt, dist)
        if dist > 0:
            nx = x + dx / dist * step
            nz = z + dz / dist * step
            self.position = (nx, 0.05, nz)