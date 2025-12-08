import random
from typing import List, Tuple

class Particle:
    def _init_(self, position: Tuple[float, float, float], velocity: Tuple[float, float, float], color: Tuple[float, float, float, float], lifetime: float):
        self.position = list(position)
        self.velocity = list(velocity)
        self.color = list(color)
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt: float):
        self.age += dt
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt
        # Fade out
        self.color[3] = max(0.0, self.color[3] * (1 - dt / self.lifetime))

    def is_alive(self):
        return self.age < self.lifetime

class ParticleSystem:
    def _init_(self):
        self.particles: List[Particle] = []

    def emit(self, position: Tuple[float, float, float], count: int, color: Tuple[float, float, float, float], speed: float, lifetime: float):
        for _ in range(count):
            vx = (random.random() - 0.5) * speed
            vy = random.random() * speed
            vz = (random.random() - 0.5) * speed
            self.particles.append(Particle(position, (vx, vy, vz), color, lifetime))

    def update(self, dt: float):
        for particle in self.particles:
            particle.update(dt)
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]