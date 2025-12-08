"""
Forest Scene with Enhanced Audio
Main scene controller that integrates all forest systems.
Uses standard Agent, PathfindingEngine, and PathRender.
"""

import random
from typing import List, Tuple, Dict
from OpenGL.GL import *
from OpenGL.GLU import *

from .maze_generator import ForestMazeGenerator
from .environment_objects import render_tree_at, EnvironmentObjectManager
from .particles import FireflyParticleSystem
from .audio_system import AudioSystem
from .slow_zones import SlowZoneManager


class ForestScene:
    """
    Main forest maze scene controller with enhanced audio.
    """
    
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0, 
                 config: Dict = None):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.config = config or self._default_config()
        
        # Core systems
        self.maze_generator = ForestMazeGenerator(grid_size, 0.25)
        self.grid = None
        self.forest_zones = []
        self.slow_zone_positions = []
        
        # Enhanced subsystems
        self.environment_manager = EnvironmentObjectManager(grid_size, cell_size)
        self.firefly_system = FireflyParticleSystem(grid_size, cell_size, 
        self.config.get('num_fireflies', 15))
        self.audio_system = AudioSystem(assets_dir="assets/audio")
        self.slow_zone_manager = SlowZoneManager()
        
        # Player
        self.player = None
        
        # State
        self._last_player_cell = None
        self.debug_render = False
        
        print("[SCENE] Forest scene initialized with enhanced audio")
    
    def _default_config(self) -> Dict:
        """Return enhanced configuration"""
        return {
            'grid_size': 25,
            'cell_size': 1.0,
            'forest_density': 0.3,
            'num_fireflies': 15,
            'slow_zone_factor': 0.1,
            'num_slow_zones': 10,
            'audio_volume': 1,
        }
    
    def initialize(self, pathfinding_engine, start: Tuple[int, int] = (0, 0), 
                   goal: Tuple[int, int] = None, agent_color: Tuple[float, float, float] = (0.0, 1.0, 1.0),
                   algo: str = 'astar'):
        """Initialize scene with maze and audio, using standard Agent and PathfindingEngine"""
        if goal is None:
            goal = (self.grid_size - 1, self.grid_size - 1)
        
        # Generate maze
        max_retries = 5
        path = None
        for attempt in range(max_retries):
            self.grid, self.forest_zones, self.slow_zone_positions = self.maze_generator.generate()
            
            if pathfinding_engine is None:
                try:
                    from PathfindingEngine import PathfindingEngine
                except Exception:
                    from ..PathfindingEngine import PathfindingEngine
                pathfinding_engine = PathfindingEngine(self.grid)
            else:
                pathfinding_engine.grid = self.grid
            
            # Check start/goal validity
            start_cell_value = self.grid[start[1]][start[0]]
            goal_cell_value = self.grid[goal[1]][goal[0]]
            
            if start_cell_value == 1 or goal_cell_value == 1:
                if attempt < max_retries - 1:
                    continue
                else:
                    start = (1, 1)
                    goal = (self.grid_size - 2, self.grid_size - 2)
            
            # Find path using standard algorithm
            path = pathfinding_engine.find_path(start, goal, algo)
            if path:
                print(f"[SCENE] Maze generated with path length: {len(path)}")
                break
            elif attempt == max_retries - 1:
                path = [start, goal]
        
        # Initialize subsystems
        self.environment_manager.generate_trees_from_grid(self.grid)
        self.slow_zone_manager.create_from_grid_positions(
            self.slow_zone_positions,
            self.grid_size,
            self.cell_size,
            self.config.get('slow_zone_factor', 0.4)
        )
        
        # Setup audio
        self._setup_audio_zones()
        
        # Create player using standard Agent class
        try:
            from Agent import Agent
        except ImportError:
            from ..Agent import Agent
        
        self.player = Agent(start, goal, path, speed=2.0, color=agent_color)
        
        print(f"[SCENE] Scene initialized with {len(self.environment_manager.trees)} trees")
        return self.player
    
    def _setup_audio_zones(self):
        """Setup positional audio zones"""
        half_grid = self.grid_size / 2 * self.cell_size
        
        # Wind zones
        self.audio_system.add_sound_zone(
            'wind_north',
            (0, 3, -half_grid * 0.8),
            sound_type='wind',
            volume=0.4,
            radius=20.0
        )
        
        self.audio_system.add_sound_zone(
            'wind_south',
            (0, 3, half_grid * 0.8),
            sound_type='wind',
            volume=0.4,
            radius=20.0
        )
        
        # Bird zones
        self.audio_system.add_sound_zone(
            'birds_east',
            (half_grid * 0.7, 4, 0),
            sound_type='birds',
            volume=0.3,
            radius=15.0
        )
        
        self.audio_system.add_sound_zone(
            'birds_west',
            (-half_grid * 0.7, 4, 0),
            sound_type='birds',
            volume=0.3,
            radius=15.0
        )
        
        print("[AUDIO] Audio zones setup complete")
    
    def world_to_grid(self, pos: Tuple[float, float, float]) -> Tuple[int, int]:
        """Convert world position to grid coordinates"""
        xw, yw, zw = pos
        gx = int(round(xw / self.cell_size + self.grid_size // 2))
        gy = int(round(zw / self.cell_size + self.grid_size // 2))
        return gx, gy
    
    def update(self, dt: float):
        """Update all scene systems"""
        if self.player:
            # Smooth player update
            old_pos = self.player.position
            self.player.update(dt)
            new_pos = self.player.position
            
            # Footstep sounds
            curr_cell = self.world_to_grid(new_pos)
            if curr_cell != self._last_player_cell:
                self._last_player_cell = curr_cell
                self.audio_system.play_global_sound('footstep', volume=0.5)
                
                # Random bird chirps
                if random.random() < 0.03:
                    self.audio_system.play_global_sound('birds', volume=0.3)
        
        # Update other systems
        self.firefly_system.update(dt)
        self.audio_system.update(dt)
        
        # Update positional audio for player
        if self.player:
            self.audio_system.update_positional_audio(self.player.position)
    
    def render(self):
        """Render entire scene"""
        self._render_floor()
        self.environment_manager.render_all()
        
        if self.debug_render:
            self.slow_zone_manager.render_zones()
        
        self.firefly_system.render()
    
    def _render_floor(self):
        """Render detailed forest floor"""
        half = self.grid_size / 2 * self.cell_size
        
        glDisable(GL_LIGHTING)
        glColor3f(0.45, 0.35, 0.25)
        
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-half, -0.15, -half)
        glVertex3f(half, -0.15, -half)
        glVertex3f(half, -0.15, half)
        glVertex3f(-half, -0.15, half)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.2, 0.5, 0.2, 1.0))
        
        tile_size = 2.0
        for x in range(int(-half), int(half), int(tile_size)):
            for z in range(int(-half), int(half), int(tile_size)):
                glBegin(GL_QUADS)
                r = 0.2 + random.uniform(-0.05, 0.05)
                g = 0.5 + random.uniform(-0.05, 0.05)
                b = 0.2 + random.uniform(-0.05, 0.05)
                glColor3f(r, g, b)
                glNormal3f(0, 1, 0)
                
                y1 = random.uniform(0, 0.02)
                y2 = random.uniform(0, 0.02)
                y3 = random.uniform(0, 0.02)
                y4 = random.uniform(0, 0.02)
                
                glVertex3f(x, y1, z)
                glVertex3f(x + tile_size, y2, z)
                glVertex3f(x + tile_size, y3, z + tile_size)
                glVertex3f(x, y4, z + tile_size)
                glEnd()
    
    def render_player(self):
        """Render player with glow effect (standard 3D sphere)"""
        if not self.player:
            return
        
        px, py, pz = self.player.position
        
        glPushMatrix()
        glTranslatef(px, py + 0.25, pz)
        
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        glColor3f(*self.player.color)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, 0.25, 24, 24)
        gluDeleteQuadric(quad)
        
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*self.player.color, 0.2)
        
        quad_glow = gluNewQuadric()
        gluSphere(quad_glow, 0.35, 16, 16)
        gluDeleteQuadric(quad_glow)
        
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def set_debug_render(self, enabled: bool):
        self.debug_render = enabled
    
    def get_maze_data(self) -> Dict:
        return self.maze_generator.get_maze_data()
    
    def cleanup(self):
        self.audio_system.cleanup()
        print("[SCENE] Cleanup complete")
