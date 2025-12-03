import time
import math
from OpenGL.GL import *
from OpenGL.GLU import *


class GoalRender:
    """
    Class: GoalRender
    Purpose:
        Responsible for rendering and animating the goal indicator in the 3D scene.
    
    Features:
        • Animated bouncing sphere.
        • Glow effect using layered transparent spheres.
        • Dynamic expanding rings around the goal.
        • Soft shadow projected on the ground.
        • Optional real-time lighting effects.

    Parameters:
        cellSize (float): Scaling factor for converting grid units to world units.
    """

    def __init__(self, cellSize: float = 1.0):
        # World scaling
        self.cellSize = cellSize

        # Sphere properties
        self.goalRadius = 0.3
        self.goalHeight = 0.42
        self.goalColor = (1.0, 1.0, 0.0)

        # Bounce animation
        self.bounceEnabled = True
        self.bounceSpeed = 4.0
        self.bounceAmplitude = 0.07
        self.startTime = time.time()

        # Shadow + rings toggles
        self.shadowEnabled = True
        self.ringsEnabled = True

        # Lighting settings
        self.lightingEnabled = True

        if self.lightingEnabled:
            self._initialize_lighting()

    # ------------------------------------------------------
    # Lighting Setup
    # ------------------------------------------------------
    def _initialize_lighting(self):
        """Configure OpenGL lighting for the goal sphere."""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glLightfv(GL_LIGHT0, GL_POSITION,  [10.0, 20.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT,   [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,   [1.0, 1.0, 0.9, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR,  [1.0, 1.0, 1.0, 1.0])

    # ------------------------------------------------------
    # Public Rendering Function
    # ------------------------------------------------------
    def draw_goal(self, agent):
        """
        Render the complete animated goal at the agent's current goal coordinates.
        """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        gx, gy = agent.goal
        self._render_single_goal(gx, gy)

        glDisable(GL_BLEND)

    # ------------------------------------------------------
    # Internal Rendering
    # ------------------------------------------------------
    def _render_single_goal(self, gx: int, gy: int):
        """Render all components of the goal (sphere, shadow, rings)."""
        screen_x = gx * self.cellSize + self.cellSize / 2.0
        screen_z = gy * self.cellSize + self.cellSize / 2.0

        current_time = time.time() - self.startTime

        # Bounce animation
        if self.bounceEnabled:
            bounce_offset = math.sin(current_time * self.bounceSpeed) * self.bounceAmplitude
            screen_y = self.goalHeight + bounce_offset
        else:
            screen_y = self.goalHeight

        # Visual effects
        self._draw_goal_rings(screen_x, screen_z, current_time)
        self._draw_goal_shadow(screen_x, screen_z, screen_y)

        # Main sphere
        glPushMatrix()
        glTranslatef(screen_x, screen_y, screen_z)

        rotation = (current_time * 20.0) % 360
        glRotatef(rotation, 0, 1, 0)

        self._draw_goal_sphere()
        glPopMatrix()

    # ------------------------------------------------------
    # Sphere Rendering
    # ------------------------------------------------------
    def _draw_goal_sphere(self):
        """Render glowing goal sphere with lighting + layered glow."""
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)

        if self.lightingEnabled:
            glEnable(GL_LIGHTING)
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,   [0.4, 0.4, 0.0, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,   [1.0, 1.0, 0.0, 1.0])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  [1.0, 1.0, 0.6, 1.0])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS,  80.0)

        # Main sphere
        glColor3f(*self.goalColor)
        gluSphere(quadric, self.goalRadius, 32, 32)

        # Glow layers (lighting off)
        glDisable(GL_LIGHTING)
        glDepthMask(False)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        glColor4f(1.0, 1.0, 0.0, 0.10)
        gluSphere(quadric, self.goalRadius * 1.15, 24, 24)

        glColor4f(1.0, 1.0, 0.0, 0.05)
        gluSphere(quadric, self.goalRadius * 1.25, 20, 20)

        glDisable(GL_BLEND)
        glDepthMask(True)

        gluDeleteQuadric(quadric)

    # ------------------------------------------------------
    # Shadow Rendering
    # ------------------------------------------------------
    def _draw_goal_shadow(self, x, z, sphere_y):
        """Draw soft projected shadow under the goal sphere."""
        if not self.shadowEnabled:
            return

        height_diff = sphere_y - self.goalHeight
        scale = max(0.7, min(1.3, 1.0 - height_diff * 2.0))

        shadow_radius = self.goalRadius * 1.5 * scale
        shadow_alpha = 0.35 * scale

        glPushMatrix()
        glTranslatef(x, 0.02, z)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)

        glColor4f(0.0, 0.0, 0.0, shadow_alpha)

        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        for i in range(37):
            angle = i * (2 * math.pi / 36)
            glVertex3f(shadow_radius * math.cos(angle), 0, shadow_radius * math.sin(angle))
        glEnd()

        glDisable(GL_BLEND)
        glPopMatrix()

    # ------------------------------------------------------
    # Expanding Rings Rendering
    # ------------------------------------------------------
    def _draw_goal_rings(self, x, z, current_time):
        """Draw expanding fade-out rings around the goal."""
        if not self.ringsEnabled:
            return

        glPushMatrix()
        glTranslatef(x, 0.03, z)

        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.5)

        ring_duration = 3.0

        for i in range(3):
            offset = i * 1.0
            t = (current_time - offset) % ring_duration
            progress = t / ring_duration

            radius = 0.1 + progress * 0.6
            alpha = 0.5 * (1.0 - progress)

            glColor4f(1.0, 1.0, 0.0, alpha)

            glBegin(GL_LINE_LOOP)
            for j in range(36):
                angle = j * (2 * math.pi / 36)
                glVertex3f(radius * math.cos(angle), 0, radius * math.sin(angle))
            glEnd()

        glDisable(GL_BLEND)
        glPopMatrix()
