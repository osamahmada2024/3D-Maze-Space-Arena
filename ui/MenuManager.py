# ui/MenuManager.py
import pygame
import sys
import math

class MenuManager:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1024, 720  # Safe Resolution
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
        self.ORANGE = (255, 140, 50)  # ✅ جديد - للون الحمم

        # Agent shapes with descriptions
        self.agents = [
            {"name": "Sphere Droid", "key": "sphere_droid", "desc": "Classic glowing orb"},
            {"name": "Robo Cube", "key": "robo_cube", "desc": "Mechanical cube"},
            {"name": "Mini Drone", "key": "mini_drone", "desc": "Flying quad-copter"},
            {"name": "Crystal Alien", "key": "crystal_alien", "desc": "Mysterious gem entity"}
        ]
        
        # ✅ تحديث الـ themes لإضافة LAVA
        self.themes = [
            {"name": "Standard (Space)", "key": "DEFAULT", "desc": "Classic sci-fi maze experience", "color": self.CYAN},
            {"name": "Forest Maze", "key": "FOREST", "desc": "Atmospheric forest with fog and fireflies", "color": (100, 200, 100)},
            {"name": "Lava Maze 🔥", "key": "LAVA", "desc": "Deadly volcanic maze with lava pools!", "color": self.ORANGE}  # ✅ جديد
        ]
        
        self.algorithms = ["A* search", "Dijkstra", "DFS", "BFS"]
        self.selected_agent = None
        self.selected_theme = None
        self.selected_algo = None
        self.cursor_pos = 0
        self.stage = 0
        self.running = True

    def draw_animated_gradient(self, t):
        """Animated background gradient"""
        for i in range(self.HEIGHT):
            r = int(10 + 20 * math.sin(t + i/50))
            g = int(15 + 20 * math.sin(t/1.5 + i/60))
            b = int(25 + 20 * math.sin(t/2 + i/70))
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            pygame.draw.line(self.screen, (r, g, b), (0, i), (self.WIDTH, i))

    def draw_cursor(self, x, y, t):
        """Animated cursor"""
        pulse = int((math.sin(t*5) + 1)/2 * 55)
        color = (
            min(255, self.TEAL[0] + pulse),
            min(255, self.TEAL[1] + pulse),
            min(255, self.TEAL[2] + pulse),
        )
        pygame.draw.circle(self.screen, color, (x, y), 10)

    def draw_theme_icon(self, x, y, theme_key, size=40):
        """✅ رسم أيقونة لكل theme"""
        center_x, center_y = x + size//2, y + size//2
        
        if theme_key == "DEFAULT":
            # نجوم للفضاء
            pygame.draw.circle(self.screen, self.CYAN, (center_x, center_y), size//3, 2)
            for i in range(5):
                angle = i * (2 * math.pi / 5) - math.pi/2
                px = center_x + int(size//2.5 * math.cos(angle))
                py = center_y + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(self.screen, self.CYAN, (px, py), 3)
                
        elif theme_key == "FOREST":
            # شجرة
            pygame.draw.rect(self.screen, (139, 90, 43), (center_x-3, center_y, 6, size//2))
            pygame.draw.polygon(self.screen, (34, 139, 34), [
                (center_x, y),
                (x + size, center_y + 5),
                (x, center_y + 5)
            ])
            
        elif theme_key == "LAVA":
            # حمم/نار
            pygame.draw.polygon(self.screen, self.ORANGE, [
                (center_x, y),
                (x + size - 5, y + size),
                (x + 5, y + size)
            ])
            pygame.draw.polygon(self.screen, (255, 200, 50), [
                (center_x, y + size//4),
                (x + size - 12, y + size),
                (x + 12, y + size)
            ])

    def draw_agent_icon(self, x, y, agent_type, size=40):
        """Draw a simple icon representing each agent type"""
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
        """Main menu rendering"""
        if self.stage == 0:
            # Theme selection screen
            title = self.FONT.render("Select Game Theme", True, self.WHITE)
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 40))
            
            subtitle = self.FONT_TINY.render("Choose your environment", True, self.GRAY)
            self.screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, 85))

            for i, theme in enumerate(self.themes):
                y = 140 + i * 100  # ✅ تعديل المسافات
                
                # Highlight selected
                if self.selected_theme == theme["key"]:
                    box = pygame.Rect(80, y-10, self.WIDTH-160, 90)
                    pygame.draw.rect(self.screen, (50, 60, 80), box, border_radius=10)
                
                # ✅ رسم أيقونة الـ theme
                self.draw_theme_icon(100, y + 10, theme["key"], 45)
                
                # Theme name with color
                txt_color = theme.get("color", self.WHITE) if self.selected_theme == theme["key"] else self.WHITE
                txt = self.FONT.render(theme["name"], True, txt_color)
                self.screen.blit(txt, (180, y + 5))
                
                # Description
                desc_txt = self.FONT_SMALL.render(theme["desc"], True, self.GRAY)
                self.screen.blit(desc_txt, (180, y + 40))
                
                # Cursor
                if i == self.cursor_pos:
                    self.draw_cursor(70, y + 35, t)
            
            # ✅ تحذير للـ Lava
            if self.cursor_pos == 2:  # LAVA selected
                warning = self.FONT_TINY.render("⚠️ Warning: Lava pools cause damage! Watch your health!", True, self.ORANGE)
                self.screen.blit(warning, (self.WIDTH//2 - warning.get_width()//2, self.HEIGHT - 80))

        # Instructions at bottom
        inst = self.FONT_TINY.render("↑↓ Navigate | ENTER Select | ESC Exit", True, self.GRAY)
        self.screen.blit(inst, (self.WIDTH//2 - inst.get_width()//2, self.HEIGHT - 40))

    def run(self):
        """Main menu loop"""
        t = 0
        self.stage = 0
        
        while self.running:
            t += 0.016
            self.screen.fill(self.WHITE)
            self.draw_animated_gradient(t)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.selected_agent = None
                    self.selected_algo = None
                    self.selected_theme = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.selected_agent = None
                        self.selected_algo = None
                        self.selected_theme = None
                        
                    elif event.key == pygame.K_DOWN:
                        self.cursor_pos += 1
                        
                    elif event.key == pygame.K_UP:
                        self.cursor_pos -= 1
                        
                    # Wrap cursor
                    if self.stage == 0:
                        self.cursor_pos %= len(self.themes)
                    elif self.stage == 1:
                        self.cursor_pos %= len(self.agents)
                    else:
                        self.cursor_pos %= len(self.algorithms)

                    if event.key == pygame.K_RETURN:
                        # Only Theme Selection
                        self.selected_theme = self.themes[self.cursor_pos]["key"]
                        self.running = False

            self.draw_menu(t)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()