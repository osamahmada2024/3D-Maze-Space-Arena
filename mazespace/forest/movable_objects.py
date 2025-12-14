import math
from OpenGL.GL import *
from OpenGL.GLU import *

class MovableObject:
    def __init__(self, x, z, obj_type="log"):
        self.x = x
        self.z = z
        self.y = 0.2  # Slightly above ground
        self.obj_type = obj_type
        self.radius = 0.4
        self.push_speed = 1.0
        # Simple friction
        self.velocity_x = 0.0
        self.velocity_z = 0.0
        self.friction = 0.9

    def update(self, dt, grid_size, cell_size, grid):
        # Apply friction
        self.velocity_x *= self.friction
        self.velocity_z *= self.friction
        
        # Stop if very slow
        if abs(self.velocity_x) < 0.01: self.velocity_x = 0
        if abs(self.velocity_z) < 0.01: self.velocity_z = 0

        # Proposed new position
        new_x = self.x + self.velocity_x * dt
        new_z = self.z + self.velocity_z * dt

        # Collision with Walls (Grid)
        # Convert world to grid
        # grid center is at 0,0 world? No, standard mapping:
        # standard mapping usually: wx = (gx - size/2)*cell_size
        # so gx = wx/cell + size/2
        
        half_grid = grid_size // 2
        gx = int(round(new_x / cell_size + half_grid))
        gy = int(round(new_z / cell_size + half_grid))

        # Check bounds
        if 0 <= gx < grid_size and 0 <= gy < grid_size:
            if grid[gy][gx] == 1: # Wall
                # Simple bounce/stop
                self.velocity_x *= -0.5
                self.velocity_z *= -0.5
            else:
                self.x = new_x
                self.z = new_z

    def push(self, pusher_x, pusher_z, force=2.0):
        # Vector from pusher to object
        dx = self.x - pusher_x
        dz = self.z - pusher_z
        dist = math.sqrt(dx*dx + dz*dz)
        if dist > 0:
            nx = dx / dist
            nz = dz / dist
            self.velocity_x += nx * force * 2.0  # Boost
            self.velocity_z += nz * force * 2.0

    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        if self.obj_type == "log":
            # Brown Log
            glColor3f(0.4, 0.25, 0.1)
            glRotatef(90, 0, 1, 0) # Orient horizontally
            glRotatef(90, 1, 0, 0)
            quad = gluNewQuadric()
            gluCylinder(quad, 0.2, 0.2, 1.0, 12, 1) # Length 1.0
            gluDeleteQuadric(quad)
            # End caps
            gluDisk(quad, 0, 0.2, 12, 1)
            glTranslatef(0, 0, 1.0)
            gluDisk(quad, 0, 0.2, 12, 1)
            
        elif self.obj_type == "rock":
            # Grey Rock
            glColor3f(0.5, 0.5, 0.55)
            glScalef(0.5, 0.4, 0.5)
            quad = gluNewQuadric()
            gluSphere(quad, 1.0, 8, 8) # Low poly rock
            gluDeleteQuadric(quad)

        glPopMatrix()

class MovableObjectManager:
    def __init__(self, grid_size, cell_size):
        self.objects = []
        self.grid_size = grid_size
        self.cell_size = cell_size

    def add_object(self, x, z, obj_type="log"):
        self.objects.append(MovableObject(x, z, obj_type))

    def update(self, dt, grid):
        for obj in self.objects:
            obj.update(dt, self.grid_size, self.cell_size, grid)

    def check_collisions(self, player_x, player_z):
        # Checking player collision with objects to push them
        # Pass player radius approx 0.3
        for obj in self.objects:
            dx = player_x - obj.x
            dz = player_z - obj.z
            dist = math.sqrt(dx*dx + dz*dz)
            if dist < (0.3 + obj.radius):
                # PUSH!
                obj.push(player_x, player_z)

    def render(self):
        for obj in self.objects:
            obj.render()
