# forest/environment_objects.py
"""
Environment Objects Manager - OPTIMIZED VERSION
Uses shared display lists and cached quadrics
"""

import random
import math
from typing import List, Tuple
from OpenGL.GL import *
from OpenGL.GLU import *


class EnvironmentObjectManager:
    """
    Manages all environment objects with collision.
    OPTIMIZED: Uses a single display list for all trees.
    """
    
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.trees = []
        self.collision_radius = 0.35
        
        # ✅ Shared quadric - إنشاء مرة واحدة فقط
        self._quadric = gluNewQuadric()
        gluQuadricNormals(self._quadric, GLU_SMOOTH)
        
        # ✅ Display list for ALL trees combined
        self._all_trees_display_list = None
        self._initialized = False
    
    def __del__(self):
        """تنظيف الموارد"""
        try:
            if self._quadric:
                gluDeleteQuadric(self._quadric)
            if self._all_trees_display_list:
                glDeleteLists(self._all_trees_display_list, 1)
        except:
            pass
    
    def generate_trees_from_grid(self, grid):
        """Generate trees from maze grid"""
        self.trees = []
        
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if grid[y][x] == 1:  # Wall = Tree
                    # تقليل الكثافة 50%
                    if random.random() > 0.5:
                        continue

                    wx = (x - self.grid_size // 2) * self.cell_size
                    wz = (y - self.grid_size // 2) * self.cell_size
                    
                    scale = random.uniform(0.8, 1.2)
                    y_offset = random.uniform(-0.05, 0.05)
                    
                    self.trees.append({
                        'x': wx,
                        'y': y_offset,
                        'z': wz,
                        'scale': scale,
                        'collision_radius': 0.28 * scale
                    })
        
        print(f"[ENV] Generated {len(self.trees)} trees")
        
        # ✅ بناء Display List لكل الأشجار مرة واحدة
        self._build_trees_display_list()
    
    def _build_trees_display_list(self):
        """بناء Display List واحد لكل الأشجار"""
        if self._all_trees_display_list:
            glDeleteLists(self._all_trees_display_list, 1)
        
        self._all_trees_display_list = glGenLists(1)
        glNewList(self._all_trees_display_list, GL_COMPILE)
        
        for tree in self.trees:
            self._draw_tree(tree['x'], tree['y'], tree['z'], tree['scale'])
        
        glEndList()
        
        self._initialized = True
        print(f"[ENV] Trees display list built successfully!")
    
    def _draw_tree(self, x: float, y: float, z: float, scale: float):
        """رسم شجرة واحدة (للـ display list)"""
        trunk_height = 1.8 * scale
        trunk_radius = 0.12 * scale
        foliage_radius = 0.8 * scale
        
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # ========== الجذع ==========
        glColor3f(0.55, 0.35, 0.15)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        gluCylinder(self._quadric, trunk_radius, trunk_radius * 0.85, 
                   trunk_height, 12, 4)  # ✅ تقليل segments
        glPopMatrix()
        
        # ========== أوراق الشجر الرئيسية ==========
        # Main foliage
        glPushMatrix()
        glTranslatef(0, trunk_height * 0.7, 0)
        glColor3f(0.12, 0.35, 0.15)
        gluSphere(self._quadric, foliage_radius, 12, 12)  # ✅ تقليل segments
        glPopMatrix()
        
        # Upper foliage
        glPushMatrix()
        glTranslatef(0, trunk_height * 0.9, 0)
        glColor3f(0.18, 0.45, 0.20)
        gluSphere(self._quadric, foliage_radius * 0.75, 10, 10)  # ✅ تقليل segments
        glPopMatrix()
        
        # ========== أوراق جانبية (مُبسطة) ==========
        glColor3f(0.15, 0.40, 0.18)
        
        # فقط 4 كرات جانبية بدلاً من 6
        side_positions = [
            (-0.4 * scale, trunk_height * 0.6, 0),
            (0.4 * scale, trunk_height * 0.6, 0),
            (0, trunk_height * 0.6, -0.4 * scale),
            (0, trunk_height * 0.6, 0.4 * scale),
        ]
        
        for px, py, pz in side_positions:
            glPushMatrix()
            glTranslatef(px, py, pz)
            gluSphere(self._quadric, foliage_radius * 0.45, 8, 8)  # ✅ تقليل segments
            glPopMatrix()
        
        glPopMatrix()
    
    def render_all(self):
        """Render all trees using display list"""
        if not self._initialized:
            return
        
        glEnable(GL_LIGHTING)
        
        # ✅ استدعاء Display List واحد فقط!
        if self._all_trees_display_list:
            glCallList(self._all_trees_display_list)
    
    def check_collision(self, position: Tuple[float, float, float]) -> bool:
        """Check if position collides with any tree"""
        px, py, pz = position
        
        for tree in self.trees:
            dx = px - tree['x']
            dz = pz - tree['z']
            dist_sq = dx * dx + dz * dz
            
            if dist_sq < (self.collision_radius + tree['collision_radius']) ** 2:
                return True
        
        return False

    def clear_area(self, grid_pos: Tuple[int, int], radius: int = 1):
        """Remove trees within a radius of a grid position (e.g., goal area)."""
        cx, cy = grid_pos
        
        # Convert grid to world coordinates
        center_wx = (cx - self.grid_size // 2) * self.cell_size
        center_wz = (cy - self.grid_size // 2) * self.cell_size
        
        # Calculate world radius
        world_radius = (radius + 0.5) * self.cell_size
        
        # Filter out trees within radius
        original_count = len(self.trees)
        self.trees = [
            tree for tree in self.trees
            if (tree['x'] - center_wx) ** 2 + (tree['z'] - center_wz) ** 2 > world_radius ** 2
        ]
        
        removed = original_count - len(self.trees)
        if removed > 0:
            print(f"[ENV] Cleared {removed} trees near goal")
            # Rebuild display list
            self._build_trees_display_list()


# ✅ للتوافق مع الكود القديم (إذا كان مستخدم في مكان آخر)
def render_tree_at(wx: float, wy: float, wz: float, scale: float = 1.0):
    """Backward compatibility - not recommended for many trees"""
    pass  # لا تفعل شيء - الأشجار تُرسم من الـ display list


def render_grass_floor_at(wx: float, wz: float, size: float = 1.0):
    """Render grass - simplified"""
    pass  # الأرضية تُرسم من forest_scene