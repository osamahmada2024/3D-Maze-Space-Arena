import time
import math

class CameraController:
    """
    Role: Manage 3D camera movement and user interaction.
    
    Responsibilities:
    - Apply rotation and zoom.
    - Maintain stable camera orientation.
    """
    
    def __init__(self, angle_x: float = 45.0, angle_y: float = 30.0, angle_z: float = 0.0, distance: float = 8.0):
        """
        Initialize camera controller with provided parameters.
        
        Args:
            angle_x: Horizontal angle in degrees (default: 45.0)
            angle_y: Vertical angle in degrees (default: 30.0)
            angle_z: Roll angle in degrees (default: 0.0)
            distance: Camera distance (default: 8.0)
        """
        self.angle_x: float = angle_x  # Horizontal angle in degrees (yaw)
        self.angle_y: float = angle_y  # Vertical angle in degrees (pitch)
        self.angle_z: float = angle_z  # Roll angle in degrees (roll)
        self.distance: float = distance  # Camera distance
        
        # Object scaling
        self.object_scale = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0
        self.scale_speed = 0.1
        
        # Control speeds
        self.rotation_speed = 50.0  # degrees per second
        
        # Keyboard state tracking
        self.key_states = {}
        
        # Target position
        self.target = [0.0, 0.0, 0.0]
        
        # View matrix placeholder
        self.view_matrix = None
        
        # Time tracking
        
        self.last_time = time.time()
    
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
        # In a real OpenGL application, this would call gluLookAt
        self.view_matrix = {
            'eye_position': self.camera_position,
            'target_position': self.target,
            'up_vector': self._calculate_up_vector(),
            'angles': (self.angle_x, self.angle_y, self.angle_z),
            'distance': self.distance,
            'object_scale': self.object_scale
        }
        
        # Optional: Print debug info
        # print(f"Camera applied: position={self.camera_position}, angles=({self.angle_x}, {self.angle_y}, {self.angle_z})")
    
    def _calculate_up_vector(self):
        """Calculate up vector considering roll angle"""
        
        # Start with standard up vector
        up_vector = [0.0, 1.0, 0.0]
        
        # If there's roll angle, rotate the up vector
        if self.angle_z != 0:
            roll_rad = math.radians(self.angle_z)
            cos_roll = math.cos(roll_rad)
            sin_roll = math.sin(roll_rad)
            
            # Simple 2D rotation in the camera's local up/right plane
            up_vector = [
                up_vector[0] * cos_roll - up_vector[2] * sin_roll,
                up_vector[1],
                up_vector[0] * sin_roll + up_vector[2] * cos_roll
            ]
        
        return up_vector
    
    def rotate(self, dx: float, dy: float, dz: float = 0.0) -> None:
        """
        Rotate the camera by the given deltas.
        
        Args:
            dx: Horizontal rotation delta (yaw)
            dy: Vertical rotation delta (pitch)
            dz: Roll rotation delta (roll, optional, default: 0.0)
        """
        self.angle_x += dx
        self.angle_y += dy
        self.angle_z += dz
        
        # Apply limits (prevent flipping)
        self.angle_y = max(-89.0, min(89.0, self.angle_y))
        
        # Normalize angles to keep them in reasonable range
        self.angle_x = self.angle_x % 360.0
        self.angle_z = self.angle_z % 360.0
        
        self.apply()
    
    def zoom(self, delta: float) -> None:
        """
        Adjust camera zoom/distance.
        
        Args:
            delta: Zoom delta (positive zooms out, negative zooms in)
        """
        self.distance += delta
        # Add minimum/maximum distance constraints
        if self.distance < 1.0:
            self.distance = 1.0
        self.apply()
    
    def update_input(self):
        """Update camera based on keyboard input"""
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # Apply rotation based on key states
        if self.key_states.get('right', False): 
            self.angle_x += self.rotation_speed * delta_time
        if self.key_states.get('left', False):
            self.angle_x -= self.rotation_speed * delta_time
        if self.key_states.get('up', False):
            self.angle_y += self.rotation_speed * delta_time
        if self.key_states.get('down', False):
            self.angle_y -= self.rotation_speed * delta_time
            
        # Apply limits (prevent flipping)
        self.angle_y = max(-89.0, min(89.0, self.angle_y))
        
        # Normalize horizontal angle
        self.angle_x = self.angle_x % 360.0
        
        self.apply()
    
    def handle_mouse_wheel(self, delta):
        """Handle mouse wheel for object scaling"""
        self.object_scale += delta * self.scale_speed
        
        # Apply scale limits
        self.object_scale = max(self.min_scale, min(self.max_scale, self.object_scale))
        
        self.apply()
    
    def calculate_camera_position(self):
        """Calculate camera position using spherical coordinates"""
        
        angle_h_rad = math.radians(self.angle_x)
        angle_v_rad = math.radians(self.angle_y)
        
        # Spherical coordinates to Cartesian
        camera_x = (self.target[0] + 
                   self.distance * math.cos(angle_h_rad) * math.cos(angle_v_rad))
        camera_y = (self.target[1] + 
                   self.distance * math.sin(angle_v_rad))
        camera_z = (self.target[2] + 
                   self.distance * math.sin(angle_h_rad) * math.cos(angle_v_rad))
        
        return [camera_x, camera_y, camera_z]
    
    def update_view_matrix(self, width, height):
        """Update the view matrix for rendering"""
        # Note: In actual OpenGL code, this would use gluLookAt
        # For this example, we just update our internal view matrix
        self.apply()
        return self.camera_position
    
    def set_key_state(self, key, state):
        """Set the state of a keyboard key"""
        self.key_states[key] = state
        self.apply()
    
    def get_camera_info(self):
        """Get current camera parameters for display"""
        # Make sure view matrix is up to date
        if self.view_matrix is None:
            self.apply()
            
        return {
            'horizontal_angle': self.angle_x,
            'vertical_angle': self.angle_y,
            'roll_angle': self.angle_z,
            'distance': self.distance,
            'object_scale': self.object_scale,
            'camera_position': self.camera_position,
            'target_position': self.target,
            'view_matrix_available': self.view_matrix is not None
        }
    
    def set_angles(self, angle_x: float = None, angle_y: float = None, angle_z: float = None):
        """
        Set camera angles directly.
        
        Args:
            angle_x: Horizontal angle in degrees (optional)
            angle_y: Vertical angle in degrees (optional)
            angle_z: Roll angle in degrees (optional)
        """
        if angle_x is not None:
            self.angle_x = angle_x
        if angle_y is not None:
            self.angle_y = max(-89.0, min(89.0, angle_y))
        if angle_z is not None:
            self.angle_z = angle_z
        
        # Normalize angles
        self.angle_x = self.angle_x % 360.0
        self.angle_z = self.angle_z % 360.0
        
        self.apply()
    
    def get_view_matrix(self):
        """Get the current view matrix data"""
        if self.view_matrix is None:
            self.apply()
        return self.view_matrix