import pygame
import random
import sys
from typing import List, Tuple

# ==================== CONFIG ====================
class RenderConfig:
    """Configuration for rendering."""
    # Visual sizes
    cell_size = 36
    margin = 4
    window_padding = 18
    radius = 7

    # Colors (R, G, B) - FIXED FOR VISIBILITY
    grid_background_color = (28, 34, 30)
    floor_top_color = (20, 25, 22)          # ← Darker
    floor_bottom_color = (15, 20, 18)       # ← Darker

    # tile colors - MORE VIBRANT
    tile_color = (100, 200, 120)            # ← Brighter green
    tile_alt_color = (85, 180, 105)         # ← Brighter green alt
    obstacle_color = (50, 50, 60)           # ← Darker grey

    # lighting/shadow
    shadow_color = (0, 0, 0, 120)
    shading_color = (255, 255, 255, 45)

    # overlays
    hover_color = (255, 240, 100)
    start_color = (230, 80, 80)
    goal_color = (255, 210, 50)
    path_color = (70, 170, 255)

    fps = 60

# ==================== GRID GENERATOR ====================
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

    def set_manual(self, grid):
        """Manually set a grid."""
        self.grid = grid
        self.grid_size = len(grid)
        return self.grid


# ==================== GRID UTILS ====================
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


# ==================== GRID VIEW CONTROLLER ====================
class GridViewController:
    """Manages view state (hover, selection)."""

    def __init__(self):
        self.hover_cell = None
        self.selected_cell = None

    def set_hover(self, cell):
        """Set which cell is being hovered."""
        self.hover_cell = cell

    def set_selected(self, cell):
        """Set which cell is selected."""
        self.selected_cell = cell


# ==================== TILE PAINTER ====================
class TilePainter:
    """Renders individual tiles and visual elements."""

    def __init__(self, cfg: RenderConfig = RenderConfig()):
        self.cfg = cfg

    def draw_shadow(self, surface, rect):
        """Draw a drop shadow under a tile."""
        x, y, w, h = rect
        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        shadow.fill(self.cfg.shadow_color)
        surface.blit(shadow, (x + 3, y + 3))

    def draw_tile(self, surface, rect, *, is_obstacle=False, alt=False, hover=False):
        """Draw a single tile with all effects."""
        x, y, w, h = rect

        # shadow
        self.draw_shadow(surface, rect)

        # tile base - FIXED
        color = self.cfg.obstacle_color if is_obstacle else (self.cfg.tile_alt_color if alt else self.cfg.tile_color)
        
        # Draw filled rectangle directly
        pygame.draw.rect(surface, color, pygame.Rect(x, y, w, h), border_radius=self.cfg.radius)

        # thin grid line
        pygame.draw.rect(surface, (35, 45, 40), pygame.Rect(x, y, w, h), width=1, border_radius=self.cfg.radius)

        # hover outline
        if hover:
            pygame.draw.rect(surface, self.cfg.hover_color, pygame.Rect(x + 2, y + 2, w - 4, h - 4), width=3, border_radius=self.cfg.radius)

    def draw_start(self, surface, rect):
        """Draw start marker."""
        x, y, w, h = rect
        inner = (x + 6, y + 6, w - 12, h - 12)
        pygame.draw.rect(surface, self.cfg.start_color, inner, border_radius=self.cfg.radius)

    def draw_goal(self, surface, rect):
        """Draw goal marker."""
        x, y, w, h = rect
        cx, cy = x + w // 2, y + h // 2
        radius = min(w, h) // 3
        pygame.draw.circle(surface, self.cfg.goal_color, (cx, cy), radius)

    def draw_path(self, surface, points):
        """Draw a path line with nodes."""
        if len(points) < 2:
            return
        pygame.draw.lines(surface, self.cfg.path_color, False, points, width=4)
        # draw small circles at nodes
        for p in points:
            pygame.draw.circle(surface, self.cfg.path_color, p, 5)


# ==================== ENVIRONMENT RENDERER ====================
class EnvironmentRenderer:
    """Main renderer for the environment (Page 7)."""

    def __init__(self, grid: List[List[int]], cfg: RenderConfig = RenderConfig()):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.cfg = cfg
        self.painter = TilePainter(cfg)
        self.controller = GridViewController()

        self.cell_w = cfg.cell_size
        self.cell_h = cfg.cell_size
        self.margin = cfg.margin
        self.padding = cfg.window_padding

        self.window_width = self.cols * (self.cell_w + self.margin) + self.padding * 2 - self.margin
        self.window_height = self.rows * (self.cell_h + self.margin) + self.padding * 2 - self.margin

        # cached centers
        self._centers_cache = {}

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

    def make_window(self):
        """Create pygame window."""
        pygame.init()
        screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Environment Renderer")
        return screen

    def draw_floor(self, surface):
        """Draw gradient floor background."""
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

    def draw_tiles(self, surface: pygame.Surface):
        """Draw all tiles on the grid (free cells and obstacles)."""
        for y in range(self.rows):
            for x in range(self.cols):
                rect = self.cell_to_screen_rect(x, y)
                is_obstacle = (self.grid[y][x] == 1)
                # alternate tile pattern for subtle variation
                alt = ((x + y) % 2 == 0)
                hover = (self.controller.hover_cell == (x, y))
                self.painter.draw_tile(surface, rect, is_obstacle=is_obstacle, alt=alt, hover=hover)

    def draw(self, surface: pygame.Surface, *, start: Tuple[int, int] = None, goal: Tuple[int, int] = None, path: List[Tuple[int, int]] = None):
        """Main draw method - calls floor and tiles rendering."""
        # Draw floor
        self.draw_floor(surface)

        # Draw tiles
        self.draw_tiles(surface)

        # draw path if provided (convert grid coords to centers)
        if path:
            centers = [self.cell_center(px, py) for (px, py) in path]
            self.painter.draw_path(surface, centers)

        # draw start/goal overlays last so they appear on top
        if start:
            if 0 <= start[0] < self.cols and 0 <= start[1] < self.rows:
                self.painter.draw_start(surface, self.cell_to_screen_rect(start[0], start[1]))

        if goal:
            if 0 <= goal[0] < self.cols and 0 <= goal[1] < self.rows:
                self.painter.draw_goal(surface, self.cell_to_screen_rect(goal[0], goal[1]))

    def handle_mouse(self, mouse_pos):
        """Translate mouse position to grid cell."""
        mx, my = mouse_pos
        # compute relative coordinates
        rx = mx - self.padding
        ry = my - self.padding
        if rx < 0 or ry < 0:
            self.controller.set_hover(None)
            return
        cell_w_total = self.cell_w + self.margin
        x = rx // cell_w_total
        y = ry // cell_w_total
        # bounds check
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.controller.set_hover((int(x), int(y)))
        else:
            self.controller.set_hover(None)


# ==================== MAIN ====================
def main():
    """Main application loop."""
    GRID_SIZE = 20
    OBSTACLE_PROB = 0.18

    gen = GridGenerator(grid_size=GRID_SIZE, obstacle_prob=OBSTACLE_PROB)
    grid = gen.generate()
    utils = GridUtils(grid)

    start = None
    goal = None
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if utils.free(x, y):
                if start is None:
                    start = (x, y)
                elif goal is None:
                    goal = (x, y)
        if goal:
            break

    renderer = EnvironmentRenderer(grid)
    screen = renderer.make_window()
    clock = pygame.time.Clock()

    if start and goal:
        # naive straight-line cells approximation (for demo only)
        path = []
        sx, sy = start
        gx, gy = goal
        steps = max(abs(gx - sx), abs(gy - sy))
        if steps == 0:
            path = [start]
        else:
            for i in range(steps + 1):
                t = i / steps
                x = round(sx + (gx - sx) * t)
                y = round(sy + (gy - sy) * t)
                path.append((x, y))
    else:
        path = None

    running = True
    while running:
        dt = clock.tick(renderer.cfg.fps) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                renderer.handle_mouse(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                renderer.controller.set_selected(renderer.controller.hover_cell)

        renderer.draw(screen, start=start, goal=goal, path=path)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()