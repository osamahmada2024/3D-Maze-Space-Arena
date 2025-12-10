"""
Lava Maze Scene - Main Game Scene
Integrates all lava systems into a complete hellish maze.
"""

import time

# Assuming these imports from your core system
try:
    from core.Scene import Scene
    from core.Agent import Agent
    from core.PathfindingEngine import PathfindingEngine
    from rendering.AgentRender import AgentRender
    from rendering.GoalRender import GoalRender
    from rendering.PathRender import PathRender
    from ui.CameraController import CameraController
    from core.GridGenerator import GridGenerator
except ImportError:
    print("[WARNING] Core imports not available - using stubs")
    Scene = object
    Agent = None


class LavaMazeScene(Scene):
    def __init__(self, width, height, num_agents=1, algos=None):
        self.width = width
        self.height = height
        self.grid_size = 25
        self.cell_size = 1.0
        
        # Game State
        self.start_time = 0
        self.agent = None
        self.camera = None
        self.game_active = False
        
        # Health system
        self.player_health = 100.0
        self.last_damage_time = 0.0
        
        # Lava Systems
        self.lava_manager = LavaZoneManager()
        self.fire_particles = FireParticleSystem(self.grid_size, self.cell_size)
        self.volcanic_env = VolcanicEnvironmentManager(self.grid_size, self.cell_size)
        self.heat_fog = HeatHazeFog()
        self.audio_system = LavaAudioSystem()
        
        # Renderers
        self.agent_renderer = AgentRender(cell_size=self.cell_size, grid_size=self.grid_size)
        self.goal_renderer = GoalRender(cellSize=self.cell_size, grid_size=self.grid_size)
        self.path_renderer = None
        
        self.grid = None
        self.path = None
        self.last_player_cell = None
        self.fog_pulse = 0.0
    
    def initialize(self, agent_shape="sphere_droid", algo_name="astar"):
        self._init_opengl()
        
        # Generate Maze
        maze_gen = GridGenerator(self.grid_size, obstacle_prob=0.55)
        self.grid = maze_gen.generate()
        
        # Setup Start/Goal
        start = (0, 0)
        goal = (self.grid_size-1, self.grid_size-1)
        self.grid[start[1]][start[0]] = 0
        self.grid[goal[1]][goal[0]] = 0
        
        # Pathfinding
        engine = PathfindingEngine(self.grid)
        algo_map = {
            "A* search": "astar",
            "Dijkstra": "dijkstra",
            "DFS": "dfs",
            "BFS": "bfs"
        }
        engine_algo = algo_map.get(algo_name, algo_name.lower())
        self.path = engine.find_path(start, goal, engine_algo)
        if not self.path:
            self.path = [start, goal]
        
        # Generate lava zones (EXCLUDING path)
        path_set = set(self.path)
        lava_positions = []
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x] == 0 and (x, y) not in path_set:
                    if random.random() < 0.15:  # 15% lava coverage
                        lava_positions.append((x, y))
        
        self.lava_manager.create_from_grid_positions(lava_positions, self.grid_size, self.cell_size)
        
        # Setup fire particles spawn points
        spawn_points = []
        for zone in self.lava_manager.zones:
            spawn_points.append(zone.get_position())
        self.fire_particles.set_spawn_points(spawn_points)
        
        # Generate volcanic environment
        self.volcanic_env.generate_rocks_from_grid(self.grid)
        
        # Agent colors
        shape_colors = {
            "sphere_droid": (1.0, 0.5, 0.0),   # Orange (fire resistant)
            "robo_cube": (0.8, 0.2, 0.2),      # Dark red
            "mini_drone": (1.0, 0.3, 0.0),     # Bright orange
            "crystal_alien": (1.0, 0.8, 0.0)   # Yellow-orange
        }
        agent_color = shape_colors.get(agent_shape, (1.0, 0.4, 0.0))
        
        # Initialize Agent
        self.agent = Agent(
            start, goal, self.path,
            speed=2.5,
            color=agent_color,
            shape_type=agent_shape,
            trail_length=25
        )
        
        # Path Renderer
        self.path_renderer = PathRender(
            cell_size=self.cell_size,
            grid_size=self.grid_size,
            ground_sampler=lambda x, z: 0.0
        )
        
        # Camera
        self.camera = CameraController(distance=12, angle_x=45, angle_y=35)
        
        # Audio
        self.audio_system.start_ambient()
        
        self.start_time = time.time()
        self.game_active = True
        
        print(f"[LAVA MAZE] Initialized! {len(lava_positions)} lava pools created")
        return self.agent
    
    def _init_opengl(self):
        glClearColor(0.1, 0.05, 0.0, 1.0)  # Dark reddish background
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Hellish lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 30.0, 0.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.1, 0.05, 1.0])  # Red ambient
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.4, 0.1, 1.0])   # Orange light
        
        # Enable heat fog
        self.heat_fog.enable()
    
    def update(self, dt):
        if not self.game_active:
            return
        
        # Agent movement
        self.agent.update(dt)
        self.agent_renderer.update_time(dt)
        
        # Camera controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.camera.angle_x -= 60 * dt
        if keys[pygame.K_RIGHT]: self.camera.angle_x += 60 * dt
        if keys[pygame.K_UP]: self.camera.angle_y += 60 * dt
        if keys[pygame.K_DOWN]: self.camera.angle_y -= 60 * dt
        self.camera.angle_y = max(15, min(85, self.camera.angle_y))
        
        # Get agent world position
        wx = (self.agent.position[0] - self.grid_size//2) * self.cell_size
        wy = self.agent.position[1]
        wz = (self.agent.position[2] - self.grid_size//2) * self.cell_size
        
        # Camera follow
        self.camera.target = [
            self.camera.target[0] * 0.85 + wx * 0.15,
            self.camera.target[1] * 0.85 + wy * 0.15,
            self.camera.target[2] * 0.85 + wz * 0.15
        ]
        
        # Check lava damage
        if self.lava_manager.is_in_lava((wx, wy, wz)):
            current_time = time.time()
            if current_time - self.last_damage_time > 0.5:
                damage = self.lava_manager.get_damage_rate((wx, wy, wz))
                self.player_health -= damage * dt
                self.audio_system.play_burn_damage()
                self.last_damage_time = current_time
                print(f"[LAVA] BURNING! Health: {self.player_health:.1f}")
                
                if self.player_health <= 0:
                    print("[LAVA] GAME OVER - Burned to death!")
                    self.game_active = False
        
        # Footsteps
        gx = int(round(wx / self.cell_size + self.grid_size // 2))
        gy = int(round(wz / self.cell_size + self.grid_size // 2))
        if (gx, gy) != self.last_player_cell:
            self.last_player_cell = (gx, gy)
            self.audio_system.play_footstep()
        
        # Update systems
        self.lava_manager.update(dt)
        self.fire_particles.update(dt)
        self.volcanic_env.update(dt)
        self.audio_system.update(dt)
        
        # Pulsing fog effect
        self.fog_pulse += dt
        intensity = 0.8 + 0.2 * math.sin(self.fog_pulse * 0.5)
        self.heat_fog.update_intensity(intensity)
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Setup Camera
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65, self.width / self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        pos = self.camera.calculate_camera_position()
        target = self.camera.target
        gluLookAt(pos[0], pos[1], pos[2], target[0], target[1], target[2], 0, 1, 0)
        
        # Render volcanic floor
        self._render_volcanic_floor()
        
        # Render volcanic rocks (walls)
        self.volcanic_env.render_all()
        
        # Render lava pools
        self.lava_manager.render_zones()
        
        # Render fire particles
        self.fire_particles.render()
        
        # Render path
        glDisable(GL_LIGHTING)
        if self.path_renderer:
            self.path_renderer.draw_path(self.agent)
            self.path_renderer.draw_history(self.agent)
        glEnable(GL_LIGHTING)
        
        # Render agent
        self.agent_renderer.draw_agent(self.agent, self.agent.shape_type)
        
        # Render goal
        if not self.agent.arrived:
            self.goal_renderer.draw_goal(self.agent)
        
        # Health bar (simple overlay)
        self._render_health_bar()
    
    def _render_volcanic_floor(self):
        """Render dark volcanic rock floor"""
        glDisable(GL_LIGHTING)
        
        half_world = self.grid_size * self.cell_size / 2.0
        
        # Base dark floor
        glColor3f(0.1, 0.05, 0.05)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-half_world, -0.1, -half_world)
        glVertex3f(half_world, -0.1, -half_world)
        glVertex3f(half_world, -0.1, half_world)
        glVertex3f(-half_world, -0.1, half_world)
        glEnd()
        
        # Cracked patterns
        glColor3f(0.15, 0.1, 0.08)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        for _ in range(100):
            x1 = random.uniform(-half_world, half_world)
            z1 = random.uniform(-half_world, half_world)
            length = random.uniform(0.5, 2.0)
            angle = random.uniform(0, math.pi * 2)
            x2 = x1 + length * math.cos(angle)
            z2 = z1 + length * math.sin(angle)
            glVertex3f(x1, -0.09, z1)
            glVertex3f(x2, -0.09, z2)
        glEnd()
        glLineWidth(1.0)
        
        glEnable(GL_LIGHTING)
    
    def _render_health_bar(self):
        """Render health bar in screen space"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Health bar background
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = self.height - 40
        
        glColor3f(0.2, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_width, bar_y)
        glVertex2f(bar_x + bar_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        
        # Health bar fill
        health_pct = max(0.0, min(1.0, self.player_health / 100.0))
        fill_width = bar_width * health_pct
        
        if health_pct > 0.5:
            glColor3f(1.0, 0.5, 0.0)  # Orange
        elif health_pct > 0.25:
            glColor3f(1.0, 0.3, 0.0)  # Red-orange
        else:
            glColor3f(1.0, 0.0, 0.0)  # Red
        
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + fill_width, bar_y)
        glVertex2f(bar_x + fill_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def cleanup(self):
        """Cleanup all systems"""
        self.audio_system.cleanup()
        print("[LAVA MAZE] Scene cleaned up")


# ==================== USAGE EXAMPLE ====================
"""
To integrate this into your main game:

1. Import the scene:
   from scenes.lava_maze import LavaMazeScene

2. Create and initialize:
   scene = LavaMazeScene(width=1920, height=1080)
   scene.initialize(agent_shape="sphere_droid", algo_name="astar")

3. In your game loop:
   scene.update(delta_time)
   scene.render()

4. On exit:
   scene.cleanup()

Features:
- Deadly lava pools that damage the player
- Rising fire particles and embers
- Volcanic rock walls with glowing cracks
- Heat haze fog system
- Health system with visual bar
- Ambient lava sounds and rumbling
- Pulsing atmospheric effects
- Safe pathfinding (lava excluded from agent path)
"""


# ==================== ADDITIONAL ENHANCEMENTS ====================

class LavaGeyser:
    """Erupting lava geysers for extra danger"""
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.eruption_timer = 0.0
        self.eruption_interval = random.uniform(5.0, 10.0)
        self.is_erupting = False
        self.eruption_duration = 2.0
        self.warning_time = 1.0
        self.state = "dormant"  # dormant, warning, erupting
    
    def update(self, dt: float):
        self.eruption_timer += dt
        
        if self.state == "dormant":
            if self.eruption_timer >= self.eruption_interval:
                self.state = "warning"
                self.eruption_timer = 0.0
        
        elif self.state == "warning":
            if self.eruption_timer >= self.warning_time:
                self.state = "erupting"
                self.eruption_timer = 0.0
        
        elif self.state == "erupting":
            if self.eruption_timer >= self.eruption_duration:
                self.state = "dormant"
                self.eruption_timer = 0.0
                self.eruption_interval = random.uniform(5.0, 10.0)
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        if self.state == "warning":
            # Pulsing red glow
            intensity = abs(math.sin(self.eruption_timer * 10))
            glDisable(GL_LIGHTING)
            glColor4f(1.0, 0.0, 0.0, 0.5 * intensity)
            
            quad = gluNewQuadric()
            gluDisk(quad, 0, 0.5, 16, 1)
            gluDeleteQuadric(quad)
            glEnable(GL_LIGHTING)
        
        elif self.state == "erupting":
            # Erupting column of lava
            glDisable(GL_LIGHTING)
            glColor4f(1.0, 0.5, 0.0, 0.8)
            
            height = 3.0 * (self.eruption_timer / self.eruption_duration)
            quad = gluNewQuadric()
            gluCylinder(quad, 0.3, 0.1, height, 12, 1)
            gluDeleteQuadric(quad)
            glEnable(GL_LIGHTING)
        
        glPopMatrix()
    
    def is_dangerous(self, position: Tuple[float, float, float]) -> bool:
        """Check if position is in danger zone"""
        if self.state != "erupting":
            return False
        
        px, py, pz = position
        dx = px - self.x
        dz = pz - self.z
        dist = math.sqrt(dx*dx + dz*dz)
        return dist < 1.0


class ScreenShakeEffect:
    """Camera shake for eruptions and impacts"""
    
    def __init__(self):
        self.shake_amount = 0.0
        self.shake_duration = 0.0
        self.shake_timer = 0.0
    
    def trigger(self, intensity: float = 0.5, duration: float = 0.5):
        self.shake_amount = intensity
        self.shake_duration = duration
        self.shake_timer = 0.0
    
    def update(self, dt: float):
        if self.shake_timer < self.shake_duration:
            self.shake_timer += dt
        else:
            self.shake_amount = 0.0
    
    def get_offset(self) -> Tuple[float, float, float]:
        if self.shake_amount == 0.0:
            return (0, 0, 0)
        
        progress = 1.0 - (self.shake_timer / self.shake_duration)
        current_shake = self.shake_amount * progress
        
        return (
            random.uniform(-current_shake, current_shake),
            random.uniform(-current_shake, current_shake),
            random.uniform(-current_shake, current_shake)
        )


class HeatDamageIndicator:
    """Visual indicator when taking damage"""
    
    def __init__(self):
        self.flash_timer = 0.0
        self.flash_duration = 0.3
    
    def trigger(self):
        self.flash_timer = self.flash_duration
    
    def update(self, dt: float):
        if self.flash_timer > 0:
            self.flash_timer -= dt
    
    def render_overlay(self, width: int, height: int):
        """Render red damage overlay"""
        if self.flash_timer <= 0:
            return
        
        alpha = self.flash_timer / self.flash_duration
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor4f(1.0, 0.0, 0.0, 0.4 * alpha)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(width, 0)
        glVertex2f(width, height)
        glVertex2f(0, height)
        glEnd()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)


# ==================== ENHANCED LAVA SCENE WITH ALL FEATURES ====================

class EnhancedLavaMazeScene(LavaMazeScene):
    """
    Enhanced version with geysers, screen shake, and damage indicators
    """
    
    def __init__(self, width, height, num_agents=1, algos=None):
        super().__init__(width, height, num_agents, algos)
        self.geysers = []
        self.screen_shake = ScreenShakeEffect()
        self.damage_indicator = HeatDamageIndicator()
    
    def initialize(self, agent_shape="sphere_droid", algo_name="astar"):
        result = super().initialize(agent_shape, algo_name)
        
        # Add some lava geysers in safe areas
        path_set = set(self.path)
        geyser_count = 0
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x] == 0 and (x, y) not in path_set:
                    if random.random() < 0.03 and geyser_count < 5:  # Max 5 geysers
                        wx = (x - self.grid_size // 2) * self.cell_size
                        wz = (y - self.grid_size // 2) * self.cell_size
                        self.geysers.append(LavaGeyser(wx, 0, wz))
                        geyser_count += 1
        
        print(f"[LAVA MAZE] Added {len(self.geysers)} lava geysers")
        return result
    
    def update(self, dt):
        if not self.game_active:
            return
        
        # Call parent update
        super().update(dt)
        
        # Update geysers
        for geyser in self.geysers:
            geyser.update(dt)
            
            # Check geyser damage
            wx = (self.agent.position[0] - self.grid_size//2) * self.cell_size
            wy = self.agent.position[1]
            wz = (self.agent.position[2] - self.grid_size//2) * self.cell_size
            
            if geyser.is_dangerous((wx, wy, wz)):
                current_time = time.time()
                if current_time - self.last_damage_time > 0.3:
                    self.player_health -= 15.0
                    self.damage_indicator.trigger()
                    self.screen_shake.trigger(0.3, 0.4)
                    self.audio_system.play_burn_damage()
                    self.last_damage_time = current_time
                    print(f"[GEYSER] Hit by eruption! Health: {self.player_health:.1f}")
        
        # Update effects
        self.screen_shake.update(dt)
        self.damage_indicator.update(dt)
    
    def render(self):
        # Apply screen shake to camera
        shake_offset = self.screen_shake.get_offset()
        original_target = self.camera.target.copy()
        self.camera.target[0] += shake_offset[0]
        self.camera.target[1] += shake_offset[1]
        self.camera.target[2] += shake_offset[2]
        
        # Render scene
        super().render()
        
        # Restore camera
        self.camera.target = original_target
        
        # Render geysers
        for geyser in self.geysers:
            geyser.render()
        
        # Render damage indicator
        self.damage_indicator.render_overlay(self.width, self.height)


print("""
╔════════════════════════════════════════════════════════════╗
║           LAVA MAZE - COMPLETE SYSTEM                      ║
║                                                            ║
║  Features:                                                 ║
║  ✓ Deadly lava pools with damage system                  ║
║  ✓ Rising fire particles and ember effects               ║
║  ✓ Volcanic rocks with glowing cracks                    ║
║  ✓ Heat haze fog system                                   ║
║  ✓ Lava geysers with warning indicators                  ║
║  ✓ Health bar and damage indicators                      ║
║  ✓ Screen shake effects                                   ║
║  ✓ Ambient audio (bubbling, rumbling)                    ║
║  ✓ Safe pathfinding (no lava on path)                    ║
║                                                            ║
║  الحمد لله - الـ maze جامد موووووت! 🔥                   ║
╚════════════════════════════════════════════════════════════╝
""")