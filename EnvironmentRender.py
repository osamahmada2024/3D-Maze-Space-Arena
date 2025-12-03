import sys
import pygame
import random
from typing import List, Tuple


# ============================================================
#  CONFIGURATION
# ============================================================

class RenderConfig:
    """Defines rendering constants and visual configuration."""
    
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


# ============================================================
#  ENVIRONMENT RENDERER
# ============================================================

class EnvironmentRender:
    """
    Class: EnvironmentRenderer
    Purpose:
        Render a complete top-down 2D tile environment using pygame.

    Responsibilities:
        • Render terrain, obstacles, and tiled layout.
        • Provide utilities for drawing path, start, and goal.
        • Convert grid coordinates to pixel coordinates.
    """

    def __init__(self, grid: List[List[int]], cfg: RenderConfig = RenderConfig()):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows else 0

        # Configuration
        self.cfg = cfg

        # Utility lambdas
        self._in_bounds = lambda x, y: 0 <= x < self.cols and 0 <= y < self.rows
        self._is_free = lambda x, y: self._in_bounds(x, y) and self.grid[y][x] == 0

        # Hover & Selection
        self.hover_cell = None
        self.selected_cell = None

        # Layout
        self.cell_w = cfg.cell_size
        self.cell_h = cfg.cell_size
        self.margin = cfg.margin
        self.padding = cfg.window_padding

        self.window_width = (
            self.cols * (self.cell_w + self.margin)
            + self.padding * 2 - self.margin
        )
        self.window_height = (
            self.rows * (self.cell_h + self.margin)
            + self.padding * 2 - self.margin
        )

        # Center caching for path rendering
        self._centers_cache = {}

    # --------------------------------------------------------

    def cell_to_screen_rect(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """Convert a grid cell coordinate to a pixel-space rectangle."""
        px = self.padding + x * (self.cell_w + self.margin)
        py = self.padding + y * (self.cell_h + self.margin)
        return px, py, self.cell_w, self.cell_h

    def cell_center(self, x: int, y: int) -> Tuple[int, int]:
        """Return pixel center for a tile position."""
        if (x, y) not in self._centers_cache:
            px, py, w, h = self.cell_to_screen_rect(x, y)
            self._centers_cache[(x, y)] = (px + w // 2, py + h // 2)
        return self._centers_cache[(x, y)]

    # --------------------------------------------------------

    def make_window(self):
        """Create and return a pygame window surface."""
        pygame.init()
        surface = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Environment Renderer")
        return surface

    # --------------------------------------------------------

    def draw_floor(self, surface):
        """Draw gradient background."""
        top = self.cfg.floor_top_color
        bottom = self.cfg.floor_bottom_color
        width, height = surface.get_size()

        for i in range(height):
            t = i / height
            color = (
                int(top[0] * (1 - t) + bottom[0] * t),
                int(top[1] * (1 - t) + bottom[1] * t),
                int(top[2] * (1 - t) + bottom[2] * t),
            )
            pygame.draw.line(surface, color, (0, i), (width, i))

    # --------------------------------------------------------

    def _draw_shadow(self, surface, rect):
        x, y, w, h = rect
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(self.cfg.shadow_color)
        surface.blit(s, (x + 3, y + 3))

    def _draw_tile(self, surface, rect, *, is_obstacle=False, alt=False, hover=False):
        x, y, w, h = rect

        # Shadow
        self._draw_shadow(surface, rect)

        # Main tile
        color = (
            self.cfg.obstacle_color
            if is_obstacle
            else (self.cfg.tile_alt_color if alt else self.cfg.tile_color)
        )
        pygame.draw.rect(surface, color, (x, y, w, h), border_radius=self.cfg.radius)

        # Border line
        pygame.draw.rect(surface, (35, 45, 40), (x, y, w, h), 1, border_radius=self.cfg.radius)

        # Hover highlight
        if hover:
            pygame.draw.rect(
                surface,
                self.cfg.hover_color,
                (x + 2, y + 2, w - 4, h - 4),
                width=3,
                border_radius=self.cfg.radius,
            )

    # --------------------------------------------------------

    def draw_tiles(self, surface: pygame.Surface):
        """Render all tiles including obstacles."""
        for y in range(self.rows):
            for x in range(self.cols):
                rect = self.cell_to_screen_rect(x, y)
                is_obs = self.grid[y][x] == 1
                alt = (x + y) % 2 == 0
                hover = (self.hover_cell == (x, y))
                self._draw_tile(surface, rect, is_obstacle=is_obs, alt=alt, hover=hover)

    # --------------------------------------------------------

    def _draw_start(self, surface, rect):
        x, y, w, h = rect
        inner = (x + 6, y + 6, w - 12, h - 12)
        pygame.draw.rect(surface, self.cfg.start_color, inner, border_radius=self.cfg.radius)

    def _draw_goal(self, surface, rect):
        x, y, w, h = rect
        cx, cy = x + w // 2, y + h // 2
        r = min(w, h) // 3
        pygame.draw.circle(surface, self.cfg.goal_color, (cx, cy), r)

    def _draw_path(self, surface, points):
        if len(points) < 2:
            return
        pygame.draw.lines(surface, self.cfg.path_color, False, points, width=4)
        for p in points:
            pygame.draw.circle(surface, self.cfg.path_color, p, 5)

    # --------------------------------------------------------

    def draw(self, surface: pygame.Surface, *, start=None, goal=None, path=None):
        """Render the full environment: floor, tiles, and overlays."""
        self.draw_floor(surface)
        self.draw_tiles(surface)

        if path:
            pts = [self.cell_center(px, py) for (px, py) in path]
            self._draw_path(surface, pts)

        if start and self._in_bounds(*start):
            self._draw_start(surface, self.cell_to_screen_rect(*start))

        if goal and self._in_bounds(*goal):
            self._draw_goal(surface, self.cell_to_screen_rect(*goal))

    # --------------------------------------------------------

    def handle_mouse(self, pos):
        mx, my = pos
        rx = mx - self.padding
        ry = my - self.padding

        if rx < 0 or ry < 0:
            self.hover_cell = None
            return

        step = self.cell_w + self.margin
        x = rx // step
        y = ry // step

        self.hover_cell = (int(x), int(y)) if self._in_bounds(x, y) else None


# ============================================================
#  GRID GENERATOR
# ============================================================

class GridGenerator:
    """Generate a random square grid of free/obstacle tiles."""

    def __init__(self, grid_size: int = 16, obstacle_prob: float = 0.18):
        self.grid_size = grid_size
        self.obstacle_prob = obstacle_prob

    def generate(self) -> List[List[int]]:
        return [
            [1 if random.random() < self.obstacle_prob else 0 for _ in range(self.grid_size)]
            for _ in range(self.grid_size)
        ]


# ============================================================
#  GRID UTILITIES
# ============================================================

class GridUtils:
    """Helper functions for validating grid positions."""

    def __init__(self, grid: List[List[int]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows else 0

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def free(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.grid[y][x] == 0
