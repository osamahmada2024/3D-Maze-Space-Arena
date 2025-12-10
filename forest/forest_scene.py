"""
Forest Scene - Main Game Scene
Updated to be the primary scene (Scene subclass) for the Forest Maze application.
Integrates Fog, Slow Zones, Movable Objects, and Audio.
Now with Lucky Blocks, Power-ups, Black Holes, and Player Logic Integration
"""

import math
import time
import random
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from datetime import datetime, timedelta

from core.Scene import Scene
from core.Agent import Agent
from rendering.GoalRender import GoalRender
from rendering.AgentRender import AgentRender
from ui.CameraController import CameraController
from core.PathfindingEngine import PathfindingEngine
from rendering.PathRender import PathRender  # Re-using standard path render for now

from game_logic.Player import Player, PowerUpType
from features.lucky_blocks import LuckyBlockTeleportSystem, EffectType, GameFlowIntegration

from .fog import FogSystem
from .audio_system import AudioSystem
from .slow_zones import SlowZoneManager
from .particles import FireflyParticleSystem
from .movable_objects import MovableObjectManager
# Forest specific modules
# from .maze_generator import ForestMazeGenerator # Removed unused
from .environment_objects import EnvironmentObjectManager, render_grass_floor_at


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
        
        # Player Logic Integration
        self.player = None  # Player instance for power-up management
        self.round_counter = 0  # For 3-round variable system
        self.round_max = 3  # 3 rounds
        
        # Subsystems
        self.maze_generator = None # Initialized in initialize()
        self.env_manager = EnvironmentObjectManager(self.grid_size, self.cell_size)
        self.audio_system = AudioSystem(assets_dir="assets/audio")
        self.slow_zone_manager = SlowZoneManager()
        self.fog_system = FogSystem(fog_color=(0.0, 0.0, 0.0), fog_density=0.20) # Pitch black fog, increased density
        self.fireflies = FireflyParticleSystem(self.grid_size, self.cell_size, num_fireflies=30)
        self.movables = MovableObjectManager(self.grid_size, self.cell_size)
        
        # Lucky Blocks & Teleports System
        self.lucky_system = None  # Initialized in initialize()
        self.game_flow = None  # Initialized in initialize()
        
        # Black Holes System
        self.black_holes = []  # List of black hole positions
        self.black_hole_freeze_radius = 3.0  # Detection radius for freeze effect
        
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
        black_hole_positions = []
        
        # Populate zones based on open spaces, EXCLUDING path
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x] == 0:
                    if (x, y) not in path_set:
                        if random.random() < 0.1: # 10% chance for forest props
                            forest_zones.append((x, y))
                        if random.random() < 0.05: # 5% chance for slow zone
                            slow_zones.append((x, y))
                        if random.random() < 0.03: # 3% chance for black hole (freezing zone)
                            black_hole_positions.append((x, y))
            
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
        
        # Initialize Player Logic
        self.player = Player(player_id="player_1", is_ai=False)
        self.player.start_time = datetime.now()
        self.round_counter = random.randint(1, self.round_max)  # Random initial round (1-3)
        
        # Initialize Lucky Blocks & Teleport System
        # Calculate walkable positions for distribution
        walkable_positions = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x] == 0 and (x, y) not in path_set:
                    wx = (x - self.grid_size//2) * self.cell_size
                    wz = (y - self.grid_size//2) * self.cell_size
                    walkable_positions.append((wx, 0.0, wz))
        
        # Create lucky block system
        maze_bounds = (
            -self.grid_size * self.cell_size / 2.0,
            self.grid_size * self.cell_size / 2.0,
            -self.grid_size * self.cell_size / 2.0,
            self.grid_size * self.cell_size / 2.0
        )
        self.lucky_system = LuckyBlockTeleportSystem(maze_bounds, num_lucky_blocks=8, num_teleports=4)
        self.game_flow = GameFlowIntegration(self.lucky_system)
        
        if len(walkable_positions) >= 12:  # Need at least 8 + 4
            self.lucky_system.initialize_distribution(walkable_positions)
        
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
        
        # Initialize Black Holes (store world coordinates)
        for bx, by in black_hole_positions:
            wx = (bx - self.grid_size//2) * self.cell_size
            wz = (by - self.grid_size//2) * self.cell_size
            self.black_holes.append((wx, 0.0, wz))
        
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
        
        print("[FOREST] Initialized with Lucky Blocks, Power-ups, Black Holes, and Player Logic.")
        print(f"[FOREST] Black Holes: {len(self.black_holes)}, Lucky Blocks: 8, Teleports: 4")
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
        
        # Update Player power-up effects (duration tracking)
        if self.player:
            self.player.reset_power_up_effects()
        
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
        
        player_world_pos = (wx, wy, wz)
        
        # ============ Check Black Hole Collision (Freeze Effect) ============
        self._check_black_hole_collision(player_world_pos)
        
        # ============ Check Lucky Block Collision ============
        if self.lucky_system:
            effect = self.lucky_system.check_lucky_block_collision(
                player_world_pos, 
                self.player.id if self.player else "player_1",
                collision_radius=1.5
            )
            if effect:
                self._handle_lucky_block_effect(effect)
        
        # ============ Update Round Counter on Movement ============
        # Change random rounds (1-3) on each movement
        if (int(self.agent.position[0]), int(self.agent.position[2])) != self.last_player_cell:
            self.round_counter = random.randint(1, self.round_max)
            self.last_player_cell = (int(self.agent.position[0]), int(self.agent.position[2]))
        
        # ============ Check Teleport Proximity ============
        if self.lucky_system:
            nearby_teleport = self.lucky_system.check_teleport_proximity(player_world_pos, proximity_radius=2.0)
            if nearby_teleport:
                # Could trigger teleport interaction here
                pass
        
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
        self.audio_system.update_positional_audio(player_world_pos)
        
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
        
        # Update Lucky Block round counter
        if self.lucky_system:
            self.lucky_system.update_round()
    
    def _check_black_hole_collision(self, player_pos):
        """Check if player is in black hole freeze zone and apply freeze effect"""
        for bh_pos in self.black_holes:
            distance = self._calculate_distance(player_pos, bh_pos)
            if distance <= self.black_hole_freeze_radius:
                # Apply freeze effect from black hole
                if self.player and not self.player.is_frozen:
                    self.player.apply_power_up_effect(PowerUpType.FREEZE, duration_seconds=3)
                    print(f"[BLACK HOLE] Player frozen! Distance: {distance:.2f}")
                break
    
    def _handle_lucky_block_effect(self, effect):
        """Handle the effect from collected lucky block"""
        if not self.player:
            return
        
        # Map EffectType to PowerUpType
        effect_mapping = {
            EffectType.FREEZE: PowerUpType.FREEZE,
            EffectType.BOOST: PowerUpType.BOOST,
            EffectType.SKIP: PowerUpType.SKIP,
            EffectType.STOP_TWO_ROUNDS: PowerUpType.STOP,
        }
        
        power_up_type = effect_mapping.get(effect)
        if power_up_type:
            duration = 5 if effect in [EffectType.BOOST, EffectType.FREEZE] else 3
            self.player.apply_power_up_effect(power_up_type, duration_seconds=duration)
            
            # Play sound
            sound = self.lucky_system.get_lucky_block_sound()
            if sound:
                self.audio_system.play_effect(sound)
            
            print(f"[LUCKY BLOCK] Player received: {effect.value}")
            
            # Apply speed boost if applicable
            if effect == EffectType.BOOST:
                self.agent.speed *= 1.5
    
    def _calculate_distance(self, pos1, pos2):
        """Calculate 3D Euclidean distance between two positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        return (dx**2 + dy**2 + dz**2) ** 0.5

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
        
        # Render Black Holes (Visual representation)
        self._render_black_holes()
        
        # Render Lucky Blocks (Beautiful visual effects)
        self._render_lucky_blocks()
        
        # Render Teleports
        self._render_teleports()
        
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

    def _render_black_holes(self):
        """Render Black Holes as dark swirling voids with freeze effect"""
        glDisable(GL_LIGHTING)
        
        current_time = time.time()
        
        for bh_pos in self.black_holes:
            wx, wy, wz = bh_pos
            
            # Animate black hole - pulsing/rotating effect
            pulse = 0.5 + 0.3 * math.sin(current_time * 3.0)  # Pulsing effect
            rotation = current_time * 100.0  # Rotating animation
            
            # Draw outer glow (dark red/purple haze indicating freeze danger)
            glPushMatrix()
            glTranslatef(wx, wy + 0.2, wz)
            
            # Outer glow ring
            glColor4f(0.3, 0.0, 0.3, 0.3)  # Purple glow
            glBegin(GL_LINE_LOOP)
            segments = 32
            for i in range(segments):
                theta = 2.0 * math.pi * i / segments
                x = (self.black_hole_freeze_radius + pulse * 0.5) * math.cos(theta)
                z = (self.black_hole_freeze_radius + pulse * 0.5) * math.sin(theta)
                glVertex3f(x, 0.0, z)
            glEnd()
            
            # Inner dark swirl
            glColor4f(0.1, 0.0, 0.1, 0.6)  # Very dark purple
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0.0, 0.0, 0.0)  # Center
            for i in range(segments + 1):
                theta = 2.0 * math.pi * i / segments
                x = (self.black_hole_freeze_radius * 0.4 * pulse) * math.cos(theta)
                z = (self.black_hole_freeze_radius * 0.4 * pulse) * math.sin(theta)
                glVertex3f(x, 0.0, z)
            glEnd()
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
    
    def _render_lucky_blocks(self):
        """Render Lucky Blocks with beautiful glowing effects"""
        if not self.lucky_system:
            return
        
        glDisable(GL_LIGHTING)
        current_time = time.time()
        
        for block in self.lucky_system.lucky_blocks:
            if block.is_collected:
                continue  # Don't render collected blocks
            
            bx, by, bz = block.position
            
            # Animate: floating and rotating
            bob_offset = 0.3 * math.sin(current_time * 2.0 + bx + bz)
            rotation = current_time * 45.0  # Rotation angle
            
            glPushMatrix()
            glTranslatef(bx, by + bob_offset, bz)
            glRotatef(rotation, 0, 1, 0)
            
            # Get effect color based on lucky block type
            if block.effect:
                color = self._get_effect_color(block.effect)
            else:
                color = (1.0, 0.84, 0.0)  # Default gold
            
            # Draw glowing cube/box
            size = 0.3
            glColor3f(*color)
            glBegin(GL_QUADS)
            
            # Front face
            glVertex3f(-size, -size, size)
            glVertex3f(size, -size, size)
            glVertex3f(size, size, size)
            glVertex3f(-size, size, size)
            
            # Back face
            glVertex3f(-size, -size, -size)
            glVertex3f(-size, size, -size)
            glVertex3f(size, size, -size)
            glVertex3f(size, -size, -size)
            
            # Top face
            glVertex3f(-size, size, -size)
            glVertex3f(-size, size, size)
            glVertex3f(size, size, size)
            glVertex3f(size, size, -size)
            
            # Bottom face
            glVertex3f(-size, -size, -size)
            glVertex3f(size, -size, -size)
            glVertex3f(size, -size, size)
            glVertex3f(-size, -size, size)
            
            glEnd()
            
            # Glow around block
            glColor4f(*color, 0.3)
            glBegin(GL_LINE_LOOP)
            segments = 16
            for i in range(segments):
                theta = 2.0 * math.pi * i / segments
                x = (size * 1.5) * math.cos(theta)
                y = (size * 0.5) * math.sin(theta)
                glVertex3f(x, y, 0.0)
            glEnd()
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
    
    def _render_teleports(self):
        """Render Teleport Points as shimmering portals"""
        if not self.lucky_system:
            return
        
        glDisable(GL_LIGHTING)
        current_time = time.time()
        
        for teleport in self.lucky_system.teleport_points:
            if not teleport.is_active:
                continue
            
            tx, ty, tz = teleport.position
            
            # Portal animation: expand/contract and rotate
            scale = 0.5 + 0.3 * math.sin(current_time * 1.5 + tx)
            rotation = current_time * 60.0
            
            glPushMatrix()
            glTranslatef(tx, ty, tz)
            
            # Portal frame (spinning ring)
            glColor3f(0.0, 0.8, 1.0)  # Cyan
            glBegin(GL_LINE_LOOP)
            segments = 24
            for i in range(segments):
                theta = 2.0 * math.pi * i / segments + math.radians(rotation)
                x = (scale + 0.3) * math.cos(theta)
                z = (scale + 0.3) * math.sin(theta)
                glVertex3f(x, 0.1, z)
            glEnd()
            
            # Inner glowing disc
            glColor4f(0.0, 0.8, 1.0, 0.5)
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0.0, 0.0, 0.0)
            for i in range(segments + 1):
                theta = 2.0 * math.pi * i / segments
                x = scale * math.cos(theta)
                z = scale * math.sin(theta)
                glVertex3f(x, 0.0, z)
            glEnd()
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
    
    def _get_effect_color(self, effect):
        """Return RGB color based on effect type"""
        color_map = {
            EffectType.FREEZE: (0.0, 0.5, 1.0),  # Cyan/Blue (freeze)
            EffectType.BOOST: (1.0, 0.5, 0.0),   # Orange (boost)
            EffectType.SKIP: (0.5, 0.0, 1.0),    # Purple (skip)
            EffectType.STOP_TWO_ROUNDS: (1.0, 0.0, 0.0),  # Red (stop)
        }
        return color_map.get(effect, (1.0, 0.84, 0.0))  # Default gold

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
