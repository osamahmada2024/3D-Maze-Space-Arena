import time
import math


class CameraController:
    """
    Role: Manage 3D camera movement with overhead view and smooth animations.
    """
    
    def __init__(self, angle_x: float = 0.0, angle_y: float = 80.0, 
                 angle_z: float = 0.0, distance: float = 25.0):
        """
        Initialize camera controller with overhead view.
        
        Args:
            angle_x: Horizontal angle in degrees
            angle_y: Vertical angle in degrees
            angle_z: Roll angle in degrees
            distance: Camera distance
        """
        self.initial_angle_x = angle_x
        self.initial_angle_y = angle_y
        self.initial_angle_z = angle_z
        self.initial_distance = distance
        
        self.angle_x: float = angle_x
        self.angle_y: float = angle_y
        self.angle_z: float = angle_z
        self.distance: float = distance
        
        self.final_angle_x = 0.0
        self.final_angle_y = 45.0
        self.final_angle_z = 0.0
        self.final_distance = 12.0
        
        self.animation_duration = 2.0
        self.animation_start_time = None
        self.is_animating = False
        self.animation_complete = False
        
        self.target = [0.0, 0.0, 0.0]
        self.rotation_speed = 45.0
        self.zoom_speed = 2.5
        self.view_matrix = None
        self.camera_position = [0.0, 0.0, 0.0]
        self.last_time = time.time()
    
    def start_animation(self):
        """Start the zoom-in animation."""
        self.animation_start_time = time.time()
        self.is_animating = True
        self.animation_complete = False
    
    def update_animation(self):
        """Update the camera animation if active."""
        if not self.is_animating or self.animation_complete:
            return
        
        current_time = time.time()
        elapsed = current_time - self.animation_start_time
        
        if elapsed >= self.animation_duration:
            self.angle_x = self.final_angle_x
            self.angle_y = self.final_angle_y
            self.angle_z = self.final_angle_z
            self.distance = self.final_distance
            self.is_animating = False
            self.animation_complete = True
            self.apply()
            return
        
        t = elapsed / self.animation_duration
        t = 1 - (1 - t) ** 3  # Cubic easing
        
        self.angle_x = self.lerp(self.initial_angle_x, self.final_angle_x, t)
        self.angle_y = self.lerp(self.initial_angle_y, self.final_angle_y, t)
        self.angle_z = self.lerp(self.initial_angle_z, self.final_angle_z, t)
        self.distance = self.lerp(self.initial_distance, self.final_distance, t)
        
        self.apply()
    
    def lerp(self, start, end, t):
        """Linear interpolation with clamping."""
        return start + (end - start) * max(0.0, min(1.0, t))
    
    def apply(self) -> None:
        """Apply current camera transformations."""
        angle_h_rad = math.radians(self.angle_x)
        angle_v_rad = math.radians(self.angle_y)
        
        camera_x = (self.target[0] + 
                   self.distance * math.cos(angle_h_rad) * math.cos(angle_v_rad))
        camera_y = (self.target[1] + 
                   self.distance * math.sin(angle_v_rad))
        camera_z = (self.target[2] + 
                   self.distance * math.sin(angle_h_rad) * math.cos(angle_v_rad))
        
        self.camera_position = [camera_x, camera_y, camera_z]
        
        self.view_matrix = {
            'eye_position': self.camera_position,
            'target_position': self.target,
            'up_vector': self._calculate_up_vector(),
            'angles': (self.angle_x, self.angle_y, self.angle_z),
            'distance': self.distance
        }
    
    def _calculate_up_vector(self):
        """Calculate up vector for overhead view."""
        roll_rad = math.radians(self.angle_z)
        cos_roll = math.cos(roll_rad)
        sin_roll = math.sin(roll_rad)
        
        return [sin_roll, cos_roll, 0.0]
    
    def calculate_camera_position(self):
        """Calculate camera position for OpenGL gluLookAt."""
        return self.camera_position
    
    def zoom(self, delta: float) -> None:
        """Adjust camera zoom/distance."""
        self.distance += delta
        self.distance = max(3.0, min(40.0, self.distance))
        self.apply()
    
    def rotate(self, dx: float, dy: float) -> None:
        """Rotate the camera."""
        self.angle_x += dx
        self.angle_y += dy
        self.angle_y = max(60.0, min(89.0, self.angle_y))
        self.angle_x = self.angle_x % 360.0
        self.apply()
    
    def follow_target(self, target_position, height_offset=0.0):
        """Make the camera follow a target."""
        self.target = [
            target_position[0],
            target_position[1] + height_offset,
            target_position[2]
        ]
        self.apply()
    
    def reset_to_overhead(self):
        """Reset camera to standard overhead view."""
        self.angle_x = 0.0
        self.angle_y = 75.0
        self.angle_z = 0.0
        self.distance = 12.0
        self.apply()