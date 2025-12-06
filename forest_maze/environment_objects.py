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
from .model_loader import load_model, load_texture, SimpleModel

try:
    from .model_loader import Model3DS, render_fallback_tree
except ImportError:
    try:
        from model_loader import Model3DS, render_fallback_tree
    except ImportError:
        # Fallback if model_loader unavailable
        Model3DS = None
        def render_fallback_tree(scale: float = 1.0):
            pass


# Global model cache (loaded once, used many times)
_model_cache = {
    'tree': None,
    'grass': None
}

def load_models(model_dir: str = "models"):
    """Load 3D models with better error handling"""
    global _model_cache
    
    tree_model_path = os.path.join(model_dir, "tree", "Tree1.3ds")
    tree_texture_path = os.path.join(model_dir, "tree", "bark_loo.jpg")
    
    grass_model_path = os.path.join(model_dir, "grass", "grass-block.3DS")
    
    # Load tree model with texture
    if os.path.exists(tree_model_path):
        _model_cache['tree'] = load_model(tree_model_path)
        if os.path.exists(tree_texture_path):
            _model_cache['tree_texture'] = load_texture(tree_texture_path)
    
    # Load grass model
    if os.path.exists(grass_model_path):
        _model_cache['grass'] = load_model(grass_model_path)

def get_tree_model() -> Optional[Model3DS]:
    """Get cached tree model"""
    return _model_cache['tree']


def get_grass_model() -> Optional[Model3DS]:
    """Get cached grass model"""
    return _model_cache['grass']


def render_tree_at(wx: float, wy: float, wz: float, scale: float = 1.0):
    """Render a tree at the given position"""
    tree_model = _model_cache.get('tree')
    tree_texture = _model_cache.get('tree_texture')
    
    glPushMatrix()
    glTranslatef(wx, wy, wz)
    glScalef(scale, scale, scale)
    
    if tree_model:
        if hasattr(tree_model, 'render'):
            tree_model.render()
        else:
            # Handle PyWavefront scene
            for mesh in tree_model.mesh_list:
                if tree_texture:
                    glEnable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, tree_texture)
                else:
                    glColor3f(0.5, 0.3, 0.1)  # Brown color for tree
                    
                glBegin(GL_TRIANGLES)
                for face in mesh.faces:
                    for vertex in face:
                        if vertex < len(mesh.vertices):
                            glVertex3f(*mesh.vertices[vertex])
                glEnd()
    else:
        # Fallback rendering
        glColor3f(0.4, 0.3, 0.2)  # Brown for trunk
        # Draw trunk (simple cube)
        glPushMatrix()
        glTranslatef(0, 0.5, 0)
        glScalef(0.1, 0.5, 0.1)
        # Draw cube faces...
        glPopMatrix()
        
        # Draw foliage (green sphere)
        glColor3f(0.2, 0.5, 0.2)
        glPushMatrix()
        glTranslatef(0, 1.2, 0)
        quad = gluNewQuadric()
        gluSphere(quad, 0.3, 16, 16)
        glPopMatrix()
    
    glPopMatrix()
class EnvironmentObject:
    """Base class for environment objects"""
    
    def __init__(self, x: float, y: float, z: float, obj_type: str, scale: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.type = obj_type
        self.scale = scale
        self.color = (0.6, 0.5, 0.4)
        self.collision_radius = 0.25 * scale
    
    def get_position(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def get_collision_sphere(self) -> Tuple[float, float, float, float]:
        """Returns (x, y, z, radius) for collision detection"""
        return (self.x, self.y, self.z, self.collision_radius)


class Tree(EnvironmentObject):
    """Tree object with support for 3DS models and procedural fallback"""
    
    def __init__(self, x: float, y: float, z: float, scale: float = 1.0):
        super().__init__(x, y, z, "tree", scale)
        self.height = 3.0 * scale
        self.trunk_radius = 0.15 * scale
        self.foliage_radius = 0.8 * scale
        self.color = (0.4, 0.3, 0.2)  # Brown trunk
        self.collision_radius = 0.28 * scale
    
    def render(self):
        """Render tree using 3DS model if available, else procedural"""
        tree_model = get_tree_model()
        
        if tree_model and tree_model.meshes:
            # Use 3DS model
            tree_model.render(self.x, self.y, self.z, scale=self.scale)
        else:
            # Fallback to procedural rendering
            render_tree_at(self.x, self.y, self.z, self.scale)


class Rock(EnvironmentObject):
    """Rock object"""
    
    def __init__(self, x: float, y: float, z: float, scale: float = 1.0):
        super().__init__(x, y, z, "rock", scale)
        self.size = 0.5 * scale
        self.color = (0.6, 0.6, 0.6)  # Gray
        self.collision_radius = 0.25 * scale
    
    def render(self):
        """Render rock as scaled sphere"""
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(*self.color)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, self.size, 12, 12)
        gluDeleteQuadric(quad)
        
        glPopMatrix()


class Stump(EnvironmentObject):
    """Tree stump object"""
    
    def __init__(self, x: float, y: float, z: float, scale: float = 1.0):
        super().__init__(x, y, z, "stump", scale)
        self.height = 0.4 * scale
        self.radius = 0.25 * scale
        self.color = (0.5, 0.3, 0.1)  # Brown wood
        self.collision_radius = 0.22 * scale
    
    def render(self):
        """Render stump as cylinder"""
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(*self.color)
        
        # Rotate cylinder to be vertical (gluCylinder defaults to Z-axis)
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluCylinder(quad, self.radius, self.radius * 0.9, self.height, 12, 4)
        gluDeleteQuadric(quad)
        
        glPopMatrix()


class Log(EnvironmentObject):
    """Fallen log object"""
    
    def __init__(self, x: float, y: float, z: float, scale: float = 1.0, angle: float = 0):
        super().__init__(x, y, z, "log", scale)
        self.length = 2.0 * scale
        self.radius = 0.15 * scale
        self.angle = angle  # Rotation in degrees around Y axis
        self.color = (0.4, 0.25, 0.1)
        self.collision_radius = 0.20 * scale
    
    def render(self):
        """Render log as horizontal cylinder (fallen)"""
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # Rotate around Y axis for directional variation
        glRotatef(self.angle, 0, 1, 0)
        
        # gluCylinder is drawn along Z-axis, so rotate -90 around X to make it horizontal (Z-axis aligned)
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        
        glColor3f(*self.color)
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluCylinder(quad, self.radius, self.radius, self.length, 10, 4)
        gluDeleteQuadric(quad)
        
        glPopMatrix()


class EnvironmentObjectManager:
    """Manages all environment objects in the forest"""
    
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0, model_dir: str = "models"):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.objects: List[EnvironmentObject] = []
        self.collision_objects = []
        
        # Load 3DS models on first initialization
        if not _model_cache['tree'] and not _model_cache['grass']:
            load_models(model_dir)
    
    def generate_from_forest_zones(self, forest_zones: List[Tuple[int, int]]):
        """
        Generate environment objects from forest zones.
        SIMPLIFIED: Only place trees (no collision checks).
        
        Args:
            forest_zones: List of (x, y) forest region cells
        """
        self.objects = []
        self.collision_objects = []  # Not used

        for gx, gy in forest_zones:
            # Convert grid coordinates to world coordinates
            wx = (gx - self.grid_size // 2) * self.cell_size
            wz = (gy - self.grid_size // 2) * self.cell_size
            
            # ONLY place trees
            scale = random.uniform(0.8, 1.3)
            obj = Tree(wx, 0, wz, scale)
            self.objects.append(obj)

    def remove_blocking_objects(self, path_cells: List[Tuple[int, int]], clearance: float = 0.35):
        """
        Remove any placed objects whose collision sphere intersects the path corridor.

        Args:
            path_cells: list or set of (gx, gy) grid coordinates forming the path
            clearance: extra clearance (world units) around path cell centers
        """
        if not path_cells:
            return

        remaining = []
        remaining_collision = []

        # Precompute world centers for path cells
        path_world_centers = []
        for gx, gy in path_cells:
            wx = (gx - self.grid_size // 2) * self.cell_size
            wz = (gy - self.grid_size // 2) * self.cell_size
            path_world_centers.append((wx, wz))

        for obj in self.collision_objects:
            ox, oy, oz, obj_r = obj.get_collision_sphere()
            blocked = False
            for wx, wz in path_world_centers:
                dx = ox - wx
                dz = oz - wz
                dist = math.sqrt(dx*dx + dz*dz)
                if dist < (obj_r + clearance):
                    blocked = True
                    break
            if not blocked:
                remaining.append(obj)
                remaining_collision.append(obj)

        # Update lists to keep only non-blocking objects
        self.objects = [o for o in self.objects if o in remaining]
        self.collision_objects = remaining_collision
    
    def render_all(self):
        """Render all environment objects"""
        glEnable(GL_LIGHTING)
        for obj in self.objects:
            # Prefer centralized tree renderer to avoid orientation issues
            if isinstance(obj, Tree):
                render_tree_at(obj.x, obj.y, obj.z, obj.scale)
            else:
                obj.render()

        # Debug mode: render collision spheres if enabled
        if getattr(self, 'debug', False):
            self.render_debug()

    def render_debug(self):
        """Render debug markers for collision objects (small translucent spheres)."""
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for obj in self.collision_objects:
            glPushMatrix()
            glTranslatef(obj.x, obj.y + 0.05, obj.z)
            r = min(1.0, obj.collision_radius * 1.5)
            glColor4f(1.0, 0.2, 0.2, 0.35)
            quad = gluNewQuadric()
            gluSphere(quad, r, 8, 8)
            gluDeleteQuadric(quad)
            glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def check_collision(self, position: Tuple[float, float, float], 
                       collision_radius: float = 0.25) -> bool:
        """
        Check if a position collides with any environment object.
        
        Args:
            position: (x, y, z) position to check
            collision_radius: Radius of the checking sphere
        
        Returns:
            True if collision detected, False otherwise
        """
        px, py, pz = position
        
        for obj in self.collision_objects:
            ox, oy, oz, obj_radius = obj.get_collision_sphere()
            
            # Calculate distance
            dx = px - ox
            dy = py - oy
            dz = pz - oz
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Check collision
            if dist < (collision_radius + obj_radius):
                return True
        
        return False
    
    def get_closest_object(self, position: Tuple[float, float, float]) -> EnvironmentObject:
        """Get closest environment object to a position"""
        px, py, pz = position
        closest = None
        closest_dist = float('inf')
        
        for obj in self.objects:
            ox, oy, oz = obj.get_position()
            dx = px - ox
            dy = py - oy
            dz = pz - oz
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < closest_dist:
                closest_dist = dist
                closest = obj
        
        return closest
