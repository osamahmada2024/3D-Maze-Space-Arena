"""
Forest Scene - Forest-specific implementation
"""

import time
from OpenGL.GL import *

from core.scene import Scene
from config.settings import GRID_SETTINGS, THEME_SETTINGS

# Forest specific modules
from .environment_objects import EnvironmentObjectManager
from .particles import FireflyParticleSystem
from .audio_system import AudioSystem
from .slow_zones import SlowZoneManager
from .fog import FogSystem
from .movable_objects import MovableObjectManager


class ForestScene(Scene):
    def __init__(self, width, height, agent_shape="sphere_droid", algo_name="astar"):
        super().__init__(width, height, agent_shape, algo_name)
        
        # Forest-specific settings
        self.theme = THEME_SETTINGS["FOREST"]
        
        # Forest-specific systems
        self.env_manager = None
        self.audio_system = None
        self.slow_zone_manager = None
        self.fog_system = None
        self.fireflies = None
        self.movables = None
        
        self.last_player_cell = None

    def initialize(self, agent_shape=None, algo_name=None):
        # Override if passed
        if agent_shape:
            self.agent_shape = agent_shape
        if algo_name:
            self.algo_name = algo_name
        
        self._init_opengl()
        
        # Create grid and path (from base class)
        obstacle_prob = GRID_SETTINGS["obstacle_prob_forest"]
        start, goal = self._create_grid(obstacle_prob)
        
        # Create agent (from base class)
        self._create_agent(start, goal)
        
        # Create camera (from base class)
        self._create_camera()
        
        # Create base renderers
        self._create_base_renderers(ground_sampler=lambda x, z: 0.0)
        
        # Forest-specific initialization
        self._init_forest_systems()
        
        self.start_time = time.time()
        self.game_active = True
        
        print("[FOREST] Scene initialized successfully!")
        return self.agent

    def _init_opengl(self):
        bg = self.theme["bg_color"]
        glClearColor(*bg)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 20.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.15, 0.1, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.6, 0.6, 0.5, 1.0])

    def _init_forest_systems(self):
        """Initialize forest-specific systems"""
        # Environment
        self.env_manager = EnvironmentObjectManager(self.grid_size, self.cell_size)
        self.env_manager.generate_trees_from_grid(self.grid)
        
        # Clear goal area of trees (safety measure)
        goal_pos = (self.grid_size - 1, self.grid_size - 1)
        self.env_manager.clear_area(goal_pos, radius=1)
        
        # Fog
        self.fog_system = FogSystem(
            fog_color=self.theme["fog_color"],
            fog_density=self.theme["fog_density"]
        )
        if self.theme["fog_enabled"]:
            self.fog_system.enable()
        
        # Particles
        self.fireflies = FireflyParticleSystem(
            self.grid_size, self.cell_size, num_fireflies=30
        )
        
        # Audio
        self.audio_system = AudioSystem(assets_dir="assets/audio")
        self.audio_system.add_sound_zone(
            "center_wind", (0, 5, 0), "wind", volume=0.3, radius=20.0
        )
        
        # Slow zones
        self.slow_zone_manager = SlowZoneManager()
        
        # Movable objects
        self.movables = MovableObjectManager(self.grid_size, self.cell_size)

    def update(self, dt):
        if not self.game_active:
            return
        
        # Camera input (from base class)
        self._update_camera_input(dt)
        
        # Agent update
        for agent in self.agents:
            agent.update(dt)
        self.agent_renderer.update_time(dt)
        
        # Camera follow (from base class)
        self._update_camera_follow()
        
        # Forest-specific updates
        self._update_forest_systems(dt)
        
        # Check victory
        self._check_victory()

    def _update_forest_systems(self, dt):
        """Update forest-specific systems"""
        wx = (self.agent.position[0] - self.grid_size // 2) * self.cell_size
        wy = self.agent.position[1]
        wz = (self.agent.position[2] - self.grid_size // 2) * self.cell_size
        
        # 1. Check Tree Collisions (FIX)
        if self.env_manager.check_collision((wx, wy, wz)):
             # Push agent back if it hits a tree
             self.agent.position = self.agent.prev_position

        # Movables
        self.movables.check_collisions(wx, wz)
        self.movables.update(dt, self.grid)
        
        # Particles
        self.fireflies.update(dt)
        
        # Audio
        self.audio_system.update(dt)
        self.audio_system.update_positional_audio((wx, wy, wz))
        
        # Footsteps
        gx = int(round(wx / self.cell_size + self.grid_size // 2))
        gy = int(round(wz / self.cell_size + self.grid_size // 2))
        if (gx, gy) != self.last_player_cell:
            self.last_player_cell = (gx, gy)
            self.audio_system.play_footstep()
        
        # Fog time of day
        current_time = time.time() - self.start_time
        day_cycle = (current_time % 120) / 120.0
        self.fog_system.update_time_of_day(day_cycle)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._setup_view()


        
        # Forest floor
        self._render_floor()
        
        # Environment (trees)
        self.env_manager.render_all()
        
        # Movables
        self.movables.render()
        
        # Slow zones
        self.slow_zone_manager.render_zones()
        
        # Agent and goal (Disable fog to prevent fading)
        glDisable(GL_FOG)
        self._render_agent_and_goal()
        if self.theme["fog_enabled"]:
            glEnable(GL_FOG)
        
        # Fireflies
        self.fireflies.render()

    def _render_floor(self):
        """Render forest floor"""
        glDisable(GL_LIGHTING)
        half_world = self.grid_size * self.cell_size / 2.0
        
        glColor3f(0.05, 0.35, 0.05)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-half_world, -0.1, -half_world)
        glVertex3f(half_world, -0.1, -half_world)
        glVertex3f(half_world, -0.1, half_world)
        glVertex3f(-half_world, -0.1, half_world)
        glEnd()
        
        glEnable(GL_LIGHTING)

    def cleanup(self):
        if self.audio_system:
            self.audio_system.cleanup()
        print("[FOREST] Cleanup complete.")