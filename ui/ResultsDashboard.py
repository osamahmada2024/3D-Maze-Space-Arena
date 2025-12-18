
import pygame
import sys

# Modern Color Palette (matching SimConfigPanel)
COLORS = {
    "bg": (10, 15, 30),
    "panel": (20, 30, 50),
    "accent": (0, 200, 255),
    "text": (240, 240, 255),
    "text_dim": (140, 150, 170),
    "success": (50, 220, 100),
    "danger": (255, 60, 80),
    "border": (40, 60, 90),
    "focus": (255, 220, 50)
}

def draw_rounded_rect(surface, rect, color, corner_radius, width=0):
    """Draws a rounded rect"""
    pygame.draw.rect(surface, color, rect, width, border_radius=corner_radius)

class Button:
    def __init__(self, x, y, w, h, text, font, bg_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hovered = False
        
    def draw(self, screen):
        # Lighten on hover
        if self.hovered:
            color = tuple(min(255, c + 30) for c in self.bg_color)
        else:
            color = self.bg_color
            
        draw_rounded_rect(screen, self.rect, color, 8)
        
        txt_surf = self.font.render(self.text, True, COLORS["text"])
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

class ResultsDashboard:
    def __init__(self, agents):
        pygame.init()
        self.WIDTH, self.HEIGHT = 900, 650
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Simulation Results & Analytics")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.FONT_TITLE = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.FONT_HEADER = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.FONT_BODY = pygame.font.SysFont("Consolas", 16)
        self.FONT_SMALL = pygame.font.SysFont("Segoe UI", 14)
        
        # Sort agents by steps (Step Efficiency)
        self.agents = sorted(agents, key=lambda a: a.steps_taken)
        self.running = True
        self.action = None
        
        # Create buttons
        self._init_buttons()
        
    def _init_buttons(self):
        btn_w = 150
        btn_h = 50
        btn_gap = 20
        total_w = 2 * btn_w + btn_gap
        start_x = (self.WIDTH - total_w) // 2
        btn_y = self.HEIGHT - 80
        
        self.btn_exit = Button(
            start_x, btn_y, btn_w, btn_h,
            "EXIT", self.FONT_HEADER,
            COLORS["danger"]
        )
        
        self.btn_reset = Button(
            start_x + btn_w + btn_gap, btn_y, btn_w, btn_h,
            "RESET", self.FONT_HEADER,
            COLORS["success"]
        )
        
        self.buttons = [self.btn_exit, self.btn_reset]
        
    def draw(self):
        self.screen.fill(COLORS["bg"])
        
        # Header
        title = self.FONT_TITLE.render("Simulation Results", True, COLORS["accent"])
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 30))
        
        # Table Header
        headers_y = 90
        pygame.draw.line(self.screen, COLORS["accent"], (50, headers_y + 30), (self.WIDTH-50, headers_y + 30), 2)
        
        h_rank = self.FONT_HEADER.render("Rank", True, COLORS["text"])
        h_algo = self.FONT_HEADER.render("Algorithm", True, COLORS["text"])
        h_steps = self.FONT_HEADER.render("Steps", True, COLORS["text"])
        h_time = self.FONT_HEADER.render("Time (s)", True, COLORS["text"])
        
        self.screen.blit(h_rank, (60, headers_y))
        self.screen.blit(h_algo, (180, headers_y))
        self.screen.blit(h_steps, (500, headers_y))
        self.screen.blit(h_time, (680, headers_y))
        
        # Rows
        start_y = 140
        for i, agent in enumerate(self.agents):
            y = start_y + i * 55
            
            # Rank
            rank_col = COLORS["focus"] if i == 0 else COLORS["text"]
            rank_txt = self.FONT_BODY.render(f"#{i+1}", True, rank_col)
            self.screen.blit(rank_txt, (70, y))
            
            # Icon/Color
            pygame.draw.circle(self.screen, agent.color, (150, y+12), 8)
            
            # Algo Name
            algo_txt = self.FONT_BODY.render(agent.algo_name, True, COLORS["text"])
            self.screen.blit(algo_txt, (180, y))
            
            # Steps
            steps_col = COLORS["focus"] if i == 0 else COLORS["text"]
            steps_txt = self.FONT_BODY.render(str(agent.steps_taken), True, steps_col)
            self.screen.blit(steps_txt, (520, y))
            
            # Time
            if agent.stuck:
                time_str = f"{agent.travel_time:.2f}s (FAILED)"
                time_col = COLORS["danger"]
            else:
                time_str = f"{agent.travel_time:.2f}s"
                time_col = COLORS["success"]
                
            time_txt = self.FONT_BODY.render(time_str, True, time_col)
            self.screen.blit(time_txt, (700, y))
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.action = "QUIT"
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.btn_exit.rect.collidepoint(mouse_pos):
                            self.running = False
                            self.action = "EXIT"
                        elif self.btn_reset.rect.collidepoint(mouse_pos):
                            self.running = False
                            self.action = "RESTART"
                            
                # Keyboard shortcuts still work
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.action = "EXIT"
                    if event.key == pygame.K_r:
                        self.running = False
                        self.action = "RESTART"
            
            # Update hover states
            for btn in self.buttons:
                btn.hovered = btn.rect.collidepoint(mouse_pos)
            
            self.draw()
            self.clock.tick(60)
            
        return self.action
