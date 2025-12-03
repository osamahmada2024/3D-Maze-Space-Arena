import pygame, sys, math

class MenuManager:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Upgraded Menu System")
        self.clock = pygame.time.Clock()
        self.FONT = pygame.font.Font(None, 40)
        self.FONT_SMALL = pygame.font.Font(None, 28)

        self.WHITE = (255, 255, 255)
        self.TEAL = (0, 220, 200)
        self.GRAY = (120, 120, 120)
        self.YELLOW = (255, 220, 90)
        self.BLUE = (90, 170, 255)

        self.agents = ["AC", "ACS", "Hybrid"]
        self.algorithms = ["A* search", "Dijkstra", "DFS", "BFS"]
        self.selected_agent = None
        self.selected_algo = None
        self.cursor_pos = 0
        self.stage = 1
        self.running = True

    def draw_animated_gradient(self, t):
        for i in range(self.HEIGHT):
            r = int(10 + 20 * math.sin(t + i/50))
            g = int(15 + 20 * math.sin(t/1.5 + i/60))
            b = int(25 + 20 * math.sin(t/2 + i/70))
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            pygame.draw.line(self.screen, (r, g, b), (0, i), (self.WIDTH, i))

    def draw_cursor(self, x, y, t):
        pulse = int((math.sin(t*5) + 1)/2 * 55)
        color = (
            min(255, self.TEAL[0] + pulse),
            min(255, self.TEAL[1] + pulse),
            min(255, self.TEAL[2] + pulse),
        )
        pygame.draw.circle(self.screen, color, (x, y), 8)

    def draw_menu(self, t):
        if self.stage == 1:
            title = self.FONT.render("Select Agent", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 50))

            for i, item in enumerate(self.agents):
                txt_color = self.YELLOW if self.selected_agent == item else self.WHITE
                txt = self.FONT.render(item, True, txt_color)
                y = 150 + i*70
                self.screen.blit(txt, (200, y))
                if i == self.cursor_pos:
                    self.draw_cursor(170, y + 15, t)

        elif self.stage == 2:
            title = self.FONT.render("Select Algorithm", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 50))

            for i, item in enumerate(self.algorithms):
                txt_color = self.BLUE if self.selected_algo == item else self.WHITE
                txt = self.FONT.render(item, True, txt_color)
                y = 150 + i*60
                self.screen.blit(txt, (200, y))
                if self.selected_algo == item:
                    check = self.FONT_SMALL.render("✔", True, self.YELLOW)
                    self.screen.blit(check, (150, y))
                if i == self.cursor_pos:
                    self.draw_cursor(170, y + 15, t)

    def run(self):
        t = 0
        while self.running:
            t += 0.016
            self.screen.fill(self.WHITE)
            self.draw_animated_gradient(t)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.cursor_pos += 1
                    elif event.key == pygame.K_UP:
                        self.cursor_pos -= 1
                    self.cursor_pos %= (3 if self.stage == 1 else 4)

                    if event.key == pygame.K_RETURN:
                        if self.stage == 1:
                            self.selected_agent = self.agents[self.cursor_pos]
                            self.stage = 2
                            self.cursor_pos = 0
                        else:
                            self.selected_algo = self.algorithms[self.cursor_pos]
                            self.running = False  # Exit loop after selection

            self.draw_menu(t)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        # Removed sys.exit() to continue program execution