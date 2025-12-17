
import pygame
import sys

# Modern Color Palette
COLORS = {
    "bg": (15, 23, 42),       # Dark Blue-Grey
    "panel": (30, 41, 59),    # Lighter Blue-Grey
    "panel_hover": (40, 55, 80),
    "accent": (6, 182, 212),  # Cyan
    "accent_hover": (34, 211, 238),
    "text": (241, 245, 249),
    "text_dim": (148, 163, 184),
    "success": (34, 197, 94),
    "success_hover": (74, 222, 128),
    "danger": (239, 68, 68),
    "border": (51, 65, 85),
    "focus": (250, 204, 21)   # Yellow for keyboard focus ring
}

class SmoothFloat:
    """Helper for smooth value transitions"""
    def __init__(self, value, speed=0.2):
        self.target = value
        self.current = value
        self.speed = speed
    
    def update(self):
        self.current += (self.target - self.current) * self.speed
    
    def set(self, value):
        self.target = value

class UIElement:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.hovered = False
        self.focused = False

class Button(UIElement):
    def __init__(self, x, y, w, h, text, font, on_click=None, color_key="panel"):
        super().__init__(x, y, w, h)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.color_key = color_key
        # Smooth animation for background
        self.anim_hover = SmoothFloat(0.0, 0.2)

    def update(self):
        self.anim_hover.target = 1.0 if (self.hovered or self.focused) else 0.0
        self.anim_hover.update()

    def draw(self, screen):
        # Interpolate color between base and hover
        base = COLORS[self.color_key]
        hover = COLORS.get(self.color_key + "_hover", COLORS["accent_hover"])
        
        t = self.anim_hover.current
        color = (
            int(base[0] + (hover[0] - base[0]) * t),
            int(base[1] + (hover[1] - base[1]) * t),
            int(base[2] + (hover[2] - base[2]) * t)
        )
        
        # Shadow
        if t > 0.1:
            s_rect = self.rect.move(0, 2)
            pygame.draw.rect(screen, (0,0,0, 50), s_rect, border_radius=8)

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        border_col = COLORS["focus"] if self.focused else COLORS["border"]
        width = 2 if self.focused else 1
        pygame.draw.rect(screen, border_col, self.rect, width, border_radius=8)
        
        txt_surf = self.font.render(self.text, True, COLORS["text"])
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

class Slider(UIElement):
    def __init__(self, x, y, w, h, value=0.0):
        super().__init__(x, y, w, h)
        self.value = value # 0.0 to 1.0
        self.handle_anim = SmoothFloat(value, 0.3)
        self.dragging = False

    def update(self):
        # Only smooth towards value if not dragging (direct control)
        # But for nice visual lag, we can always smooth the display handle
        self.handle_anim.target = self.value
        self.handle_anim.update()

    def draw(self, screen):
        # Track
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 4, self.rect.width, 8)
        pygame.draw.rect(screen, COLORS["panel"], track_rect, border_radius=4)
        
        # Fill
        fill_w = int(self.handle_anim.current * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.centery - 4, fill_w, 8)
        pygame.draw.rect(screen, COLORS["accent"], fill_rect, border_radius=4)
        
        # Handle
        hx = self.rect.x + fill_w
        hy = self.rect.centery
        radius = 12 if self.hovered or self.dragging or self.focused else 10
        col = COLORS["focus"] if self.focused else COLORS["text"]
        pygame.draw.circle(screen, col, (hx, hy), radius)
        
        # Border for focus
        if self.focused:
            pygame.draw.rect(screen, COLORS["focus"], self.rect.inflate(10, 10), 1, border_radius=4)

class SimConfigPanel:
    def __init__(self):
        pygame.init()
        # Use a safe resolution
        self.WIDTH, self.HEIGHT = 1024, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Advanced Simulation Configuration")
        self.clock = pygame.time.Clock()
        
        # Fonts - Adjusted sizes
        self.FONT_TITLE = pygame.font.Font(None, 42)
        self.FONT_HEADER = pygame.font.Font(None, 28) # Smaller
        self.FONT_BODY = pygame.font.Font(None, 24)   # Readable
        
        self.running = True
        
        # Config State
        self.config = {
            "entropy": 0.3,
            "target_dist": "Medium",
            "agents": []
        }
        
        self.algorithms = ["A* search", "Genetic", "BFS", "DFS", "Dijkstra"]
        self.shapes = ["sphere_droid", "robo_cube", "mini_drone", "crystal_alien"]
        self.dist_options = ["Near", "Medium", "Far"]
        
        # Initialize default agents
        for i in range(4):
            self.config["agents"].append({
                "algo_index": 0,
                "shape_index": i,
                "active": i == 0
            })
            
        self.elements = []
        self.focus_index = -1
        self._init_ui()

    def _init_ui(self):
        self.elements = []
        
        # Dynamic Layout Constants (Percentages)
        W, H = self.WIDTH, self.HEIGHT
        
        # Margins
        MARGIN_X = int(W * 0.05)
        
        # 1. Entropy Slider
        slider_y = int(H * 0.18)
        self.slider_entropy = Slider(MARGIN_X, slider_y, int(W * 0.9), 30, self.config["entropy"])
        self.elements.append(self.slider_entropy)
        
        # 2. Target Dist Buttons
        dist_y = int(H * 0.28)
        btn_w = int(W * 0.12)
        btn_h = 40
        start_x = int(W * 0.25)
        gap = int(W * 0.02)
        
        for i, opt in enumerate(self.dist_options):
            btn = Button(
                start_x + i * (btn_w + gap), dist_y, btn_w, btn_h, 
                opt, self.FONT_BODY, 
                lambda o=opt: self._set_dist(o),
                color_key="accent" if self.config["target_dist"] == opt else "panel"
            )
            self.elements.append(btn)
            
        # 3. Agents List
        agents_start_y = int(H * 0.40)
        row_h = int(H * 0.11)
        
        # Column X positions
        col_act_x = MARGIN_X
        # col_name_x = MARGIN_X + 60 (Label, simplified)
        col_algo_x = int(W * 0.25)
        col_shape_x = int(W * 0.55)
        
        algo_w = int(W * 0.25)
        shape_w = int(W * 0.25)
        
        for i in range(4):
            y = agents_start_y + i * row_h
            
            # Active Toggle
            btn_act = Button(
                col_act_x, y + 10, 50, 50, 
                "✔" if self.config["agents"][i]["active"] else "X",
                self.FONT_HEADER,
                lambda idx=i: self._toggle_agent(idx),
                color_key="success" if self.config["agents"][i]["active"] else "panel"
            )
            self.elements.append(btn_act)
            
            if not self.config["agents"][i]["active"]:
                continue
                
            # Algo Cycle
            curr_algo = self.algorithms[self.config["agents"][i]["algo_index"]]
            btn_algo = Button(
                col_algo_x, y + 10, algo_w, 50,
                f"Algo: {curr_algo}",
                self.FONT_BODY,
                lambda idx=i: self._cycle_algo(idx)
            )
            self.elements.append(btn_algo)
            
            # Shape Cycle
            curr_shape = self.shapes[self.config["agents"][i]["shape_index"]]
            btn_shape = Button(
                col_shape_x, y + 10, shape_w, 50,
                f"Shape: {curr_shape}",
                self.FONT_BODY,
                lambda idx=i: self._cycle_shape(idx)
            )
            self.elements.append(btn_shape)
            
        # 4. Start Button
        start_btn_w = int(W * 0.2)
        start_btn_h = int(H * 0.08)
        self.btn_start = Button(
            W - start_btn_w - MARGIN_X, H - start_btn_h - 30, start_btn_w, start_btn_h, 
            "START ENGINE", self.FONT_HEADER, 
            self._start_sim, 
            "success"
        )
        self.elements.append(self.btn_start)

    # --- Callbacks ---
    def _set_dist(self, val):
        self.config["target_dist"] = val
        self._refresh_ui_state()

    def _toggle_agent(self, idx):
        active_count = sum(1 for a in self.config["agents"] if a["active"])
        if self.config["agents"][idx]["active"] and active_count > 1:
            self.config["agents"][idx]["active"] = False
        elif not self.config["agents"][idx]["active"]:
            self.config["agents"][idx]["active"] = True
        self._refresh_ui_state()

    def _cycle_algo(self, idx):
        self.config["agents"][idx]["algo_index"] = (self.config["agents"][idx]["algo_index"] + 1) % len(self.algorithms)
        self._refresh_ui_state()

    def _cycle_shape(self, idx):
        self.config["agents"][idx]["shape_index"] = (self.config["agents"][idx]["shape_index"] + 1) % len(self.shapes)
        self._refresh_ui_state()
        
    def _start_sim(self):
        self.running = False
        
    def _refresh_ui_state(self):
        prev_focus_idx = self.focus_index
        
        # Capture slider value
        self.config["entropy"] = self.elements[0].value
        
        self._init_ui()
        
        # Clamp focus
        if prev_focus_idx >= len(self.elements):
            self.focus_index = len(self.elements) - 1
        else:
            self.focus_index = prev_focus_idx
            
        # Restore slider value
        self.elements[0].value = self.config["entropy"]

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        
        action_triggered = False
        rebuild_needed = False
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
                elif event.key == pygame.K_TAB:
                    shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
                    if shift:
                        self.focus_index = (self.focus_index - 1) % len(self.elements)
                    else:
                        self.focus_index = (self.focus_index + 1) % len(self.elements)
                        
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if 0 <= self.focus_index < len(self.elements):
                        elem = self.elements[self.focus_index]
                        if isinstance(elem, Button) and elem.on_click:
                            elem.on_click()
                            rebuild_needed = True
                            
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    if 0 <= self.focus_index < len(self.elements):
                        elem = self.elements[self.focus_index]
                        if isinstance(elem, Slider):
                            delta = -0.05 if event.key == pygame.K_LEFT else 0.05
                            elem.value = max(0.0, min(1.0, elem.value + delta))
                            self.config["entropy"] = elem.value
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = False
                    for i, elem in enumerate(self.elements):
                        if elem.rect.collidepoint(mouse_pos):
                            self.focus_index = i
                            if isinstance(elem, Button) and elem.on_click:
                                elem.on_click()
                                rebuild_needed = True
                            if isinstance(elem, Slider):
                                elem.dragging = True
                                rel_x = mouse_pos[0] - elem.rect.x
                                elem.value = max(0.0, min(1.0, rel_x / elem.rect.width))
                                self.config["entropy"] = elem.value
                            clicked = True
                            break
                    if not clicked:
                        self.focus_index = -1
                        
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for elem in self.elements:
                        if isinstance(elem, Slider):
                            elem.dragging = False
                            
        for i, elem in enumerate(self.elements):
            elem.hovered = elem.rect.collidepoint(mouse_pos)
            elem.focused = (i == self.focus_index)
            
            if isinstance(elem, Slider) and elem.dragging:
                rel_x = mouse_pos[0] - elem.rect.x
                elem.value = max(0.0, min(1.0, rel_x / elem.rect.width))
                self.config["entropy"] = elem.value
                
            elem.update()
            
        if rebuild_needed:
            self._refresh_ui_state()

    def draw(self):
        self.screen.fill(COLORS["bg"])
        W, H = self.WIDTH, self.HEIGHT
        MARGIN_X = int(W * 0.05)
        
        # --- Header ---
        title = self.FONT_TITLE.render("Simulation Configuration", True, COLORS["accent"])
        self.screen.blit(title, (MARGIN_X, int(H * 0.05)))
        
        # --- Separator ---
        sep_y = int(H * 0.12)
        pygame.draw.line(self.screen, COLORS["border"], (MARGIN_X, sep_y), (W-MARGIN_X, sep_y), 2)
        
        # --- Labels ---
        # Entropy
        ent_y = int(H * 0.14)
        lbl_ent = self.FONT_HEADER.render(f"Obstacle Density: {int(self.config['entropy']*100)}%", True, COLORS["text"])
        self.screen.blit(lbl_ent, (MARGIN_X, ent_y))
        
        # Distance
        dist_y = int(H * 0.24)
        lbl_dist = self.FONT_HEADER.render("Goal Distance:", True, COLORS["text"])
        self.screen.blit(lbl_dist, (MARGIN_X, dist_y))
        
        # Separator 2
        sep2_y = int(H * 0.35)
        pygame.draw.line(self.screen, COLORS["border"], (MARGIN_X, sep2_y), (W-MARGIN_X, sep2_y), 2)
        
        # Agents Header
        agents_head_y = int(H * 0.37)
        lbl_agents = self.FONT_TITLE.render("Agents Setup", True, COLORS["accent"])
        self.screen.blit(lbl_agents, (MARGIN_X, agents_head_y))
        
        # Agent Labels (Row headers)
        agents_start_y = int(H * 0.40)
        row_h = int(H * 0.11)
        for i in range(4):
            y = agents_start_y + i * row_h
            idx_txt = self.FONT_HEADER.render(f"Agent {i+1}", True, COLORS["text"])
            self.screen.blit(idx_txt, (MARGIN_X + 70, y + 25))
        
        # --- Dynamic Elements ---
        for elem in self.elements:
            elem.draw(self.screen)
            
        pygame.display.flip()

    def finalize_config(self):
        final_agents = []
        for a in self.config["agents"]:
            if a["active"]:
                final_agents.append({
                    "algo_name": self.algorithms[a["algo_index"]],
                    "shape": self.shapes[a["shape_index"]]
                })
        
        return {
            "entropy": self.config["entropy"],
            "target_dist": self.config["target_dist"],
            "agents": final_agents
        }

    def run(self):
        while self.running:
            self.handle_input()
            if not self.running: break
            self.draw()
            self.clock.tick(60)
        return self.finalize_config()
