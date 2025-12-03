import math
import pygame
from typing import List, Optional

class MenuManager:
    """
    Class: MenuManager
    Purpose:
        Handle pre-simulation user input via a graphical menu.
    
    Responsibilities:
        • Allow user to select an agent type.
        • Allow user to select a pathfinding algorithm.
        • Track navigation cursor and menu stage.
        • Provide visual feedback (animated background, pulsing cursor, selection highlights).

    Attributes:
        agents (List[str]): Available agent types.
        algorithms (List[str]): Available algorithms.
        selected_agent (Optional[str]): User-selected agent.
        selected_algo (Optional[str]): User-selected algorithm.
        stage (int): Current menu stage (1=Agent, 2=Algorithm).
        cursor_pos (int): Position of navigation cursor.
        running (bool): Menu loop flag.
    """

    def __init__(self):
        """Initialize Pygame, fonts, colors, menu options, and state."""
        pygame.init()
        self.WIDTH: int = 800
        self.HEIGHT: int = 600
        self.screen: pygame.Surface = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Upgraded Menu System")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.FONT: pygame.font.Font = pygame.font.Font(None, 40)
        self.FONT_SMALL: pygame.font.Font = pygame.font.Font(None, 28)

        # Colors
        self.WHITE = (255, 255, 255)
        self.TEAL = (0, 220, 200)
        self.GRAY = (120, 120, 120)
        self.YELLOW = (255, 220, 90)
        self.BLUE = (90, 170, 255)

        # Menu options
        self.agents: List[str] = ["AC", "ACS", "Hybrid"]
        self.algorithms: List[str] = ["A*", "DFS", "BFS"]
        self.selected_agent: Optional[str] = None
        self.selected_algo: Optional[str] = None
        self.cursor_pos: int = 0
        self.stage: int = 1
        self.running: bool = True

    # ------------------------------------------------------
    # Private Method: Animated Background
    # ------------------------------------------------------
    def _draw_animated_gradient(self, t: float):
        """Draw dynamic gradient background for menu."""
        for i in range(self.HEIGHT):
            r = max(0, min(255, int(10 + 20 * math.sin(t + i / 50))))
            g = max(0, min(255, int(15 + 20 * math.sin(t / 1.5 + i / 60))))
            b = max(0, min(255, int(25 + 20 * math.sin(t / 2 + i / 70))))
            pygame.draw.line(self.screen, (r, g, b), (0, i), (self.WIDTH, i))

    # ------------------------------------------------------
    # Private Method: Draw Cursor
    # ------------------------------------------------------
    def _draw_cursor(self, x: int, y: int, t: float):
        """Draw a pulsing cursor circle next to the selected menu item."""
        pulse: int = int((math.sin(t * 5) + 1) / 2 * 55)
        color = (
            min(255, self.TEAL[0] + pulse),
            min(255, self.TEAL[1] + pulse),
            min(255, self.TEAL[2] + pulse),
        )
        pygame.draw.circle(self.screen, color, (x, y), 8)

    # ------------------------------------------------------
    # Public Method: Draw Menu Stage
    # ------------------------------------------------------
    def draw_menu(self, t: float):
        """Render the current menu stage with options and selection indicators."""
        if self.stage == 1:
            # Agent selection
            title = self.FONT.render("Select Agent", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 50))

            for i, item in enumerate(self.agents):
                txt_color = self.YELLOW if self.selected_agent == item else self.WHITE
                txt = self.FONT.render(item, True, txt_color)
                y = 150 + i * 70
                self.screen.blit(txt, (200, y))
                if i == self.cursor_pos:
                    self._draw_cursor(170, y + 15, t)

        elif self.stage == 2:
            # Algorithm selection
            title = self.FONT.render("Select Algorithm", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 50))

            for i, item in enumerate(self.algorithms):
                txt_color = self.BLUE if self.selected_algo == item else self.WHITE
                txt = self.FONT.render(item, True, txt_color)
                y = 150 + i * 60
                self.screen.blit(txt, (200, y))
                if self.selected_algo == item:
                    check = self.FONT_SMALL.render("✔", True, self.YELLOW)
                    self.screen.blit(check, (150, y))
                if i == self.cursor_pos:
                    self._draw_cursor(170, y + 15, t)

    # ------------------------------------------------------
    # Public Method: Run Menu Loop
    # ------------------------------------------------------
    def run(self):
        """Execute the menu loop until user makes selections."""
        t: float = 0
        while self.running:
            t += 0.016
            self.screen.fill(self.WHITE)
            self._draw_animated_gradient(t)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # Navigation
                    if event.key == pygame.K_DOWN:
                        self.cursor_pos += 1
                    elif event.key == pygame.K_UP:
                        self.cursor_pos -= 1

                    self.cursor_pos %= len(self.agents) if self.stage == 1 else len(self.algorithms)

                    # Selection
                    if event.key == pygame.K_RETURN:
                        if self.stage == 1:
                            self.selected_agent = self.agents[self.cursor_pos]
                            self.stage = 2
                            self.cursor_pos = 0
                        else:
                            self.selected_algo = self.algorithms[self.cursor_pos]
                            self.running = False  # Exit loop

            self.draw_menu(t)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
