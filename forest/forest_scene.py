"""
Forest Scene - Main Game Scene
Updated to be the primary scene (Scene subclass) for the Forest Maze application.
Integrates Fog, Slow Zones, Movable Objects, and Audio.
"""

import math
import random
import time
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

from core.Scene import Scene
from core.Agent import Agent
from core.PathfindingEngine import PathfindingEngine
from rendering.AgentRender import AgentRender
from rendering.GoalRender import GoalRender
from rendering.PathRender import PathRender  # Re-using standard path render for now
from ui.CameraController import CameraController

# Forest specific modules
# from .maze_generator import ForestMazeGenerator # Removed unused
from .environment_objects import EnvironmentObjectManager, render_grass_floor_at
from .particles import FireflyParticleSystem
from .audio_system import AudioSystem
from .slow_zones import SlowZoneManager
from .fog import FogSystem
from .movable_objects import MovableObjectManager


class ForestScene(Scene):
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
        
        # Subsystems
        self.maze_generator = None # Initialized in initialize()
        self.env_manager = EnvironmentObjectManager(self.grid_size, self.cell_size)
        self.audio_system = AudioSystem(assets_dir="assets/audio")
        self.slow_zone_manager = SlowZoneManager()
        self.fog_system = FogSystem(fog_color=(0.0, 0.0, 0.0), fog_density=0.20) # Pitch black fog, increased density
        self.fireflies = FireflyParticleSystem(self.grid_size, self.cell_size, num_fireflies=30)
        self.movables = MovableObjectManager(self.grid_size, self.cell_size)
        
        # Renderers
        self.agent_renderer = AgentRender(cell_size=self.cell_size, grid_size=self.grid_size)
        self.goal_renderer = GoalRender(cellSize=self.cell_size, grid_size=self.grid_size)
        # Using a simpler path renderer or None if we want 'exploration' mode? 
        # Using standard for now so path is visible.
        self.path_renderer = None 

        self.grid = None
        self.path = None
        self.last_player_cell = None

    def initialize(self, agent_shape="sphere_droid", algo_name="astar"):
        self._init_opengl()
        
        # Generate Maze
        # Core Maze Generation (Same logic as Space Theme for consistency)
        # Using GridGenerator (random scatter) instead of DFS Forest Generator
        from core.GridGenerator import GridGenerator
        self.maze_generator = GridGenerator(self.grid_size, obstacle_prob=0.6)
        self.grid = self.maze_generator.generate()
        
        # Setup Start/Goal
        start = (0, 0)
        goal = (self.grid_size-1, self.grid_size-1)
        self.grid[start[1]][start[0]] = 0
        self.grid[goal[1]][goal[0]] = 0
        
        # Pathfinding (for Agent)
        engine = PathfindingEngine(self.grid)
        
        # Map menu algo name to engine key if needed
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
            
        # Manually generate auxiliary zones since GridGenerator doesn't provide them
        # CRITICAL: We must NOT place objects on the calculated path, or the agent gets stuck!
        # "iwant to always always have correct path always"
        path_set = set(self.path)
        forest_zones = []
        slow_zones = []
        
        # Populate zones based on open spaces, EXCLUDING path
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x] == 0:
                    if (x, y) not in path_set:
                        if random.random() < 0.1: # 10% chance for forest props
                            forest_zones.append((x, y))
                        if random.random() < 0.05: # 5% chance for slow zone
                            slow_zones.append((x, y))
            
        # Agent Colors (Matched with Space Theme)
        shape_colors = {
            "sphere_droid": (0.0, 1.0, 1.0),   # Cyan
            "robo_cube": (1.0, 0.3, 0.3),      # Red/Orange
            "mini_drone": (0.2, 0.7, 0.3),     # Green
            "crystal_alien": (0.8, 0.3, 1.0)   # Purple
        }
        agent_color = shape_colors.get(agent_shape, (0.0, 1.0, 0.5))

        # Initialize Agent
        self.agent = Agent(
            start, goal, self.path, 
            speed=2.0, 
            color=agent_color, # Dynamic color
            shape_type=agent_shape,
            trail_length=20
        )
        
        # Initialize Path Renderer
        self.path_renderer = PathRender(
            cell_size=self.cell_size,
            grid_size=self.grid_size,
            # Simple ground height function for path renderer
            ground_sampler=lambda x,z: 0.0 
        )

        # Environment Setup
        self.env_manager.generate_trees_from_grid(self.grid)
        self.slow_zone_manager.create_from_grid_positions(slow_zones, self.grid_size, self.cell_size)
        
        # Add some movable logs in open areas (simple random placement in forest zones)
        for fx, fy in forest_zones:
            if random.random() < 0.3: # User Request: "add more rocks" (Increased from 0.15 to 0.3)
                # World coords
                wx = (fx - self.grid_size//2) * self.cell_size
                wz = (fy - self.grid_size//2) * self.cell_size
                # Favor rocks: > 0.3 was 70% logs. Now < 0.7 is 70% rocks.
                self.movables.add_object(wx, wz, "rock" if random.random() < 0.7 else "log")

        # Audio
        self._setup_audio()

        # Camera
        self.camera = CameraController(distance=10, angle_x=45, angle_y=30)
        
        self.start_time = time.time()
        self.game_active = True
        
        print("[FOREST] Initialized. Welcome to the Dark Forest.")
        return self.agent

    def _init_opengl(self):
        glClearColor(0.0, 0.0, 0.0, 1.0) # Pure Black BG (User Request: fix "light in out")
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Forest Lighting (Dim, Directional)
        glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 20.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.15, 0.1, 1.0])  # Greenish ambient
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.6, 0.6, 0.5, 1.0]) # Moon/Sun light

        # Enable Fog
        self.fog_system.enable()

        # Generate Ground Patches (Deterministic)
        self.ground_patches = []
        # Generate Ground Patches (Deterministic)
        self.ground_patches = []
        # Generate Ground Patches (Deterministic per session, random placement "random places")
        self.ground_patches = []
        rng = random.Random() # No seed -> truly random each run
        for _ in range(12): # Increased from 5 to 12 for "random places" density 
            # Ensure patches stay strictly inside the grid (Extra safe)
            # Circle radius
            radius = rng.uniform(2.5, 4.0) # slightly random size
            
            # Center ensure it's away from edges by at least radius
            cx_min = 2 + int(radius)
            cx_max = self.grid_size - 2 - int(radius)
            
            if cx_max > cx_min:
                cx = rng.randint(cx_min, cx_max)
                cy = rng.randint(cx_min, cx_max)
                
                # Convert to world coords
                wx = (cx - self.grid_size//2) * self.cell_size
                wz = (cy - self.grid_size//2) * self.cell_size
                self.ground_patches.append((wx, wz, radius))

    def _setup_audio(self):
        # We can add sound zones like the original code
        # Center of map wind
        self.audio_system.add_sound_zone("center_wind", (0, 5, 0), "wind", volume=0.3, radius=20.0)

    def update(self, dt):
        if not self.game_active: return
        
        # Standard Movement (User Requirement: "moves in his way like in standerd mode")
        # Removing slow zone speed penalty for agent movement itself
        self.agent.update(dt)
        self.agent_renderer.update_time(dt)
        
        # Update Camera
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.camera.angle_x -= 60 * dt
        if keys[pygame.K_RIGHT]: self.camera.angle_x += 60 * dt
        if keys[pygame.K_UP]: self.camera.angle_y += 60 * dt
        if keys[pygame.K_DOWN]: self.camera.angle_y -= 60 * dt
        self.camera.angle_y = max(10, min(89, self.camera.angle_y)) # Keep camera above ground mostly
        
        wx = (self.agent.position[0] - self.grid_size//2) * self.cell_size
        wy = self.agent.position[1]
        wz = (self.agent.position[2] - self.grid_size//2) * self.cell_size
        
        # Camera Follow Smoothly
        self.camera.target = [
            self.camera.target[0] * 0.9 + wx * 0.1,
            self.camera.target[1] * 0.9 + wy * 0.1,
            self.camera.target[2] * 0.9 + wz * 0.1
        ]
        
        # Check Movable collisions
        self.movables.check_collisions(wx, wz)
        self.movables.update(dt, self.grid) # Need grid for wall collisions
        
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
            # Check if in slow zone -> 'squish' sound? or standard footstep
            # For simplicity just play footstep
            self.audio_system.play_footstep()

        # Update Fog time of day
        current_time = time.time() - self.start_time
        day_cycle = (current_time % 120) / 120.0 # 2 minute day cycle
        self.fog_system.update_time_of_day(day_cycle)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Setup Camera
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width / self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        pos = self.camera.calculate_camera_position()
        target = self.camera.target
        gluLookAt(pos[0], pos[1], pos[2], target[0], target[1], target[2], 0, 1, 0)
        
        # Render Sky/Fog Quad? 
        # Background is cleared color, so we rely on fog.
        
        # Render Floor (Detailed Forest Floor)
        self._render_detailed_floor()
        
        # Render Environment (Trees)
        self.env_manager.render_all()
        
        # Render Movables
        self.movables.render()
        
        # Render Slow Zones (Visual indicator - slight brown overlay)
        self.slow_zone_manager.render_zones()
        
        # Render Path
        glDisable(GL_LIGHTING)
        if self.path_renderer:
            self.path_renderer.draw_path(self.agent)
            self.path_renderer.draw_history(self.agent)
        glEnable(GL_LIGHTING)

        # Render Agent
        self.agent_renderer.draw_agent(self.agent, self.agent.shape_type)
        
        # Render Goal
        if not self.agent.arrived:
            self.goal_renderer.draw_goal(self.agent)
            
        # Particles (Fireflies)
        self.fireflies.render()

    def _render_detailed_floor(self):
        """Render grass tiles for the floor"""
        # We can use the logic from render_grass_floor_at
        # Optimization: Display List this if too slow. 
        # But for 25x25 it might be heavy to draw individual blades.
        # Let's draw a base big quad plane first, then some details.
        
        # Plain Ground Rendering (User Request: "plain pls")
        # Single large green field
        glDisable(GL_LIGHTING)
        # glDisable(GL_FOG) # User Request: "add fog" -> Re-enable fog for better atmosphere
        
        half_world = self.grid_size * self.cell_size / 2.0
        
        half_world = self.grid_size * self.cell_size / 2.0
        
        # 1. Main Green Field
        glColor3f(0.05, 0.35, 0.05) # Solid Green
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-half_world, -0.1, -half_world)
        glVertex3f(half_world, -0.1, -half_world)
        glVertex3f(half_world, -0.1, half_world)
        glVertex3f(-half_world, -0.1, half_world)
        glEnd()
        
        # 2. "Some area in dart" (Dark patches) - Drawn as overlays
        # Using pre-calculated patches to avoid per-frame random changes and flickering
        glColor3f(0.15, 0.12, 0.08) # Dark Dirt
        
        # Draw Circles
        for (wx, wz, radius) in self.ground_patches:
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(wx, -0.08, wz) # Center
            num_segments = 20
            for i in range(num_segments + 1):
                theta = 2.0 * math.pi * float(i) / float(num_segments)
                dx = radius * math.cos(theta)
                dz = radius * math.sin(theta)
                glVertex3f(wx + dx, -0.08, wz + dz)
            glEnd()
        
        glEnable(GL_LIGHTING)

    def cleanup(self):
        self.audio_system.cleanup()
