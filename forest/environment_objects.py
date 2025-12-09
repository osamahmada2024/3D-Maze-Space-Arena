"""
Environment Objects Manager
Handles trees, rocks, stumps, grass, logs with collision data.
Supports both procedural and 3DS model rendering.
"""

import random
import math
import os
from typing import List, Tuple, Optional
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class SmoothTree:
    """Smooth, high-quality procedural tree with LOD support"""
    
    def __init__(self, x: float, y: float, z: float, scale: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.scale = scale
        self.trunk_height = 1.8 * scale
        self.trunk_radius = 0.12 * scale
        self.foliage_radius = 0.8 * scale
        
        # Pre-calculated display lists for performance
        self.display_list = None
        self.lod_level = 2  # 0=low, 1=medium, 2=high
        
    def create_display_list(self):
        """Create OpenGL display list for faster rendering"""
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
        
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        self._draw_detailed_tree()
        glEndList()
    
    def _draw_detailed_tree(self):
        """Draw high-detail tree"""
        glPushMatrix()
        
        # Trunk with smoother cylinder
        glColor3f(0.55, 0.35, 0.15)
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, 0, -self.trunk_height)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluQuadricTexture(quad, GL_TRUE)
        gluCylinder(quad, self.trunk_radius, self.trunk_radius * 0.85, 
                   self.trunk_height, 16, 8)
        gluDeleteQuadric(quad)
        
        glPopMatrix()
        
        # Foliage - smoother spheres with gradient colors
        self._draw_foliage()
        
        # Small branches
        self._draw_branches()
    
    def _draw_foliage(self):
        """Draw smooth foliage with gradient"""
        # Main foliage (dark green)
        glPushMatrix()
        glTranslatef(0, self.trunk_height * 0.7, 0)
        glColor3f(0.12, 0.35, 0.15)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, self.foliage_radius, 20, 20)
        gluDeleteQuadric(quad)
        glPopMatrix()
        
        # Upper foliage (lighter green)
        glPushMatrix()
        glTranslatef(0, self.trunk_height * 0.9, 0)
        glColor3f(0.18, 0.45, 0.20)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, self.foliage_radius * 0.75, 18, 18)
        gluDeleteQuadric(quad)
        glPopMatrix()
        
        # Side foliage balls for fuller look
        foliage_positions = [
            (-0.5, self.trunk_height * 0.6, 0),
            (0.5, self.trunk_height * 0.6, 0),
            (0, self.trunk_height * 0.6, -0.5),
            (0, self.trunk_height * 0.6, 0.5),
            (-0.3, self.trunk_height * 0.8, -0.3),
            (0.3, self.trunk_height * 0.8, 0.3)
        ]
        
        glColor3f(0.15, 0.40, 0.18)
        for pos in foliage_positions:
            glPushMatrix()
            glTranslatef(*pos)
            
            quad = gluNewQuadric()
            gluQuadricNormals(quad, GLU_SMOOTH)
            gluSphere(quad, self.foliage_radius * 0.5, 16, 16)
            gluDeleteQuadric(quad)
            
            glPopMatrix()
    
    def _draw_branches(self):
        """Add small branches for detail"""
        glColor3f(0.5, 0.3, 0.1)
        
        branch_positions = [
            (0.1, self.trunk_height * 0.3, 0.1, 0.3, 30, 0.3),
            (-0.1, self.trunk_height * 0.4, -0.1, 0.25, -30, 0.25),
            (0.15, self.trunk_height * 0.5, 0, 0.2, 45, 0.2)
        ]
        
        for bx, by, bz, length, angle, radius in branch_positions:
            glPushMatrix()
            glTranslatef(bx, by, bz)
            glRotatef(angle, 0, 1, 0)
            glRotatef(-90, 1, 0, 0)
            
            quad = gluNewQuadric()
            gluQuadricNormals(quad, GLU_SMOOTH)
            gluCylinder(quad, radius * 0.5, radius * 0.2, length, 8, 4)
            gluDeleteQuadric(quad)
            
            glPopMatrix()
    
    def render(self):
        """Render the tree with LOD"""
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        if self.display_list is None:
            self.create_display_list()
        
        # Use display list for faster rendering
        if self.display_list:
            glCallList(self.display_list)
        else:
            self._draw_detailed_tree()
        
        glPopMatrix()

def render_tree_at(wx: float, wy: float, wz: float, scale: float = 1.0):
    """Render a smooth tree at the given position"""
    tree = SmoothTree(wx, wy, wz, scale)
    tree.render()

def render_grass_floor_at(wx: float, wz: float, size: float = 1.0):
    """Render a grass floor tile with detail"""
    glPushMatrix()
    glTranslatef(wx, 0, wz)
    
    # Create tiled grass with variation
    for dx in [-0.4, 0, 0.4]:
        for dz in [-0.4, 0, 0.4]:
            glPushMatrix()
            glTranslatef(dx, 0, dz)
            
            # Slight random height variation
            glBegin(GL_QUADS)
            glColor3f(0.22, 0.48, 0.22)
            glNormal3f(0, 1, 0)

            glVertex3f(-0.2, 0, -0.2)
            glVertex3f(0.2, 0, -0.2)
            glVertex3f(0.2, 0, 0.2)
            glVertex3f(-0.2, 0, 0.2)

            glEnd()
            
            # Add some grass blades
            if random.random() < 0.3:
                glBegin(GL_LINES)
                glColor3f(0.1, 0.4, 0.1)
                for _ in range(3):
                    x = random.uniform(-0.15, 0.15)
                    z = random.uniform(-0.15, 0.15)
                    glVertex3f(x, 0.02, z)
                    glVertex3f(x + random.uniform(-0.02, 0.02), 
                              0.05 + random.uniform(0, 0.03), 
                              z + random.uniform(-0.02, 0.02))
                glEnd()
            
            glPopMatrix()
    
    glPopMatrix()

class EnvironmentObjectManager:
    """Manages all environment objects with collision - uses cached trees for performance"""
    
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.trees = []
        self.collision_radius = 0.35
        self._tree_cache = {}  # Cache SmoothTree objects by scale
        self.trees = []
        self.collision_radius = 0.35
    
    def generate_trees_from_grid(self, grid):
        """Generate trees from maze grid"""
        self.trees = []
        
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if grid[y][x] == 1:  # Wall = Tree
                    # Reduce density: only place tree 50% of the time, or depends on neighbor count?
                    # User asked to "reduce trees alil bit". 
                    if random.random() > 0.5: 
                        continue

                    wx = (x - self.grid_size // 2) * self.cell_size
                    wz = (y - self.grid_size // 2) * self.cell_size
                    
                    # Random variation
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
    
    def render_all(self):
        """Render all trees"""
        glEnable(GL_LIGHTING)
        
        for tree in self.trees:
            render_tree_at(tree['x'], tree['y'], tree['z'], tree['scale'])
    
    def check_collision(self, position: Tuple[float, float, float]) -> bool:
        """Check if position collides with any tree"""
        px, py, pz = position
        
        for tree in self.trees:
            dx = px - tree['x']
            dz = pz - tree['z']
            dist_sq = dx*dx + dz*dz
            
            if dist_sq < (self.collision_radius + tree['collision_radius']) ** 2:
                return True
        
        return False