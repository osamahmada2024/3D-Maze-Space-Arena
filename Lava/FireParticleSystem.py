"""
Fire/Ember Particle System
Creates rising embers and flames for the lava maze.
"""

class Ember:
    """Single ember/fire particle"""
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(0.5, 1.5)
        self.vz = random.uniform(-0.2, 0.2)
        self.size = random.uniform(0.05, 0.15)
        self.lifetime = random.uniform(2.0, 4.0)
        self.age = 0.0
        self.color = (1.0, random.uniform(0.3, 0.7), 0.0)
    
    def update(self, dt: float):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        # Slow down over time
        self.vy *= 0.98
        self.size *= 0.99
    
    def is_alive(self) -> bool:
        return self.age < self.lifetime
    
    def get_alpha(self) -> float:
        return 1.0 - (self.age / self.lifetime)


class FireParticleSystem:
    """Manages fire particles rising from lava"""
    
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.embers: List[Ember] = []
        self.spawn_points = []
    
    def set_spawn_points(self, lava_positions: List[Tuple[float, float, float]]):
        """Set locations where embers spawn"""
        self.spawn_points = lava_positions
    
    def update(self, dt: float):
        # Update existing embers
        alive = []
        for ember in self.embers:
            ember.update(dt)
            if ember.is_alive():
                alive.append(ember)
        self.embers = alive
        
        # Spawn new embers
        if self.spawn_points:
            for _ in range(3):  # Spawn 3 per frame
                point = random.choice(self.spawn_points)
                x = point[0] + random.uniform(-0.3, 0.3)
                y = point[1]
                z = point[2] + random.uniform(-0.3, 0.3)
                self.embers.append(Ember(x, y, z))
    
    def render(self):
        if not self.embers:
            return
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glPointSize(4.0)
        
        glBegin(GL_POINTS)
        for ember in self.embers:
            alpha = ember.get_alpha()
            r, g, b = ember.color
            glColor4f(r, g, b, alpha)
            glVertex3f(ember.x, ember.y, ember.z)
        glEnd()
        
        glPointSize(1.0)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)
