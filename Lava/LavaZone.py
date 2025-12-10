# Lava/LavaZone.py
"""
Lava Zones Manager - ENHANCED VERSION
Realistic animated lava pools with bubbles and waves
"""

import math
import random
from typing import List, Tuple
from OpenGL.GL import *
from OpenGL.GLU import *


class LavaBubble:
    """فقاعة حمم"""
    
    def __init__(self, x: float, z: float, pool_radius: float):
        self.x = x + random.uniform(-pool_radius * 0.6, pool_radius * 0.6)
        self.z = z + random.uniform(-pool_radius * 0.6, pool_radius * 0.6)
        self.y = 0.02
        self.size = random.uniform(0.03, 0.08)
        self.max_size = self.size * random.uniform(1.5, 2.5)
        self.grow_speed = random.uniform(0.3, 0.6)
        self.alive = True
    
    def update(self, dt: float):
        self.size += self.grow_speed * dt
        self.y += dt * 0.1
        
        if self.size >= self.max_size:
            self.alive = False
    
    def render(self):
        if not self.alive:
            return
        
        alpha = 1.0 - (self.size / self.max_size)
        glColor4f(1.0, 0.6, 0.0, alpha * 0.7)
        
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # رسم دائرة للفقاعة
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        segments = 12
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            glVertex3f(
                self.size * math.cos(angle),
                0,
                self.size * math.sin(angle)
            )
        glEnd()
        
        glPopMatrix()


class LavaZone:
    """منطقة حمم محسّنة"""
    
    def __init__(self, x: float, y: float, z: float, radius: float = 0.6, 
                 damage_rate: float = 10.0):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.damage_rate = damage_rate
        
        # تأثيرات بصرية
        self.glow_intensity = random.uniform(0.8, 1.0)
        self.animation_offset = random.uniform(0, math.pi * 2)
        self.wave_offset = random.uniform(0, math.pi * 2)
        self.time = 0.0
        
        # فقاعات
        self.bubbles: List[LavaBubble] = []
        self.bubble_timer = 0.0
        self.bubble_interval = random.uniform(0.3, 0.8)
    
    def get_position(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def contains_point(self, pos: Tuple[float, float, float]) -> bool:
        px, py, pz = pos
        dx = px - self.x
        dz = pz - self.z
        distance = math.sqrt(dx * dx + dz * dz)
        return distance <= self.radius
    
    def update(self, dt: float):
        self.time += dt
        self.glow_intensity = 0.7 + 0.3 * math.sin(self.time * 2.0 + self.animation_offset)
        
        # تحديث الفقاعات
        self.bubble_timer += dt
        if self.bubble_timer >= self.bubble_interval:
            self.bubbles.append(LavaBubble(self.x, self.z, self.radius))
            self.bubble_timer = 0.0
            self.bubble_interval = random.uniform(0.2, 0.6)
        
        # تحديث وإزالة الفقاعات الميتة
        for bubble in self.bubbles:
            bubble.update(dt)
        self.bubbles = [b for b in self.bubbles if b.alive]
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        segments = 24
        
        # ========== الطبقة السفلية (أحمر داكن) ==========
        glColor4f(0.4, 0.1, 0.0, 1.0)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0.01, 0)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            glVertex3f(
                self.radius * math.cos(angle),
                0.01,
                self.radius * math.sin(angle)
            )
        glEnd()
        
        # ========== الطبقة الرئيسية (برتقالي متموج) ==========
        glColor4f(1.0, 0.4, 0.0, 0.9 * self.glow_intensity)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0.02, 0)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            # موجة على الحواف
            wave = 0.03 * math.sin(self.time * 3.0 + angle * 3 + self.wave_offset)
            r = self.radius * 0.9 + wave
            glVertex3f(
                r * math.cos(angle),
                0.02 + wave * 0.5,
                r * math.sin(angle)
            )
        glEnd()
        
        # ========== المركز المتوهج (أصفر) ==========
        glColor4f(1.0, 0.8, 0.2, 0.8 * self.glow_intensity)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0.03, 0)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            wave = 0.02 * math.sin(self.time * 4.0 + angle * 2)
            r = self.radius * 0.4 + wave
            glVertex3f(
                r * math.cos(angle),
                0.03,
                r * math.sin(angle)
            )
        glEnd()
        
        # ========== النقطة الساخنة (أبيض/أصفر فاتح) ==========
        hot_glow = 0.5 + 0.5 * math.sin(self.time * 5.0)
        glColor4f(1.0, 1.0, 0.7, 0.6 * hot_glow)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0.035, 0)
        for i in range(12):
            angle = 2.0 * math.pi * i / 12
            r = self.radius * 0.15
            glVertex3f(
                r * math.cos(angle),
                0.035,
                r * math.sin(angle)
            )
        glEnd()
        
        glPopMatrix()
        
        # رسم الفقاعات
        for bubble in self.bubbles:
            bubble.render()
    
    def render_glow(self):
        """رسم التوهج حول البركة"""
        glPushMatrix()
        glTranslatef(self.x, self.y - 0.01, self.z)
        
        # هالة خارجية
        glColor4f(1.0, 0.3, 0.0, 0.2 * self.glow_intensity)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        segments = 20
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            r = self.radius * 1.5
            glVertex3f(r * math.cos(angle), 0, r * math.sin(angle))
        glEnd()
        
        glPopMatrix()


class LavaZoneManager:
    """مدير مناطق الحمم"""
    
    def __init__(self):
        self.zones: List[LavaZone] = []
    
    def add_zone(self, x: float, y: float, z: float, 
                 radius: float = 0.6, damage_rate: float = 10.0):
        zone = LavaZone(x, y, z, radius, damage_rate)
        self.zones.append(zone)
    
    def create_from_grid_positions(self, grid_positions: List[Tuple[int, int]], 
                                   grid_size: int = 25, cell_size: float = 1.0,
                                   radius: float = 0.5):
        for gx, gy in grid_positions:
            wx = (gx - grid_size // 2) * cell_size
            wz = (gy - grid_size // 2) * cell_size
            # تنوع في الحجم
            actual_radius = radius * random.uniform(0.7, 1.2)
            self.add_zone(wx, -0.05, wz, actual_radius)
        
        print(f"[LAVA] Created {len(self.zones)} lava pools")
    
    def get_damage_rate(self, position: Tuple[float, float, float]) -> float:
        damage = 0.0
        for zone in self.zones:
            if zone.contains_point(position):
                damage += zone.damage_rate
        return damage
    
    def is_in_lava(self, position: Tuple[float, float, float]) -> bool:
        for zone in self.zones:
            if zone.contains_point(position):
                return True
        return False
    
    def update(self, dt: float):
        for zone in self.zones:
            zone.update(dt)
    
    def render_zones(self):
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # رسم التوهج أولاً (خلف)
        glDepthMask(GL_FALSE)
        for zone in self.zones:
            zone.render_glow()
        glDepthMask(GL_TRUE)
        
        # رسم البرك
        for zone in self.zones:
            zone.render()
        
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)