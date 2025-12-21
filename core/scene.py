"""
Base Scene - Contains all shared functionality
"""

from abc import ABC, abstractmethod
import time
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

from core.agent import Agent
from core.grid_generator import GridGenerator
from core.pathfinding_engine import PathfindingEngine
from rendering.agent_render import AgentRender
from rendering.goal_render import GoalRender
from rendering.path_render import PathRender
from ui.camera_controller import CameraController
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
        self.agents = [] # List of Agent objects
        self.agent = None # Deprecated, kept for backward compat (references agents[0] if exists)
        self.grid = None
        self.path = None # Deprecated/Single path
        self.camera = None
        
        # Renderers
        self.agent_renderer = None
        self.goal_renderer = None
        self.path_renderer = None
        
        # State
        self.start_time = 0
        self.game_active = False
        self.is_finished = False
        self.zoom_offset = 0.0 # Manual zoom control

    def handle_event(self, event):
        """Handle specific input events"""
        if event.type == pygame.MOUSEWHEEL:
            # Zoom In/Out
            self.zoom_offset -= event.y * 2.0
            self.zoom_offset = max(-20.0, min(50.0, self.zoom_offset))

    def _create_grid(self, obstacle_prob: float):
        """Create maze grid with pathfinding"""
        generator = GridGenerator(self.grid_size, obstacle_prob)
        self.grid = generator.generate()
        
        start = (0, 0)
        goal = (self.grid_size - 1, self.grid_size - 1)
        
        # Ensure start/goal are clear
        self.grid[start[1]][start[0]] = 0
        self.grid[goal[1]][goal[0]] = 0
        
        # Pathfinding (now returns tuple)
        engine = PathfindingEngine(self.grid)
        algo_key = ALGORITHM_MAP.get(self.algo_name, self.algo_name.lower())
        path_result, _ = engine.find_path(start, goal, algo_key)
        self.path = path_result
        
        if not self.path:
            print("No path found! Agent will fail.")
            self.path = [start] # No movement, will strictly fail
        
        return start, goal

    def add_agent(self, start, goal, agent_config=None):
        """Add an agent to the scene. 
           agent_config: dict with keys 'algo_name', 'shape', 'color'
        """
        # Default/Legacy fallback
        shape = self.agent_shape
        algo = self.algo_name
        color = AGENT_SETTINGS["colors"].get(shape, (0.0, 1.0, 1.0))
        
        if agent_config:
            shape = agent_config.get("shape", shape)
            algo = agent_config.get("algo_name", algo)
            color = AGENT_SETTINGS["colors"].get(shape, color)
            
        # Recalculate path for this agent
        engine = PathfindingEngine(self.grid)
        t0 = time.time()
        path, nodes_explored = engine.find_path(start, goal, algo)
        execution_time = (time.time() - t0) * 1000 # ms
        
        if not path:
             # Logic for failure: Empty path or just start pos
             path = [start]
             
        new_agent = Agent(
            start=start,
            goal=goal,
            path=path,
            speed=AGENT_SETTINGS["speed"],
            color=color,
            shape_type=shape,
            trail_length=AGENT_SETTINGS["trail_length"],
            algo_name=algo,
            execution_time=execution_time,
            nodes_explored=nodes_explored
        )
        
        self.agents.append(new_agent)
        
        # Maintain legacy single-agent reference if this is the first one
        if len(self.agents) == 1:
            self.agent = new_agent
            self.path = path # Legacy path ref
            
        return new_agent

    def _create_agent(self, start, goal):
        """Legacy wrapper for add_agent"""
        return self.add_agent(start, goal)

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
        """Dynamic camera to keep all active agents in view"""
        if not self.agents: return
        
        # 1. Calculate Centroid (Average Position)
        sum_x = sum_y = sum_z = 0
        count = 0
        
        # Find min/max bounds for zoom
        min_x, max_x = float('inf'), float('-inf')
        min_z, max_z = float('inf'), float('-inf')
        
        for agent in self.agents:
            wx = (agent.position[0] - self.grid_size // 2) * self.cell_size
            wy = agent.position[1]
            wz = (agent.position[2] - self.grid_size // 2) * self.cell_size
            
            sum_x += wx
            sum_y += wy
            sum_z += wz
            
            min_x = min(min_x, wx)
            max_x = max(max_x, wx)
            min_z = min(min_z, wz)
            max_z = max(max_z, wz)
            count += 1
            
        if count == 0: return
        
        # Centroid
        target_x = sum_x / count
        target_y = sum_y / count
        target_z = sum_z / count
        
        # 2. Calculate Zoom (Spread)
        spread_x = max_x - min_x
        spread_z = max_z - min_z
        max_spread = max(spread_x, spread_z)
        
        # Base distance + spread factor
        base_dist = 30.0 # Closer standard view
        zoom_factor = 0.8 # Tighter fit
        
        target_dist = base_dist + (max_spread * zoom_factor) + self.zoom_offset
        target_dist = min(200.0, max(15.0, target_dist)) # Wider clamp, but allow close-up
        
        # Smooth transition
        smooth = 0.05
        self.camera.target = [
            self.camera.target[0] * (1 - smooth) + target_x * smooth,
            self.camera.target[1] * (1 - smooth) + target_y * smooth,
            self.camera.target[2] * (1 - smooth) + target_z * smooth
        ]
        
        # Smoothly adjust distance
        self.camera.distance = self.camera.distance * (1 - smooth) + target_dist * smooth

    def _setup_view(self):
        """Setup OpenGL view matrix (shared)"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width / self.height, 0.1, 500.0) # Increased zFar to prevent clipping
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
        """Render agents, goals and paths (shared)"""
        # Coverage
        self.path_renderer.draw_coverage(self.agents)
        
        # Path & History
        glDisable(GL_LIGHTING)
        for agent in self.agents:
            self.path_renderer.draw_path(agent)
            self.path_renderer.draw_history(agent)
        glEnable(GL_LIGHTING)
        
        # Goal (Draw for all agents, though likely shared)
        # Using set to avoid drawing same goal multiple times if identical? 
        # For now, simplistic loop (goals might be different in future)
        for agent in self.agents:
            if not agent.arrived:
                glDisable(GL_LIGHTING)
                self.goal_renderer.draw_goal(agent)
                glEnable(GL_LIGHTING)
        
        # Agents
        for agent in self.agents:
            self.agent_renderer.draw_agent(agent, agent.shape_type)

    def _check_victory(self):
        """Check if agents reached goal OR failed"""
        all_finished = True
        for agent in self.agents:
            if agent.arrived:
                if not hasattr(agent, '_victory_printed'):
                    print(f"🎉 Agent ({agent.algo_name}) reached goal! Steps: {agent.steps_taken}, Nodes Explored: {agent.nodes_explored}, Time: {agent.travel_time:.2f}s")
                    agent._victory_printed = True
            elif agent.stuck:
                if not hasattr(agent, '_failure_printed'):
                    print(f"❌ Agent ({agent.algo_name}) FAILED. Steps: {agent.steps_taken}, Nodes Explored: {agent.nodes_explored}, Time: {agent.travel_time:.2f}s")
                    agent._failure_printed = True
            else:
                all_finished = False
        
        if all_finished and self.agents:
            if not hasattr(self, '_all_finished_printed'):
                print("🏁 Consensus: All agents have finished (Success or Fail).")
                self._all_finished_printed = True
                self.is_finished = True

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