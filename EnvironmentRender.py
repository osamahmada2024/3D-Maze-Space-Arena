<<<<<<< HEAD
import sys
import pygame
import random
from typing import List, Tuple

# ==================== CONFIG ====================
class RenderConfig:
    """Configuration for rendering."""
    cell_size = 36
    margin = 4
    window_padding = 18
    radius = 7

    grid_background_color = (28, 34, 30)
    floor_top_color = (20, 25, 22)
    floor_bottom_color = (15, 20, 18)

    tile_color = (100, 200, 120)
    tile_alt_color = (85, 180, 105)
    obstacle_color = (50, 50, 60)

    shadow_color = (0, 0, 0, 120)
    shading_color = (255, 255, 255, 45)

    hover_color = (255, 240, 100)
    start_color = (230, 80, 80)
    goal_color = (255, 210, 50)
    path_color = (70, 170, 255)

    fps = 60


# ==================== ENVIRONMENT RENDERER  ====================
class EnvironmentRender:

    def __init__(self, grid: List[List[int]], cfg: RenderConfig = RenderConfig()):
        """Initialize with grid and configuration."""
        # Required input
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        
        # Configuration
        self.cfg = cfg
        
        # Internal state - grid utilities
        self._in_bounds = lambda x, y: 0 <= x < self.cols and 0 <= y < self.rows
        self._is_free = lambda x, y: self._in_bounds(x, y) and self.grid[y][x] == 0
        
        # Internal state - view controller 
        self.hover_cell = None
        self.selected_cell = None
        
        # Window dimensions
        self.cell_w = cfg.cell_size
        self.cell_h = cfg.cell_size
        self.margin = cfg.margin
        self.padding = cfg.window_padding

        self.window_width = self.cols * (self.cell_w + self.margin) + self.padding * 2 - self.margin
        self.window_height = self.rows * (self.cell_h + self.margin) + self.padding * 2 - self.margin

        # cached centers for path drawing
        self._centers_cache = {}

    # ==================== COORDINATE CONVERSION ====================
    def cell_to_screen_rect(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """Convert grid cell to screen rectangle."""
        px = self.padding + x * (self.cell_w + self.margin)
        py = self.padding + y * (self.cell_h + self.margin)
        return px, py, self.cell_w, self.cell_h

    def cell_center(self, x: int, y: int) -> Tuple[int, int]:
        """Get center point of a cell."""
        if (x, y) in self._centers_cache:
            return self._centers_cache[(x, y)]
        px, py, w, h = self.cell_to_screen_rect(x, y)
        center = (px + w // 2, py + h // 2)
        self._centers_cache[(x, y)] = center
        return center

    # ==================== WINDOW MANAGEMENT ====================
    def make_window(self):
        """Create pygame window."""
        pygame.init()
        screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Environment Renderer")
        return screen

    # ==================== PUBLIC: DRAW FLOOR ====================
    def draw_floor(self, surface):
        """
        PUBLIC METHOD (Page 7 Requirement)
        Draw gradient floor background.
        """
        top = self.cfg.floor_top_color
        bottom = self.cfg.floor_bottom_color
        w, h = surface.get_size()
        for i in range(h):
            t = i / h
            color = (
                int(top[0] * (1 - t) + bottom[0] * t),
                int(top[1] * (1 - t) + bottom[1] * t),
                int(top[2] * (1 - t) + bottom[2] * t),
            )
            pygame.draw.line(surface, color, (0, i), (w, i))

    # ==================== PRIVATE: SHADOW ====================
    def _draw_shadow(self, surface, rect):
        """Internal helper: Draw a drop shadow under a tile."""
        x, y, w, h = rect
        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        shadow.fill(self.cfg.shadow_color)
        surface.blit(shadow, (x + 3, y + 3))

    # ==================== PRIVATE: SINGLE TILE ====================
    def _draw_tile(self, surface, rect, *, is_obstacle=False, alt=False, hover=False):
        """Internal helper: Draw a single tile with all effects."""
        x, y, w, h = rect

        # shadow
        self._draw_shadow(surface, rect)

        # tile base
        color = self.cfg.obstacle_color if is_obstacle else (self.cfg.tile_alt_color if alt else self.cfg.tile_color)
        pygame.draw.rect(surface, color, pygame.Rect(x, y, w, h), border_radius=self.cfg.radius)

        # thin grid line
        pygame.draw.rect(surface, (35, 45, 40), pygame.Rect(x, y, w, h), width=1, border_radius=self.cfg.radius)

        # hover outline
        if hover:
            pygame.draw.rect(surface, self.cfg.hover_color, pygame.Rect(x + 2, y + 2, w - 4, h - 4), width=3, border_radius=self.cfg.radius)

    # ==================== PUBLIC: DRAW TILES ====================
    def draw_tiles(self, surface: pygame.Surface):
        """
        PUBLIC METHOD (Page 7 Requirement)
        Draw all tiles on the grid (free cells and obstacles).
        """
        for y in range(self.rows):
            for x in range(self.cols):
                rect = self.cell_to_screen_rect(x, y)
                is_obstacle = (self.grid[y][x] == 1)
                # alternate tile pattern for subtle variation
                alt = ((x + y) % 2 == 0)
                hover = (self.hover_cell == (x, y))
                self._draw_tile(surface, rect, is_obstacle=is_obstacle, alt=alt, hover=hover)

    # ==================== PRIVATE: START/GOAL/PATH ====================
    def _draw_start(self, surface, rect):
        """Internal helper: Draw start marker."""
        x, y, w, h = rect
        inner = (x + 6, y + 6, w - 12, h - 12)
        pygame.draw.rect(surface, self.cfg.start_color, inner, border_radius=self.cfg.radius)

    def _draw_goal(self, surface, rect):
        """Internal helper: Draw goal marker."""
        x, y, w, h = rect
        cx, cy = x + w // 2, y + h // 2
        radius = min(w, h) // 3
        pygame.draw.circle(surface, self.cfg.goal_color, (cx, cy), radius)

    def _draw_path(self, surface, points):
        """Internal helper: Draw a path line with nodes."""
        if len(points) < 2:
            return
        pygame.draw.lines(surface, self.cfg.path_color, False, points, width=4)
        for p in points:
            pygame.draw.circle(surface, self.cfg.path_color, p, 5)

    # ==================== MAIN DRAW METHOD ====================
    def draw(self, surface: pygame.Surface, *, start: Tuple[int, int] = None, goal: Tuple[int, int] = None, path: List[Tuple[int, int]] = None):
        """Main draw method - renders everything."""
        # Draw floor (PUBLIC METHOD)
        self.draw_floor(surface)

        # Draw tiles (PUBLIC METHOD)
        self.draw_tiles(surface)

        # Draw path 
        if path:
            centers = [self.cell_center(px, py) for (px, py) in path]
            self._draw_path(surface, centers)

        # Draw start/goal overlays
        if start:
            if self._in_bounds(start[0], start[1]):
                self._draw_start(surface, self.cell_to_screen_rect(start[0], start[1]))

        if goal:
            if self._in_bounds(goal[0], goal[1]):
                self._draw_goal(surface, self.cell_to_screen_rect(goal[0], goal[1]))

    # ==================== MOUSE HANDLING ====================
    def handle_mouse(self, mouse_pos):
        """Translate mouse position to grid cell."""
        mx, my = mouse_pos
        rx = mx - self.padding
        ry = my - self.padding
        if rx < 0 or ry < 0:
            self.hover_cell = None
            return
        cell_w_total = self.cell_w + self.margin
        x = rx // cell_w_total
        y = ry // cell_w_total
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.hover_cell = (int(x), int(y))
        else:
            self.hover_cell = None


# ==================== HELPERS FOR TESTING (Can be removed) ====================
class GridGenerator:
    """Generate random grids with obstacles."""

    def __init__(self, grid_size: int = 16, obstacle_prob: float = 0.18):
        self.grid_size = grid_size
        self.obstacle_prob = obstacle_prob
        self.grid = []

    def generate(self) -> List[List[int]]:
        """Generate a random grid (0=free, 1=obstacle)."""
        self.grid = []
        for y in range(self.grid_size):
            row = []
            for x in range(self.grid_size):
                val = 1 if random.random() < self.obstacle_prob else 0
                row.append(val)
            self.grid.append(row)
        return self.grid


class GridUtils:
    """Utility functions for grid operations."""

    def __init__(self, grid: List[List[int]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows else 0

    def in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within grid bounds."""
        return 0 <= x < self.cols and 0 <= y < self.rows

    def free(self, x: int, y: int) -> bool:
        """Check if a cell is free (0)."""
        if not self.in_bounds(x, y):
            return False
        return self.grid[y][x] == 0


# # ==================== MAIN (For Testing) ====================
# def main():
#     """Main application loop."""
#     GRID_SIZE = 20
#     OBSTACLE_PROB = 0.18

#     # Generate grid using helper (can be removed later)
#     gen = GridGenerator(grid_size=GRID_SIZE, obstacle_prob=OBSTACLE_PROB)
#     grid = gen.generate()
    
#     # Find start/goal using helper (can be removed later)
#     utils = GridUtils(grid)
#     start = None
#     goal = None
#     for y in range(GRID_SIZE):
#         for x in range(GRID_SIZE):
#             if utils.free(x, y):
#                 if start is None:
#                     start = (x, y)
#                 elif goal is None:
#                     goal = (x, y)
#         if goal:
#             break

#     # Create renderer (THIS IS THE MAIN CLASS FROM PAGE 7)
#     renderer = EnvironmentRender(grid)
#     screen = renderer.make_window()
#     clock = pygame.time.Clock()

#     # Generate demo path
#     if start and goal:
#         path = []
#         sx, sy = start
#         gx, gy = goal
#         steps = max(abs(gx - sx), abs(gy - sy))
#         if steps == 0:
#             path = [start]
#         else:
#             for i in range(steps + 1):
#                 t = i / steps
#                 x = round(sx + (gx - sx) * t)
#                 y = round(sy + (gy - sy) * t)
#                 path.append((x, y))
#     else:
#         path = None

#     running = True
#     while running:
#         dt = clock.tick(renderer.cfg.fps) / 1000.0
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             elif event.type == pygame.MOUSEMOTION:
#                 renderer.handle_mouse(event.pos)
#             elif event.type == pygame.MOUSEBUTTONDOWN:
#                 renderer.selected_cell = renderer.hover_cell

#         renderer.draw(screen, start=start, goal=goal, path=path)
#         pygame.display.flip()

#     pygame.quit()
#     sys.exit()


# if __name__ == "__main__":
#     main()
=======
# EnvironmentRender3D.py
# Enhanced environment renderer — Perlin ground mesh, improved mountains and trees with COLORS.
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
    GROUND_RES = 32        # grid resolution per side (higher = smoother ground)
    GROUND_NOISE_SCALE = 0.7
    GROUND_NOISE_AMP = 0.25  # max ground height (in cell units)

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

        # lighting — slightly brighter to showcase colors
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.22, 0.22, 0.24, 1.0])
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
    # Ground mesh (Perlin heightfield) — NOW WITH GRASS/SOIL COLORS
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

        # trunk — warm golden-brown wood
        apply_material(0.50, 0.32, 0.16, shininess=10)
        glPushMatrix()
        glTranslatef(x, 0.0, z)
        quad = gluNewQuadric(); gluQuadricNormals(quad, GLU_SMOOTH)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quad, trunk_r, max(0.06* self.cell_size, trunk_r*0.7), trunk_h, 12, 6)
        gluDeleteQuadric(quad)
        glPopMatrix()

        # leaves — BRIGHT LIME GREEN (was too dark before)
        apply_material(0.35, 0.78, 0.24, shininess=14)
        glPushMatrix()
        glTranslatef(x, trunk_h + 0.05 * self.cell_size, z)
        quad2 = gluNewQuadric(); gluQuadricNormals(quad2, GLU_SMOOTH)
        gluSphere(quad2, leaf1, 16, 12)
        gluDeleteQuadric(quad2)
        glPopMatrix()

        # secondary leaves — EVEN BRIGHTER GREEN for depth
        apply_material(0.40, 0.82, 0.28, shininess=14)
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

    def _draw_floor(self):
        pass

    def _draw_mountains(self):
        glPushMatrix()
        glTranslatef(-self.grid_size * 0.42 * self.cell_size, 0.0, -self.grid_size * 0.7 * self.cell_size)
        glScalef(self.cell_size, self.cell_size, self.cell_size)
        radius1 = max(2.0, self.grid_size * 0.06)
        height1 = max(2.8, self.grid_size * 0.12)
        self._draw_mountain_mesh(radius1, height1, radial_res=28, angular_res=68, noise_scale=1.0, noise_amp=1.05, seed=42)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(self.grid_size * 0.5 * self.cell_size, 0.0, self.grid_size * 0.85 * self.cell_size)
        glScalef(self.cell_size, self.cell_size, self.cell_size)
        radius2 = max(2.4, self.grid_size * 0.07)
        height2 = max(3.6, self.grid_size * 0.14)
        self._draw_mountain_mesh(radius2, height2, radial_res=24, angular_res=60, noise_scale=0.9, noise_amp=0.9, seed=999)
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

        - Each particle uses its 'ttl' timer; when ttl <= 0 it is respawned.
        - Particles are drawn with an inner solid (additive) sphere and a larger
          outer translucent glow sphere. Lighting is disabled for them.
        """
        # compute dt from the last call so ttl updates are time-consistent
        if self._last_particles_time is None:
            dt = 0.0
        else:
            dt = max(0.0, t - self._last_particles_time)
        self._last_particles_time = t

        # scene radius for respawn area
        S = self.grid_size * self.cell_size * 0.5

        # prepare GL state for additive glowing spheres
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        # reuse a quadric for all spheres this frame
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)

        for p in self._particles:
            # update timer and respawn if needed
            p["ttl"] -= dt
            if p["ttl"] <= 0.0:
                # respawn in a new random position and reset ttl
                p["x"] = random.uniform(-S, S)
                p["z"] = random.uniform(-S, S)
                p["y_base"] = random.uniform(0.6, 1.8)
                p["phase"] = random.uniform(0.0, math.pi * 2.0)
                p["speed"] = random.uniform(0.6, 1.6)
                p["size"] = random.uniform(3.0, 6.0)
                p["ttl"] = random.uniform(1.2, 4.0)

            # compute animated position
            x, y, z = self._update_particle_pos(p, t)

            # size tuning: convert p["size"] (~3..6) into world radius
            base_radius = 0.06 * self.cell_size  # base radius for the inner sphere
            radius = base_radius * (p["size"] / 4.5)

            # alpha pulsates with time; clamp to [0,1]
            alpha = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * p["speed"] + p["phase"]))
            alpha = max(0.02, min(1.0, alpha))

            # lower alpha when very close to respawn to give popping effect
            # (optional subtle fade when ttl is small)
            if p["ttl"] < 0.35:
                alpha *= max(0.0, p["ttl"] / 0.35)

            # Draw inner solid core (small bright sphere)
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor4f(1.0, 0.95, 0.6, alpha)
            gluSphere(quad, radius, 12, 8)
            glPopMatrix()

            # Draw outer glow (larger, softer, more transparent)
            glow_radius = radius * 2.6
            glow_alpha = alpha * 0.45

            # disable depth write so glows blend nicely over objects
            glDepthMask(GL_FALSE)
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor4f(1.0, 0.95, 0.6, glow_alpha)
            gluSphere(quad, glow_radius, 12, 8)
            glPopMatrix()
            glDepthMask(GL_TRUE)

        gluDeleteQuadric(quad)

        # restore GL state
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glPointSize(4.0)
        glBegin(GL_POINTS)
        for p in self._particles:
            x, y, z = self._update_particle_pos(p, t)
            alpha = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(t * p["speed"] + p["phase"]))
            glColor4f(1.0, 0.95, 0.6, alpha)
            glVertex3f(x, y, z)
        glEnd()

        glPointSize(1.5)
        glBegin(GL_POINTS)
        for p in self._particles:
            x, y, z = self._update_particle_pos(p, t)
            glColor4f(1.0, 0.98, 0.6, 1.0)
            glVertex3f(x, y, z)
        glEnd()

        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

    def draw(self, time_value):
        self._draw_sky_dome()
        self._draw_ground_mesh()
        self._draw_mountains()
        self._draw_obstacles()
        self._draw_forest()
        self._draw_particles(time_value)
>>>>>>> origin/enviroment-design
