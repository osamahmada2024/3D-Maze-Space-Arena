import pygame
import sys

# ----- Config -----
WIDTH, HEIGHT = 1200, 720
FPS = 60

# Colors
BG = (12, 18, 24)
PANEL = (14, 30, 36)
ACCENT = (0, 170, 170)
ACCENT_DARK = (6, 95, 95)
CARD = (18, 30, 38)
WHITE = (230, 230, 230)
LIGHT = (150, 170, 180)
GREEN = (60, 220, 100)
BUTTON = (25, 45, 52)
BUTTON_H = (40, 90, 95)

def get_font(size, bold=False):
    try:
        return pygame.font.SysFont("Arial", size, bold=bold)
    except:
        return pygame.font.SysFont(None, size, bold=bold)

TITLE_FONT = get_font(46, True)
H_FONT = get_font(28, True)
REG_FONT = get_font(20)
SM_FONT = get_font(16)

# Mouse helper
def inside(rect, pos):
    x, y, w, h = rect
    return x <= pos[0] <= x+w and y <= pos[1] <= y+h

def rounded_rect(surface, rect, color, r=8, border=0, border_color=(0,0,0)):
    x,y,w,h = rect
    shape_surf = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, (0,0,w,h), border_radius=r)
    if border:
        pygame.draw.rect(shape_surf, border_color, (0,0,w,h), border, border_radius=r)
    surface.blit(shape_surf, (x,y))

# NOTE: UI drawing functions (same as you provided) but expecting a surface argument
def draw_grid_area(screen):
    outer = pygame.Rect(30, 40, 520, 520)
    rounded_rect(screen, outer, (8,58,58), r=8)
    inner = pygame.Rect(50, 60, 480, 480)
    rounded_rect(screen, inner, CARD, r=6, border=2, border_color=ACCENT_DARK)
    gx, gy = inner.topleft
    gw, gh = inner.size
    cell = 12
    for i in range(0, gw, cell):
        pygame.draw.line(screen, (60,60,60), (gx+i, gy), (gx+i, gy+gh))
    for j in range(0, gh, cell):
        pygame.draw.line(screen, (60,60,60), (gx, gy+j), (gx+gw, gy+j))
    btns = [("Start", (0,180,180)), ("Reset", (200,30,30)), ("Step", (200,180,0))]
    bx = 50
    by = inner.bottom + 14
    for text, col in btns:
        rect = pygame.Rect(bx, by, 120, 34)
        rounded_rect(screen, rect, col, r=6)
        label = REG_FONT.render(text, True, (10,10,10))
        screen.blit(label, (bx + (120-label.get_width())//2, by + (34 - label.get_height())//2))
        bx += 140

def draw_right_ui(screen, num_agents, algos, menu_stage, cursor, available_algos):
    title_surf = TITLE_FONT.render("Menu & Input Manager", True, WHITE)
    title_box = pygame.Rect(590, 20, 560, 72)
    rounded_rect(screen, title_box, ACCENT, r=6)
    screen.blit(title_surf, (title_box.x + 18, title_box.y + 10))

    text_block = [
        "التحكم في القائمة والمدخلات",
        "التحكم في اختيار عدد ال agents وخوارزمياتهم قبل بداية اللعبة",
        "",
        "مداخلات: keyboard input أو الأزرار ثم تأكيد",
    ]
    y = 120
    for i, line in enumerate(text_block):
        if i == 0:
            surf = H_FONT.render(line, True, WHITE)
        else:
            surf = REG_FONT.render(line, True, LIGHT)
        screen.blit(surf, (610, y))
        y += surf.get_height() + 8

    big_rect = pygame.Rect(590, 200, 560, 240)
    rounded_rect(screen, big_rect, PANEL, r=8, border=2, border_color=(20,70,80))

    steps = [
        "عملية المعالجة:",
        "1) اختيار عدد ال agents من 1 - 8",
        "2) اختيار الخوارزمية لكل agent",
        "3) A*=1, BFS=2, DFS=3",
    ]
    yy = big_rect.y + 12
    for i, s in enumerate(steps):
        color = GREEN if i>0 and i<4 else LIGHT if i==0 else LIGHT
        f = REG_FONT if i>0 else H_FONT
        surf = f.render(s, True, color)
        screen.blit(surf, (big_rect.x + 18, yy))
        yy += surf.get_height() + 8

    v_surf = SM_FONT.render("menu_num_agents, menu_agent_algo, menu_stage", True, GREEN)
    screen.blit(v_surf, (big_rect.x + 18, big_rect.bottom - 26))

    bx = big_rect.x + 12
    by = big_rect.bottom + 6
    for n in range(1,9):
        brect = pygame.Rect(bx, by, 48, 36)
        rounded_rect(screen, brect, BUTTON_H if n==num_agents else BUTTON, r=6)
        label = REG_FONT.render(str(n), True, WHITE)
        screen.blit(label, (brect.x + (48 - label.get_width())//2, brect.y + 6))
        bx += 52

    card = pygame.Rect(590, 460, 560, 180)
    rounded_rect(screen, card, PANEL, r=8, border=2, border_color=(20,70,80))
    st = "Configuration:"
    s1 = f"Agents: {num_agents}"
    s2 = "Algorithms: " + (", ".join(algos) if algos else "—")
    screen.blit(H_FONT.render(st, True, ACCENT), (card.x + 18, card.y + 12))
    screen.blit(REG_FONT.render(s1, True, WHITE), (card.x + 18, card.y + 52))
    screen.blit(REG_FONT.render(s2, True, WHITE), (card.x + 18, card.y + 82))
    hint = SM_FONT.render("Use W/S or Up/Down to move, ENTER to select, R to reset", True, LIGHT)
    screen.blit(hint, (card.x + 18, card.bottom - 34))

def draw_left_small_menu(screen):
    box = pygame.Rect(30, 600, 300, 100)
    rounded_rect(screen, box, PANEL, r=8, border=2, border_color=(20,70,80))
    title = H_FONT.render("مفاهيم أساسية", True, ACCENT)
    screen.blit(title, (box.x + 12, box.y + 8))
    items = ["واجهة مستخدم تفاعلية", "تحديد عدد الوكلاء", "اختيار الخوارزميات", "بدء المحاكاة"]
    yy = box.y + 44
    for it in items:
        s = SM_FONT.render("• " + it, True, LIGHT)
        screen.blit(s, (box.x + 16, yy))
        yy += s.get_height() + 6

def draw_selection_menu(screen, menu_stage, cursor, num_agents, algos, available_algos):
    area = pygame.Rect(350, 120, 220, 420)
    rounded_rect(screen, area, CARD, r=8, border=2, border_color=ACCENT_DARK)
    if menu_stage == 0:
        label = H_FONT.render("اختر عدد الوكلاء (1-8)", True, WHITE)
        screen.blit(label, (area.x + 12, area.y + 12))
        for i in range(1,6):
            y = area.y + 60 + (i-1)*52
            r = pygame.Rect(area.x + 12, y, area.width - 24, 44)
            rounded_rect(screen, r, BUTTON_H if (i-1)==cursor else BUTTON, r=6)
            txt = REG_FONT.render(str(i), True, WHITE)
            screen.blit(txt, (r.x + 12, r.y + (44 - txt.get_height())//2))
    elif menu_stage == 1:
        ag = len(algos) + 1
        label = H_FONT.render(f"اختار خوارزمية للـ Agent {ag}", True, WHITE)
        screen.blit(label, (area.x + 12, area.y + 12))
        for i, a in enumerate(available_algos):
            y = area.y + 60 + i*52
            r = pygame.Rect(area.x + 12, y, area.width - 24, 44)
            rounded_rect(screen, r, BUTTON_H if i==cursor else BUTTON, r=6)
            txt = REG_FONT.render(a, True, WHITE)
            screen.blit(txt, (r.x + 12, r.y + (44 - txt.get_height())//2))
    else:
        label = H_FONT.render("Configuration Completed", True, GREEN)
        screen.blit(label, (area.x + 12, area.y + 12))
        y = area.y + 60
        for i in range(num_agents):
            text = f"Agent {i+1}: {algos[i] if i < len(algos) else '—'}"
            txt = REG_FONT.render(text, True, WHITE)
            screen.blit(txt, (area.x + 12, y))
            y += txt.get_height() + 8

def reset_menu_state(state):
    state['menu_stage'] = 0
    state['num_agents'] = 1
    state['algos'] = []
    state['cursor'] = 0

def handle_bottom_click(pos, state):
    area = pygame.Rect(590 + 12, 200 + 240 + 6, 560 - 24, 40)
    if inside((area.x, area.y, area.w, area.h), pos):
        rel_x = pos[0] - area.x
        idx = rel_x // 52
        if 0 <= idx < 8:
            state['num_agents'] = int(idx) + 1
            state['algos'] = []
            if state['menu_stage'] == 2:
                state['menu_stage'] = 0

# === public API: main() ===
def main():
    # initialize pygame inside main (so module import won't init)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Menu & Input Manager - Demo")
    clock = pygame.time.Clock()

    state = {
        'menu_stage': 0,
        'num_agents': 1,
        'algos': [],
        'cursor': 0,
        'available_algos': ["A*", "BFS", "DFS"]
    }

    running = True
    while running:
        dt = clock.tick(FPS)
        screen.fill(BG)

        draw_grid_area(screen)
        draw_right_ui(screen, state['num_agents'], state['algos'], state['menu_stage'], state['cursor'], state['available_algos'])
        draw_left_small_menu(screen)
        draw_selection_menu(screen, state['menu_stage'], state['cursor'], state['num_agents'], state['algos'], state['available_algos'])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # user closed window -> return current state (or None to indicate cancel)
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_menu_state(state)
                elif event.key in (pygame.K_w, pygame.K_UP):
                    if state['cursor'] > 0:
                        state['cursor'] -= 1
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    if state['menu_stage'] == 0:
                        if state['cursor'] < 4: state['cursor'] += 1
                    elif state['menu_stage'] == 1:
                        if state['cursor'] < len(state['available_algos'])-1: state['cursor'] += 1
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if state['menu_stage'] == 0:
                        chosen = state['cursor'] + 1
                        state['num_agents'] = chosen
                        state['algos'] = []
                        state['menu_stage'] = 1
                        state['cursor'] = 0
                    elif state['menu_stage'] == 1:
                        choice = state['available_algos'][state['cursor']]
                        state['algos'].append(choice)
                        if len(state['algos']) >= state['num_agents']:
                            state['menu_stage'] = 2
                        else:
                            state['cursor'] = 0
                    elif state['menu_stage'] == 2:
                        # final screen: ENTER will finish and return selections
                        running = False
                        break
                elif event.key == pygame.K_1:
                    state['num_agents'] = 1; state['algos'] = []; state['menu_stage'] = 1; state['cursor'] = 0
                elif event.key == pygame.K_2:
                    state['num_agents'] = 2; state['algos'] = []; state['menu_stage'] = 1; state['cursor'] = 0
                elif event.key == pygame.K_3:
                    state['num_agents'] = 3; state['algos'] = []; state['menu_stage'] = 1; state['cursor'] = 0
                elif event.key == pygame.K_4:
                    state['num_agents'] = 4; state['algos'] = []; state['menu_stage'] = 1; state['cursor'] = 0
                elif event.key == pygame.K_5:
                    state['num_agents'] = 5; state['algos'] = []; state['menu_stage'] = 1; state['cursor'] = 0
                elif event.key == pygame.K_q:
                    running = False
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mpos = pygame.mouse.get_pos()
                sel_area = pygame.Rect(350, 120, 220, 420)
                if sel_area.collidepoint(mpos):
                    if state['menu_stage'] == 0:
                        for i in range(1,6):
                            y = sel_area.y + 60 + (i-1)*52
                            r = pygame.Rect(sel_area.x + 12, y, sel_area.width - 24, 44)
                            if r.collidepoint(mpos):
                                state['num_agents'] = i
                                state['algos'] = []
                                state['menu_stage'] = 1
                                state['cursor'] = 0
                    elif state['menu_stage'] == 1:
                        for i, a in enumerate(state['available_algos']):
                            y = sel_area.y + 60 + i*52
                            r = pygame.Rect(sel_area.x + 12, y, sel_area.width - 24, 44)
                            if r.collidepoint(mpos):
                                state['algos'].append(a)
                                if len(state['algos']) >= state['num_agents']:
                                    state['menu_stage'] = 2
                                else:
                                    state['cursor'] = 0
                handle_bottom_click(mpos, state)

        # clamp cursor
        if state['menu_stage'] == 0:
            state['cursor'] = max(0, min(state['cursor'], 4))
        elif state['menu_stage'] == 1:
            state['cursor'] = max(0, min(state['cursor'], len(state['available_algos'])-1))
        else:
            state['cursor'] = 0

        vign = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vign, (0,0,0,30), (0,0,WIDTH,HEIGHT))
        screen.blit(vign, (0,0))

        pygame.display.flip()

    # Clean up but don't sys.exit() so caller can continue
    pygame.quit()

    # return final choices: (num_agents, algos)
    return state['num_agents'], state['algos']
