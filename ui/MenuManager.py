import sys
import math
import pygame

class MenuManager:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 900, 650
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("3D Maze Arena - Agent & Algorithm Selection")
        self.clock = pygame.time.Clock()
        self.FONT = pygame.font.Font(None, 42)
        self.FONT_SMALL = pygame.font.Font(None, 30)
        self.FONT_TINY = pygame.font.Font(None, 22)

        self.WHITE = (255, 255, 255)
        self.TEAL = (0, 220, 200)
        self.GRAY = (120, 120, 120)
        self.YELLOW = (255, 220, 90)
        self.BLUE = (90, 170, 255)
        self.CYAN = (100, 230, 255)

        # Agent shapes with descriptions
        self.agents = [
            {"name": "Sphere Droid", "key": "sphere_droid", "desc": "Classic glowing orb"},
            {"name": "Robo Cube", "key": "robo_cube", "desc": "mechanical cube"},
            {"name": "Mini Drone", "key": "mini_drone", "desc": "Flying quad-copter"},
            {"name": "Crystal Alien", "key": "crystal_alien", "desc": "Mysterious gem entity"}
        ]

        self.themes = [
            {"name": "Standard (Space)", "key": "DEFAULT", "desc": "Classic sci-fi maze experience"},
            {"name": "Forest Maze", "key": "FOREST", "desc": "Atmospheric forest with fog and obstacles"}
        ]

        ### 3amak osama ####
        self.GameModes = ["PlayerVsAI", "PlayerVsPlayer", "AIvsAI"]
        ### 3amak osama ####

        self.algorithms = ["A* search", "Dijkstra", "DFS", "BFS"]

        self.selected_agent = None
        self.selected_theme = None
        self.selected_gamemode = None
        self.selected_algo = None

        self.cursor_pos = 0
        self.stage = 0
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
        pygame.draw.circle(self.screen, color, (x, y), 10)

    def draw_agent_icon(self, x, y, agent_type, size=40):
        center_x, center_y = x + size//2, y + size//2
        
        if agent_type == "sphere_droid":
            pygame.draw.circle(self.screen, self.CYAN, (center_x, center_y), size//2, 3)
            pygame.draw.circle(self.screen, self.CYAN, (center_x, center_y), size//4)
            
        elif agent_type == "robo_cube":
            rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(self.screen, self.CYAN, rect, 3)
            pygame.draw.line(self.screen, self.CYAN, (x, y), (x+size, y+size), 2)
            pygame.draw.line(self.screen, self.CYAN, (x+size, y), (x, y+size), 2)
            
        elif agent_type == "mini_drone":
            pygame.draw.line(self.screen, self.CYAN, (center_x-size//2, center_y), (center_x+size//2, center_y), 3)
            pygame.draw.line(self.screen, self.CYAN, (center_x, center_y-size//2), (center_x, center_y+size//2), 3)
            for px, py in [(x, y), (x+size, y), (x, y+size), (x+size, y+size)]:
                pygame.draw.circle(self.screen, self.CYAN, (px, py), 8, 2)
                
        elif agent_type == "crystal_alien":
            points = [
                (center_x, y),
                (x+size, center_y),
                (center_x, y+size),
                (x, center_y)
            ]
            pygame.draw.polygon(self.screen, self.CYAN, points, 3)
            pygame.draw.line(self.screen, self.CYAN, (center_x, y), (center_x, y+size), 2)

    def draw_menu(self, t):

        # ============= STAGE 0 — SELECT THEME ============ 
        if self.stage == 0:
            title = self.FONT.render("Select Game Theme", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 40))

            subtitle = self.FONT_TINY.render("Choose your environment", True, self.GRAY)
            self.screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, 85))

            for i, theme in enumerate(self.themes):
                y = 150 + i*110
                if self.selected_theme == theme["key"]:
                    box = pygame.Rect(80, y-10, self.WIDTH-160, 100)
                    pygame.draw.rect(self.screen, (50, 60, 80), box, border_radius=10)

                txt_color = self.YELLOW if self.selected_theme == theme["key"] else self.WHITE
                txt = self.FONT.render(theme["name"], True, txt_color)
                self.screen.blit(txt, (180, y+5))

                desc_txt = self.FONT_SMALL.render(theme["desc"], True, self.GRAY)
                self.screen.blit(desc_txt, (180, y+40))

                if i == self.cursor_pos:
                    self.draw_cursor(70, y+35, t)

        # ============= STAGE 1 — SELECT AGENT ============
        elif self.stage == 1:
            title = self.FONT.render("Select Your Agent Shape", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 40))

            subtitle = self.FONT_TINY.render("Choose the visual appearance of your agent", True, self.GRAY)
            self.screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, 85))

            for i, agent in enumerate(self.agents):
                y = 150 + i*110
                if self.selected_agent == agent["key"]:
                    box = pygame.Rect(80, y-10, self.WIDTH-160, 100)
                    pygame.draw.rect(self.screen, (50, 60, 80), box, border_radius=10)

                self.draw_agent_icon(100, y+10, agent["key"], 50)

                txt_color = self.YELLOW if self.selected_agent == agent["key"] else self.WHITE
                txt = self.FONT.render(agent["name"], True, txt_color)
                self.screen.blit(txt, (180, y+5))

                desc_txt = self.FONT_SMALL.render(agent["desc"], True, self.GRAY)
                self.screen.blit(desc_txt, (180, y+40))

                if i == self.cursor_pos:
                    self.draw_cursor(70, y+35, t)

        # ============= STAGE 2 — SELECT GAMEMODE ============  ### 3amak osama ####
        elif self.stage == 2:
            title = self.FONT.render("Select Game Mode", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 40))

            subtitle = self.FONT_TINY.render("Choose how gameplay works", True, self.GRAY)
            self.screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, 85))

            for i, gm in enumerate(self.GameModes):
                y = 150 + i*95

                if self.selected_gamemode == gm:
                    box = pygame.Rect(80, y-10, self.WIDTH-160, 85)
                    pygame.draw.rect(self.screen, (50, 60, 80), box, border_radius=10)

                txt_color = self.BLUE if self.selected_gamemode == gm else self.WHITE
                txt = self.FONT.render(gm, True, txt_color)
                self.screen.blit(txt, (120, y))

                if self.selected_gamemode == gm:
                    check = self.FONT.render("✔", True, self.YELLOW)
                    self.screen.blit(check, (self.WIDTH - 100, y+10))

                if i == self.cursor_pos:
                    self.draw_cursor(70, y+25, t)

        # ============= STAGE 3 — SELECT ALGORITHM ============
        elif self.stage == 3:
            title = self.FONT.render("Select Pathfinding Algorithm", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 40))

            subtitle = self.FONT_TINY.render("Choose how your agent finds its path", True, self.GRAY)
            self.screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, 85))

            algo_descriptions = {
                "A* search": "Optimal & efficient - uses heuristics",
                "Dijkstra": "Optimal - explores uniformly",
                "DFS": "Depth-first - fast but not optimal",
                "BFS": "Breadth-first - guarantees shortest path"
            }

            for i, algo in enumerate(self.algorithms):
                y = 150 + i*95

                if self.selected_algo == algo:
                    box = pygame.Rect(80, y-10, self.WIDTH-160, 85)
                    pygame.draw.rect(self.screen, (50, 60, 80), box, border_radius=10)

                txt_color = self.BLUE if self.selected_algo == algo else self.WHITE
                txt = self.FONT.render(algo, True, txt_color)
                self.screen.blit(txt, (120, y))

                desc_txt = self.FONT_SMALL.render(algo_descriptions[algo], True, self.GRAY)
                self.screen.blit(desc_txt, (120, y+35))

                if self.selected_algo == algo:
                    check = self.FONT.render("✔", True, self.YELLOW)
                    self.screen.blit(check, (self.WIDTH - 100, y+10))

                if i == self.cursor_pos:
                    self.draw_cursor(70, y+25, t)

        # FOOTER
        if self.stage < 3:
            inst = self.FONT_TINY.render("↑↓ Navigate | ENTER Select | ESC Exit", True, self.GRAY)
        else:
            inst = self.FONT_TINY.render("↑↓ Navigate | ENTER Confirm & Start | ESC Exit", True, self.GRAY)

        self.screen.blit(inst, (self.WIDTH//2 - inst.get_width()//2, self.HEIGHT - 40))

    def run(self):
        t = 0
        self.stage = 0
        
        while self.running:
            t += 0.016
            self.screen.fill(self.WHITE)
            self.draw_animated_gradient(t)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                    elif event.key == pygame.K_DOWN:
                        self.cursor_pos += 1

                    elif event.key == pygame.K_UP:
                        self.cursor_pos -= 1

                    # wrap cursor per stage
                    if self.stage == 0:
                        self.cursor_pos %= len(self.themes)
                    elif self.stage == 1:
                        self.cursor_pos %= len(self.agents)
                    elif self.stage == 2:
                        self.cursor_pos %= len(self.GameModes)  ### 3amak osama ####
                    else:
                        self.cursor_pos %= len(self.algorithms)

                    if event.key == pygame.K_RETURN:
                        if self.stage == 0:
                            self.selected_theme = self.themes[self.cursor_pos]["key"]
                            self.stage = 1
                            self.cursor_pos = 0

                        elif self.stage == 1:
                            self.selected_agent = self.agents[self.cursor_pos]["key"]
                            self.stage = 2
                            self.cursor_pos = 0

                        elif self.stage == 2:  ### 3amak osama ####
                            self.selected_gamemode = self.GameModes[self.cursor_pos]
                            self.stage = 3
                            self.cursor_pos = 0

                        else:
                            self.selected_algo = self.algorithms[self.cursor_pos]
                            self.running = False

            self.draw_menu(t)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
