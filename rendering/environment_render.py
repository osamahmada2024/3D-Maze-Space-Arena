# rendering/EnvironmentRender.py

import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *

try:
    import numpy as np
except Exception:
    np = None

from noise import pnoise2

def apply_material(r, g, b, shininess=24):
    ambient = [r * 0.25, g * 0.25, b * 0.25, 1.0]
    diffuse = [r, g, b, 1.0]
    specular = [0.6, 0.6, 0.6, 1.0]
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, ambient)
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, diffuse)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)


class EnvironmentRender3D:
    """
    Environment renderer - OPTIMIZED VERSION with path collision avoidance
    Uses Display Lists for static geometry
    """

    GROUND_RES = 64
    GROUND_NOISE_SCALE = 0.9
    GROUND_NOISE_AMP = 0.6

    def __init__(self, grid, cell_size=1.0, agent_path=None):
        self.grid = grid
        self.grid_size = len(grid)
        self.cell_size = float(cell_size) if cell_size else 1.0
        self.agent_path = agent_path

        self._particles = []
        self._tree_instances = []
        
        self._shared_quadric = gluNewQuadric()
        gluQuadricNormals(self._shared_quadric, GLU_SMOOTH)
        
        self._ground_display_list = None
        self._mountains_display_list = None
        self._obstacles_display_list = None
        self._forest_display_list = None
        self._sky_display_list = None
        
        self._path_cells = set()
        if agent_path:
            for pos in agent_path:
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        self._path_cells.add((pos[0] + dx, pos[1] + dy))
        
        # Tree instances - with collision detection
        _tree_points = [
            (-5, 4), (6, -3), (-4, -6), (3, 8), (8, 8),
            (-8, 6), (7, -7), (-9, -3), (2, -2), (-3, 5),
            (4, 4), (-6, -1), (5, -5), (-7, 7), (9, -2)
        ]
        
        rnd = random.Random(42)
        for (tx, tz) in _tree_points:
            tree_grid_x = tx + self.grid_size // 2
            tree_grid_z = tz + self.grid_size // 2
            
            if self._is_safe_position(tree_grid_x, tree_grid_z):
                trunk_h = 0.9 * self.cell_size * rnd.uniform(0.85, 1.25)
                trunk_r = 0.12 * self.cell_size * rnd.uniform(0.9, 1.1)
                leaf1 = 0.45 * self.cell_size * rnd.uniform(0.8, 1.1)
                leaf2 = 0.33 * self.cell_size * rnd.uniform(0.8, 1.1)
                offset_x = 0.12 * self.cell_size * rnd.uniform(0.8, 1.2)
                offset_z = 0.08 * self.cell_size * rnd.uniform(0.6, 1.0)
                self._tree_instances.append({
                    "x": tx * self.cell_size,
                    "z": tz * self.cell_size,
                    "trunk_h": trunk_h,
                    "trunk_r": trunk_r,
                    "leaf1": leaf1,
                    "leaf2": leaf2,
                    "offset_x": offset_x,
                    "offset_z": offset_z
                })
        
        self._init_particles(48)
        self._mesh_cache = {}
        self._ground_mesh = None
        self._last_particles_time = None

        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)

        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.10, 0.10, 0.10, 1.0])
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [-20.0, 40.0, -20.0, 0.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.65, 0.63, 0.68, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.58, 0.58, 0.62, 1.0])
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.001)
        glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.0005)

        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, [0.05, 0.06, 0.09, 1.0])
        glFogf(GL_FOG_DENSITY, 0.018)
        glFogi(GL_FOG_MODE, GL_EXP2)
        
        self._build_all_display_lists()

    def __del__(self):
        """Clean up resources"""
        try:
            gluDeleteQuadric(self._shared_quadric)
        except:
            pass

    def _is_safe_position(self, grid_x, grid_z):
        if grid_x < 0 or grid_x >= self.grid_size or grid_z < 0 or grid_z >= self.grid_size:
            return False
        
        if (grid_x, grid_z) in self._path_cells:
            return False
        
        if self.grid[grid_z][grid_x] == 1:
            return False
        
        return True

    def _get_safe_mountain_positions(self):
        """Get safe positions for mountains away from the path"""
        safe_positions = []
        
        potential_positions = [
            (-self.grid_size * 0.25, -self.grid_size * 0.10),
            (self.grid_size * 0.20, self.grid_size * 0.055),
            (0.0, self.grid_size * 0.35),
            (-self.grid_size * 0.30, self.grid_size * 0.25),
            (self.grid_size * 0.28, -self.grid_size * 0.20),
        ]
        
        for pos in potential_positions:
            x_pos, z_pos = pos
            grid_x = int((x_pos / self.cell_size) + self.grid_size // 2)
            grid_z = int((z_pos / self.cell_size) + self.grid_size // 2)
            
            is_safe = True
            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    check_x = grid_x + dx
                    check_z = grid_z + dz
                    if (check_x, check_z) in self._path_cells:
                        is_safe = False
                        break
                if not is_safe:
                    break
            
            if is_safe:
                safe_positions.append(pos)
            
            if len(safe_positions) >= 3:
                break
        
        return safe_positions

    def _init_particles(self, n):
        S = self.grid_size * self.cell_size * 0.5
        for _ in range(n):
            p = {
                "x": random.uniform(-S, S),
                "z": random.uniform(-S, S),
                "y_base": random.uniform(0.6, 1.8),
                "phase": random.uniform(0.0, math.pi * 2.0),
                "speed": random.uniform(0.6, 1.6),
                "size": random.uniform(3.0, 6.0),
                "ttl": random.uniform(1.2, 4.0),
            }
            self._particles.append(p)

    # =========================================================================
    # =========================================================================
    
    def _build_all_display_lists(self):
        """Build all Display Lists once"""
        print("[ENV] Building display lists...")
        
        # Sky
        self._sky_display_list = glGenLists(1)
        glNewList(self._sky_display_list, GL_COMPILE)
        self._build_sky_dome()
        glEndList()
        
        # Ground
        self._ground_display_list = glGenLists(1)
        glNewList(self._ground_display_list, GL_COMPILE)
        self._build_ground()
        glEndList()
        
        # Mountains - with collision detection
        self._mountains_display_list = glGenLists(1)
        glNewList(self._mountains_display_list, GL_COMPILE)
        self._build_mountains()
        glEndList()
        
        # Obstacles
        self._obstacles_display_list = glGenLists(1)
        glNewList(self._obstacles_display_list, GL_COMPILE)
        self._build_obstacles()
        glEndList()
        
        # Forest
        self._forest_display_list = glGenLists(1)
        glNewList(self._forest_display_list, GL_COMPILE)
        self._build_forest()
        glEndList()
        
        print("[ENV] Display lists built successfully!")

    def _build_sky_dome(self):
        """Build the sky"""
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glColor3f(0.035, 0.045, 0.08)
        glTranslatef(0.0, -2.5, 0.0)
        radius = max(60, self.grid_size * self.cell_size * 3.0)
        gluSphere(self._shared_quadric, radius, 36, 20)
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def _build_ground(self):
        """Build the ground"""
        mesh = self._build_ground_mesh()
        verts = mesh["verts"]
        normals = mesh["normals"]
        indices = mesh["indices"]

        apply_material(0.12, 0.14, 0.08, shininess=8)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)

        glBegin(GL_TRIANGLES)
        for tri in indices:
            for vi in tri:
                n = normals[vi]
                v = verts[vi]
                slope = max(0.0, min(1.0, n[1]))
                
                soil = (0.12, 0.10, 0.08)
                grass = (0.18, 0.28, 0.12)
                moss = (0.15, 0.22, 0.10)
                
                if slope > 0.7:
                    r = soil[0] * 0.2 + grass[0] * 0.8
                    g = soil[1] * 0.2 + grass[1] * 0.8
                    b = soil[2] * 0.2 + grass[2] * 0.8
                elif slope > 0.4:
                    r = soil[0] * 0.4 + moss[0] * 0.6
                    g = soil[1] * 0.4 + moss[1] * 0.6
                    b = soil[2] * 0.4 + moss[2] * 0.6
                else:
                    r, g, b = soil
                
                glColor3f(r, g, b)
                glNormal3f(n[0], n[1], n[2])
                glVertex3f(v[0], v[1], v[2])
        glEnd()
        glColor3f(1.0, 1.0, 1.0)

    def _build_ground_mesh(self):
        if self._ground_mesh is not None:
            return self._ground_mesh

        res = max(8, int(self.GROUND_RES))
        size = self.grid_size * self.cell_size
        half = size * 0.5

        verts = []
        normals = []
        indices = []

        for j in range(res + 1):
            z = -half + (j / res) * size
            for i in range(res + 1):
                x = -half + (i / res) * size
                nx = x * (self.GROUND_NOISE_SCALE / max(1.0, size))
                nz = z * (self.GROUND_NOISE_SCALE / max(1.0, size))
                h = pnoise2(nx, nz, repeatx=1024, repeaty=1024)
                y = h * self.GROUND_NOISE_AMP * self.cell_size
                verts.append([x, y, z])
                normals.append([0.0, 1.0, 0.0])

        def idx(i, j):
            return j * (res + 1) + i

        for j in range(res):
            for i in range(res):
                v00 = idx(i, j)
                v10 = idx(i + 1, j)
                v01 = idx(i, j + 1)
                v11 = idx(i + 1, j + 1)
                indices.append((v00, v01, v11))
                indices.append((v00, v11, v10))

        for tri in indices:
            i0, i1, i2 = tri
            v0 = verts[i0]; v1 = verts[i1]; v2 = verts[i2]
            ex1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
            ex2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
            nx = ex1[1]*ex2[2] - ex1[2]*ex2[1]
            ny = ex1[2]*ex2[0] - ex1[0]*ex2[2]
            nz = ex1[0]*ex2[1] - ex1[1]*ex2[0]
            normals[i0][0] += nx; normals[i0][1] += ny; normals[i0][2] += nz
            normals[i1][0] += nx; normals[i1][1] += ny; normals[i1][2] += nz
            normals[i2][0] += nx; normals[i2][1] += ny; normals[i2][2] += nz

        for i, n in enumerate(normals):
            lx, ly, lz = n
            l = math.sqrt(lx*lx + ly*ly + lz*lz) + 1e-9
            normals[i] = [lx/l, ly/l, lz/l]

        self._ground_mesh = {"verts": verts, "normals": normals, "indices": indices}
        return self._ground_mesh

    def get_ground_height(self, x_world, z_world):
        size = self.grid_size * self.cell_size
        nx = x_world * (self.GROUND_NOISE_SCALE / max(1.0, size))
        nz = z_world * (self.GROUND_NOISE_SCALE / max(1.0, size))
        try:
            h = pnoise2(nx, nz, repeatx=1024, repeaty=1024)
        except Exception:
            h = 0.0
        y = h * self.GROUND_NOISE_AMP * self.cell_size
        return y

    def _build_mountains(self):
        """Build mountains in safe positions only"""
        safe_positions = self._get_safe_mountain_positions()
        
        configs = [
            (max(1.0, self.grid_size * 0.03) * 1.25, max(1.7, self.grid_size * 0.069) * 1.25, 20, 48, 0.9, 0.99, 11),
            (max(0.8, self.grid_size * 0.025) * 1.25, max(1.6, self.grid_size * 0.059) * 1.25, 18, 44, 0.8, 0.89, 42),
            (max(0.9, self.grid_size * 0.028) * 1.25, max(1.1, self.grid_size * 0.055) * 1.25, 20, 52, 1.0, 0.95, 999),
        ]
        
        for i, pos in enumerate(safe_positions):
            if i >= len(configs):
                break
            
            x_pos, z_pos = pos
            cfg = configs[i]
            radius, height, radial_res, angular_res, noise_scale, noise_amp, seed = cfg
            glPushMatrix()
            glTranslatef(x_pos * self.cell_size, 0.0, z_pos * self.cell_size)
            glScalef(self.cell_size, self.cell_size, self.cell_size)
            self._build_mountain_mesh_geometry(radius, height, radial_res, angular_res, noise_scale, noise_amp, seed)
            glPopMatrix()

    def _build_mountain_mesh_geometry(self, radius, height, radial_res, angular_res, noise_scale, noise_amp, seed):
        """Draw the mountain directly (for the display list)"""
        mesh = self._get_or_build_mountain_mesh(radius, height, radial_res, angular_res, noise_scale, noise_amp, seed)
        verts = mesh["verts"]
        normals = mesh["normals"]
        indices = mesh["indices"]

        apply_material(0.28, 0.24, 0.18, shininess=12)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)

        glBegin(GL_TRIANGLES)
        for tri in indices:
            for vi in tri:
                n = normals[vi]
                v = verts[vi]
                up_dot = max(0.0, min(1.0, n[1]))
                
                rock = (0.28, 0.22, 0.16)
                snow = (0.96, 0.98, 1.0)
                moss = (0.16, 0.24, 0.10)
                
                if up_dot > 0.8:
                    r = rock[0] * 0.1 + snow[0] * 0.9
                    g = rock[1] * 0.1 + snow[1] * 0.9
                    b = rock[2] * 0.1 + snow[2] * 0.9
                elif up_dot > 0.5:
                    r = rock[0] * 0.5 + moss[0] * 0.5
                    g = rock[1] * 0.5 + moss[1] * 0.5
                    b = rock[2] * 0.5 + moss[2] * 0.5
                else:
                    r, g, b = rock
                
                glColor3f(r, g, b)
                glNormal3f(n[0], n[1], n[2])
                glVertex3f(v[0], v[1], v[2])
        glEnd()
        glColor3f(1.0, 1.0, 1.0)

    def _get_or_build_mountain_mesh(self, radius, height, radial_res, angular_res, noise_scale, noise_amp, seed):
        key = ("mount", radius, height, radial_res, angular_res, noise_scale, noise_amp, seed)
        if key in self._mesh_cache:
            return self._mesh_cache[key]

        if seed is None:
            seed = random.randint(0, 10000)

        verts = []
        normals = []
        indices = []

        for r_i in range(radial_res + 1):
            r_frac = r_i / float(radial_res)
            r_world = r_frac * radius
            for a_i in range(angular_res):
                theta = (a_i / float(angular_res)) * 2.0 * math.pi
                x = math.cos(theta) * r_world
                z = math.sin(theta) * r_world
                base_profile = (1.0 - r_frac)
                n_val = 0.0
                freq = 1.0
                amp = 1.0
                for octv in range(3):
                    nx = (x + seed) * (noise_scale * freq) / max(1.0, radius)
                    nz = (z + seed) * (noise_scale * freq) / max(1.0, radius)
                    n_val += pnoise2(nx, nz, repeatx=1024, repeaty=1024) * amp    
                    freq *= 2.0
                    amp *= 0.5
                y = max(0.0, base_profile * height + (n_val * noise_amp * base_profile * height * 0.6))
                verts.append([x, y, z])
                normals.append([0.0, 0.0, 0.0])

        def vindex(r, a):
            return r * angular_res + (a % angular_res)

        for r_i in range(radial_res):
            for a_i in range(angular_res):
                v00 = vindex(r_i, a_i)
                v10 = vindex(r_i+1, a_i)
                v01 = vindex(r_i, a_i+1)
                v11 = vindex(r_i+1, a_i+1)
                indices.append((v00, v10, v11))
                indices.append((v00, v11, v01))

        for tri in indices:
            i0, i1, i2 = tri
            v0 = verts[i0]; v1 = verts[i1]; v2 = verts[i2]
            ex1 = (v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2])
            ex2 = (v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2])
            nx = ex1[1]*ex2[2] - ex1[2]*ex2[1]
            ny = ex1[2]*ex2[0] - ex1[0]*ex2[2]
            nz = ex1[0]*ex2[1] - ex1[1]*ex2[0]
            normals[i0][0] += nx; normals[i0][1] += ny; normals[i0][2] += nz
            normals[i1][0] += nx; normals[i1][1] += ny; normals[i1][2] += nz
            normals[i2][0] += nx; normals[i2][1] += ny; normals[i2][2] += nz

        for i, n in enumerate(normals):
            lx, ly, lz = n
            l = math.sqrt(lx*lx + ly*ly + lz*lz) + 1e-9
            normals[i] = [lx/l, ly/l, lz/l]

        mesh = {"verts": verts, "normals": normals, "indices": indices}
        self._mesh_cache[key] = mesh
        return mesh

    def _build_obstacles(self):
        """Build obstacles"""
        half_grid = self.grid_size // 2
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x] == 1:
                    wx = (x - half_grid) * self.cell_size
                    wz = (y - half_grid) * self.cell_size
                    v = (math.sin(x * 12.17 + y * 7.31) * 0.035)
                    r = 0.32 + v * 0.15
                    g = 0.28 + v * 0.12
                    b = 0.32 + v * 0.10
                    apply_material(r, g, b, shininess=8)
                    glColor3f(r, g, b)
                    glPushMatrix()
                    glTranslatef(wx, 0.5 * self.cell_size, wz)
                    jitter = (math.sin(x * 3.13 + y * 1.7) * 0.02) * self.cell_size
                    glTranslatef(jitter, 0.0, jitter)
                    glScalef(self.cell_size * 0.9, self.cell_size * 0.9, self.cell_size * 0.9)
                    self._draw_cube(1.0)
                    glPopMatrix()

    def _build_forest(self):
        """Build trees"""
        for inst in self._tree_instances:
            self._build_tree_instance(inst)

    def _build_tree_instance(self, inst):
        """Build a single tree (for the display list)"""
        x = inst["x"]
        z = inst["z"]
        trunk_h = inst["trunk_h"]
        trunk_r = inst["trunk_r"]
        leaf1 = inst["leaf1"]
        leaf2 = inst["leaf2"]
        off_x = inst["offset_x"]
        off_z = inst["offset_z"]

        # Trunk
        apply_material(0.50, 0.32, 0.16, shininess=10)
        glColor3f(0.50, 0.32, 0.16)
        glPushMatrix()
        glTranslatef(x, 0.0, z)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(self._shared_quadric, trunk_r, max(0.06 * self.cell_size, trunk_r * 0.7), trunk_h, 12, 6)
        glPopMatrix()

        # Leaves 1
        apply_material(0.35, 0.78, 0.24, shininess=14)
        glColor3f(0.35, 0.78, 0.24)
        glPushMatrix()
        glTranslatef(x, trunk_h + 0.05 * self.cell_size, z)
        gluSphere(self._shared_quadric, leaf1, 16, 12)
        glPopMatrix()

        # Leaves 2
        apply_material(0.40, 0.82, 0.28, shininess=14)
        glColor3f(0.40, 0.82, 0.28)
        glPushMatrix()
        glTranslatef(x + off_x, trunk_h + 0.45 * self.cell_size, z - off_z)
        gluSphere(self._shared_quadric, leaf2, 14, 10)
        glPopMatrix()

    def _draw_cube(self, size):
        s = size / 2.0
        glBegin(GL_QUADS)
        glNormal3f(0,0,1); glVertex3f(-s,-s,s); glVertex3f(s,-s,s); glVertex3f(s,s,s); glVertex3f(-s,s,s)
        glNormal3f(0,0,-1); glVertex3f(-s,-s,-s); glVertex3f(-s,s,-s); glVertex3f(s,s,-s); glVertex3f(s,-s,-s)
        glNormal3f(0,1,0); glVertex3f(-s,s,-s); glVertex3f(-s,s,s); glVertex3f(s,s,s); glVertex3f(s,s,-s)
        glNormal3f(0,-1,0); glVertex3f(-s,-s,-s); glVertex3f(s,-s,-s); glVertex3f(s,-s,s); glVertex3f(-s,-s,s)
        glNormal3f(1,0,0); glVertex3f(s,-s,-s); glVertex3f(s,s,-s); glVertex3f(s,s,s); glVertex3f(s,-s,s)
        glNormal3f(-1,0,0); glVertex3f(-s,-s,-s); glVertex3f(-s,-s,s); glVertex3f(-s,s,s); glVertex3f(-s,s,-s)
        glEnd()

    def _update_particle_pos(self, p, t):
        x = p["x"] + math.sin(t * 0.6 + p["phase"]) * 0.45
        z = p["z"] + math.cos(t * 0.7 + p["phase"]) * 0.45
        y = p["y_base"] + math.sin(t * p["speed"] + p["phase"]) * 0.35
        return x, y, z

    # =========================================================================
    # =========================================================================

    def _draw_sky_dome(self):
        """Draw the sky (from Display List)"""
        if self._sky_display_list:
            glCallList(self._sky_display_list)

    def _draw_ground_mesh(self):
        """Draw the ground (from Display List)"""
        if self._ground_display_list:
            glCallList(self._ground_display_list)

    def _draw_mountains(self):
        """Draw mountains (from Display List)"""
        if self._mountains_display_list:
            glCallList(self._mountains_display_list)

    def _draw_obstacles(self):
        """Draw obstacles (from Display List)"""
        if self._obstacles_display_list:
            glCallList(self._obstacles_display_list)

    def _draw_forest(self):
        """Draw trees (from Display List)"""
        if self._forest_display_list:
            glCallList(self._forest_display_list)

    def _draw_particles(self, t):
        """Draw particles (dynamic - cannot use display list)"""
        if self._last_particles_time is None:
            dt = 0.0
        else:
            dt = max(0.0, t - self._last_particles_time)
        self._last_particles_time = t

        S = self.grid_size * self.cell_size * 0.5

        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        for p in self._particles:
            p["ttl"] -= dt
            if p["ttl"] <= 0.0:
                p["x"] = random.uniform(-S, S)
                p["z"] = random.uniform(-S, S)
                p["y_base"] = random.uniform(0.6, 1.8)
                p["phase"] = random.uniform(0.0, math.pi * 2.0)
                p["speed"] = random.uniform(0.6, 1.6)
                p["size"] = random.uniform(3.0, 6.0)
                p["ttl"] = random.uniform(1.2, 4.0)

            x, y, z = self._update_particle_pos(p, t)
            base_radius = 0.06 * self.cell_size
            radius = base_radius * (p["size"] / 4.5)

            alpha = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * p["speed"] + p["phase"]))
            alpha = max(0.02, min(1.0, alpha))

            if p["ttl"] < 0.35:
                alpha *= max(0.0, p["ttl"] / 0.35)

            glPushMatrix()
            glTranslatef(x, y, z)
            glColor4f(1.0, 0.95, 0.6, alpha)
            gluSphere(self._shared_quadric, radius, 8, 6)
            glPopMatrix()

            glow_radius = radius * 2.0
            glow_alpha = alpha * 0.3

            glDepthMask(GL_FALSE)
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor4f(1.0, 0.95, 0.6, glow_alpha)
            gluSphere(self._shared_quadric, glow_radius, 6, 4)
            glPopMatrix()
            glDepthMask(GL_TRUE)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

    # =========================================================================
    # ✅ Main Draw
    # =========================================================================

    def draw(self, time_value):
        """The main drawing function"""
        self._draw_sky_dome()
        self._draw_ground_mesh()
        self._draw_mountains()
        self._draw_obstacles()
        self._draw_forest()
        self._draw_particles(time_value)