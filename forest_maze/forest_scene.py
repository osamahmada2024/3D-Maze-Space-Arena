"""
Forest Scene
Main scene controller that integrates all forest systems.
"""

import random
import json
from typing import List, Tuple, Dict
from OpenGL.GL import *
from OpenGL.GLU import *

from .maze_generator import ForestMazeGenerator
from .environment_objects import EnvironmentObjectManager, render_tree_at
from .particles import FireflyParticleSystem
from .fog import FogSystem
from .audio_system import AudioSystem
from .slow_zones import SlowZoneManager
from .player_controller import ForestPlayerController


class ForestScene:
    """
    Main forest maze scene controller.
    Orchestrates maze generation, rendering, and all systems.
    """
    
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0, 
                 config: Dict = None):
        """
        Initialize forest scene.
        
        Args:
            grid_size: Size of maze grid
            cell_size: Size of each cell
            config: Optional configuration dictionary
        """
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.config = config or self._default_config()
        
        # Core systems
        self.maze_generator = ForestMazeGenerator(grid_size, 0.3)
        self.grid = None
        self.forest_zones = []
        self.slow_zone_positions = []
        
        # Subsystems
        self.environment_manager = EnvironmentObjectManager(grid_size, cell_size)
        self.firefly_system = FireflyParticleSystem(grid_size, cell_size, 
                                                     self.config.get('num_fireflies', 50))
        self.fog_system = FogSystem(
            fog_color=tuple(self.config.get('fog_color', (0.2, 0.5, 0.3))),
            fog_density=self.config.get('fog_density', 0.15),
            fog_start=self.config.get('fog_start', 5.0),
            fog_end=self.config.get('fog_end', 50.0)
        )
        self.audio_system = AudioSystem()
        self.slow_zone_manager = SlowZoneManager()
        
        # Player
        self.player = None
        
        # Rendering state
        self.debug_render = False
    
    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'grid_size': 25,
            'cell_size': 1.0,
            'forest_density': 0.3,
            'num_fireflies': 50,
            'fog_color': (0.2, 0.5, 0.3),
            'fog_density': 0.15,
            'fog_start': 5.0,
            'fog_end': 50.0,
            'slow_zone_factor': 0.5,
            'num_slow_zones': 20,
            # Placement buffer (manhattan) around path/start/goal where objects won't be placed
            'placement_buffer': 2,  # Increased from 1 to 2 for safer path
            'removal_clearance': 0.25,  # Reduced from 0.35 to allow closer objects
        }
    
    def initialize(self, pathfinding_engine, start: Tuple[int, int] = (0, 0), 
                   goal: Tuple[int, int] = None, agent_color: Tuple[float, float, float] = (0.0, 1.0, 1.0),
                   algo: str = 'astar'):
        """
        Initialize the forest scene with maze and all systems.
        
        Args:
            pathfinding_engine: PathfindingEngine instance for pathfinding
            start: Starting position
            goal: Goal position (defaults to opposite corner)
            agent_color: Player color
        
        Returns:
            player: The initialized player controller
        """
        if goal is None:
            goal = (self.grid_size - 1, self.grid_size - 1)
        
        # Generate maze and ensure it has a valid path
        max_retries = 5
        path = None
        for attempt in range(max_retries):
            self.grid, self.forest_zones, self.slow_zone_positions = self.maze_generator.generate()

            # If caller didn't pass a pathfinding engine, create one now with the generated grid
            if pathfinding_engine is None:
                try:
                    from PathfindingEngine import PathfindingEngine
                except Exception:
                    from .PathfindingEngine import PathfindingEngine
                pathfinding_engine = PathfindingEngine(self.grid)
            else:
                # Update grid in existing engine
                pathfinding_engine.grid = self.grid

            # Debug: check grid at start and goal
            start_cell_value = self.grid[start[1]][start[0]]
            goal_cell_value = self.grid[goal[1]][goal[0]]
            
            # Ensure start and goal are on walkable cells (0 = walkable, 1 = wall)
            if start_cell_value == 1 or goal_cell_value == 1:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1}: Start cell={start_cell_value} or goal cell={goal_cell_value} on wall, regenerating maze...")
                    continue
                else:
                    print("ERROR: Could not generate maze with valid start/goal after retries!")
                    # Fallback: use corners that are likely walkable
                    start = (1, 1)
                    goal = (self.grid_size - 2, self.grid_size - 2)

            # Compute path using pathfinding engine
            path = pathfinding_engine.find_path(start, goal, algo)
            if path:
                print(f"[OK] Maze generated successfully with valid path (attempt {attempt + 1}, path length: {len(path)})")
                break
            else:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1}: No path found for {algo} from {start} to {goal}, regenerating maze...")
                else:
                    print("ERROR: Could not generate solvable maze after retries! Using straight line fallback.")
                    path = [start, goal]
        
        # Initialize environment objects from forest zones (trees only, no collision)
        self.environment_manager.generate_from_forest_zones(self.forest_zones)
        
        # Initialize slow zones
        self.slow_zone_manager.create_from_grid_positions(
            self.slow_zone_positions,
            self.grid_size,
            self.cell_size,
            self.config.get('slow_zone_factor', 0.5)
        )
        
        # Initialize firefly system (already done in __init__)
        
        # Initialize audio zones
        self._setup_audio_zones()
        
        # Create and return player
        self.player = ForestPlayerController(start, goal, path, 
                                            speed=3.0, color=agent_color)  # Moderate speed
        
        return self.player

    def world_to_grid(self, pos: Tuple[float, float, float]) -> Tuple[int, int]:
        """Convert world position to grid coordinates (x, y)."""
        xw, yw, zw = pos
        gx = int(round(xw / self.cell_size + self.grid_size // 2))
        gy = int(round(zw / self.cell_size + self.grid_size // 2))
        return gx, gy
    
    def _setup_audio_zones(self):
        """Set up audio zones around the forest"""
        # Add ambient wind zones
        half_grid = self.grid_size / 2 * self.cell_size
        
        self.audio_system.add_sound_zone(
            'wind_north',
            (-half_grid/2, 2, -half_grid),
            sound_type='wind'
        )
        self.audio_system.add_sound_zone(
            'wind_south',
            (-half_grid/2, 2, half_grid),
            sound_type='wind'
        )
        self.audio_system.add_sound_zone(
            'birds_east',
            (half_grid, 3, 0),
            sound_type='birds'
        )
        self.audio_system.add_sound_zone(
            'birds_west',
            (-half_grid, 3, 0),
            sound_type='birds'
        )
    
    def update(self, dt: float):
        """
        Update all scene systems.
        
        Args:
            dt: Delta time in seconds
        """
        if self.player:
            self.player.update(dt, self.environment_manager, self.slow_zone_manager)

            # Determine grid cell and emit footstep when entering a new cell
            curr_cell = self.world_to_grid(self.player.get_position())
            last = getattr(self, '_last_player_cell', None)
            if curr_cell != last:
                self._last_player_cell = curr_cell
                # Footstep sound selection
                if tuple(curr_cell) in set(self.forest_zones):
                    self.audio_system.play_footstep('grass')
                else:
                    self.audio_system.play_footstep('stone')
                # Occasional bird chirp
                if random.random() < 0.02:
                    self.audio_system.play_bird_chirp()

        self.firefly_system.update(dt)
        self.audio_system.update(dt)

        if self.player:
            self.audio_system.update_positional_audio(self.player.get_position())
    
    def render(self):
        """Render entire scene"""
        # Enable fog
        self.fog_system.enable()
        
        # Render grid
        self._render_grid()
        
        # Render obstacles (walls)
        self._render_obstacles()
        
        # Render environment objects
        self.environment_manager.render_all()
        
        # Disable fog for particle effects
        self.fog_system.disable()
        
        # Render particles
        self.firefly_system.render()
        
        # Debug rendering
        if self.debug_render:
            self.slow_zone_manager.render_zones()
    
    def render_player(self):
        """Render the player"""
        if not self.player:
            return
        
        px, py, pz = self.player.get_position()
        
        glPushMatrix()
        glTranslatef(px - self.grid_size // 2, py, pz - self.grid_size // 2)
        
        # Main solid sphere
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        glColor3f(*self.player.color)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, 0.25, 24, 24)
        gluDeleteQuadric(quad)
        
        # Glow effect
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*self.player.color, 0.15)
        
        quad_glow = gluNewQuadric()
        gluSphere(quad_glow, 0.4, 16, 16)
        gluDeleteQuadric(quad_glow)
        
        # Restore states
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
    
    def _render_grid(self):
        """Render grid floor using 3DS model if available, else grass"""
        grass_model = None
        try:
            from .environment_objects import get_grass_model
            grass_model = get_grass_model()
        except:
            pass
        
        glDisable(GL_LIGHTING)
        
        if grass_model and hasattr(grass_model, 'meshes') and grass_model.meshes:
            # Render grass using 3DS model
            glEnable(GL_LIGHTING)
            half = self.grid_size / 2 * self.cell_size
            grass_model.render(0, -0.1, 0, scale=self.grid_size * 0.4)
            glDisable(GL_LIGHTING)
        else:
            # Fallback to procedural grass
            # Draw grass floor
            glColor3f(0.2, 0.6, 0.2)  # Green grass color
            half = self.grid_size / 2 * self.cell_size
            
            glBegin(GL_QUADS)
            glVertex3f(-half, -0.01, -half)
            glVertex3f(half, -0.01, -half)
            glVertex3f(half, -0.01, half)
            glVertex3f(-half, -0.01, half)
            glEnd()

            # Draw subtle grid lines (light gray)
            glColor3f(0.15, 0.4, 0.15)  # Darker green for lines
            glLineWidth(0.5)
            glBegin(GL_LINES)
            for i in range(-self.grid_size//2, self.grid_size//2 + 1):
                x = i * self.cell_size
                glVertex3f(x, 0, -half)
                glVertex3f(x, 0, half)
                glVertex3f(-half, 0, x)
                glVertex3f(half, 0, x)
            glEnd()

            # Draw outer frame
            glColor3f(0.1, 0.5, 0.1)  # Even darker green
            glLineWidth(2.0)
            glBegin(GL_LINE_LOOP)
            glVertex3f(-half, 0, -half)
            glVertex3f(half, 0, -half)
            glVertex3f(half, 0, half)
            glVertex3f(-half, 0, half)
            glEnd()
        
        glEnable(GL_LIGHTING)
    
    def _render_obstacles(self):
        """Render maze obstacles using 3DS tree models or procedural fallback"""
        tree_model = None
        try:
            from .environment_objects import get_tree_model
            tree_model = get_tree_model()
        except:
            pass
        
        glEnable(GL_LIGHTING)
        
        for y in range(self.grid_size):
            for x in range(len(self.grid[0])):
                if self.grid[y][x] == 1:  # Wall = Tree obstacle
                    wx = (x - self.grid_size // 2) * self.cell_size
                    wz = (y - self.grid_size // 2) * self.cell_size
                    
                    if tree_model and hasattr(tree_model, 'meshes') and tree_model.meshes:
                        # Use 3DS model
                        tree_model.render(wx, 0, wz, scale=1.0)
                    else:
                        # Fallback to procedural tree
                        render_tree_at(wx, 0, wz, scale=1.0)
    
    def _draw_cube(self, size: float):
        """Draw a cube"""
        s = size / 2.0
        
        glBegin(GL_QUADS)
        
        # Front face
        glNormal3f(0, 0, 1)
        glVertex3f(-s, -s, s)
        glVertex3f(s, -s, s)
        glVertex3f(s, s, s)
        glVertex3f(-s, s, s)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, -s, -s)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(-s, s, -s)
        glVertex3f(-s, s, s)
        glVertex3f(s, s, s)
        glVertex3f(s, s, -s)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-s, -s, -s)
        glVertex3f(s, -s, -s)
        glVertex3f(s, -s, s)
        glVertex3f(-s, -s, s)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(s, -s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, s, s)
        glVertex3f(s, -s, s)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, -s, s)
        glVertex3f(-s, s, s)
        glVertex3f(-s, s, -s)
        
        glEnd()
    
    def set_debug_render(self, enabled: bool):
        """Enable/disable debug rendering"""
        self.debug_render = enabled
    
    def get_maze_data(self) -> Dict:
        """Get maze data for export"""
        return self.maze_generator.get_maze_data()
    
    def cleanup(self):
        """Clean up resources"""
        self.audio_system.cleanup()