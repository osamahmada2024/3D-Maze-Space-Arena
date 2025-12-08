"""
ui/MenuManager.py - Enhanced Menu System
Agent shape selection with visual icons and descriptions
"""

import sys
import math
import pygame


class MenuManager:
    def __init__(self, include_forest_maze: bool = True):
        """
        Initialize enhanced menu manager.
        
        Args:
            include_forest_maze: Whether to include forest maze option
        """
        pygame.init()
        self.WIDTH, self.HEIGHT = 900, 650
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("3D Maze Arena - Agent & Algorithm Selection")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.FONT = pygame.font.Font(None, 42)
        self.FONT_SMALL = pygame.font.Font(None, 30)
        self.FONT_TINY = pygame.font.Font(None, 22)

        # Colors
        self.WHITE = (255, 255, 255)
        self.TEAL = (0, 220, 200)
        self.GRAY = (120, 120, 120)
        self.YELLOW = (255, 220, 90)
        self.BLUE = (90, 170, 255)
        self.CYAN = (100, 230, 255)

        # Maze modes
        self.modes = ["Standard Maze", "Forest Maze"] if include_forest_maze else ["Standard Maze"]
        self.selected_mode = None

        # Agent shapes with descriptions
        self.agents = [
            {"name": "Sphere Droid", "key": "sphere_droid", "desc": "Classic glowing orb"},
            {"name": "Robo Cube", "key": "robo_cube", "desc": "Mechanical cube"},
            {"name": "Mini Drone", "key": "mini_drone", "desc": "Flying quad-copter"},
            {"name": "Crystal Alien", "key": "crystal_alien", "desc": "Mysterious gem entity"}
        ]
        
        # Algorithms with descriptions
        self.algorithms = ["A* search", "Dijkstra", "DFS", "BFS"]
        self.algo_descriptions = {
            "A* search": "Optimal & efficient - uses heuristics",
            "Dijkstra": "Optimal - explores uniformly",
            "DFS": "Depth-first - fast but not optimal",
            "BFS": "Breadth-first - guarantees shortest path"
        }
        
        self.selected_agent = None
        self.selected_algo = None
        self.cursor_pos = 0
        self.stage = 0 if include_forest_maze else 1  # 0: mode, 1: agent, 2: algorithm
        self.running = True

    def draw_animated_gradient(self, t):
        """Animated background gradient."""
        for i in range(self.HEIGHT):
            r = int(10 + 20 * math.sin(t + i/50))
            g = int(15 + 20 * math.sin(t/1.5 + i/60))
            b = int(25 + 20 * math.sin(t/2 + i/70))
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            pygame.draw.line(self.screen, (r, g, b), (0, i), (self.WIDTH, i))

    def draw_cursor(self, x, y, t):
        """Animated cursor."""
        pulse = int((math.sin(t*5) + 1)/2 * 55)
        color = (
            min(255, self.TEAL[0] + pulse),
            min(255, self.TEAL[1] + pulse),
            min(255, self.TEAL[2] + pulse),
        )
        pygame.draw.circle(self.screen, color, (x, y), 10)

    def draw_agent_icon(self, x, y, agent_type, size=40):
        """Draw icon representing each agent type."""
        center_x, center_y = x + size//2, y + size//2
        
        if agent_type == "sphere_droid":
            # Circle
            pygame.draw.circle(self.screen, self.CYAN, (center_x, center_y), size//2, 3)
            pygame.draw.circle(self.screen, self.CYAN, (center_x, center_y), size//4)
            
        elif agent_type == "robo_cube":
            # Square
            rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(self.screen, self.CYAN, rect, 3)
            pygame.draw.line(self.screen, self.CYAN, (x, y), (x+size, y+size), 2)
            pygame.draw.line(self.screen, self.CYAN, (x+size, y), (x, y+size), 2)
            
        elif agent_type == "mini_drone":
            # Drone shape
            pygame.draw.line(self.screen, self.CYAN, 
                           (center_x-size//2, center_y), 
                           (center_x+size//2, center_y), 3)
            pygame.draw.line(self.screen, self.CYAN, 
                           (center_x, center_y-size//2), 
                           (center_x, center_y+size//2), 3)
            # Propellers
            for px, py in [(x, y), (x+size, y), (x, y+size), (x+size, y+size)]:
                pygame.draw.circle(self.screen, self.CYAN, (px, py), 8, 2)
                
        elif agent_type == "crystal_alien":
            # Diamond shape
            points = [
                (center_x, y),
                (x+size, center_y),
                (center_x, y+size),
                (x, center_y)
            ]
            pygame.draw.polygon(self.screen, self.CYAN, points, 3)
            pygame.draw.line(self.screen, self.CYAN, 
                           (center_x, y), (center_x, y+size), 2)

    def draw_menu(self, t):
        """Main menu rendering."""
        if self.stage == 0:
            # Mode selection
            title = self.FONT.render("Select Game Mode", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 40))
            
            for i, mode in enumerate(self.modes):
                y = 150 + i*100
                
                if self.selected_mode == mode:
                    box = pygame.Rect(80, y-10, self.WIDTH-160, 90)
                    pygame.draw.rect(self.screen, (50, 60, 80), box, border_radius=10)
                
                txt_color = self.YELLOW if self.selected_mode == mode else self.WHITE
                txt = self.FONT.render(mode, True, txt_color)
                self.screen.blit(txt, (120, y))
                
                if i == self.cursor_pos:
                    self.draw_cursor(70, y+20, t)
        
        elif self.stage == 1:
            # Agent selection
            title = self.FONT.render("Select Your Agent Shape", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 40))
            
            subtitle = self.FONT_TINY.render(
                "Choose the visual appearance of your pathfinding agent", 
                True, self.GRAY
            )
            self.screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, 85))

            for i, agent in enumerate(self.agents):
                y = 150 + i*110
                
                # Highlight selected
                if self.selected_agent == agent["key"]:
                    box = pygame.Rect(80, y-10, self.WIDTH-160, 100)
                    pygame.draw.rect(self.screen, (50, 60, 80), box, border_radius=10)
                
                # Draw icon
                self.draw_agent_icon(100, y+10, agent["key"], 50)
                
                # Agent name
                txt_color = self.YELLOW if self.selected_agent == agent["key"] else self.WHITE
                txt = self.FONT.render(agent["name"], True, txt_color)
                self.screen.blit(txt, (180, y+5))
                
                # Description
                desc_txt = self.FONT_SMALL.render(agent["desc"], True, self.GRAY)
                self.screen.blit(desc_txt, (180, y+40))
                
                # Cursor
                if i == self.cursor_pos:
                    self.draw_cursor(70, y+35, t)

        elif self.stage == 2:
            # Algorithm selection
            title = self.FONT.render("Select Pathfinding Algorithm", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 40))
            
            subtitle = self.FONT_TINY.render(
                "Choose how your agent finds its path through the maze", 
                True, self.GRAY
            )
            self.screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, 85))

            for i, algo in enumerate(self.algorithms):
                y = 150 + i*95
                
                # Highlight selected
                if self.selected_algo == algo:
                    box = pygame.Rect(80, y-10, self.WIDTH-160, 85)
                    pygame.draw.rect(self.screen, (50, 60, 80), box, border_radius=10)
                
                # Algorithm name
                txt_color = self.BLUE if self.selected_algo == algo else self.WHITE
                txt = self.FONT.render(algo, True, txt_color)
                self.screen.blit(txt, (120, y))
                
                # Description
                desc_txt = self.FONT_SMALL.render(
                    self.algo_descriptions[algo], True, self.GRAY
                )
                self.screen.blit(desc_txt, (120, y+35))
                
                # Checkmark if selected
                if self.selected_algo == algo:
                    check = self.FONT.render("✓", True, self.YELLOW)
                    self.screen.blit(check, (self.WIDTH - 100, y+10))
                
                # Cursor
                if i == self.cursor_pos:
                    self.draw_cursor(70, y+25, t)
        
        # Instructions at bottom
        if self.stage == 2:
            inst = self.FONT_TINY.render(
                "↑↓ Navigate | ENTER Confirm & Start | ESC Exit", 
                True, self.GRAY
            )
        else:
            inst = self.FONT_TINY.render(
                "↑↓ Navigate | ENTER Select | ESC Exit", 
                True, self.GRAY
            )
        self.screen.blit(inst, (self.WIDTH//2 - inst.get_width()//2, self.HEIGHT - 40))

    def run(self):
        """Main menu loop."""
        t = 0
        while self.running:
            t += 0.016
            self.screen.fill(self.WHITE)
            self.draw_animated_gradient(t)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.selected_agent = None
                    self.selected_algo = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.selected_agent = None
                        self.selected_algo = None
                        
                    elif event.key == pygame.K_DOWN:
                        self.cursor_pos += 1
                        
                    elif event.key == pygame.K_UP:
                        self.cursor_pos -= 1
                        
                    # Wrap cursor
                    if self.stage == 0:
                        self.cursor_pos %= len(self.modes)
                    elif self.stage == 1:
                        self.cursor_pos %= len(self.agents)
                    else:
                        self.cursor_pos %= len(self.algorithms)

                    if event.key == pygame.K_RETURN:
                        if self.stage == 0:
                            self.selected_mode = self.modes[self.cursor_pos]
                            self.stage = 1
                            self.cursor_pos = 0
                        elif self.stage == 1:
                            self.selected_agent = self.agents[self.cursor_pos]["key"]
                            self.stage = 2
                            self.cursor_pos = 0
                        else:
                            self.selected_algo = self.algorithms[self.cursor_pos]
                            self.running = False

            self.draw_menu(t)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()