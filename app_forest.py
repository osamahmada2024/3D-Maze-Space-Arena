# CameraController.py
import time
import math

class CameraController:
    """
    Role: Manage 3D camera movement with overhead view and smooth animations.
    
    Responsibilities:
    - Apply rotation and zoom with overhead perspective.
    - Maintain stable camera orientation.
    - Handle smooth animations for zoom-in effect.
    """
    
    def __init__(self, angle_x: float = 0.0, angle_y: float = 80.0, angle_z: float = 0.0, distance: float = 25.0):
        """
        Initialize camera controller with overhead view.
        
        Args:
            angle_x: Horizontal angle in degrees (default: 0.0 for overhead)
            angle_y: Vertical angle in degrees (default: 80.0 for nearly top-down)
            angle_z: Roll angle in degrees (default: 0.0)
            distance: Camera distance (default: 25.0)
        """
        # Initial angles for distant overhead view
        self.initial_angle_x = angle_x
        self.initial_angle_y = angle_y
        self.initial_angle_z = angle_z
        self.initial_distance = distance
        
        # Current angles and distance (will be animated)
        self.angle_x: float = angle_x
        self.angle_y: float = angle_y
        self.angle_z: float = angle_z
        self.distance: float = distance
        
        # Final angles and distance for gameplay (closer overhead view)
        self.final_angle_x = 0.0
        self.final_angle_y = 45.0  # Slightly less steep than initial
        self.final_angle_z = 0.0
        self.final_distance = 12.0  # Closer than initial
        
        # Animation control
        self.animation_duration = 2.0  # seconds
        self.animation_start_time = None
        self.is_animating = False
        self.animation_complete = False
        
        # Target position (center of grid)
        self.target = [0.0, 0.0, 0.0]
        
        # Control speeds
        self.rotation_speed = 45.0  # degrees per second
        self.zoom_speed = 2.5  # units per second
        
        # View matrix placeholder
        self.view_matrix = None
        self.camera_position = [0.0, 0.0, 0.0]
        
        # Time tracking
        self.last_time = time.time()
    
    def start_animation(self):
        """Start the zoom-in animation"""
        self.animation_start_time = time.time()
        self.is_animating = True
        self.animation_complete = False
    
    def update_animation(self):
        """Update the camera animation if active"""
        if not self.is_animating or self.animation_complete:
            return
        
        current_time = time.time()
        elapsed = current_time - self.animation_start_time
        
        if elapsed >= self.animation_duration:
            # Animation complete
            self.angle_x = self.final_angle_x
            self.angle_y = self.final_angle_y
            self.angle_z = self.final_angle_z
            self.distance = self.final_distance
            self.is_animating = False
            self.animation_complete = True
            self.apply()
            return
        
        # Calculate interpolation factor (smooth easing)
        t = elapsed / self.animation_duration
        # Cubic easing out
        t = 1 - (1 - t) ** 3
        
        # Interpolate values
        self.angle_x = self.lerp(self.initial_angle_x, self.final_angle_x, t)
        self.angle_y = self.lerp(self.initial_angle_y, self.final_angle_y, t)
        self.angle_z = self.lerp(self.initial_angle_z, self.final_angle_z, t)
        self.distance = self.lerp(self.initial_distance, self.final_distance, t)
        
        self.apply()
    
    def lerp(self, start, end, t):
        """Linear interpolation with clamping"""
        return start + (end - start) * max(0.0, min(1.0, t))
    
    def apply(self) -> None:
        """
        Apply current camera transformations.
        This method updates the camera view matrix based on current state.
        """
        
        # Calculate camera position using spherical coordinates
        angle_h_rad = math.radians(self.angle_x)
        angle_v_rad = math.radians(self.angle_y)
        
        # Spherical coordinates to Cartesian
        camera_x = (self.target[0] + 
                   self.distance * math.cos(angle_h_rad) * math.cos(angle_v_rad))
        camera_y = (self.target[1] + 
                   self.distance * math.sin(angle_v_rad))
        camera_z = (self.target[2] + 
                   self.distance * math.sin(angle_h_rad) * math.cos(angle_v_rad))
        
        # Store camera position
        self.camera_position = [camera_x, camera_y, camera_z]
        
        # Calculate view matrix (simplified for this example)
        self.view_matrix = {
            'eye_position': self.camera_position,
            'target_position': self.target,
            'up_vector': self._calculate_up_vector(),
            'angles': (self.angle_x, self.angle_y, self.angle_z),
            'distance': self.distance
        }
    
    def _calculate_up_vector(self):
        """Calculate up vector for overhead view"""
        # For overhead view, we want up to be mostly vertical
        # but adjusted for any roll
        roll_rad = math.radians(self.angle_z)
        cos_roll = math.cos(roll_rad)
        sin_roll = math.sin(roll_rad)
        
        # Standard up vector rotated by roll
        up_vector = [
            sin_roll,  # Small x component for roll
            cos_roll,  # Main y component
            0.0        # No z component for pure overhead
        ]
        
        return up_vector
    
    def calculate_camera_position(self):
        """Calculate camera position for OpenGL gluLookAt"""
        return self.camera_position
    
    def zoom(self, delta: float) -> None:
        """
        Adjust camera zoom/distance.
        
        Args:
            delta: Zoom delta (positive zooms out, negative zooms in)
        """
        self.distance += delta
        # Clamp distance
        self.distance = max(3.0, min(40.0, self.distance))
        self.apply()
    
    def rotate(self, dx: float, dy: float) -> None:
        """
        Rotate the camera by the given deltas.
        
        Args:
            dx: Horizontal rotation delta (yaw)
            dy: Vertical rotation delta (pitch)
        """
        self.angle_x += dx
        self.angle_y += dy
        
        # Apply limits to maintain overhead view
        self.angle_y = max(60.0, min(89.0, self.angle_y))  # Keep it overhead
        self.angle_x = self.angle_x % 360.0
        
        self.apply()
    
    def follow_target(self, target_position, height_offset=0.0):
        """
        Make the camera follow a target.
        
        Args:
            target_position: [x, y, z] position to follow
            height_offset: Additional height offset
        """
        self.target = [
            target_position[0],
            target_position[1] + height_offset,
            target_position[2]
        ]
        self.apply()
    
    def get_camera_info(self):
        """Get current camera parameters for display"""
        if self.view_matrix is None:
            self.apply()
            
        return {
            'horizontal_angle': self.angle_x,
            'vertical_angle': self.angle_y,
            'distance': self.distance,
            'camera_position': self.camera_position,
            'target_position': self.target,
            'is_animating': self.is_animating,
            'animation_complete': self.animation_complete
        }
    
    def reset_to_overhead(self):
        """Reset camera to standard overhead view"""
        self.angle_x = 0.0
        self.angle_y = 75.0
        self.angle_z = 0.0
        self.distance = 12.0
        self.apply()