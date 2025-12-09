"""
ðŸ”¥ VOLCANIC MAZE ARENA - COMPLETE STANDALONE GAME ðŸ”¥
All features in ONE file - just run and play!

Run: python volcanic_maze.py

Features: Lava rivers, falling stones, particles, audio, health system
Dependencies: pygame PyOpenGL numpy (for audio, optional)
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import sys, time, pygame, random, math

# ========== PARTICLE SYSTEM ==========
class Particle:
    def __init__(self, x, y, z, vx, vy, vz, lifetime, color, size):
        self.x, self.y, self.z, self.vx, self.vy, self.vz = x, y, z, vx, vy, vz
        self.lifetime = self.max_lifetime = lifetime
        self.color, self.size, self.alive = color, size, True
    
    def update(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt; self.z += self.vz * dt
        self.vy -= 2.0 * dt; self.vx *= 0.98; self.vz *= 0.98
        self.lifetime -= dt
        if self.lifetime <= 0: self.alive = False
    
    def get_alpha(self): return self.lifetime / self.max_lifetime

class ParticleSystem:
    def __init__(self):
        self.particles, self.max_particles = [], 500
    
    def emit_fire(self, x, y, z, count=5):
        for _ in range(count):
            self.particles.append(Particle(x, y, z, random.uniform(-0.5, 0.5), random.uniform(0.5, 2.0), 
                random.uniform(-0.5, 0.5), random.uniform(0.5, 1.5), (random.uniform(0.8, 1.0), random.uniform(0.2, 0.5), 0), random.uniform(0.05, 0.15)))
    
    def emit_sparks(self, x, y, z, count=10):
        for _ in range(count):
            angle, speed = random.uniform(0, 2*math.pi), random.uniform(2.0, 5.0)
            self.particles.append(Particle(x, y, z, math.cos(angle)*speed, random.uniform(1.0, 3.0), 
                math.sin(angle)*speed, random.uniform(0.2, 0.6), (1.0, random.uniform(0.8, 1.0), random.uniform(0, 0.3)), random.uniform(0.03, 0.08)))
    
    def emit_steam(self, x, y, z, count=15):
        for _ in range(count):
            gray = random.uniform(0.6, 0.9)
            self.particles.append(Particle(x, y, z, random.uniform(-1, 1), random.uniform(2, 5), 
                random.uniform(-1, 1), random.uniform(1, 2), (gray, gray, gray), random.uniform(0.1, 0.3)))
    
    def update(self, dt):
        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if p.alive][-self.max_particles:]
    
    def draw(self):
        if not self.particles: return
        glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glBegin(GL_QUADS)
        for p in self.particles:
            glColor4f(*p.color, p.get_alpha())
            s = p.size
            glVertex3f(p.x-s, p.y-s, p.z); glVertex3f(p.x+s, p.y-s, p.z)
            glVertex3f(p.x+s, p.y+s, p.z); glVertex3f(p.x-s, p.y+s, p.z)
        glEnd()
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)

# ========== LAVA ENVIRONMENT ==========
class LavaEnvironment:
    def __init__(self, gs, cs):
        self.gs, self.cs, self.time = gs, cs, 0
        self.cracks = [{'segs': [((x:=random.uniform(-gs//2, gs//2), z:=random.uniform(-gs//2, gs//2)), 
            (x:=x+math.cos(a:=random.uniform(0, 2*math.pi))*random.uniform(0.5, 2), z:=z+math.sin(a)*random.uniform(0.5, 2))) 
            for _ in range(random.randint(3, 8))], 'glow': random.uniform(0.3, 0.8)} for _ in range(random.randint(15, 30))]
        self.rivers = [{'pts': [(x:=random.uniform(-gs//2, gs//2), z:=-gs//2)] + 
            [(x:=max(-gs//2, min(gs//2, x+random.uniform(-0.5, 0.5))), z:=z+random.uniform(1, 2)) 
            for _ in range(int(gs))], 'w': random.uniform(0.8, 1.5), 'sp': random.uniform(0.5, 1.5), 'off': random.uniform(0, 100)} 
            for _ in range(random.randint(2, 4))]
        self.stones = [{'x': random.uniform(-gs//2, gs//2), 'z': random.uniform(-gs//2, gs//2), 
            'sz': random.uniform(0.15, 0.4), 'g': random.uniform(0.5, 1), 'ps': random.uniform(1, 3), 
            'po': random.uniform(0, 2*math.pi)} for _ in range(random.randint(20, 40))]
        self.vents = [{'x': random.uniform(-gs//2, gs//2), 'z': random.uniform(-gs//2, gs//2), 
            'lb': time.time()-random.uniform(0, 5), 'bi': random.uniform(3, 7)} for _ in range(random.randint(5, 10))]
    
    def update(self, dt): self.time += dt
    
    def draw_cracks(self):
        glDisable(GL_LIGHTING); glLineWidth(2.0)
        for c in self.cracks:
            g = c['glow']*(0.7+0.3*math.sin(self.time*2))
            glColor3f(g, 0.3*g, 0); glBegin(GL_LINES)
            for s in c['segs']: glVertex3f(s[0][0], 0.01, s[0][1]); glVertex3f(s[1][0], 0.01, s[1][1])
            glEnd()
        glEnable(GL_LIGHTING)
    
    def draw_rivers(self):
        glDisable(GL_LIGHTING)
        for r in self.rivers:
            glBegin(GL_QUAD_STRIP)
            for i, (x, z) in enumerate(r['pts']):
                w = math.sin(i*0.5+r['off']+self.time*r['sp'])*0.3+0.7
                glColor4f(1, 0.4*w, 0, 0.9)
                glVertex3f(x-r['w']/2, 0.05, z); glVertex3f(x+r['w']/2, 0.05, z)
            glEnd()
        glEnable(GL_LIGHTING)
    
    def draw_stones(self):
        for s in self.stones:
            p = math.sin(self.time*s['ps']+s['po'])*0.3+0.7; g = s['g']*p
            glPushMatrix(); glTranslatef(s['x'], s['sz']*0.3, s['z'])
            glColor3f(0.3+0.7*g, 0.1*g, 0)
            q = gluNewQuadric(); gluSphere(q, s['sz'], 8, 8); gluDeleteQuadric(q)
            glPopMatrix()
    
    def check_damage(self, x, z):
        for r in self.rivers:
            for i in range(len(r['pts'])-1):
                p1, p2 = r['pts'][i], r['pts'][i+1]
                dx, dz = p2[0]-p1[0], p2[1]-p1[1]
                if dx==0 and dz==0: d = math.sqrt((x-p1[0])**2+(z-p1[1])**2)
                else:
                    t = max(0, min(1, ((x-p1[0])*dx+(z-p1[1])*dz)/(dx*dx+dz*dz)))
                    d = math.sqrt((x-(p1[0]+t*dx))**2+(z-(p1[1]+t*dz))**2)
                if d < r['w']: return True
        return False
    
    def burst_steam(self, ct):
        return [v for v in self.vents if ct-v['lb']>v['bi'] and not (v.update({'lb': ct}) or True)]

# ========== OBSTACLES ==========
class MovingLava:
    def __init__(self, gs, o='h'):
        self.gs, self.o = gs, o
        self.y, self.x = (random.uniform(-gs//2, gs//2), -gs//2) if o=='h' else (random.uniform(-gs//2, gs//2), -gs//2)
        self.sp, self.l, self.w = random.uniform(2, 4), random.uniform(3, 6), 0.4
    
    def update(self, dt):
        if self.o=='h':
            self.x += self.sp*dt
            if self.x > self.gs//2+self.l: self.x = -self.gs//2-self.l
        else:
            self.y += self.sp*dt
            if self.y > self.gs//2+self.l: self.y = -self.gs//2-self.l
    
    def draw(self, t):
        glDisable(GL_LIGHTING); p = math.sin(t*5)*0.3+0.7
        glBegin(GL_QUADS); glColor4f(1, 0.3*p, 0, 0.9)
        if self.o=='h':
            glVertex3f(self.x, 0.08, self.y-self.w); glVertex3f(self.x+self.l, 0.08, self.y-self.w)
            glVertex3f(self.x+self.l, 0.08, self.y+self.w); glVertex3f(self.x, 0.08, self.y+self.w)
        else:
            glVertex3f(self.x-self.w, 0.08, self.y); glVertex3f(self.x+self.w, 0.08, self.y)
            glVertex3f(self.x+self.w, 0.08, self.y+self.l); glVertex3f(self.x-self.w, 0.08, self.y+self.l)
        glEnd(); glEnable(GL_LIGHTING)
    
    def hit(self, x, z):
        if self.o=='h': return self.x<=x<=self.x+self.l and abs(z-self.y)<self.w
        return self.y<=z<=self.y+self.l and abs(x-self.x)<self.w

class FallingStone:
    def __init__(self, gs):
        self.x, self.z, self.y = random.uniform(-gs//2, gs//2), random.uniform(-gs//2, gs//2), random.uniform(8, 12)
        self.vy, self.sz, self.r, self.rs = 0, random.uniform(0.3, 0.6), random.uniform(0, 360), random.uniform(50, 150)
        self.ok, self.fall, self.wt, self.wtm = True, False, random.uniform(0.5, 1), 0
    
    def update(self, dt):
        if not self.ok: return
        if not self.fall:
            self.wtm += dt
            if self.wtm >= self.wt: self.fall = True
        if self.fall:
            self.vy -= 15*dt; self.y += self.vy*dt; self.r += self.rs*dt
            if self.y <= 0.3: self.ok = False
    
    def draw(self):
        if not self.ok: return
        glPushMatrix(); glTranslatef(self.x, self.y, self.z); glRotatef(self.r, 1, 1, 0)
        glColor3f((math.sin(self.wtm*10)*0.5+0.5 if not self.fall else 0.3), (0 if not self.fall else 0.3), (0 if not self.fall else 0.35))
        s = self.sz
        glBegin(GL_TRIANGLES)
        glVertex3f(0,s,0); glVertex3f(s,0,0); glVertex3f(0,0,s)
        glVertex3f(0,s,0); glVertex3f(0,0,s); glVertex3f(-s,0,0)
        glEnd(); glPopMatrix()
    
    def hit(self, x, z): return self.fall and self.y<=1 and math.sqrt((x-self.x)**2+(z-self.z)**2)<self.sz

class BurnTile:
    def __init__(self, x, z, cs):
        self.x, self.z, self.cs = x, z, cs
        self.ps, self.po = random.uniform(1.5, 3), random.uniform(0, 2*math.pi)
        self.ad, self.id = random.uniform(2, 4), random.uniform(1, 3)
        self.tm, self.on = 0, False
    
    def update(self, dt, t):
        self.tm += dt
        if self.on and self.tm >= self.ad: self.tm, self.on = 0, False
        elif not self.on and self.tm >= self.id: self.tm, self.on = 0, True
    
    def draw(self, t):
        if not self.on: return
        glDisable(GL_LIGHTING); p = math.sin(t*self.ps+self.po)*0.5+0.5; s = self.cs*0.45
        glColor4f(1, 0.2*p, 0, 0.6*p); glBegin(GL_QUADS)
        glVertex3f(self.x-s, 0.02, self.z-s); glVertex3f(self.x+s, 0.02, self.z-s)
        glVertex3f(self.x+s, 0.02, self.z+s); glVertex3f(self.x-s, 0.02, self.z+s)
        glEnd(); glEnable(GL_LIGHTING)
    
    def dmg(self, x, z):
        if not self.on: return False
        s = self.cs*0.45; return abs(x-self.x)<s and abs(z-self.z)<s

class Obstacles:
    def __init__(self, gs, cs):
        self.ll = [MovingLava(gs, random.choice(['h','v'])) for _ in range(random.randint(3,5))]
        self.fs, self.sst, self.ssi = [], 0, random.uniform(2, 4)
        self.bt = [BurnTile(random.randint(-gs//2, gs//2), random.randint(-gs//2, gs//2), cs) for _ in range(random.randint(10,20))]
        self.gs = gs
    
    def update(self, dt, t):
        for l in self.ll: l.update(dt)
        self.sst += dt
        if self.sst >= self.ssi:
            self.sst, self.ssi = 0, random.uniform(2, 4)
            self.fs.append(FallingStone(self.gs))
        for s in self.fs: s.update(dt)
        self.fs = [s for s in self.fs if s.ok]
        for b in self.bt: b.update(dt, t)
    
    def draw(self, t):
        for l in self.ll: l.draw(t)
        for s in self.fs: s.draw()
        for b in self.bt: b.draw(t)
    
    def dmg(self, x, z):
        for l in self.ll:
            if l.hit(x, z): return True
        for s in self.fs:
            if s.hit(x, z): return True
        for b in self.bt:
            if b.dmg(x, z): return True
        return False

# ========== AUDIO ==========
class Audio:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.on = True; self.ac, self.ec = pygame.mixer.Channel(0), pygame.mixer.Channel(1)
        try:
            import numpy as np
            sr, ns = 22050, int(3*22050)
            s = np.random.randint(-32768, 32767, (ns, 2), dtype=np.int16)
            for i in range(1, ns): s[i] = (s[i]*0.3+s[i-1]*0.7).astype(np.int16)
            self.la = pygame.sndarray.make_sound(s)
            self.ac.play(self.la, loops=-1); self.ac.set_volume(0.3)
        except: self.la = None
    
    def toggle(self):
        self.on = not self.on
        if self.on and self.la: self.ac.play(self.la, loops=-1)
        else: self.ac.stop(); self.ec.stop()
    
    def cleanup(self): self.ac.stop(); self.ec.stop()

# # ========== SIMPLE GRID GENERATOR ==========
# def make_grid(sz, prob):
#     g = [[1 if random.random()<prob else 0 for _ in range(sz)] for _ in range(sz)]
#     g[0][0] = g[sz-1][sz-1] = 0
#     return g

# # ========== PATHFINDING (A*) ==========
# def astar(grid, start, goal):
#     from heapq import heappush, heappop
#     open_set, came_from = [(0, start)], {}
#     g_score = {start: 0}
    
#     while open_set:
#         _, cur = heappop(open_set)
#         if cur == goal:
#             path = []
#             while cur in came_from:
#                 path.append(cur); cur = came_from[cur]
#             return list(reversed(path))
        
#         for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
#             nb = (cur[0]+dx, cur[1]+dy)
#             if 0<=nb[0]<len(grid) and 0<=nb[1]<len(grid[0]) and grid[nb[1]][nb[0]]==0:
#                 ng = g_score[cur]+1
#                 if nb not in g_score or ng<g_score[nb]:
#                     g_score[nb] = ng
#                     f = ng+abs(nb[0]-goal[0])+abs(nb[1]-goal[1])
#                     heappush(open_set, (f, nb))
#                     came_from[nb] = cur
#     return []

# # ========== AGENT ==========
# class Agent:
#     def __init__(self, start, goal, path, speed, color):
#         self.path, self.sp, self.col = path, speed, color
#         self.pos, self.pi, self.done = [start[0], 0.3, start[1]], 0, False
    
#     def update(self, dt):
#         if self.done or not self.path or self.pi>=len(self.path): 
#             self.done = True; return
#         t = self.path[self.pi]; tp = [t[0], 0.3, t[1]]
#         dx, dz = tp[0]-self.pos[0], tp[2]-self.pos[2]
#         d = math.sqrt(dx*dx+dz*dz)
#         if d < 0.1: self.pi += 1
#         else:
#             move = min(self.sp*dt, d)
#             self.pos[0] += (dx/d)*move; self.pos[2] += (dz/d)*move

# # ========== CAMERA ==========
# class Cam:
#     def __init__(self, d=15, ax=45, ay=45):
#         self.d, self.ax, self.ay, self.tgt = d, ax, ay, [0,0,0]
    
#     def pos(self):
#         rx, ry = math.radians(self.ax), math.radians(self.ay)
#         return [self.tgt[0]+self.d*math.cos(ry)*math.sin(rx), 
#                 self.tgt[1]+self.d*math.sin(ry), 
#                 self.tgt[2]+self.d*math.cos(ry)*math.cos(rx)]

# # ========== RENDERING ==========
# def init_gl():
#     glClearColor(0.08, 0.02, 0, 1); glEnable(GL_DEPTH_TEST); glEnable(GL_BLEND)
#     glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#     glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_COLOR_MATERIAL)
#     glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
#     glLightfv(GL_LIGHT0, GL_POSITION, [0, 15, 0, 1])
#     glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.1, 0, 1])

# def setup_view(cam, w, h):
#     glMatrixMode(GL_PROJECTION); glLoadIdentity()
#     gluPerspective(60, w/h, 0.1, 100)
#     glMatrixMode(GL_MODELVIEW); glLoadIdentity()
#     p = cam.pos()
#     gluLookAt(p[0], p[1], p[2], cam.tgt[0], cam.tgt[1], cam.tgt[2], 0, 1, 0)

# def draw_grid(sz):
#     glDisable(GL_LIGHTING); glColor3f(0.2, 0.1, 0.05); glLineWidth(1)
#     h = sz//2; glBegin(GL_LINES)
#     for i in range(-h, h+1):
#         glVertex3f(i, 0, -h); glVertex3f(i, 0, h)
#         glVertex3f(-h, 0, i); glVertex3f(h, 0, i)
#     glEnd(); glEnable(GL_LIGHTING)

# def draw_cube(sz):
#     s = sz/2; glBegin(GL_QUADS)
#     glNormal3f(0,0,1); glVertex3f(-s,-s,s); glVertex3f(s,-s,s); glVertex3f(s,s,s); glVertex3f(-s,s,s)
#     glNormal3f(0,1,0); glVertex3f(-s,s,-s); glVertex3f(-s,s,s); glVertex3f(s,s,s); glVertex3f(s,s,-s)
#     glEnd()

# def draw_obstacles(g, gs, t):
#     glEnable(GL_LIGHTING)
#     for y in range(gs):
#         for x in range(gs):
#             if g[y][x]==1:
#                 glPushMatrix(); glTranslatef(x-gs//2, 0.5, y-gs//2)
#                 p = 0.3+0.2*(0.5+0.5*math.sin(t*2+(x-gs//2)+(y-gs//2)))
#                 glColor3f(0.15+p*0.2, 0.1+p*0.1, 0.08)
#                 draw_cube(0.9); glPopMatrix()

# # ========== MAIN ==========
# def main():
#     print("ðŸ”¥ VOLCANIC MAZE ARENA ðŸ”¥")
#     pygame.init()
#     W, H, GS = 1200, 800, 25
#     screen = pygame.display.set_mode((W, H), pygame.DOUBLEBUF|pygame.OPENGL)
#     pygame.display.set_caption("ðŸ”¥ Volcanic Maze")
#     clock = pygame.time.Clock()
    
#     init_gl()
#     grid = make_grid(GS, 0.25)
#     path = astar(grid, (0,0), (GS-1, GS-1))
#     if not path:
#         print("No path!"); return
    
#     agent = Agent((0,0), (GS-1,GS-1), path, 2.0, (1,0.5,0))
#     cam = Cam()
#     lava = LavaEnvironment(GS, 1.0)
#     parts = ParticleSystem()
#     obs = Obstacles(GS, 1.0)
#     aud = Audio()
    
#     hp, last_dmg, gt, fpt, spt = 100, 0, 0, 0, 0
#     run, lt = True, time.time()
    
#     print(f"Start: (0,0) | Goal: ({GS-1},{GS-1}) | Path: {len(path)} | HP: {hp}")
    
#     while run:
#         ct, dt, lt = time.time(), time.time()-lt, time.time()
#         gt += dt
        
#         for e in pygame.event.get():
#             if e.type==pygame.QUIT or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE): run = False
#             elif e.type==pygame.KEYDOWN and e.key==pygame.K_m: aud.toggle()
#             elif e.type==pygame.MOUSEWHEEL: cam.d = max(3, min(40, cam.d-e.y*2))
        
#         k = pygame.key.get_pressed()
#         if k[pygame.K_LEFT]: cam.ax -= 60*dt
#         if k[pygame.K_RIGHT]: cam.ax += 60*dt
#         if k[pygame.K_UP]: cam.ay = min(89, cam.ay+60*dt)
#         if k[pygame.K_DOWN]: cam.ay = max(-89, cam.ay-60*dt)
        
#         agent.update(dt); lava.update(dt); parts.update(dt); obs.update(dt, gt)
#         cam.tgt = [agent.pos[0], agent.pos[1], agent.pos[2]]
        
#         agx, agz = agent.pos[0], agent.pos[2]
#         if ct-last_dmg>0.5 and (lava.check_damage(agx, agz) or obs.dmg(agx, agz)):
#             hp -= 5; last_dmg = ct; parts.emit_sparks(agent.pos[0], agent.pos[1], agent.pos[2], 20)
#             print(f"ðŸ’¥ HP: {hp}")
#             if hp<=0: print("ðŸ’€ GAME OVER!"); run = False
        
#         fpt += dt
#         if fpt>0.1:
#             fpt = 0
#             parts.emit_fire(random.uniform(-GS//2, GS//2), 0, random.uniform(-GS//2, GS//2), 1)
        
#         spt += dt
#         if spt>0.3:
#             spt = 0
#             if random.random()>0.7:
#                 parts.emit_sparks(random.uniform(-GS//2, GS//2), 0, random.uniform(-GS//2, GS//2), 5)
        
#         for v in lava.vents:
#             if ct-v['lb']>v['bi']:
#                 v['lb'] = ct
#                 parts.emit_steam(v['x'], 0, v['z'], 20)
        
#         glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
#         setup_view(cam, W, H)
#         draw_grid(GS)
#         lava.draw_cracks(); lava.draw_rivers(); lava.draw_stones()
#         draw_obstacles(grid, GS, gt)
#         obs.draw(gt)
#         parts.draw()
        
#         # Agent
#         glPushMatrix()
#         glTranslatef(agent.pos[0]-GS//2, 0.3, agent.pos[2]-GS//2)
#         glColor3f(*agent.col)
#         q = gluNewQuadric(); gluSphere(q, 0.25, 24, 24); gluDeleteQuadric(q)
#         glDisable(GL_LIGHTING); glColor4f(*agent.col, 0.3)
#         q2 = gluNewQuadric(); gluSphere(q2, 0.4, 16, 16); gluDeleteQuadric(q2)
#         glEnable(GL_LIGHTING)
#         glPopMatrix()
        
#         if agent.done:
#             print(f"ðŸŽ‰ WIN! Time: {gt:.2f}s | HP: {hp}"); run = False
        
#         pygame.display.flip()
#         clock.tick(60)
    
#     aud.cleanup(); pygame.quit(); sys.exit()

# if __name__ == "__main__":
#     main()