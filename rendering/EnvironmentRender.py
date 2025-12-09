# EnvironmentRender.py
# Enhanced environment renderer – Perlin ground mesh, improved mountains and trees with COLORS.
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
    Environment renderer with:
    - Perlin-ground mesh (gentle terrain) with grass/soil colors
    - Perlin mountain meshes (cached) with rock/snow/moss colors
    - improved trees (varied) with wood + leaf colors
    """

    # TUNING: change these to trade quality vs speed
    GROUND_RES = 64        # increased resolution for smoother, more detailed ground
    GROUND_NOISE_SCALE = 0.9
    GROUND_NOISE_AMP = 0.6   # larger amplitude so terrain relief is clearly visible

    def __init__(self, grid, cell_size=1.0):
        self.grid = grid
        self.grid_size = len(grid)
        self.cell_size = float(cell_size) if cell_size else 1.0

        self._particles = []
        # precompute tree instances (positions + deterministic random parameters)
        self._tree_instances = []
        _tree_points = [
            (-5, 4), (6, -3), (-4, -6), (3, 8), (8, 8),
            (-8, 6), (7, -7), (-9, -3)
        ]
        # seed for reproducible forest layout each run
        rnd = random.Random(42)
        for (tx, tz) in _tree_points:
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

        # caches
        self._mesh_cache = {}
        self._ground_mesh = None

        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)

        # lighting – reduce global ambient so directional lighting shows relief
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.10, 0.10, 0.10, 1.0])
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [-20.0, 40.0, -20.0, 0.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.65, 0.63, 0.68, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.58, 0.58, 0.62, 1.0])
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.001)
        glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.0005)

        # fog
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, [0.05, 0.06, 0.09, 1.0])
        glFogf(GL_FOG_DENSITY, 0.018)
        glFogi(GL_FOG_MODE, GL_EXP2)

    # -------------------------
    # particles
    # -------------------------
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
                # lifecycle: ttl in seconds; when <=0 respawn somewhere else
                "ttl": random.uniform(1.2, 4.0),
            }
            self._particles.append(p)

        # track last time used for dt
        self._last_particles_time = None

    def _update_particle_pos(self, p, t):
        x = p["x"] + math.sin(t * 0.6 + p["phase"]) * 0.45
        z = p["z"] + math.cos(t * 0.7 + p["phase"]) * 0.45
        y = p["y_base"] + math.sin(t * p["speed"] + p["phase"]) * 0.35
        return x, y, z

    # -------------------------
    # small cube primitive
    # -------------------------
    def _draw_cube(self, size):
        s = size / 2.0
        glBegin(GL_QUADS)
        # front
        glNormal3f(0,0,1); glVertex3f(-s,-s,s); glVertex3f(s,-s,s); glVertex3f(s,s,s); glVertex3f(-s,s,s)
        # back
        glNormal3f(0,0,-1); glVertex3f(-s,-s,-s); glVertex3f(-s,s,-s); glVertex3f(s,s,-s); glVertex3f(s,-s,-s)
        # top
        glNormal3f(0,1,0); glVertex3f(-s,s,-s); glVertex3f(-s,s,s); glVertex3f(s,s,s); glVertex3f(s,s,-s)
        # bottom
        glNormal3f(0,-1,0); glVertex3f(-s,-s,-s); glVertex3f(s,-s,-s); glVertex3f(s,-s,s); glVertex3f(-s,-s,s)
        # right
        glNormal3f(1,0,0); glVertex3f(s,-s,-s); glVertex3f(s,s,-s); glVertex3f(s,s,s); glVertex3f(s,-s,s)
        # left
        glNormal3f(-1,0,0); glVertex3f(-s,-s,-s); glVertex3f(-s,-s,s); glVertex3f(-s,s,s); glVertex3f(-s,s,-s)
        glEnd()

    # -------------------------
    # Ground mesh (Perlin heightfield) – NOW WITH GRASS/SOIL COLORS
    # -------------------------
    def _build_ground_mesh(self):
        if self._ground_mesh is not None:
            return self._ground_mesh

        res = max(8, int(self.GROUND_RES))
        size = self.grid_size * self.cell_size
        half = size * 0.5

        # grid in world units
        verts = []
        normals = []
        indices = []

        # create vertex grid (res+1)^2
        for j in range(res + 1):
            z = -half + (j / res) * size
            for i in range(res + 1):
                x = -half + (i / res) * size

                # sample perlin at scaled coordinates
                nx = x * (self.GROUND_NOISE_SCALE / max(1.0, size))
                nz = z * (self.GROUND_NOISE_SCALE / max(1.0, size))
                h = pnoise2(nx, nz, repeatx=1024, repeaty=1024)
                y = h * self.GROUND_NOISE_AMP * self.cell_size  # small amplitude

                verts.append([x, y, z])
                normals.append([0.0, 1.0, 0.0])  # placeholder

        # indices
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

        # compute normals
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
        """
        Return the estimated ground height (y) at world coordinates (x_world, z_world).
        This uses the same Perlin sampling as the ground mesh so the result matches
        the rendered ground heights.
        """
        size = self.grid_size * self.cell_size
        # map world x/z to the normalized coordinates used when building the mesh
        nx = x_world * (self.GROUND_NOISE_SCALE / max(1.0, size))
        nz = z_world * (self.GROUND_NOISE_SCALE / max(1.0, size))
        try:
            h = pnoise2(nx, nz, repeatx=1024, repeaty=1024)
        except Exception:
            # if noise unavailable, fallback to zero height
            h = 0.0
        y = h * self.GROUND_NOISE_AMP * self.cell_size
        return y

    def _draw_ground_mesh(self):
        mesh = self._build_ground_mesh()
        verts = mesh["verts"]; normals = mesh["normals"]; indices = mesh["indices"]

        # ground material
        apply_material(0.12, 0.14, 0.08, shininess=8)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)

        glBegin(GL_TRIANGLES)
        for tri in indices:
            for vi in tri:
                n = normals[vi]; v = verts[vi]
                # color depend on slope: flat areas are grass, steep are soil
                slope = max(0.0, min(1.0, n[1]))
                
                # dark soil (base)
                soil = (0.12, 0.10, 0.08)
                # bright grass green
                grass = (0.18, 0.28, 0.12)
                # moss green (for mid-slopes)
                moss = (0.15, 0.22, 0.10)
                
                # blend: steep=soil, flat=grass, mid=moss
                if slope > 0.7:
                    # flat: mostly grass
                    r = soil[0] * 0.2 + grass[0] * 0.8
                    g = soil[1] * 0.2 + grass[1] * 0.8
                    b = soil[2] * 0.2 + grass[2] * 0.8
                elif slope > 0.4:
                    # mid-slope: moss
                    r = soil[0] * 0.4 + moss[0] * 0.6
                    g = soil[1] * 0.4 + moss[1] * 0.6
                    b = soil[2] * 0.4 + moss[2] * 0.6
                else:
                    # steep: mostly soil
                    r = soil[0]
                    g = soil[1]
                    b = soil[2]
                
                glColor3f(r, g, b)
                glNormal3f(n[0], n[1], n[2])
                glVertex3f(v[0], v[1], v[2])
        glEnd()
        glColor3f(1.0, 1.0, 1.0)

    # -------------------------
    # Mountain mesh builder (cached)
    # -------------------------
    def _build_mountain_mesh(self, radius, height, radial_res=24, angular_res=56, noise_scale=1.0, noise_amp=1.0, seed=None):
        key = ("mount", radius, height, radial_res, angular_res, noise_scale, noise_amp, seed)
        if key in self._mesh_cache:
            return self._mesh_cache[key]

        if seed is None:
            seed = random.randint(0, 10000)

        verts = []; normals = []; indices = []

        for r_i in range(radial_res + 1):
            r_frac = r_i / float(radial_res)
            r_world = r_frac * radius
            for a_i in range(angular_res):
                theta = (a_i / float(angular_res)) * 2.0 * math.pi
                x = math.cos(theta) * r_world
                z = math.sin(theta) * r_world
                base_profile = (1.0 - r_frac)
                n_val = 0.0; freq = 1.0; amp = 1.0
                for octv in range(3):
                    nx = (x + seed) * (noise_scale * freq) / max(1.0, radius)
                    nz = (z + seed) * (noise_scale * freq) / max(1.0, radius)
                    n_val += pnoise2(nx, nz, repeatx=1024, repeaty=1024) * amp    
                    freq *= 2.0; amp *= 0.5
                y = max(0.0, base_profile * height + (n_val * noise_amp * base_profile * height * 0.6))
                verts.append([x, y, z]); normals.append([0.0, 0.0, 0.0])

        def vindex(r, a): return r * angular_res + (a % angular_res)

        for r_i in range(radial_res):
            for a_i in range(angular_res):
                v00 = vindex(r_i, a_i)
                v10 = vindex(r_i+1, a_i)
                v01 = vindex(r_i, a_i+1)
                v11 = vindex(r_i+1, a_i+1)
                indices.append((v00, v10, v11)); indices.append((v00, v11, v01))

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

    

    def _draw_mountain_mesh(self, radius, height, radial_res=24, angular_res=56, noise_scale=1.0, noise_amp=1.0, seed=None):
        mesh = self._build_mountain_mesh(radius, height, radial_res, angular_res, noise_scale, noise_amp, seed)
        verts = mesh["verts"]; normals = mesh["normals"]; indices = mesh["indices"]

        apply_material(0.28, 0.24, 0.18, shininess=12)
        glEnable(GL_NORMALIZE); glShadeModel(GL_SMOOTH)

        glBegin(GL_TRIANGLES)
        for tri in indices:
            for vi in tri:
                n = normals[vi]; v = verts[vi]
                up_dot = max(0.0, min(1.0, n[1]))
                
                # rock color (warm brown)
                rock = (0.28, 0.22, 0.16)
                # snow/peak (bright white)
                snow = (0.96, 0.98, 1.0)
                # moss green for mid-slopes
                moss = (0.16, 0.24, 0.10)
                
                # blend based on upward normal (slope)
                if up_dot > 0.8:
                    # mostly upward = peak = snow
                    r = rock[0] * 0.1 + snow[0] * 0.9
                    g = rock[1] * 0.1 + snow[1] * 0.9
                    b = rock[2] * 0.1 + snow[2] * 0.9
                elif up_dot > 0.5:
                    # mid-slope = moss
                    r = rock[0] * 0.5 + moss[0] * 0.5
                    g = rock[1] * 0.5 + moss[1] * 0.5
                    b = rock[2] * 0.5 + moss[2] * 0.5
                else:
                    # steep = rock
                    r = rock[0]
                    g = rock[1]
                    b = rock[2]
                
                glColor3f(r, g, b)
                glNormal3f(n[0], n[1], n[2])
                glVertex3f(v[0], v[1], v[2])
        glEnd()
        glColor3f(1.0, 1.0, 1.0)

    # -------------------------
    # Improved tree with COLORS
    # -------------------------
    def _draw_tree_instance(self, inst):
        x = inst["x"]; z = inst["z"]
        trunk_h = inst["trunk_h"]; trunk_r = inst["trunk_r"]
        leaf1 = inst["leaf1"]; leaf2 = inst["leaf2"]
        off_x = inst["offset_x"]; off_z = inst["offset_z"]

        # trunk – warm golden-brown wood
        apply_material(0.50, 0.32, 0.16, shininess=10)
        # ensure a fallback color is set (works if color material/state changes)
        glColor3f(0.50, 0.32, 0.16)
        glPushMatrix()
        glTranslatef(x, 0.0, z)
        quad = gluNewQuadric(); gluQuadricNormals(quad, GLU_SMOOTH)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quad, trunk_r, max(0.06* self.cell_size, trunk_r*0.7), trunk_h, 12, 6)
        gluDeleteQuadric(quad)
        glPopMatrix()

        # leaves – BRIGHT LIME GREEN
        apply_material(0.35, 0.78, 0.24, shininess=14)
        glColor3f(0.35, 0.78, 0.24)
        glPushMatrix()
        glTranslatef(x, trunk_h + 0.05 * self.cell_size, z)
        quad2 = gluNewQuadric(); gluQuadricNormals(quad2, GLU_SMOOTH)
        gluSphere(quad2, leaf1, 16, 12)
        gluDeleteQuadric(quad2)
        glPopMatrix()

        # secondary leaves – EVEN BRIGHTER GREEN for depth
        apply_material(0.40, 0.82, 0.28, shininess=14)
        glColor3f(0.40, 0.82, 0.28)
        glPushMatrix()
        glTranslatef(x + off_x, trunk_h + 0.45 * self.cell_size, z - off_z)
        quad3 = gluNewQuadric(); gluQuadricNormals(quad3, GLU_SMOOTH)
        gluSphere(quad3, leaf2, 14, 10)
        gluDeleteQuadric(quad3)
        glPopMatrix()
        
    # -------------------------
    # Scene building & draw()
    # -------------------------
    def _draw_sky_dome(self):
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glColor3f(0.035, 0.045, 0.08)
        glTranslatef(0.0, -2.5, 0.0)
        quad = gluNewQuadric(); gluQuadricDrawStyle(quad, GLU_FILL)
        radius = max(60, self.grid_size * self.cell_size * 3.0)
        gluSphere(quad, radius, 36, 20)
        gluDeleteQuadric(quad)
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_mountains(self):
        """
        Place several slightly larger mountains inside the map bounds.
        Each mountain uses a deterministic seed so layout is reproducible.
        """
        # three positions inside the play area (relative to center)
        positions = [
            (-self.grid_size * 0.25 * self.cell_size, -self.grid_size * 0.10 * self.cell_size),
            ( self.grid_size * 0.20 * self.cell_size,  self.grid_size * 0.055  * self.cell_size),
            ( 0.0,                                 self.grid_size * 0.35  * self.cell_size),
        ]

        # configs: (radius, height, radial_res, angular_res, noise_scale, noise_amp, seed)
        configs = [
            (max(1.0, self.grid_size * 0.03) * 1.25, max(1.7, self.grid_size * 0.069) * 1.25, 20, 48, 0.9, 0.99, 11),
            (max(0.8, self.grid_size * 0.025) * 1.25, max(1.6, self.grid_size * 0.059) * 1.25, 18, 44, 0.8, 0.89, 42),
            (max(0.9, self.grid_size * 0.028) * 1.25, max(1.1, self.grid_size * 0.055) * 1.25, 20, 52, 1.0, 0.95, 999),
        ]

        for (pos, cfg) in zip(positions, configs):
            x_pos, z_pos = pos
            radius, height, radial_res, angular_res, noise_scale, noise_amp, seed = cfg
            glPushMatrix()
            # translate to the chosen position (already in world units)
            glTranslatef(x_pos, 0.0, z_pos)
            # scale by cell_size to match world-to-grid scaling
            glScalef(self.cell_size, self.cell_size, self.cell_size)
            # draw mountain
            self._draw_mountain_mesh(
                radius,
                height,
                radial_res=radial_res,
                angular_res=angular_res,
                noise_scale=noise_scale,
                noise_amp=noise_amp,
                seed=seed
            )
            glPopMatrix()


    def _draw_forest(self):
        for inst in self._tree_instances:
            self._draw_tree_instance(inst)

    def _draw_obstacles(self):
        base = 0.9 * self.cell_size
        half_grid = self.grid_size // 2
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x] == 1:
                    wx = (x - half_grid) * self.cell_size
                    wz = (y - half_grid) * self.cell_size
                    v = (math.sin(x * 12.17 + y * 7.31) * 0.035)
                    # warmer, more saturated obstacle colors
                    r = 0.32 + v * 0.15; g = 0.28 + v * 0.12; b = 0.32 + v * 0.10
                    apply_material(r, g, b, shininess=8)
                    # fallback color (in case material is not taking effect)
                    glColor3f(r, g, b)
                    glPushMatrix()
                    glTranslatef(wx, 0.5 * self.cell_size, wz)
                    jitter = (math.sin(x * 3.13 + y * 1.7) * 0.02) * self.cell_size
                    glTranslatef(jitter, 0.0, jitter)
                    glScalef(self.cell_size * 0.9, self.cell_size * 0.9, self.cell_size * 0.9)
                    self._draw_cube(1.0)
                    glPopMatrix()

    def _draw_particles(self, t):
        """
        Draw particles as small glowing spheres that periodically disappear
        and respawn at a different position.
        """
        if self._last_particles_time is None:
            dt = 0.0
        else:
            dt = max(0.0, t - self._last_particles_time)
        self._last_particles_time = t

        S = self.grid_size * self.cell_size * 0.5

        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)

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
            gluSphere(quad, radius, 12, 8)
            glPopMatrix()

            glow_radius = radius * 2.6
            glow_alpha = alpha * 0.45

            glDepthMask(GL_FALSE)
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor4f(1.0, 0.95, 0.6, glow_alpha)
            gluSphere(quad, glow_radius, 12, 8)
            glPopMatrix()
            glDepthMask(GL_TRUE)

        gluDeleteQuadric(quad)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

    def draw(self, time_value):
        self._draw_sky_dome()
        self._draw_ground_mesh()
        self._draw_mountains()
        self._draw_obstacles()
        self._draw_forest()
        self._draw_particles(time_value)