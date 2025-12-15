import pygame
import sys
import math
from typing import List, Optional, Any
from mazespace.config.definitions import GlobalConfig, ThemeConfig, AgentConfig

class MenuState:
    """Base class for menu states"""
    def handle_input(self, event, manager) -> Optional['MenuState']:
        return None
    
    def draw(self, screen, manager, t):
        pass

class SelectionState(MenuState):
    """Generic selection menu"""
    def __init__(self, title: str, subtitle: str, items: List[Any], next_state_factory=None):
        self.title = title
        self.subtitle = subtitle
        self.items = items
        self.cursor = 0
        self.next_state_factory = next_state_factory # Function taking selected item, returning next state
        
    def handle_input(self, event, manager):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.cursor = (self.cursor - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.cursor = (self.cursor + 1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                selected = self.items[self.cursor]
                if self.next_state_factory:
                    return self.next_state_factory(selected)
                return selected # Return value (leaf)
        return None

    def draw(self, screen, manager, t):
        # Draw Title
        title_surf = manager.FONT.render(self.title, True, manager.WHITE)
        screen.blit(title_surf, (manager.WIDTH//2 - title_surf.get_width()//2, 40))
        
        sub_surf = manager.FONT_TINY.render(self.subtitle, True, manager.GRAY)
        screen.blit(sub_surf, (manager.WIDTH//2 - sub_surf.get_width()//2, 85))
        
        # Draw Items
        start_y = 150
        gap = 80
        
        for i, item in enumerate(self.items):
            y = start_y + i * gap
            
            # Extract name/desc/key safely
            name = getattr(item, 'name', str(item))
            desc = getattr(item, 'desc', "")
            
            color = manager.WHITE
            if i == self.cursor:
                color = manager.YELLOW
                manager.draw_cursor(100, y + 20, t)

            txt = manager.FONT_SMALL.render(name, True, color)
            screen.blit(txt, (140, y))
            
            if desc:
                d_txt = manager.FONT_TINY.render(desc, True, manager.GRAY)
                screen.blit(d_txt, (140, y + 25))

class TextInputState(MenuState):
    """Main menu with text command support"""
    def __init__(self):
        self.user_text = ""
        self.options = ["Start Game", "Configure", "Exit"]
        self.cursor = 0
        
    def handle_input(self, event, manager):
        if event.type == pygame.KEYDOWN:
            # Typed Input Handling
            if event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            elif event.key == pygame.K_RETURN:
                cmd = self.user_text.strip().lower()
                if cmd == "exit":
                    sys.exit()
                elif cmd == "return":
                    if len(manager.stack) > 1:
                        manager.pop_state()
                        return None
                elif cmd == "":
                    # Normal menu selection
                    if self.cursor == 0: # Start
                        # Configure default flow
                        # 1. Select Theme -> Select Agent -> Run
                        def on_agent_select(agent):
                            manager.config.app.default_agent = agent.key
                            manager.finished = True # Signal to run app
                            return None
                            
                        def on_theme_select(theme):
                            manager.config.app.default_theme = theme.key
                            return SelectionState(
                                "Select Agent", "Choose your character",
                                manager.config.agents,
                                on_agent_select
                            )

                        return SelectionState(
                            "Select Theme", "Choose your environment",
                            manager.config.themes,
                            on_theme_select
                        )
                    elif self.cursor == 1: # Configure
                        # Just show theme selection for now as an example
                         return SelectionState(
                            "Configuration", "Review Settings",
                             manager.config.themes,
                             None
                         )
                    elif self.cursor == 2: # Exit
                        sys.exit()
                
                self.user_text = "" # Reset if consumed (but usually we transition)
                
            else:
                # Add unicode chars
                if len(self.user_text) < 20 and event.unicode.isprintable():
                    self.user_text += event.unicode
            
            # Nav arrows (only if text empty? mixed mode)
            if event.key == pygame.K_UP:
                self.cursor = (self.cursor - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.cursor = (self.cursor + 1) % len(self.options)

        return None
        
    def draw(self, screen, manager, t):
        # Title
        title = manager.FONT.render("MazeSpace Arena", True, manager.CYAN)
        screen.blit(title, (manager.WIDTH//2 - title.get_width()//2, 60))
        
        # Options
        for i, opt in enumerate(self.options):
            color = manager.YELLOW if i == self.cursor else manager.WHITE
            txt = manager.FONT.render(opt, True, color)
            screen.blit(txt, (manager.WIDTH//2 - txt.get_width()//2, 200 + i * 60))
            
            if i == self.cursor:
                manager.draw_cursor(manager.WIDTH//2 - 100, 200 + i * 60 + 15, t)

        # Text Input Box
        box_y = manager.HEIGHT - 100
        txt_surf = manager.FONT_SMALL.render(f"Command > {self.user_text}_", True, manager.TEAL)
        screen.blit(txt_surf, (50, box_y))
        
        hint = manager.FONT_TINY.render("Type 'return' or 'exit', or use Arrow Keys + Enter", True, manager.GRAY)
        screen.blit(hint, (50, box_y + 40))


class MenuManager:
    def __init__(self, config: GlobalConfig):
        pygame.init()
        self.config = config
        self.WIDTH = config.app.width
        self.HEIGHT = config.app.height
        
        flags = pygame.DOUBLEBUF
        if config.app.fullscreen:
            flags |= pygame.FULLSCREEN
            
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags)
        pygame.display.set_caption("MazeSpace - Configurable")
        
        self.clock = pygame.time.Clock()
        self.stack: List[MenuState] = [TextInputState()]
        self.finished = False

        # Fonts & Colors
        self.FONT = pygame.font.Font(None, 42)
        self.FONT_SMALL = pygame.font.Font(None, 32)
        self.FONT_TINY = pygame.font.Font(None, 22)
        
        self.WHITE = (255, 255, 255)
        self.GRAY = (120, 120, 120)
        self.CYAN = (0, 255, 255)
        self.TEAL = (0, 200, 180)
        self.YELLOW = (255, 220, 50)

    def draw_cursor(self, x, y, t):
        s = 5 + math.sin(t * 5) * 2
        pygame.draw.circle(self.screen, self.TEAL, (x, y), s)

    def push_state(self, state: MenuState):
        self.stack.append(state)
        
    def pop_state(self):
        if len(self.stack) > 1:
            self.stack.pop()
            
    def run(self):
        t = 0
        while not self.finished and self.stack:
            t += 0.016
            self.screen.fill((20, 20, 30)) # Dark Blue BG
            
            # Gradient
            for i in range(self.HEIGHT):
                c = 20 + i // 20
                pygame.draw.line(self.screen, (10, 10, min(50, c)), (0, i), (self.WIDTH, i))

            current_state = self.stack[-1]
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                
                # Global Back
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if len(self.stack) > 1:
                        self.pop_state()
                    else:
                        # Top level escape -> Confirm Exit?
                        # For now just exit
                        sys.exit()
                    continue
                
                # State-specific input
                next_state_or_result = current_state.handle_input(event, self)
                
                if isinstance(next_state_or_result, MenuState):
                    self.push_state(next_state_or_result)
                elif next_state_or_result is not None:
                    # Generic input handling might return something else?
                    pass
            
            current_state.draw(self.screen, self, t)
            
            # Overlay Back hint
            if len(self.stack) > 1:
                back = self.FONT_TINY.render("[ESC] Back", True, self.GRAY)
                self.screen.blit(back, (20, 20))
            
            pygame.display.flip()
            self.clock.tick(60)
            
        return self.config