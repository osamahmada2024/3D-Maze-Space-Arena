"""
Space Scene - Space-specific implementation with path collision avoidance
"""

import time
from OpenGL.GL import *

from mazespace.core.Scene import Scene
from mazespace.config.settings import GRID_SETTINGS, THEME_SETTINGS
from mazespace.rendering.EnvironmentRender import EnvironmentRender3D


class SpaceScene(Scene):
    def __init__(self, selected_shape, selected_algo, width, height):
        super().__init__(width, height, selected_shape, selected_algo)
        
        # Space-specific settings
        self.theme = THEME_SETTINGS["DEFAULT"]
        
        # Space-specific systems
        self.environment_renderer = None

    def initialize(self):
        self._init_opengl()
        
        # Create grid and path (from base class)
        obstacle_prob = GRID_SETTINGS["obstacle_prob_space"]
        start, goal = self._create_grid(obstacle_prob)
        
        # Create agent (from base class)
        self._create_agent(start, goal)
        
        # ✅ الآن لدينا agent.path - نمرره للـ environment
        agent_path = self.agent.path if hasattr(self.agent, 'path') else None
        
        # Create camera (from base class)
        self._create_camera()
        
        # Space-specific: Environment renderer with path collision detection
        self.environment_renderer = EnvironmentRender3D(
            self.grid, 
            cell_size=self.cell_size,
            agent_path=agent_path  # ✅ تمرير المسار
        )
        
        # Create base renderers with ground sampler
        self._create_base_renderers(
            ground_sampler=self.environment_renderer.get_ground_height
        )
        
        self.start_time = time.time()
        self.game_active = True
        
        print("[SPACE] Scene initialized successfully!")
        print(f"[SPACE] Path length: {len(agent_path) if agent_path else 0}")
        return self.agent

    def _init_opengl(self):
        bg = self.theme["bg_color"]
        glClearColor(*bg)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glClearDepth(1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 5.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])

    def update(self, dt):
        if not self.game_active:
            return
        
        # Camera input (from base class)
        self._update_camera_input(dt)
        
        # Agent update
        self.agent.update(dt)
        self.agent_renderer.update_time(dt)
        
        # Camera follow (from base class)
        self._update_camera_follow()
        
        # Check victory
        self._check_victory()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._setup_view()
        
        # Environment
        elapsed_time = time.time() - self.start_time
        self.environment_renderer.draw(elapsed_time)
        
        # Agent and goal (from base class)
        self._render_agent_and_goal()

    def cleanup(self):
        print("[SPACE] Cleanup complete.")