import math

class Agent:
    def __init__(self, start, goal, path, speed, color=(1,1,1)):
        self.start = start              
        self.goal = goal                
        self.path = path                
        self.speed = speed             

        self.path_i = 0                 
        self.position = (start[0], 0.05, start[1])  
        self.color = color
        self.history = []
        self.arrived = False           

    def update(self, dt):
        if self.arrived:
            return

        self.move(dt)

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
            self.position = (tx, 0.05, ty)
            self.path_i += 1

            if self.reached_goal():
                self.arrived = True

            return

        step = self.speed * dt
        nx = x + (dx / dist) * step
        nz = z + (dz / dist) * step

        self.position = (nx, 0.05, nz)

    def next_target(self):
        if self.path_i >= len(self.path):
            return self.goal
        
        return self.path[self.path_i]

    def reached_goal(self):
        return self.path_i >= len(self.path)