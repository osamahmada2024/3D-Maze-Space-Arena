"""
Camera Controller for 3D OpenGL rendering.
Handles perspective camera, position, rotation, and view matrix management.
"""

import math
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class Camera:
    """
    3D perspective camera for OpenGL rendering.
    Supports rotation around target, zoom, and pan.
    """
    def __init__(self, position=(0, 5, 15), target=(0, 0, 0), up=(0, 1, 0)):
        """
        Initialize camera.
        
        Args:
            position (tuple): Camera position (x, y, z)
            target (tuple): Look-at target (x, y, z)
            up (tuple): Up vector (0, 1, 0) for Y-up coordinate system
        """
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        
        # Camera parameters
        self.fov = 45.0
        self.near = 0.1
        self.far = 1000.0
        self.aspect_ratio = 16.0 / 9.0
        
        # Rotation parameters
        self.yaw = 0.0
        self.pitch = 0.0
        self.distance = np.linalg.norm(self.position - self.target)
        
        self.projection_matrix = None
        self.view_matrix = None
    
    def set_perspective(self, width, height):
        """
        Set perspective projection for the given window size.
        
        Args:
            width (int): Window width in pixels
            height (int): Window height in pixels
        """
        self.aspect_ratio = width / height if height > 0 else 1.0
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.aspect_ratio, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)
    
    def update_view(self):
        """Update and apply the view matrix (lookAt)"""
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Calculate new position based on yaw, pitch, and distance
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)
        
        offset_x = self.distance * math.cos(rad_pitch) * math.sin(rad_yaw)
        offset_y = self.distance * math.sin(rad_pitch)
        offset_z = self.distance * math.cos(rad_pitch) * math.cos(rad_yaw)
        
        self.position = self.target + np.array([offset_x, offset_y, offset_z])
        
        # Apply lookAt transformation
        gluLookAt(
            self.position[0], self.position[1], self.position[2],  # Camera position
            self.target[0], self.target[1], self.target[2],        # Look-at target
            self.up[0], self.up[1], self.up[2]                     # Up vector
        )
    
    def rotate(self, delta_yaw, delta_pitch):
        """
        Rotate camera around target.
        
        Args:
            delta_yaw (float): Rotation around Y axis in degrees
            delta_pitch (float): Rotation around X axis in degrees
        """
        self.yaw += delta_yaw
        self.pitch += delta_pitch
        
        # Clamp pitch to avoid flipping
        self.pitch = max(-89.0, min(89.0, self.pitch))
        
        # Normalize yaw to 0-360
        self.yaw = self.yaw % 360.0
    
    def zoom(self, delta):
        """
        Zoom in/out by changing distance from target.
        
        Args:
            delta (float): Distance change (negative for zoom in)
        """
        self.distance += delta
        self.distance = max(1.0, min(100.0, self.distance))
    
    def pan(self, delta_x, delta_y, delta_z=0):
        """
        Pan camera (move target).
        
        Args:
            delta_x (float): Move along X axis
            delta_y (float): Move along Y axis
            delta_z (float): Move along Z axis
        """
        pan_vector = np.array([delta_x, delta_y, delta_z])
        self.target += pan_vector
        self.position += pan_vector
    
    def reset(self):
        """Reset camera to default position"""
        self.position = np.array([0, 5, 15], dtype=np.float32)
        self.target = np.array([0, 0, 0], dtype=np.float32)
        self.yaw = 0.0
        self.pitch = 0.0
        self.distance = np.linalg.norm(self.position - self.target)


class CameraController:
    """
    Input handler for camera control via keyboard and mouse.
    """
    def __init__(self, camera):
        """
        Initialize controller.
        
        Args:
            camera (Camera): Camera instance to control
        """
        self.camera = camera
        self.mouse_sensitivity = 0.5
        self.movement_speed = 0.1
        self.zoom_speed = 0.5
    
    def handle_keyboard(self, keys):
        """
        Handle keyboard input for camera control.
        
        Args:
            keys (dict): Pressed keys from pygame
        """
        import pygame
        pressed = pygame.key.get_pressed()
        
        # Rotation controls (arrow keys)
        if pressed[pygame.K_LEFT]:
            self.camera.rotate(-2, 0)
        if pressed[pygame.K_RIGHT]:
            self.camera.rotate(2, 0)
        if pressed[pygame.K_UP]:
            self.camera.rotate(0, 2)
        if pressed[pygame.K_DOWN]:
            self.camera.rotate(0, -2)
        
        # Pan controls (WASD)
        if pressed[pygame.K_w]:
            self.camera.pan(0, 0.5, 0)
        if pressed[pygame.K_s]:
            self.camera.pan(0, -0.5, 0)
        if pressed[pygame.K_a]:
            self.camera.pan(-0.5, 0, 0)
        if pressed[pygame.K_d]:
            self.camera.pan(0.5, 0, 0)
        
        # Reset
        if pressed[pygame.K_r]:
            self.camera.reset()
    
    def handle_mouse_wheel(self, event_y):
        """
        Handle mouse wheel for zoom.
        
        Args:
            event_y (int): Mouse wheel event Y value
        """
        if event_y > 0:
            self.camera.zoom(-self.zoom_speed)
        elif event_y < 0:
            self.camera.zoom(self.zoom_speed)
