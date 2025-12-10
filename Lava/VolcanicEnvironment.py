"""
Volcanic Rock Objects
Dark rocks with glowing cracks for the lava maze environment.
"""

class VolcanicRock:
    def __init__(self, x: float, y: float, z: float, scale: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.scale = scale
        self.rotation = random.uniform(0, 360)
        self.glow_phase = random.uniform(0, math.pi * 2)
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 1, 0)
        glScalef(self.scale, self.scale * 0.7, self.scale)
        
        # Dark volcanic rock
        glColor3f(0.15, 0.15, 0.15)
        quad = gluNewQuadric()
        gluSphere(quad, 0.5, 8, 8)
        gluDeleteQuadric(quad)
        
        # Glowing cracks (small orange lines)
        glDisable(GL_LIGHTING)
        glow = 0.5 + 0.5 * math.sin(self.glow_phase)
        glColor3f(1.0 * glow, 0.3 * glow, 0.0)
        glLineWidth(2.0)
        
        glBegin(GL_LINES)
        for _ in range(4):
            angle = random.uniform(0, math.pi * 2)
            r = random.uniform(0.3, 0.5)
            x1 = r * math.cos(angle)
            z1 = r * math.sin(angle)
            x2 = x1 * 1.2
            z2 = z1 * 1.2
            glVertex3f(x1, 0, z1)
            glVertex3f(x2, 0, z2)
        glEnd()
        
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
        glPopMatrix()


class VolcanicEnvironmentManager:
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.rocks = []
    
    def generate_rocks_from_grid(self, grid):
        """Generate volcanic rocks from maze walls"""
        self.rocks = []
        
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if grid[y][x] == 1:
                    if random.random() > 0.3:  # 70% density
                        wx = (x - self.grid_size // 2) * self.cell_size
                        wz = (y - self.grid_size // 2) * self.cell_size
                        scale = random.uniform(0.8, 1.3)
                        self.rocks.append(VolcanicRock(wx, 0.2, wz, scale))
        
        print(f"[LAVA ENV] Generated {len(self.rocks)} volcanic rocks")
    
    def update(self, dt: float):
        for rock in self.rocks:
            rock.glow_phase += dt * 0.5
    
    def render_all(self):
        glEnable(GL_LIGHTING)
        for rock in self.rocks:
            rock.render()

