
import pygame
import sys
import math

# --- Modern Palette (Cyberpunk / Glassmorphism) ---
COLORS = {
    "bg": (10, 15, 30),         # Deep Space Blue
    "panel": (20, 30, 50),      # Card Background
    "panel_hover": (30, 45, 70),
    "accent": (0, 200, 255),    # Cyan Neon
    "accent_dim": (0, 100, 130),
    "text": (240, 240, 255),
    "text_dim": (140, 150, 170),
    "success": (50, 220, 100),
    "danger": (255, 60, 80),
    "border": (40, 60, 90),
    "focus": (255, 220, 50),    # Golden Focus Ring
    "glow": (0, 200, 255, 50)   # Alpha Glow
}

class SmoothFloat:
    """Helper for buttery smooth animations"""
    def __init__(self, value, speed=0.15):
        self.target = value
        self.current = value
        self.speed = speed
    
    def update(self):
        self.current += (self.target - self.current) * self.speed
    
    def set(self, value):
        self.target = value

def draw_rounded_rect(surface, rect, color, corner_radius, width=0, alpha=None):
    """Draws a rounded rect with optional alpha transparency"""
    if alpha is not None:
        # Create a temp surface for alpha blending
        shape_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        color = (*color[:3], alpha)
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), width, border_radius=corner_radius)
        surface.blit(shape_surf, rect)
    else:
        pygame.draw.rect(surface, color, rect, width, border_radius=corner_radius)

class UIElement:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.hovered = False
        self.focused = False
        self.anim_focus = SmoothFloat(0.0, 0.2)

    def update(self):
        self.anim_focus.target = 1.0 if self.focused else 0.0
        self.anim_focus.update()

class Button(UIElement):
    def __init__(self, x, y, w, h, text, font, on_click=None, bg_color=None):
        super().__init__(x, y, w, h)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.bg_color = bg_color or COLORS["panel"]
        self.anim_hover = SmoothFloat(0.0, 0.2)
        
    def update(self):
        super().update()
        is_active = self.hovered or self.focused
        self.anim_hover.target = 1.0 if is_active else 0.0
        self.anim_hover.update()
        
    def draw(self, screen):
        # Base Color Interpolation
        base = self.bg_color
        hover_col = (min(255, base[0]+30), min(255, base[1]+30), min(255, base[2]+30))
        
        t = self.anim_hover.current
        color = (
            int(base[0] + (hover_col[0] - base[0]) * t),
            int(base[1] + (hover_col[1] - base[1]) * t),
            int(base[2] + (hover_col[2] - base[2]) * t)
        )
        
        # Glow Effect on Focus
        if self.anim_focus.current > 0.01:
            glow_size = int(8 * self.anim_focus.current)
            glow_rect = self.rect.inflate(glow_size, glow_size)
            draw_rounded_rect(screen, glow_rect, COLORS["accent"], 12, width=0, alpha=30)
            
        # Background
        draw_rounded_rect(screen, self.rect, color, 8)
        
        # Border (Accent if focused)
        if self.focused:
            draw_rounded_rect(screen, self.rect.inflate(4, 4), COLORS["focus"], 10, width=2)
            
        # Text
        txt_surf = self.font.render(self.text, True, COLORS["text"])
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

class Slider(UIElement):
    def __init__(self, x, y, w, h, value=0.0):
        super().__init__(x, y, w, h)
        self.value = value
        self.dragging = False
        self.handle_anim = SmoothFloat(value, 0.2)
        
    def update(self):
        super().update()
        if not self.dragging:
            self.handle_anim.target = self.value
        else:
            self.handle_anim.current = self.value # Instant when dragging
        self.handle_anim.update()
        
    def draw(self, screen):
        # Track
        center_y = self.rect.centery
        track_rect = pygame.Rect(self.rect.x, center_y - 3, self.rect.width, 6)
        draw_rounded_rect(screen, track_rect, COLORS["panel"], 3)
        
        # Fill
        fill_w = int(self.handle_anim.current * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, center_y - 3, fill_w, 6)
        draw_rounded_rect(screen, fill_rect, COLORS["accent"], 3)
        
        # Handle
        hx = self.rect.x + fill_w
        radius = 12 if (self.hovered or self.dragging) else 10
        if self.focused: radius = 13
        
        handle_col = COLORS["focus"] if self.focused else COLORS["text"]
        pygame.draw.circle(screen, handle_col, (hx, center_y), radius)
        
        # Visual Glow if focused
        if self.focused:
             pygame.draw.circle(screen, (*COLORS["focus"], 100), (hx, center_y), radius+6, width=2)

class SimConfigPanel:
    def __init__(self):
        pygame.init()
        # Safe Resolution
        self.WIDTH, self.HEIGHT = 1024, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Advanced Simulation Configuration")
        self.clock = pygame.time.Clock()
        
        # Modern Fonts (Extra Small for perfect fit)
        self.FONT_TITLE = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.FONT_HEADER = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.FONT_BODY = pygame.font.SysFont("Consolas", 12)
        self.FONT_SMALL = pygame.font.SysFont("Segoe UI", 10)
        
        self.running = True
        
        # Data
        self.config = {
            "entropy": 0.3,
            "target_dist": "Medium",
            "agents": []
        }
        
        # Shortened algorithm names for UI
        self.algorithms = ["A*", "BFS", "DFS", "UCS", "IDS", "Greedy", "Genetic"]
        self.shapes = ["Sphere", "Cube", "Drone", "Alien"]
        self.dist_options = ["Near", "Mid", "Far"]
        
        # Initialize 8 Agents
        for i in range(8):
            self.config["agents"].append({
                "algo_index": i % len(self.algorithms),
                "shape_index": i % len(self.shapes),
                "active": i < 2
            })
            
        self.elements = []
        self.focus_index = -1
        self._init_ui()

    def _init_ui(self):
        self.elements = []
        W, H = self.WIDTH, self.HEIGHT
        MARGIN_X = int(W * 0.05)
        
        # --- 1. Top Section: Global Config ---
        # Entropy Slider
        lbl_h = 30
        self.slider_entropy = Slider(MARGIN_X, int(H*0.15), int(W*0.4), 20, self.config["entropy"])
        self.elements.append(self.slider_entropy)
        
        # Distance Buttons (Group)
        btn_w, btn_h = 70, 30
        start_dist_x = int(W * 0.62)
        dist_y = int(H * 0.14)
        
        for i, opt in enumerate(self.dist_options):
            is_selected = (self.config["target_dist"] == opt)
            col = COLORS["accent_dim"] if is_selected else COLORS["panel"]
            if is_selected: col = COLORS["accent"] # Highlight selected
            
            btn = Button(
                start_dist_x + i*(btn_w+6), dist_y, btn_w, btn_h, 
                opt, self.FONT_SMALL, 
                lambda o=opt: self._set_dist(o),
                bg_color=col
            )
            self.elements.append(btn)
            
        # --- 2. Agents Grid (2 Columns x 4 Rows) ---
        grid_start_y = int(H * 0.26)
        col_width = int((W - 3*MARGIN_X) / 2)
        row_height = 55
        
        for i in range(8):
            row = i // 2
            col = i % 2
            
            x_base = MARGIN_X + col * (col_width + MARGIN_X)
            y_base = grid_start_y + row * (row_height + 10)
            
            agent_data = self.config["agents"][i]
            is_active = agent_data["active"]
            
            # Toggle Button (Left)
            btn_active = Button(
                x_base, y_base, 40, 40,
                "ON" if is_active else "OFF",
                self.FONT_SMALL,
                lambda idx=i: self._toggle_agent(idx),
                bg_color=COLORS["success"] if is_active else COLORS["border"]
            )
            self.elements.append(btn_active)
            
            if not is_active:
                continue
                
            # Algo Button (Middle) - Wider
            algo_w = int(col_width * 0.48)
            curr_algo = self.algorithms[agent_data["algo_index"]]
            btn_algo = Button(
                x_base + 45, y_base + 2, algo_w, 36,
                curr_algo, 
                self.FONT_BODY,
                lambda idx=i: self._cycle_algo(idx),
                bg_color=COLORS["panel_hover"]
            )
            self.elements.append(btn_algo)
            
            # Shape Button (Right)
            shape_w = int(col_width * 0.35)
            curr_shape = self.shapes[agent_data["shape_index"]]
            btn_shape = Button(
                x_base + 45 + algo_w + 6, y_base + 2, shape_w, 36,
                curr_shape,
                self.FONT_SMALL,
                lambda idx=i: self._cycle_shape(idx),
                bg_color=COLORS["panel"]
            )
            self.elements.append(btn_shape)

        # --- 3. Start Button (Shorter Text) ---
        start_w = 200
        self.btn_start = Button(
            (W - start_w)//2, H - 80, start_w, 50,
            "START", self.FONT_TITLE,
            self._start_sim,
            bg_color=COLORS["accent"]
        )
        self.elements.append(self.btn_start)

    # --- Actions ---
    def _set_dist(self, val):
        self.config["target_dist"] = val
        self._refresh(keep_values=True)
    def _toggle_agent(self, idx):
        self.config["agents"][idx]["active"] = not self.config["agents"][idx]["active"]
        # Ensure at least one
        if not any(a["active"] for a in self.config["agents"]):
             self.config["agents"][idx]["active"] = True
        self._refresh(keep_values=True)
    def _cycle_algo(self, idx):
        self.config["agents"][idx]["algo_index"] = (self.config["agents"][idx]["algo_index"] + 1) % len(self.algorithms)
        self._refresh(keep_values=True)
    def _cycle_shape(self, idx):
        self.config["agents"][idx]["shape_index"] = (self.config["agents"][idx]["shape_index"] + 1) % len(self.shapes)
        self._refresh(keep_values=True)
    def _start_sim(self):
        self.running = False
        
    def _refresh(self, keep_values=True):
        if keep_values:
            # Capture volatile state like slider
            self.config["entropy"] = self.slider_entropy.value
        
        old_focus = self.focus_index
        self._init_ui()
        # Restore focus nicely
        self.focus_index = min(old_focus, len(self.elements)-1)
        if keep_values:
            self.slider_entropy.value = self.config["entropy"]

    def handle_input(self):
        dt = self.clock.get_time() / 1000.0
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        
        rebuild = False
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Keyboard Navigation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
                    delta = -1 if shift else 1
                    self.focus_index = (self.focus_index + delta) % len(self.elements)
                    
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if 0 <= self.focus_index < len(self.elements):
                        elem = self.elements[self.focus_index]
                        if isinstance(elem, Button) and elem.on_click:
                            elem.on_click()
                            rebuild = True

                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    # Smart Grid Nav could go here, for now simple linear or slider control
                    if 0 <= self.focus_index < len(self.elements):
                        elem = self.elements[self.focus_index]
                        if isinstance(elem, Slider):
                            delta = 0.05 if event.key in (pygame.K_RIGHT, pygame.K_UP) else -0.05
                            elem.value = max(0.0, min(1.0, elem.value + delta))
                            self.config["entropy"] = elem.value
                        else:
                            # Linear navigation for buttons too
                            delta = 1 if event.key in (pygame.K_RIGHT, pygame.K_DOWN) else -1
                            self.focus_index = (self.focus_index + delta) % len(self.elements)

            # Mouse Interaction
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked_any = False
                    for i, elem in enumerate(self.elements):
                        if elem.rect.collidepoint(mouse_pos):
                            self.focus_index = i
                            clicked_any = True
                            if isinstance(elem, Button) and elem.on_click:
                                elem.on_click()
                                rebuild = True
                            if isinstance(elem, Slider):
                                elem.dragging = True
                                self._update_slider(elem, mouse_pos)
                            break
                    
                    if not clicked_any:
                        self.focus_index = -1

            if event.type == pygame.MOUSEBUTTONUP:
                for elem in self.elements:
                    if isinstance(elem, Slider):
                        elem.dragging = False

        # Continuous Updates
        for i, elem in enumerate(self.elements):
            elem.focused = (i == self.focus_index)
            elem.hovered = elem.rect.collidepoint(mouse_pos)
            
            if isinstance(elem, Slider) and elem.dragging:
                self._update_slider(elem, mouse_pos)
                
            elem.update()
            
        if rebuild:
            self._refresh(keep_values=True)

    def _update_slider(self, slider, pos):
        val = (pos[0] - slider.rect.x) / slider.rect.width
        slider.value = max(0.0, min(1.0, val))
        self.config["entropy"] = slider.value

    def draw(self):
        # 1. Background (Gradient-ish)
        self.screen.fill(COLORS["bg"])
        
        # 2. Global Labels
        W, H = self.WIDTH, self.HEIGHT
        MARGIN_X = int(W * 0.05)
        
        # Header
        title = self.FONT_TITLE.render("Simulation Config", True, COLORS["text"])
        self.screen.blit(title, (MARGIN_X, 25))
        
        # Entropy Label
        ent_val = int(self.config["entropy"] * 100)
        lbl_ent = self.FONT_HEADER.render(f"Entropy: {ent_val}%", True, COLORS["accent"])
        self.screen.blit(lbl_ent, (MARGIN_X, int(H*0.10)))
        
        # Distance Label
        lbl_dist = self.FONT_HEADER.render("Goal:", True, COLORS["text"])
        self.screen.blit(lbl_dist, (int(W*0.62), int(H*0.09)))
        
        # Agents Header
        lbl_agents = self.FONT_HEADER.render("Agents", True, COLORS["accent"])
        self.screen.blit(lbl_agents, (MARGIN_X, int(H*0.22)))
        
        # 3. Draw Elements
        for elem in self.elements:
            elem.draw(self.screen)
            
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            if not self.running: break
            self.draw()
            self.clock.tick(60)
        return self.finalize_config()

    def finalize_config(self):
        # Map short UI names to full algorithm names
        algo_map = {
            "A*": "A* search",
            "BFS": "BFS",
            "DFS": "DFS",
            "UCS": "UCS",
            "IDS": "IDS",
            "Greedy": "Hill Climbing",
            "Genetic": "Genetic"
        }
        
        shape_map = {
            "Sphere": "sphere_droid",
            "Cube": "robo_cube",
            "Drone": "mini_drone",
            "Alien": "crystal_alien"
        }
        
        dist_map = {
            "Near": "Near",
            "Mid": "Medium",
            "Far": "Far"
        }
        
        final_agents = []
        for a in self.config["agents"]:
            if a["active"]:
                short_algo = self.algorithms[a["algo_index"]]
                short_shape = self.shapes[a["shape_index"]]
                final_agents.append({
                    "algo_name": algo_map.get(short_algo, short_algo),
                    "shape": shape_map.get(short_shape, short_shape)
                })
        return {
            "entropy": self.config["entropy"],
            "target_dist": dist_map.get(self.config["target_dist"], self.config["target_dist"]),
            "agents": final_agents
        }
