
import pygame
import sys

class ResultsDashboard:
    def __init__(self, agents):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Simulation Results & Analytics")
        self.clock = pygame.time.Clock()
        self.FONT = pygame.font.Font(None, 42)
        self.FONT_SMALL = pygame.font.Font(None, 28)
        self.FONT_BTN = pygame.font.Font(None, 32)
        
        self.WHITE = (255, 255, 255)
        self.BG_COLOR = (20, 25, 30)
        self.TEAL = (0, 220, 200)
        self.YELLOW = (255, 220, 90)
        self.BTN_EXIT = (200, 50, 50)
        self.BTN_RESET = (50, 150, 255)
        
        # Sort agents by steps (Step Efficiency)
        self.agents = sorted(agents, key=lambda a: a.steps_taken)
        self.running = True
        self.action = None  # Track user action: "EXIT" or "RESTART"
        
        # Button rects
        btn_w, btn_h = 180, 50
        btn_y = self.HEIGHT - 80
        spacing = 30
        center_x = self.WIDTH // 2
        
        self.btn_exit_rect = pygame.Rect(center_x - btn_w - spacing//2, btn_y, btn_w, btn_h)
        self.btn_reset_rect = pygame.Rect(center_x + spacing//2, btn_y, btn_w, btn_h)
        
    def draw(self):
        self.screen.fill(self.BG_COLOR)
        
        # Header
        title = self.FONT.render("Simulation Results", True, self.TEAL)
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 30))
        
        # Table Header
        headers_y = 100
        pygame.draw.line(self.screen, self.TEAL, (50, headers_y + 30), (self.WIDTH-50, headers_y + 30), 2)
        
        h_rank = self.FONT_SMALL.render("Rank", True, self.WHITE)
        h_algo = self.FONT_SMALL.render("Algorithm", True, self.WHITE)
        h_steps = self.FONT_SMALL.render("Steps (Travel)", True, self.WHITE)
        h_time = self.FONT_SMALL.render("Time (s)", True, self.WHITE)
        
        self.screen.blit(h_rank, (60, headers_y))
        self.screen.blit(h_algo, (150, headers_y))
        self.screen.blit(h_steps, (400, headers_y))
        self.screen.blit(h_time, (600, headers_y))
        
        # Rows
        start_y = 150
        for i, agent in enumerate(self.agents):
            y = start_y + i * 60
            
            # Rank
            rank_txt = self.FONT.render(f"#{i+1}", True, self.YELLOW if i==0 else self.WHITE)
            self.screen.blit(rank_txt, (60, y))
            
            # Icon/Color
            pygame.draw.circle(self.screen, agent.color, (130, y+15), 10)
            
            # Algo Name
            algo_txt = self.FONT_SMALL.render(agent.algo_name, True, self.WHITE)
            self.screen.blit(algo_txt, (150, y+5))
            
            # Steps
            steps_txt = self.FONT.render(str(agent.steps_taken), True, self.YELLOW if i==0 else self.WHITE)
            self.screen.blit(steps_txt, (420, y))
            
            # Time
            if agent.stuck:
                time_str = f"{agent.travel_time:.2f}s (FAILED)"
                time_col = (255, 100, 100) # Red
            else:
                time_str = f"{agent.travel_time:.2f}s"
                time_col = self.TEAL
                
            time_txt = self.FONT_SMALL.render(time_str, True, time_col)
            self.screen.blit(time_txt, (620, y+5))
        
        # --- Bottom Buttons ---
        mouse_pos = pygame.mouse.get_pos()
        
        # Exit Button
        exit_hovered = self.btn_exit_rect.collidepoint(mouse_pos)
        exit_col = (220, 70, 70) if exit_hovered else self.BTN_EXIT
        pygame.draw.rect(self.screen, exit_col, self.btn_exit_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.WHITE, self.btn_exit_rect, 2, border_radius=8)
        exit_txt = self.FONT_BTN.render("EXIT", True, self.WHITE)
        exit_txt_rect = exit_txt.get_rect(center=self.btn_exit_rect.center)
        self.screen.blit(exit_txt, exit_txt_rect)
        
        # Reset Button
        reset_hovered = self.btn_reset_rect.collidepoint(mouse_pos)
        reset_col = (70, 170, 255) if reset_hovered else self.BTN_RESET
        pygame.draw.rect(self.screen, reset_col, self.btn_reset_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.WHITE, self.btn_reset_rect, 2, border_radius=8)
        reset_txt = self.FONT_BTN.render("RESET", True, self.WHITE)
        reset_txt_rect = reset_txt.get_rect(center=self.btn_reset_rect.center)
        self.screen.blit(reset_txt, reset_txt_rect)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.action = "QUIT"
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = event.pos
                        if self.btn_exit_rect.collidepoint(mouse_pos):
                            self.running = False
                            self.action = "EXIT"
                        elif self.btn_reset_rect.collidepoint(mouse_pos):
                            self.running = False
                            self.action = "RESTART"
                            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.action = "EXIT"
                    if event.key == pygame.K_r:
                        self.running = False
                        self.action = "RESTART"
            
            self.draw()
            self.clock.tick(60)
        
        return self.action
