# Lava/fire_particle_system.py
"""
Fire/Ember Particle System - ENHANCED VERSION
Realistic fire particles, embers, and ash
"""

import random
import math
from typing import List, Tuple
from OpenGL.GL import *
from OpenGL.GLU import *


class Ember:
    """Ember/fire spark"""
    
    def __init__(self, x: float, y: float, z: float, ember_type: str = "spark"):
        self.x = x
        self.y = y
        self.z = z
        self.ember_type = ember_type
        
        if ember_type == "spark":
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(1.0, 2.5)
            self.vz = random.uniform(-0.5, 0.5)
            self.size = random.uniform(0.02, 0.06)
            self.lifetime = random.uniform(1.0, 2.5)
            self.color = (1.0, random.uniform(0.4, 0.8), 0.0)
        
        elif ember_type == "ash":
            self.vx = random.uniform(-0.2, 0.2)
            self.vy = random.uniform(0.1, 0.4)
            self.vz = random.uniform(-0.2, 0.2)
            self.size = random.uniform(0.01, 0.03)
            self.lifetime = random.uniform(3.0, 6.0)
            self.color = (0.3, 0.3, 0.3)
        
        else:  # flame
            self.vx = random.uniform(-0.1, 0.1)
            self.vy = random.uniform(0.8, 1.5)
            self.vz = random.uniform(-0.1, 0.1)
            self.size = random.uniform(0.05, 0.12)
            self.lifetime = random.uniform(0.5, 1.5)
            self.color = (1.0, random.uniform(0.2, 0.5), 0.0)
        
        self.age = 0.0
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)
    
    def update(self, dt: float):
        self.age += dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        
        self.vx += random.uniform(-0.1, 0.1) * dt
        self.vz += random.uniform(-0.1, 0.1) * dt
        
        self.vy *= 0.98
        self.vx *= 0.99
        self.vz *= 0.99
        
        if self.ember_type != "ash":
            self.size *= 0.995
        
        self.rotation += self.rot_speed * dt
    
    def is_alive(self) -> bool:
        return self.age < self.lifetime and self.size > 0.005
    
    def get_alpha(self) -> float:
        life_ratio = self.age / self.lifetime
        if life_ratio < 0.1:
            return life_ratio * 10
        elif life_ratio > 0.7:
            return (1.0 - life_ratio) / 0.3
        return 1.0


class FireParticleSystem:
    """Enhanced fire particle system"""
    
    def __init__(self, grid_size: int = 25, cell_size: float = 1.0):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.particles: List[Ember] = []
        self.spawn_points: List[Tuple[float, float, float]] = []
        
        self.max_particles = 300
        self.spawn_timer = 0.0
        
        self._quadric = gluNewQuadric()
    
    def __del__(self):
        try:
            if self._quadric:
                gluDeleteQuadric(self._quadric)
        except:
            pass
    
    def set_spawn_points(self, lava_positions: List[Tuple[float, float, float]]):
        self.spawn_points = lava_positions
    
    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update(dt)
        
        self.spawn_timer += dt
        
        if self.spawn_points and len(self.particles) < self.max_particles:
            if self.spawn_timer >= 0.05:
                self.spawn_timer = 0.0
                
                point = random.choice(self.spawn_points)
                
                for _ in range(2):
                    x = point[0] + random.uniform(-0.3, 0.3)
                    z = point[2] if len(point) > 2 else point[1]
                    z += random.uniform(-0.3, 0.3)
                    self.particles.append(Ember(x, 0.05, z, "spark"))
                
                if random.random() < 0.3:
                    x = point[0] + random.uniform(-0.2, 0.2)
                    z = point[2] if len(point) > 2 else point[1]
                    z += random.uniform(-0.2, 0.2)
                    self.particles.append(Ember(x, 0.02, z, "flame"))
                
                if random.random() < 0.1:
                    x = point[0] + random.uniform(-0.5, 0.5)
                    z = point[2] if len(point) > 2 else point[1]
                    z += random.uniform(-0.5, 0.5)
                    self.particles.append(Ember(x, 0.1, z, "ash"))
    
    def render(self):
        if not self.particles:
            return
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)
        
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        for particle in self.particles:
            if particle.ember_type == "ash":
                continue
            
            alpha = particle.get_alpha()
            r, g, b = particle.color
            
            glPushMatrix()
            glTranslatef(particle.x, particle.y, particle.z)
            glRotatef(particle.rotation, 0, 1, 0)
            
            glColor4f(r, g, b, alpha * 0.9)
            glPointSize(particle.size * 100)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            
            glColor4f(r, g * 0.5, 0, alpha * 0.3)
            glPointSize(particle.size * 200)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            
            glPopMatrix()
        
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for particle in self.particles:
            if particle.ember_type != "ash":
                continue
            
            alpha = particle.get_alpha()
            r, g, b = particle.color
            
            glColor4f(r, g, b, alpha * 0.6)
            glPointSize(particle.size * 80)
            
            glBegin(GL_POINTS)
            glVertex3f(particle.x, particle.y, particle.z)
            glEnd()
        
        glPointSize(1.0)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)