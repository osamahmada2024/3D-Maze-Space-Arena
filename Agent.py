import math
from typing import List, Tuple


class Agent:
    """
    Autonomous navigation agent within the 3D Maze-Space Arena.
    Handles movement, path following, goal detection, and history tracking.
    """

    def __init__(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        path: List[Tuple[int, int]],
        speed: float,
        color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    ):
        self.start = start
        self.goal = goal
        self.path = path
        self.speed = speed
        self.color = color

        self.path_i = 0
        self.position = (start[0], 0.05, start[1])
        self.history: List[Tuple[float, float, float]] = []
        self.arrived = False

    # ---------------------------------------------------------

    def update(self, dt: float) -> None:
        """Update agent position and state."""
        if self.arrived:
            return

        self.move(dt)
        self.history.append(self.position)

        if len(self.history) > 200:
            self.history.pop(0)

    # ---------------------------------------------------------

    def move(self, dt: float) -> None:
        """Move the agent toward the next path waypoint."""
        if self.reached_goal():
            self.arrived = True
            return

        tx, ty = self.next_target()
        x, _, z = self.position

        dx = tx - x
        dz = ty - z
        dist = math.sqrt(dx * dx + dz * dz)

        if dist < 0.01:
            self.position = (tx, 0.05, ty)
            self.path_i += 1

            if self.reached_goal():
                self.arrived = True
            return

        step = self.speed * dt
        nx = x + (dx / dist) * step
        nz = z + (dz / dist) * step
        self.position = (nx, 0.05, nz)

    # ---------------------------------------------------------

    def next_target(self) -> Tuple[int, int]:
        """Return the next waypoint."""
        if self.path_i >= len(self.path):
            return self.goal
        return self.path[self.path_i]

    # ---------------------------------------------------------

    def reached_goal(self) -> bool:
        """Check if the final waypoint is reached."""
        return self.path_i >= len(self.path)
