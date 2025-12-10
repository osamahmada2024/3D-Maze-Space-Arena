"""
Base Scene - Contains all shared functionality
"""

from abc import ABC, abstractmethod
import time
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

from core.Agent import Agent
from core.GridGenerator import GridGenerator
from core.PathfindingEngine import PathfindingEngine
from rendering.AgentRender import AgentRender
from rendering.GoalRender import GoalRender
from rendering.PathRender import PathRender
from ui.CameraController import CameraController
from config.settings import AGENT_SETTINGS, CAMERA_SETTINGS, GRID_SETTINGS, ALGORITHM_MAP


class Scene(ABC):
    """
    Abstract base class for all game scenes.
    Contains shared functionality for camera, agent, grid, etc.
    """
    
    def __init__(self, width: int, height: int, agent_shape: str, algo_name: str):
        self.width = width
        self.height = height
        self.agent_shape = agent_shape
        self.algo_name = algo_name
        
        # Grid Settings (من الإعدادات المركزية)
        self.grid_size = GRID_SETTINGS["size"]
        self.cell_size = GRID_SETTINGS["cell_size"]
        
        # Game Objects
        self.agent = None
        self.grid = None
        self.path = None
        self.camera = None
        
        # Renderers
        self.agent_renderer = None
        self.goal_renderer = None
        self.path_renderer = None
        
        # State
        self.start_time = 0
        self.game_active = False

    def _create_grid(self, obstacle_prob: float):
        """Create maze grid with pathfinding"""
        generator = GridGenerator(self.grid_size, obstacle_prob)
        self.grid = generator.generate()
        
        start = (0, 0)
        goal = (self.grid_size - 1, self.grid_size - 1)
        
        # Ensure start/goal are clear
        self.grid[start[1]][start[0]] = 0
        self.grid[goal[1]][goal[0]] = 0
        
        # Pathfinding
        engine = PathfindingEngine(self.grid)
        algo_key = ALGORITHM_MAP.get(self.algo_name, self.algo_name.lower())
        self.path = engine.find_path(start, goal, algo_key)
        
        if not self.path:
            print("No path found! Using fallback.")
            self.path = [start, goal]
        
        return start, goal

    def _create_agent(self, start, goal):
        """Create agent with centralized settings"""
        agent_color = AGENT_SETTINGS["colors"].get(
            self.agent_shape, 
            (0.0, 1.0, 1.0)
        )
        
        self.agent = Agent(
            start=start,
            goal=goal,
            path=self.path,
            speed=AGENT_SETTINGS["speed"],
            color=agent_color,
            shape_type=self.agent_shape,
            trail_length=AGENT_SETTINGS["trail_length"]  # ✅ من الإعدادات المركزية
        )
        
        return self.agent

    def _create_camera(self):
        """Create camera with centralized settings"""
        self.camera = CameraController(
            distance=CAMERA_SETTINGS["distance"],
            angle_x=CAMERA_SETTINGS["angle_x"],
            angle_y=CAMERA_SETTINGS["angle_y"]
        )
        return self.camera

    def _create_base_renderers(self, ground_sampler=None):
        """Create common renderers"""
        self.agent_renderer = AgentRender(
            cell_size=self.cell_size, 
            grid_size=self.grid_size
        )
        self.goal_renderer = GoalRender(
            cellSize=self.cell_size, 
            grid_size=self.grid_size
        )
        self.path_renderer = PathRender(
            cell_size=self.cell_size,
            grid_size=self.grid_size,
            ground_sampler=ground_sampler
        )

    def _update_camera_input(self, dt):
        """Handle camera input (shared between all scenes)"""
        keys = pygame.key.get_pressed()
        
        rotation_speed = CAMERA_SETTINGS["rotation_speed"]
        
        if keys[pygame.K_LEFT]:
            self.camera.angle_x -= rotation_speed * dt
        if keys[pygame.K_RIGHT]:
            self.camera.angle_x += rotation_speed * dt
        if keys[pygame.K_UP]:
            self.camera.angle_y += rotation_speed * dt
        if keys[pygame.K_DOWN]:
            self.camera.angle_y -= rotation_speed * dt
        
        # Apply angle limits
        self.camera.angle_y = max(
            CAMERA_SETTINGS["angle_y_min"], 
            min(CAMERA_SETTINGS["angle_y_max"], self.camera.angle_y)
        )

    def _update_camera_follow(self):
        """Smooth camera follow (shared between all scenes)"""
        wx = (self.agent.position[0] - self.grid_size // 2) * self.cell_size
        wy = self.agent.position[1]
        wz = (self.agent.position[2] - self.grid_size // 2) * self.cell_size
        
        # Smooth follow
        smooth = CAMERA_SETTINGS["smooth_factor"]
        self.camera.target = [
            self.camera.target[0] * (1 - smooth) + wx * smooth,
            self.camera.target[1] * (1 - smooth) + wy * smooth,
            self.camera.target[2] * (1 - smooth) + wz * smooth
        ]

    def _setup_view(self):
        """Setup OpenGL view matrix (shared)"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width / self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        pos = self.camera.calculate_camera_position()
        target = self.camera.target
        gluLookAt(
            pos[0], pos[1], pos[2],
            target[0], target[1], target[2],
            0, 1, 0
        )

    def _render_agent_and_goal(self):
        """Render agent and goal (shared)"""
        # Path
        glDisable(GL_LIGHTING)
        self.path_renderer.draw_path(self.agent)
        self.path_renderer.draw_history(self.agent)
        glEnable(GL_LIGHTING)
        
        # Goal
        if not self.agent.arrived:
            glDisable(GL_LIGHTING)
            self.goal_renderer.draw_goal(self.agent)
            glEnable(GL_LIGHTING)
        
        # Agent
        self.agent_renderer.draw_agent(self.agent, self.agent.shape_type)

    def _check_victory(self):
        """Check if agent reached goal"""
        if self.agent.arrived:
            if not hasattr(self.agent, '_victory_printed'):
                print("🎉 Goal reached! Congratulations!")
                self.agent._victory_printed = True

    # ==========================================================================
    # Abstract methods (must be implemented by subclasses)
    # ==========================================================================
    
    @abstractmethod
    def initialize(self):
        """Initialize the scene"""
        pass

    @abstractmethod
    def update(self, dt):
        """Update scene state"""
        pass

    @abstractmethod
    def render(self):
        """Render the scene"""
        pass

    @abstractmethod
    def cleanup(self):
        """Clean up resources"""
        pass