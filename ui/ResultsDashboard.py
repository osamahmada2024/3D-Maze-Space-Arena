
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
        
        self.WHITE = (255, 255, 255)
        self.BG_COLOR = (20, 25, 30)
        self.TEAL = (0, 220, 200)
        self.YELLOW = (255, 220, 90)
        
        # Sort agents by steps (Step Efficiency)
        # We can also sort by time. For leaderboard, usually efficiency wins in pathfinding?
        # Prompt: "Rank algorithms/agents in ascending order based on Step Count"
        
        self.agents = sorted(agents, key=lambda a: a.steps_taken)
        self.running = True
        
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
        h_steps = self.FONT_SMALL.render("Steps (Efficiency)", True, self.WHITE)
        h_time = self.FONT_SMALL.render("Time (Compute Speed)", True, self.WHITE)
        
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
            time_str = f"{agent.execution_time:.2f}ms"
            time_txt = self.FONT_SMALL.render(time_str, True, self.TEAL)
            self.screen.blit(time_txt, (620, y+5))
            
            # Bar graph visual for time? Optional but nice.
        
        # Instructions
        inst = self.FONT_SMALL.render("Press ENTER to Close / R to Restart", True, (150, 150, 150))
        self.screen.blit(inst, (self.WIDTH//2 - inst.get_width()//2, self.HEIGHT - 50))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.running = False
                        return "EXIT"
                    if event.key == pygame.K_r:
                        self.running = False
                        return "RESTART"
            
            self.draw()
            self.clock.tick(60)
