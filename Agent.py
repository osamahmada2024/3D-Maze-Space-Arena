import math

class Agent:
    def __init__(self, start, goal, path, speed, color=(1,1,1)):
        self.start = start
        self.goal = goal
        self.path = path
        self.speed = speed

        self.path_i = 0
        # position stored in grid units (x, yheight, z)
        self.position = (start[0], 0.05, start[1])
        self.color = color
        self.history = []
        self.arrived = False

    def update(self, dt):
        if self.arrived:
            return

        self.move(dt)

        # record history in grid units
        self.history.append(self.position)
        if len(self.history) > 200:
            self.history.pop(0)

    def move(self, dt):
        if self.reached_goal():
            self.arrived = True
            return

        tx, ty = self.next_target()  # tx,ty are grid coordinates (x, y)

        x, _, z = self.position
        dx = tx - x
        dz = ty - z

        dist = math.sqrt(dx*dx + dz*dz)

        # if distance is extremely small, snap to target and advance
        snap_threshold = 0.01

        if dist <= snap_threshold:
            # snap exactly and advance path index
            self.position = (tx, 0.05, ty)
            self.path_i += 1
            if self.reached_goal():
                self.arrived = True
            return

        # compute step (cells per second * dt)
        step = self.speed * dt

        # If step is large enough to reach or overshoot the target, snap & advance.
        if step >= dist:
            self.position = (tx, 0.05, ty)
            self.path_i += 1
            if self.reached_goal():
                self.arrived = True
            return

        # Otherwise move proportionally toward the target
        nx = x + (dx / dist) * step
        nz = z + (dz / dist) * step
        self.position = (nx, 0.05, nz)

    def next_target(self):
        if self.path_i >= len(self.path):
            return self.goal

        return self.path[self.path_i]

    def reached_goal(self):
        return self.path_i >= len(self.path)