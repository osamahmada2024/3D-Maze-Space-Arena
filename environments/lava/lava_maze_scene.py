# Lava/lava_maze_scene.py
"""
Lava Maze Scene - Main Game Scene
"""

import time
import math
import random
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

from core.scene import Scene
from core.agent import Agent
from core.pathfinding_engine import PathfindingEngine
from core.grid_generator import GridGenerator
from rendering.agent_render import AgentRender
from rendering.goal_render import GoalRender
from rendering.path_render import PathRender
from ui.camera_controller import CameraController
from config.settings import GRID_SETTINGS, AGENT_SETTINGS, CAMERA_SETTINGS

from .lava_zone import LavaZoneManager
from .fire_particle_system import FireParticleSystem
from .volcanic_environment import VolcanicEnvironmentManager
from .heat_haze_fog import HeatHazeFog
from .lava_audio_system import LavaAudioSystem


class LavaMazeScene(Scene):
    """المشهد الرئيسي لمتاهة الحمم البركانية"""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height, agent_shape="sphere_droid", algo_name="astar")
        
        self.player_health = 100.0
        self.last_damage_time = 0.0
        
        self.lava_manager = None
        self.fire_particles = None
        self.volcanic_env = None
        self.heat_fog = None
        self.audio_system = None
        
        self.last_player_cell = None
        self.fog_pulse = 0.0
    
    def initialize(self, agent_shape: str = "sphere_droid", algo_name: str = "astar"):
        self.agent_shape = agent_shape
        self.algo_name = algo_name
        
        self._init_opengl()
        
        obstacle_prob = GRID_SETTINGS.get("obstacle_prob_lava", 0.35)
        start, goal = self._create_grid(obstacle_prob)
        
        self._create_lava_zones()
        self._create_lava_agent(start, goal)
        self._create_camera()
        self._create_base_renderers(ground_sampler=lambda x, z: 0.0)
        self._init_lava_systems()
        
        self.start_time = time.time()
        self.game_active = True
        
        print(f"[LAVA MAZE] ✅ Initialized! Health: {self.player_health}")
        return self.agent
    
    def _init_opengl(self):
        glClearColor(0.1, 0.05, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 30.0, 0.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.1, 0.05, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.4, 0.1, 1.0])
    
    def _create_lava_zones(self):
        self.lava_manager = LavaZoneManager()
        
        path_set = set(self.path) if self.path else set()
        lava_positions = []
        
        # Goal position should never have lava
        goal_pos = (self.grid_size - 1, self.grid_size - 1)
        start_pos = (0, 0)
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Skip start and goal positions
                if (x, y) == goal_pos or (x, y) == start_pos:
                    continue
                if self.grid[y][x] == 0 and (x, y) not in path_set:
                    if random.random() < 0.12:
                        lava_positions.append((x, y))
        
        self.lava_manager.create_from_grid_positions(
            lava_positions, 
            self.grid_size, 
            self.cell_size
        )
    
    def _create_lava_agent(self, start, goal):
        """✅ إنشاء Agent بالألوان الأصلية من الإعدادات"""
        # استخدام الألوان الأصلية من config/settings.py
        agent_color = AGENT_SETTINGS["colors"].get(
            self.agent_shape, 
            (0.0, 1.0, 1.0)
        )
        
        self.agent = Agent(
            start=start,
            goal=goal,
            path=self.path,
            speed=AGENT_SETTINGS.get("speed", 2.5),
            color=agent_color,
            shape_type=self.agent_shape,
            trail_length=AGENT_SETTINGS.get("trail_length", 25)
        )
    
    def _init_lava_systems(self):
        self.fire_particles = FireParticleSystem(self.grid_size, self.cell_size)
        spawn_points = [zone.get_position() for zone in self.lava_manager.zones]
        self.fire_particles.set_spawn_points(spawn_points)
        
        self.volcanic_env = VolcanicEnvironmentManager(self.grid_size, self.cell_size)
        self.volcanic_env.generate_rocks_from_grid(self.grid)
        
        self.heat_fog = HeatHazeFog()
        self.heat_fog.enable()
        
        self.audio_system = LavaAudioSystem()
        self.audio_system.start_ambient()
    
    def update(self, dt: float):
        if not self.game_active:
            return
        
        self._update_camera_input(dt)
        
        for agent in self.agents:
            agent.update(dt)
        self.agent_renderer.update_time(dt)
        
        self._update_camera_follow()
        
        # Use first agent for environmental interactions for now
        target_agent = self.agents[0] if self.agents else None
        if target_agent:
            wx = (target_agent.position[0] - self.grid_size // 2) * self.cell_size
            wy = target_agent.position[1]
            wz = (target_agent.position[2] - self.grid_size // 2) * self.cell_size
            
            self._check_lava_damage(wx, wy, wz, dt)
            self._check_footsteps(wx, wz)
        
        self.lava_manager.update(dt)
        self.fire_particles.update(dt)
        self.volcanic_env.update(dt)
        self.audio_system.update(dt)
        
        self.fog_pulse += dt
        intensity = 0.8 + 0.2 * math.sin(self.fog_pulse * 0.5)
        self.heat_fog.update_intensity(intensity)
        
        self._check_victory()
    
    def _check_lava_damage(self, wx: float, wy: float, wz: float, dt: float):
        if self.lava_manager.is_in_lava((wx, wy, wz)):
            current_time = time.time()
            if current_time - self.last_damage_time > 0.5:
                damage = self.lava_manager.get_damage_rate((wx, wy, wz))
                self.player_health -= damage * dt * 2
                self.audio_system.play_burn_damage()
                self.last_damage_time = current_time
                print(f"[LAVA] 🔥 BURNING! Health: {self.player_health:.1f}")
                
                if self.player_health <= 0:
                    print("[LAVA] 💀 GAME OVER - Burned to death!")
                    self.game_active = False
    
    def _check_footsteps(self, wx: float, wz: float):
        gx = int(round(wx / self.cell_size + self.grid_size // 2))
        gy = int(round(wz / self.cell_size + self.grid_size // 2))
        if (gx, gy) != self.last_player_cell:
            self.last_player_cell = (gx, gy)
            self.audio_system.play_footstep()
    
    def _reset_lighting_for_agent(self):
        """✅ إضاءة محايدة بيضاء للـ Agent"""
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    
    def _restore_lava_lighting(self):
        """إعادة الإضاءة البركانية"""
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.1, 0.05, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.4, 0.1, 1.0])
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._setup_view()
        
        self._render_volcanic_floor()
        self.volcanic_env.render_all()
        self.lava_manager.render_zones()
        self.fire_particles.render()
        
        # ✅ إعادة ضبط الإضاءة قبل رسم الـ Agent
        self._reset_lighting_for_agent()
        glDisable(GL_FOG)
        self._render_agent_and_goal()
        glEnable(GL_FOG)
        self._restore_lava_lighting()
        
        self._render_health_bar()
    
    def _render_volcanic_floor(self):
        """رسم الأرضية البركانية المحسّنة"""
        glDisable(GL_LIGHTING)
        
        half_world = self.grid_size * self.cell_size / 2.0
        
        # ========== الطبقة الأساسية (أسود) ==========
        glColor3f(0.05, 0.03, 0.02)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-half_world, -0.15, -half_world)
        glVertex3f(half_world, -0.15, -half_world)
        glVertex3f(half_world, -0.15, half_world)
        glVertex3f(-half_world, -0.15, half_world)
        glEnd()
        
        # ========== طبقة الصخور المتشققة ==========
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # رسم شقوق عشوائية مع حمم
        random.seed(42)  # للثبات
        
        glLineWidth(2.0)
        for _ in range(150):
            x1 = random.uniform(-half_world, half_world)
            z1 = random.uniform(-half_world, half_world)
            
            length = random.uniform(0.3, 1.5)
            angle = random.uniform(0, math.pi * 2)
            
            x2 = x1 + length * math.cos(angle)
            z2 = z1 + length * math.sin(angle)
            
            # شق مظلم
            glColor4f(0.1, 0.08, 0.06, 0.8)
            glBegin(GL_LINES)
            glVertex3f(x1, -0.12, z1)
            glVertex3f(x2, -0.12, z2)
            glEnd()
        
        # شقوق متوهجة بالحمم
        glow = 0.5 + 0.5 * math.sin(self.fog_pulse * 2)
        glLineWidth(1.5)
        
        for _ in range(50):
            x1 = random.uniform(-half_world, half_world)
            z1 = random.uniform(-half_world, half_world)
            
            length = random.uniform(0.2, 0.8)
            angle = random.uniform(0, math.pi * 2)
            
            x2 = x1 + length * math.cos(angle)
            z2 = z1 + length * math.sin(angle)
            
            # حمم في الشق
            glColor4f(1.0, 0.3 * glow, 0.0, 0.4 * glow)
            glBegin(GL_LINES)
            glVertex3f(x1, -0.10, z1)
            glVertex3f(x2, -0.10, z2)
            glEnd()
        
        glLineWidth(1.0)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
    
    def _render_health_bar(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
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
        
        health_pct = max(0.0, min(1.0, self.player_health / 100.0))
        fill_width = bar_width * health_pct
        
        if health_pct > 0.5:
            glColor3f(0.0, 1.0, 0.0)
        elif health_pct > 0.25:
            glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(1.0, 0.0, 0.0)
        
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + fill_width, bar_y)
        glVertex2f(bar_x + fill_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        
        glColor3f(1.0, 1.0, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_width, bar_y)
        glVertex2f(bar_x + bar_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        glLineWidth(1.0)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def cleanup(self):
        if self.audio_system:
            self.audio_system.cleanup()
        print("[LAVA MAZE] ✅ Cleanup complete")