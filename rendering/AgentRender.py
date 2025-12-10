# rendering/AgentRender.py

import math
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *


class AgentRender:
    """
    Renders different agent shapes with glow effects.
    Optimized for smooth performance.
    """
    
    def __init__(self, cell_size=1.0, grid_size=25):
        self.cell_size = cell_size
        self.grid_size = grid_size
        
        # Track last drone direction for rotation
        self.drone_rotation_angle = 0.0
        
        # Pre-create quadrics (reuse instead of create/delete each frame)
        self._sphere_quad = gluNewQuadric()
        gluQuadricNormals(self._sphere_quad, GLU_SMOOTH)
    
    def __del__(self):
        """Cleanup quadrics"""
        try:
            gluDeleteQuadric(self._sphere_quad)
        except:
            pass
    
    def update_time(self, dt):
        """
        ✅ Kept for backward compatibility with SpaceScene.
        Not needed anymore since we use pygame.time.get_ticks()
        """
        pass
    
    def draw_agent(self, agent, shape_type="sphere_droid"):
        """Main draw method that delegates to specific shape renderers"""
        agent_x = agent.position[0] - self.grid_size//2
        agent_y = agent.position[1]
        agent_z = agent.position[2] - self.grid_size//2
        
        glPushMatrix()
        glTranslatef(agent_x, agent_y, agent_z)
        
        if shape_type == "sphere_droid":
            self._draw_sphere_droid(agent)
        elif shape_type == "robo_cube":
            self._draw_robo_cube(agent)
        elif shape_type == "mini_drone":
            self._draw_mini_drone(agent)
        elif shape_type == "crystal_alien":
            self._draw_crystal_alien(agent)
        else:
            self._draw_sphere_droid(agent)
        
        glPopMatrix()
    
    def _draw_sphere_droid(self, agent):
        """Sphere Droid - Classic glowing sphere"""
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        glColor3f(*agent.color)
        
        gluSphere(self._sphere_quad, 0.25, 16, 16)
        
        # Glow effect
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*agent.color, 0.15)
        
        gluSphere(self._sphere_quad, 0.4, 12, 12)
        
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
    
    def _draw_robo_cube(self, agent):
        """Robo Cube - Static cube with edges"""
        size = 0.4
        
        glEnable(GL_LIGHTING)
        glColor3f(*agent.color)
        self._draw_cube(size)
        
        glDisable(GL_LIGHTING)
        glLineWidth(2.5)
        glColor3f(
            min(1.0, agent.color[0] + 0.3),
            min(1.0, agent.color[1] + 0.3),
            min(1.0, agent.color[2] + 0.3)
        )
        self._draw_cube_edges(size)
        
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*agent.color, 0.08)
        self._draw_cube(size * 1.15)
        glDepthMask(GL_TRUE)
        
        glEnable(GL_LIGHTING)
    
    def _calculate_drone_rotation(self, agent):
        """Calculate drone rotation based on movement direction"""
        if agent.path_i >= len(agent.path):
            return self.drone_rotation_angle
        
        if agent.path_i < len(agent.path):
            target = agent.path[agent.path_i]
            current = (agent.position[0], agent.position[2])
            
            dx = target[0] - current[0]
            dz = target[1] - current[1]
            
            if abs(dx) > 0.01 or abs(dz) > 0.01:
                angle = math.degrees(math.atan2(dz, dx))
                self.drone_rotation_angle = angle
        
        return self.drone_rotation_angle
    
    def _draw_mini_drone(self, agent):
        """Mini Flying Drone - with FAST spinning propellers"""
        
        # ✅ استخدام pygame.time.get_ticks() للدقة العالية
        current_time = pygame.time.get_ticks() / 1000.0
        
        prop_rotation = (current_time * 1500.0) % 360.0

        # print(f"Time: {current_time:.3f}, Rotation: {prop_rotation:.1f}")

        bob = math.sin(current_time * 3.0) * 0.05
        
        rotation_angle = self._calculate_drone_rotation(agent)
        
        glPushMatrix()
        
        glTranslatef(0, bob, 0)
        glRotatef(-rotation_angle, 0, 1, 0)
        
        glEnable(GL_NORMALIZE)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.4, 0.4, 0.4, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [*agent.color, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 5.0)
        
        glColor3f(*agent.color)
        
        # جسم الـ Drone
        glPushMatrix()
        glScalef(0.4, 0.2, 0.2)
        gluSphere(self._sphere_quad, 1.0, 12, 12)
        glPopMatrix()
        
        glDisable(GL_LIGHTING)
        
        arm_positions = [
            (0.35, 0.12, 0.35),
            (-0.35, 0.12, 0.35),
            (0.35, 0.12, -0.35),
            (-0.35, 0.12, -0.35)
        ]
        
        # رسم الأذرع
        glColor3f(agent.color[0] * 0.4, agent.color[1] * 0.4, agent.color[2] * 0.4)
        for px, py, pz in arm_positions:
            glPushMatrix()
            glTranslatef(px/2, py/2, pz/2)
            glScalef(abs(px)*1.8, 0.03, abs(pz)*1.8)
            self._draw_cube(0.1)
            glPopMatrix()
        
        # رسم المراوح
        for i, (px, py, pz) in enumerate(arm_positions):
            glPushMatrix()
            glTranslatef(px, py, pz)
            
            glColor3f(agent.color[0] * 0.25, agent.color[1] * 0.25, agent.color[2] * 0.25)
            glBegin(GL_QUADS)
            glVertex3f(-0.02, -0.08, -0.02)
            glVertex3f(0.02, -0.08, -0.02)
            glVertex3f(0.02, 0, 0.02)
            glVertex3f(-0.02, 0, 0.02)
            glEnd()
            
            glPushMatrix()
            
            if i % 2 == 0:
                glRotatef(prop_rotation, 0, 1, 0)
            else:
                glRotatef(-prop_rotation, 0, 1, 0)
            
            glColor3f(agent.color[0] * 0.8, agent.color[1] * 0.8, agent.color[2] * 0.8)
            
            glBegin(GL_QUADS)
            glVertex3f(-0.25, 0.02, -0.04)
            glVertex3f(0.25, 0.02, -0.04)
            glVertex3f(0.25, 0.02, 0.04)
            glVertex3f(-0.25, 0.02, 0.04)
            
            glVertex3f(-0.04, 0.02, -0.25)
            glVertex3f(0.04, 0.02, -0.25)
            glVertex3f(0.04, 0.02, 0.25)
            glVertex3f(-0.04, 0.02, 0.25)
            glEnd()
            
            glPopMatrix()
            glPopMatrix()
        
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)
        
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)
        
        glPopMatrix()
    
    def _draw_crystal_alien(self, agent):
        """Crystal Alien"""
        current_time = pygame.time.get_ticks() / 1000.0
        rotation = (current_time * 30.0) % 360.0
        pulse = (math.sin(current_time * 2.0) + 1.0) / 2.0 * 0.1 + 0.9
        
        glRotatef(rotation, 0, 1, 0)
        glScalef(pulse, pulse, pulse)
        
        glEnable(GL_NORMALIZE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [
            agent.color[0] * 1.2,
            agent.color[1] * 1.2,
            agent.color[2] * 1.2,
            1.0
        ])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 128.0)
        
        glColor3f(*agent.color)
        self._draw_real_diamond(0.35)
        
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(*agent.color, 0.15)
        self._draw_real_diamond(0.28)
        
        glColor4f(*agent.color, 0.05)
        self._draw_real_diamond(0.45)
        
        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)
    
    def _draw_cube(self, size):
        """Helper: Draw a solid cube"""
        s = size / 2.0
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1); glVertex3f(-s, -s, s); glVertex3f(s, -s, s); glVertex3f(s, s, s); glVertex3f(-s, s, s)
        glNormal3f(0, 0, -1); glVertex3f(-s, -s, -s); glVertex3f(-s, s, -s); glVertex3f(s, s, -s); glVertex3f(s, -s, -s)
        glNormal3f(0, 1, 0); glVertex3f(-s, s, -s); glVertex3f(-s, s, s); glVertex3f(s, s, s); glVertex3f(s, s, -s)
        glNormal3f(0, -1, 0); glVertex3f(-s, -s, -s); glVertex3f(s, -s, -s); glVertex3f(s, -s, s); glVertex3f(-s, -s, s)
        glNormal3f(1, 0, 0); glVertex3f(s, -s, -s); glVertex3f(s, s, -s); glVertex3f(s, s, s); glVertex3f(s, -s, s)
        glNormal3f(-1, 0, 0); glVertex3f(-s, -s, -s); glVertex3f(-s, -s, s); glVertex3f(-s, s, s); glVertex3f(-s, s, -s)
        glEnd()
    
    def _draw_cube_edges(self, size):
        """Helper: Draw cube wireframe edges"""
        s = size / 2.0
        glBegin(GL_LINES)
        glVertex3f(-s, -s, -s); glVertex3f(s, -s, -s)
        glVertex3f(s, -s, -s); glVertex3f(s, -s, s)
        glVertex3f(s, -s, s); glVertex3f(-s, -s, s)
        glVertex3f(-s, -s, s); glVertex3f(-s, -s, -s)
        glVertex3f(-s, s, -s); glVertex3f(s, s, -s)
        glVertex3f(s, s, -s); glVertex3f(s, s, s)
        glVertex3f(s, s, s); glVertex3f(-s, s, s)
        glVertex3f(-s, s, s); glVertex3f(-s, s, -s)
        glVertex3f(-s, -s, -s); glVertex3f(-s, s, -s)
        glVertex3f(s, -s, -s); glVertex3f(s, s, -s)
        glVertex3f(s, -s, s); glVertex3f(s, s, s)
        glVertex3f(-s, -s, s); glVertex3f(-s, s, s)
        glEnd()
    
    def _draw_real_diamond(self, size):
        """Helper: Draw diamond shape"""
        mid_height = size * 0.4
        bottom_height = size * 1.1
        top_radius = size * 0.6
        mid_radius = size
        
        glDisable(GL_LIGHTING)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-top_radius, mid_height, top_radius)
        glVertex3f(-top_radius, mid_height, -top_radius)
        glVertex3f(top_radius, mid_height, -top_radius)
        glVertex3f(top_radius, mid_height, top_radius)
        glEnd()

        glEnable(GL_LIGHTING)
        
        glBegin(GL_QUADS)
        glNormal3f(0, 0.6, 0.8)
        glVertex3f(-top_radius, mid_height, top_radius)
        glVertex3f(top_radius, mid_height, top_radius)
        glVertex3f(mid_radius, 0, mid_radius)
        glVertex3f(-mid_radius, 0, mid_radius)
        
        glNormal3f(0.8, 0.6, 0)
        glVertex3f(top_radius, mid_height, top_radius)
        glVertex3f(top_radius, mid_height, -top_radius)
        glVertex3f(mid_radius, 0, -mid_radius)
        glVertex3f(mid_radius, 0, mid_radius)
        
        glNormal3f(0, 0.6, -0.8)
        glVertex3f(top_radius, mid_height, -top_radius)
        glVertex3f(-top_radius, mid_height, -top_radius)
        glVertex3f(-mid_radius, 0, -mid_radius)
        glVertex3f(mid_radius, 0, -mid_radius)
        
        glNormal3f(-0.8, 0.6, 0)
        glVertex3f(-top_radius, mid_height, -top_radius)
        glVertex3f(-top_radius, mid_height, top_radius)
        glVertex3f(-mid_radius, 0, mid_radius)
        glVertex3f(-mid_radius, 0, -mid_radius)
        glEnd()
        
        glBegin(GL_TRIANGLES)
        bottom_y = -bottom_height
        
        glNormal3f(0, -0.4, 0.92)
        glVertex3f(0, bottom_y, 0)
        glVertex3f(mid_radius, 0, mid_radius)
        glVertex3f(-mid_radius, 0, mid_radius)
        
        glNormal3f(0.92, -0.4, 0)
        glVertex3f(0, bottom_y, 0)
        glVertex3f(mid_radius, 0, -mid_radius)
        glVertex3f(mid_radius, 0, mid_radius)
        
        glNormal3f(0, -0.4, -0.92)
        glVertex3f(0, bottom_y, 0)
        glVertex3f(-mid_radius, 0, -mid_radius)
        glVertex3f(mid_radius, 0, -mid_radius)
        
        glNormal3f(-0.92, -0.4, 0)
        glVertex3f(0, bottom_y, 0)
        glVertex3f(-mid_radius, 0, mid_radius)
        glVertex3f(-mid_radius, 0, -mid_radius)
        glEnd()