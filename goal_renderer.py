from OpenGL.GL import *
from OpenGL.GLU import *
import time
import math

class GoalRenderer:
    def __init__(self, cellSize = 1.0):
        self.cellSize = cellSize
        self.goalRadius = 0.3
        self.goalHeight = 0.42
        self.goalColor = (1.0, 1.0, 0.0)

        # bounce effect
        self.bounceEnabled = True
        self.bounceSpeed = 4.0
        self.bounceAmplitude = 0.07
        self.startTime = time.time()

        # Shadow settings
        self.shadowEnabled = True

        # Rings settings
        self.ringsEnabled = True

        # Lighting settings
        self.lightingEnabled = True

        if self.lightingEnabled:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
            
            glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 20.0, 10.0, 1.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.9, 1.0])
            glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    def draw_goal(self, agent):

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        gx, gy = agent.goal
        self.render_single_goal(gx, gy)

        glDisable(GL_BLEND)

    def render_single_goal(self, gx, gy):
        screen_x = gx * self.cellSize + self.cellSize / 2.0
        screen_z = gy * self.cellSize + self.cellSize / 2.0

        current_time = time.time() - self.startTime

        if self.bounceEnabled:
            bounce_offset = math.sin(current_time * self.bounceSpeed) * self.bounceAmplitude
            screen_y = self.goalHeight + bounce_offset
        else:
            screen_y = self.goalHeight

        self.draw_goal_rings(screen_x, screen_z, current_time)

        self.draw_goal_shadow(screen_x, screen_z, screen_y)

        glPushMatrix()
        
        glTranslatef(screen_x, screen_y, screen_z)

        rotation = (current_time * 20.0) % 360.0
        glRotatef(rotation, 0, 1, 0)
        
        self.draw_goal_sphere()
        
        glPopMatrix()

    def draw_goal_sphere(self):
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)

        if self.lightingEnabled:
            glEnable(GL_LIGHTING)
            
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.4, 0.4, 0.0, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1.0, 1.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 0.6, 1.0])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 80.0)

        glColor3f(1.0, 0.95, 0)
        gluSphere(quadric, self.goalRadius, 32, 32)

        glDisable(GL_LIGHTING)

        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        glColor4f(1.0, 1.0, 0.0, 0.1)
        gluSphere(quadric, self.goalRadius * 1.15, 24, 24)
        
        glColor4f(1.0, 1.0, 0.0, 0.05)
        gluSphere(quadric, self.goalRadius * 1.25, 20, 20)

        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE)

        gluDeleteQuadric(quadric)

    def draw_goal_shadow(self, screen_x, screen_z, screen_y):
        if not self.shadowEnabled:
            return
        
        height_diff = screen_y - self.goalHeight
        scale = 1.0 - (height_diff * 2.0)
        scale = max(0.7, min(1.3, scale))
        
        shadow_radius = self.goalRadius * 1.5 * scale
        shadow_alpha = 0.35 * scale
        
        glPushMatrix()
        glTranslatef(screen_x, 0.02, screen_z)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)
        
        glColor4f(0.0, 0.0, 0.0, shadow_alpha)
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        for i in range(37):
            angle = i * 2.0 * math.pi / 36.0
            x = shadow_radius * math.cos(angle)
            z = shadow_radius * math.sin(angle)
            glVertex3f(x, 0, z)
        glEnd()
        
        glDisable(GL_BLEND)
        glPopMatrix()

    def draw_goal_rings(self, screen_x, screen_z, current_time):
        if not self.ringsEnabled:
            return
        
        glPushMatrix()
        glTranslatef(screen_x, 0.03, screen_z)
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.5)
        
        ring_duration = 3.0

        for i in range(3):
            time_offset = i * 1.0
            ring_time = (current_time - time_offset) % ring_duration
            
            progress = ring_time / ring_duration
            
            radius = 0.1 + (progress * 0.6)
            
            alpha = 0.5 * (1.0 - progress)
            
            glColor4f(1.0, 1.0, 0.0, alpha)
            
            glBegin(GL_LINE_LOOP)
            for j in range(36):
                angle = j * 2.0 * math.pi / 36.0
                x = radius * math.cos(angle)
                z = radius * math.sin(angle)
                glVertex3f(x, 0, z)
            glEnd()
        
        glDisable(GL_BLEND)
        glPopMatrix()