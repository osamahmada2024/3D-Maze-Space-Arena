# Lava/volcanic_environment.py
"""
Volcanic Environment - ENHANCED VERSION
Realistic volcanic rocks with glowing cracks and lava veins
"""

import random
import math
from typing import List
from OpenGL.GL import *
from OpenGL.GLU import *


class VolcanicRock:
    """صخرة بركانية محسّنة مع شقوق متوهجة"""
    
    def __init__(self, x: float, y: float, z: float, scale: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.scale = scale
        self.rotation = random.uniform(0, 360)
        self.glow_phase = random.uniform(0, math.pi * 2)
        self.glow_speed = random.uniform(1.5, 3.0)
        
        # تنوع في الشكل
        self.height_scale = random.uniform(0.6, 1.2)
        self.width_scale = random.uniform(0.8, 1.2)
        
        # شقوق متوهجة
        self.cracks = self._generate_cracks()
        
        # لون الصخرة (تنوع)
        darkness = random.uniform(0.08, 0.18)
        self.rock_color = (darkness, darkness * 0.8, darkness * 0.6)
    
    def _generate_cracks(self):
        """توليد شقوق عشوائية"""
        cracks = []
        num_cracks = random.randint(3, 7)
        
        for _ in range(num_cracks):
            # شق يبدأ من نقطة عشوائية
            start_angle = random.uniform(0, math.pi * 2)
            start_r = random.uniform(0.1, 0.3)
            
            x1 = start_r * math.cos(start_angle)
            z1 = start_r * math.sin(start_angle)
            
            # ينتهي عند نقطة أبعد
            end_r = random.uniform(0.35, 0.55)
            angle_offset = random.uniform(-0.5, 0.5)
            
            x2 = end_r * math.cos(start_angle + angle_offset)
            z2 = end_r * math.sin(start_angle + angle_offset)
            
            # سمك الشق
            width = random.uniform(0.02, 0.05)
            
            cracks.append({
                'x1': x1, 'z1': z1,
                'x2': x2, 'z2': z2,
                'width': width,
                'intensity': random.uniform(0.7, 1.0)
            })
        
        return cracks


class VolcanicEnvironmentManager:
    """مدير البيئة البركانية المحسّن"""
    
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.rocks: List[VolcanicRock] = []
        
        self._quadric = gluNewQuadric()
        gluQuadricNormals(self._quadric, GLU_SMOOTH)
        
        self._display_list = None
        self._time = 0.0
    
    def __del__(self):
        try:
            if self._quadric:
                gluDeleteQuadric(self._quadric)
            if self._display_list:
                glDeleteLists(self._display_list, 1)
        except:
            pass
    
    def generate_rocks_from_grid(self, grid):
        """توليد صخور بركانية من الشبكة"""
        self.rocks = []
        
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if grid[y][x] == 1:
                    if random.random() > 0.2:  # 80% كثافة
                        wx = (x - self.grid_size // 2) * self.cell_size
                        wz = (y - self.grid_size // 2) * self.cell_size
                        
                        # صخرة رئيسية
                        scale = random.uniform(0.7, 1.1)
                        self.rocks.append(VolcanicRock(wx, 0.0, wz, scale))
                        
                        # صخور صغيرة حولها (أحياناً)
                        if random.random() < 0.3:
                            offset_x = random.uniform(-0.3, 0.3)
                            offset_z = random.uniform(-0.3, 0.3)
                            small_scale = random.uniform(0.3, 0.5)
                            self.rocks.append(VolcanicRock(
                                wx + offset_x, 0.0, wz + offset_z, small_scale
                            ))
        
        print(f"[LAVA ENV] Generated {len(self.rocks)} volcanic rocks")
        self._build_display_list()
    
    def _build_display_list(self):
        """بناء Display List للصخور الثابتة"""
        if self._display_list:
            glDeleteLists(self._display_list, 1)
        
        self._display_list = glGenLists(1)
        glNewList(self._display_list, GL_COMPILE)
        
        for rock in self.rocks:
            self._draw_rock_geometry(rock)
        
        glEndList()
        print("[LAVA ENV] ✅ Display list built!")
    
    def _draw_rock_geometry(self, rock: VolcanicRock):
        """رسم هندسة الصخرة"""
        glPushMatrix()
        glTranslatef(rock.x, rock.y, rock.z)
        glRotatef(rock.rotation, 0, 1, 0)
        
        # الصخرة الرئيسية - شكل غير منتظم
        glColor3f(*rock.rock_color)
        
        glPushMatrix()
        glScalef(
            rock.scale * rock.width_scale,
            rock.scale * rock.height_scale,
            rock.scale * rock.width_scale
        )
        
        # قاعدة الصخرة (أعرض)
        glPushMatrix()
        glScalef(1.2, 0.4, 1.2)
        gluSphere(self._quadric, 0.5, 8, 6)
        glPopMatrix()
        
        # جسم الصخرة
        glTranslatef(0, 0.2, 0)
        gluSphere(self._quadric, 0.45, 8, 6)
        
        # قمة الصخرة (أصغر)
        glTranslatef(0, 0.25, 0)
        glScalef(0.7, 0.8, 0.7)
        gluSphere(self._quadric, 0.35, 6, 5)
        
        glPopMatrix()
        glPopMatrix()
    
    def update(self, dt: float):
        """تحديث الوقت للتأثيرات المتحركة"""
        self._time += dt
        for rock in self.rocks:
            rock.glow_phase += dt * rock.glow_speed
    
    def render_all(self):
        """رسم جميع الصخور مع الشقوق المتوهجة"""
        glEnable(GL_LIGHTING)
        
        # رسم الصخور من Display List
        if self._display_list:
            glCallList(self._display_list)
        
        # رسم الشقوق المتوهجة (ديناميكية)
        self._render_glowing_cracks()
    
    def _render_glowing_cracks(self):
        """رسم الشقوق المتوهجة"""
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending للتوهج
        glLineWidth(3.0)
        
        for rock in self.rocks:
            glow = 0.5 + 0.5 * math.sin(rock.glow_phase)
            
            glPushMatrix()
            glTranslatef(rock.x, rock.y + 0.15, rock.z)
            glRotatef(rock.rotation, 0, 1, 0)
            glScalef(rock.scale, rock.scale, rock.scale)
            
            for crack in rock.cracks:
                # لون الشق (برتقالي/أحمر متوهج)
                intensity = crack['intensity'] * glow
                glColor4f(1.0, 0.4 * intensity, 0.0, intensity * 0.8)
                
                glLineWidth(crack['width'] * 50)
                glBegin(GL_LINES)
                glVertex3f(crack['x1'], 0.01, crack['z1'])
                glVertex3f(crack['x2'], 0.01, crack['z2'])
                glEnd()
                
                # توهج حول الشق
                glColor4f(1.0, 0.3, 0.0, intensity * 0.3)
                glLineWidth(crack['width'] * 100)
                glBegin(GL_LINES)
                glVertex3f(crack['x1'], 0.005, crack['z1'])
                glVertex3f(crack['x2'], 0.005, crack['z2'])
                glEnd()
            
            glPopMatrix()
        
        glLineWidth(1.0)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)