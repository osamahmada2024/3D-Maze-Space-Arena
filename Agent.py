import math

class Agent:
    def __init__(self, start, goal, path, speed=2.0, color=(0, 1, 1), shape_type="sphere_droid"):
        self.start = start              
        self.goal = goal                
        self.path = path                
        self.speed = speed             
        self.color = color
        self.shape_type = shape_type  # NEW: Store shape type

        self.path_i = 0                 
        self.position = (start[0], 0.3, start[1])  # Y=0.3 for better visibility
        self.history = []
        self.arrived = False           

    def update(self, dt):
        if self.arrived:
            return

        self.move(dt)

        # Store history for trail
        self.history.append(self.position)

        if len(self.history) > 200:
            self.history.pop(0)

    def move(self, dt):
        if self.reached_goal():
            self.arrived = True
            return

        tx, ty = self.next_target()

        x, _, z = self.position
        dx = tx - x
        dz = ty - z

        dist = math.sqrt(dx*dx + dz*dz)

        if dist < 0.01:
            self.position = (tx, 0.3, ty)
            self.path_i += 1

            if self.reached_goal():
                self.arrived = True

            return

        step = self.speed * dt
        nx = x + (dx / dist) * step
        nz = z + (dz / dist) * step

        self.position = (nx, 0.3, nz)

    def next_target(self):
        if self.path_i >= len(self.path):
            return self.goal
        
        return self.path[self.path_i]

    def reached_goal(self):
        return self.path_i >= len(self.path)