import time
import math


class CameraController:
    """
    Minimal 3D camera controller:
    rotation, zoom, scaling, and view-matrix updates.
    """

    def __init__(
        self,
        angle_x: float = 45.0,
        angle_y: float = 30.0,
        angle_z: float = 0.0,
        distance: float = 8.0
    ):
        self.angle_x = angle_x
        self.angle_y = angle_y
        self.angle_z = angle_z
        self.distance = distance

        self.object_scale = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0
        self.scale_speed = 0.1

        self.rotation_speed = 50.0
        self.key_states: dict = {}

        self.target = [0.0, 0.0, 0.0]
        self.camera_position = [0.0, 0.0, 0.0]
        self.view_matrix = None

        self.last_time = time.time()

    # ---------------------------------------------------------

    def apply(self) -> None:
        """Recompute camera position and update view matrix."""
        h_rad = math.radians(self.angle_x)
        v_rad = math.radians(self.angle_y)

        cx = self.target[0] + self.distance * math.cos(h_rad) * math.cos(v_rad)
        cy = self.target[1] + self.distance * math.sin(v_rad)
        cz = self.target[2] + self.distance * math.sin(h_rad) * math.cos(v_rad)

        self.camera_position = [cx, cy, cz]

        self.view_matrix = {
            "eye_position": self.camera_position,
            "target_position": self.target,
            "up_vector": self._calculate_up(),
            "angles": (self.angle_x, self.angle_y, self.angle_z),
            "distance": self.distance,
            "scale": self.object_scale,
        }

    # ---------------------------------------------------------

    def _calculate_up(self):
        """Return up-vector with roll applied."""
        up = [0.0, 1.0, 0.0]

        if self.angle_z != 0:
            r = math.radians(self.angle_z)
            c = math.cos(r)
            s = math.sin(r)
            up = [up[0] * c - up[2] * s,
                  up[1],
                  up[0] * s + up[2] * c]
        return up

    # ---------------------------------------------------------

    def rotate(self, dx: float, dy: float, dz: float = 0.0) -> None:
        """Apply rotation."""
        self.angle_x = (self.angle_x + dx) % 360.0
        self.angle_z = (self.angle_z + dz) % 360.0
        self.angle_y = max(-89.0, min(89.0, self.angle_y + dy))
        self.apply()

    # ---------------------------------------------------------

    def zoom(self, delta: float) -> None:
        """Adjust camera distance."""
        self.distance = max(1.0, self.distance + delta)
        self.apply()

    # ---------------------------------------------------------

    def update_input(self) -> None:
        """Update rotation from active keys."""
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        if self.key_states.get("right"):  self.angle_x += self.rotation_speed * dt
        if self.key_states.get("left"):   self.angle_x -= self.rotation_speed * dt
        if self.key_states.get("up"):     self.angle_y += self.rotation_speed * dt
        if self.key_states.get("down"):   self.angle_y -= self.rotation_speed * dt

        self.angle_x %= 360.0
        self.angle_y = max(-89.0, min(89.0, self.angle_y))

        self.apply()

    # ---------------------------------------------------------

    def handle_mouse_wheel(self, delta: float) -> None:
        """Adjust scale."""
        self.object_scale += delta * self.scale_speed
        self.object_scale = max(self.min_scale, min(self.max_scale, self.object_scale))
        self.apply()

    # ---------------------------------------------------------

    def set_key_state(self, key: str, state: bool) -> None:
        """Set key pressed state."""
        self.key_states[key] = state
        self.apply()

    # ---------------------------------------------------------

    def get_camera_info(self) -> dict:
        """Return camera parameters."""
        if self.view_matrix is None:
            self.apply()

        return {
            "angles": (self.angle_x, self.angle_y, self.angle_z),
            "distance": self.distance,
            "scale": self.object_scale,
            "camera_position": self.camera_position,
            "target": self.target,
        }
