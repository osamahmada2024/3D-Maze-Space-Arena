import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *

class AgentRender:
    """
    Renders different agent shapes with glow effects.
    Supports: sphere_droid, robo_cube, mini_drone, crystal_alien
    """
    
    def __init__(self, cell_size=1.0, grid_size=25):
        self.cell_size = cell_size
        self.grid_size = grid_size
        self.start_time = time.time()
        
        # Track last drone direction for rotation
        self.last_drone_direction = None
        self.drone_rotation_angle = 0.0
    
    def draw_agent(self, agent, shape_type="sphere_droid"):
        """Main draw method that delegates to specific shape renderers"""
        agent_x = agent.position[0] - self.grid_size//2
        agent_y = agent.position[1]
        agent_z = agent.position[2] - self.grid_size//2
        
        glPushMatrix()
        glTranslatef(agent_x, agent_y, agent_z)
        
        # Draw based on shape type
        if shape_type == "sphere_droid":
            self._draw_sphere_droid(agent)
        elif shape_type == "robo_cube":
            self._draw_robo_cube(agent)
        elif shape_type == "mini_drone":
            self._draw_mini_drone(agent)
        elif shape_type == "crystal_alien":
            self._draw_crystal_alien(agent)
        else:
            self._draw_sphere_droid(agent)  # Default
        
        glPopMatrix()
    
    def _draw_sphere_droid(self, agent):
        """Sphere Droid - Classic glowing sphere"""
        # Main solid sphere
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        glColor3f(*agent.color)
        
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, 0.25, 24, 24)
        gluDeleteQuadric(quad)
        
        # Glow effect
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*agent.color, 0.15)
        
        quad_glow = gluNewQuadric()
        gluSphere(quad_glow, 0.4, 16, 16)
        gluDeleteQuadric(quad_glow)
        
        # Restore states
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
    
    def _draw_robo_cube(self, agent):
        """Robo Cube - Static cube with edges (NO rotation)"""
        size = 0.4
        
        # Main cube body
        glEnable(GL_LIGHTING)
        glColor3f(*agent.color)
        self._draw_cube(size)
        
        # Edge highlights
        glDisable(GL_LIGHTING)
        glLineWidth(2.5)
        glColor3f(
            min(1.0, agent.color[0] + 0.3),
            min(1.0, agent.color[1] + 0.3),
            min(1.0, agent.color[2] + 0.3)
        )
        self._draw_cube_edges(size)
        
        # Subtle glow
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
        
        # Get current target
        if agent.path_i < len(agent.path):
            target = agent.path[agent.path_i]
            current = (agent.position[0], agent.position[2])
            
            dx = target[0] - current[0]
            dz = target[1] - current[1]
            
            # Calculate angle only if there's significant movement
            if abs(dx) > 0.01 or abs(dz) > 0.01:
                # Calculate angle in degrees (0° = facing +X direction)
                angle = math.degrees(math.atan2(dz, dx))
                self.drone_rotation_angle = angle
        
        return self.drone_rotation_angle
    
    def _draw_mini_drone(self, agent):
        """Mini Flying Drone - Body with propellers, matte finish (no shine)"""
        current_time = time.time() - self.start_time
        prop_rotation = (current_time * 500.0) % 360.0
        bob = math.sin(current_time * 3.0) * 0.05
        
        # Calculate rotation based on movement direction
        rotation_angle = self._calculate_drone_rotation(agent)
        
        glTranslatef(0, bob, 0)
        
        # Rotate drone to face movement direction
        glRotatef(rotation_angle, 0, 1, 0)
        
        # Main body (ellipsoid) - MATTE finish (no specular shine)
        glEnable(GL_NORMALIZE)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        
        # Set material properties for MATTE appearance
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.4, 0.4, 0.4, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [*agent.color, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])  # Very low specular
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 5.0)  # Very low shininess (1-128)
        
        glColor3f(*agent.color)
        
        glPushMatrix()
        glScalef(0.4, 0.2, 0.2)  # Ellipsoid shape
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, 1.0, 20, 20)
        gluDeleteQuadric(quad)
        glPopMatrix()
        
        # Propeller arms (connecting body to propellers) - NO lighting
        glDisable(GL_LIGHTING)
        glColor3f(
            agent.color[0] * 0.4,
            agent.color[1] * 0.4,
            agent.color[2] * 0.4
        )
        
        arm_positions = [
            (0.35, 0.12, 0.35),   # Front right
            (-0.35, 0.12, 0.35),  # Front left
            (0.35, 0.12, -0.35),  # Back right
            (-0.35, 0.12, -0.35)  # Back left
        ]
        
        # Draw arms (thin cylinders)
        for px, py, pz in arm_positions:
            glPushMatrix()
            glTranslatef(px/2, py/2, pz/2)
            glScalef(abs(px)*1.8, 0.03, abs(pz)*1.8)
            self._draw_cube(0.1)
            glPopMatrix()
        
        # Propellers (4 corners) - SOLID, darker color for contrast
        for px, py, pz in arm_positions:
            glPushMatrix()
            glTranslatef(px, py, pz)
            
            # Propeller support (small cylinder) - DARK
            glColor3f(
                agent.color[0] * 0.25,
                agent.color[1] * 0.25,
                agent.color[2] * 0.25
            )
            glBegin(GL_QUADS)
            glVertex3f(-0.02, -0.08, -0.02)
            glVertex3f(0.02, -0.08, -0.02)
            glVertex3f(0.02, 0, 0.02)
            glVertex3f(-0.02, 0, 0.02)
            glEnd()
            
            # Rotating propeller blades - Slightly darker than body
            glRotatef(prop_rotation, 0, 1, 0)
            glColor3f(
                agent.color[0] * 0.8,
                agent.color[1] * 0.8,
                agent.color[2] * 0.8
            )
            
            # Make blades thicker and more visible
            glBegin(GL_QUADS)
            # Main blade (horizontal)
            glVertex3f(-0.28, 0.01, -0.05)
            glVertex3f(0.28, 0.01, -0.05)
            glVertex3f(0.2, 0.01, 0.04)
            glVertex3f(-0.2, 0.01, 0.04)
            
            # Cross blade (perpendicular)
            glVertex3f(-0.04, 0.01, -0.2)
            glVertex3f(0.04, 0.01, -0.2)
            glVertex3f(0.04, 0.01, 0.2)
            glVertex3f(-0.04, 0.01, 0.2)
            glEnd()
            
            glPopMatrix()
        
        # Restore default material properties
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)
        
        glEnable(GL_BLEND)
        glEnable(GL_LIGHTING)
    
    def _draw_crystal_alien(self, agent):
        """Crystal Alien - REAL Diamond shape with proper lighting"""
        current_time = time.time() - self.start_time
        rotation = (current_time * 30.0) % 360.0
        pulse = (math.sin(current_time * 2.0) + 1.0) / 2.0 * 0.1 + 0.9
        
        glRotatef(rotation, 0, 1, 0)
        glScalef(pulse, pulse, pulse)
        
        # Setup material properties for clear facet definition
        glEnable(GL_NORMALIZE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Balanced ambient - not too high, not too low
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        
        # Diffuse - main color (slightly brighter)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [
            agent.color[0] * 1.2,
            agent.color[1] * 1.2,
            agent.color[2] * 1.2,
            1.0
        ])
        
        # Specular - shiny highlights

        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 128.0)
        
        glColor3f(*agent.color)
        self._draw_real_diamond(0.35)
        
        # Very subtle inner glow
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(*agent.color, 0.15)
        self._draw_real_diamond(0.28)
        
        # Outer glow
        glColor4f(*agent.color, 0.05)
        self._draw_real_diamond(0.45)
        
        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)
    
    def _draw_cube(self, size):
        """Helper: Draw a solid cube"""
        s = size / 2.0
        glBegin(GL_QUADS)
        
        # Front
        glNormal3f(0, 0, 1)
        glVertex3f(-s, -s, s)
        glVertex3f(s, -s, s)
        glVertex3f(s, s, s)
        glVertex3f(-s, s, s)
        
        # Back
        glNormal3f(0, 0, -1)
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, -s, -s)
        
        # Top
        glNormal3f(0, 1, 0)
        glVertex3f(-s, s, -s)
        glVertex3f(-s, s, s)
        glVertex3f(s, s, s)
        glVertex3f(s, s, -s)
        
        # Bottom
        glNormal3f(0, -1, 0)
        glVertex3f(-s, -s, -s)
        glVertex3f(s, -s, -s)
        glVertex3f(s, -s, s)
        glVertex3f(-s, -s, s)
        
        # Right
        glNormal3f(1, 0, 0)
        glVertex3f(s, -s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, s, s)
        glVertex3f(s, -s, s)
        
        # Left
        glNormal3f(-1, 0, 0)
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, -s, s)
        glVertex3f(-s, s, s)
        glVertex3f(-s, s, -s)
        
        glEnd()
    
    def _draw_cube_edges(self, size):
        """Helper: Draw cube wireframe edges"""
        s = size / 2.0
        glBegin(GL_LINES)
        # Bottom square
        glVertex3f(-s, -s, -s); glVertex3f(s, -s, -s)
        glVertex3f(s, -s, -s); glVertex3f(s, -s, s)
        glVertex3f(s, -s, s); glVertex3f(-s, -s, s)
        glVertex3f(-s, -s, s); glVertex3f(-s, -s, -s)
        
        # Top square
        glVertex3f(-s, s, -s); glVertex3f(s, s, -s)
        glVertex3f(s, s, -s); glVertex3f(s, s, s)
        glVertex3f(s, s, s); glVertex3f(-s, s, s)
        glVertex3f(-s, s, s); glVertex3f(-s, s, -s)
        
        # Vertical edges
        glVertex3f(-s, -s, -s); glVertex3f(-s, s, -s)
        glVertex3f(s, -s, -s); glVertex3f(s, s, -s)
        glVertex3f(s, -s, s); glVertex3f(s, s, s)
        glVertex3f(-s, -s, s); glVertex3f(-s, s, s)
        glEnd()
    
    def _draw_real_diamond(self, size):
        """
        Helper: Draw a REAL diamond shape with PROPER normals for lighting
        Structure: Middle trapezoid + Bottom pyramid
        """
        mid_height = size * 0.4      # Middle trapezoid height
        bottom_height = size * 1.1   # Bottom pyramid height
        
        top_radius = size * 0.6      # Top point area
        mid_radius = size            # Widest part (trapezoid)
        
        # Calculate proper normals for each face
        import math

        # === TOP CAP (flat square on top to close the diamond) ===
        glDisable(GL_LIGHTING)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)  # Normal pointing up
        glVertex3f(-top_radius, mid_height, top_radius)
        glVertex3f(-top_radius, mid_height, -top_radius)
        glVertex3f(top_radius, mid_height, -top_radius)
        glVertex3f(top_radius, mid_height, top_radius)
        glEnd()

        glEnable(GL_LIGHTING)
        
        # === MIDDLE TRAPEZOID (4 faces) ===
        glBegin(GL_QUADS)
        
        # Front face - calculate outward normal
        # For a slanted face, the normal points perpendicular to the surface
        glNormal3f(0, 0.6, 0.8)
        glVertex3f(-top_radius, mid_height, top_radius)
        glVertex3f(top_radius, mid_height, top_radius)
        glVertex3f(mid_radius, 0, mid_radius)
        glVertex3f(-mid_radius, 0, mid_radius)
        
        # Right face
        glNormal3f(0.8, 0.6, 0)
        glVertex3f(top_radius, mid_height, top_radius)
        glVertex3f(top_radius, mid_height, -top_radius)
        glVertex3f(mid_radius, 0, -mid_radius)
        glVertex3f(mid_radius, 0, mid_radius)
        
        # Back face
        glNormal3f(0, 0.6, -0.8)
        glVertex3f(top_radius, mid_height, -top_radius)
        glVertex3f(-top_radius, mid_height, -top_radius)
        glVertex3f(-mid_radius, 0, -mid_radius)
        glVertex3f(mid_radius, 0, -mid_radius)
        
        # Left face
        glNormal3f(-0.8, 0.6, 0)
        glVertex3f(-top_radius, mid_height, -top_radius)
        glVertex3f(-top_radius, mid_height, top_radius)
        glVertex3f(-mid_radius, 0, mid_radius)
        glVertex3f(-mid_radius, 0, -mid_radius)
        
        glEnd()
        
        # === BOTTOM PYRAMID (4 faces) ===
        glBegin(GL_TRIANGLES)
        
        # Bottom vertex
        bottom_y = -bottom_height
        
        # For pyramid faces, calculate the normal for each triangular face
        # Front face
        glNormal3f(0, -0.4, 0.92)
        glVertex3f(0, bottom_y, 0)
        glVertex3f(mid_radius, 0, mid_radius)
        glVertex3f(-mid_radius, 0, mid_radius)
        
        # Right face
        glNormal3f(0.92, -0.4, 0)
        glVertex3f(0, bottom_y, 0)
        glVertex3f(mid_radius, 0, -mid_radius)
        glVertex3f(mid_radius, 0, mid_radius)
        
        # Back face
        glNormal3f(0, -0.4, -0.92)
        glVertex3f(0, bottom_y, 0)
        glVertex3f(-mid_radius, 0, -mid_radius)
        glVertex3f(mid_radius, 0, -mid_radius)
        
        # Left face
        glNormal3f(-0.92, -0.4, 0)
        glVertex3f(0, bottom_y, 0)
        glVertex3f(-mid_radius, 0, mid_radius)
        glVertex3f(-mid_radius, 0, -mid_radius)
        
        glEnd()
from OpenGL.GL import *
from Agent import Agent
from OpenGL.GLU import *
from OpenGL.GLUT import *

class AgentRender:
    def __init__(self, cell_size=60):
        self.cell_size = cell_size
    
    def draw(self, agent: Agent):
        screen_x = (agent.x * self.cell_size) + (self.cell_size / 2)
        screen_y = (agent.y * self.cell_size) + (self.cell_size / 2)
        
        glPushMatrix()
        glTranslatef(screen_x, screen_y, 0)
        glColor3f(*agent.color)
        glutSolidSphere(self.cell_size / 3, 20, 20)
        glPopMatrix()
    
    def draw_grid(self, width, height):
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_LINES)
        for i in range(0, width + 1, self.cell_size):
            glVertex2f(i, 0)
            glVertex2f(i, height)
        for j in range(0, height + 1, self.cell_size):
            glVertex2f(0, j)
            glVertex2f(width, j)
        glEnd()
