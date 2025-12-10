# config/settings.py
"""
Central Configuration File
All game settings in one place
"""

# =============================================================================
# AGENT SETTINGS
# =============================================================================
AGENT_SETTINGS = {
    "speed": 2.5,
    "trail_length": 30,
    "colors": {
        "sphere_droid": (0.0, 1.0, 1.0),    # Cyan
        "robo_cube": (1.0, 0.3, 0.3),       # Red
        "mini_drone": (0.2, 0.7, 0.3),      # Green
        "crystal_alien": (0.8, 0.3, 1.0)    # Purple
    }
}

# =============================================================================
# CAMERA SETTINGS
# =============================================================================
CAMERA_SETTINGS = {
    "distance": 10,
    "angle_x": 45,
    "angle_y": 30,
    "angle_y_min": 10,
    "angle_y_max": 89,
    "rotation_speed": 60,
    "smooth_factor": 0.1,
    "zoom_min": 3,
    "zoom_max": 60
}

# =============================================================================
# GRID SETTINGS
# =============================================================================
GRID_SETTINGS = {
    "size": 25,
    "cell_size": 1.0,
    "obstacle_prob_space": 0.25,
    "obstacle_prob_forest": 0.35,
    "obstacle_prob_lava": 0.35  # ✅ جديد - للمتاهة البركانية
}

# =============================================================================
# ALGORITHM MAPPING
# =============================================================================
ALGORITHM_MAP = {
    "A* search": "astar",
    "Dijkstra": "dijkstra",
    "DFS": "dfs",
    "BFS": "bfs"
}

# =============================================================================
# THEME SETTINGS
# =============================================================================
THEME_SETTINGS = {
    "FOREST": {
        "name": "Forest Maze",
        "bg_color": (0.0, 0.0, 0.0, 1.0),
        "fog_enabled": True,
        "fog_color": (0.0, 0.0, 0.0),
        "fog_density": 0.20,
        "particles_enabled": True,
        "audio_enabled": True
    },
    "DEFAULT": {
        "name": "Space Maze",
        "bg_color": (0.05, 0.05, 0.1, 1.0),
        "fog_enabled": False,
        "fog_color": (0.05, 0.06, 0.09),
        "fog_density": 0.018,
        "particles_enabled": True,
        "audio_enabled": False
    },
    # ✅ جديد - إعدادات المتاهة البركانية
    "LAVA": {
        "name": "Lava Maze",
        "bg_color": (0.1, 0.05, 0.0, 1.0),  # خلفية حمراء داكنة
        "fog_enabled": True,
        "fog_color": (0.3, 0.1, 0.05),      # ضباب برتقالي
        "fog_density": 0.025,
        "particles_enabled": True,
        "audio_enabled": True,
        # إعدادات خاصة بالحمم
        "lava_coverage": 0.12,              # نسبة تغطية الحمم
        "lava_damage": 10.0,                # الضرر من الحمم
        "health_start": 100.0               # الصحة الابتدائية
    }
}

# =============================================================================
# LAVA SPECIFIC SETTINGS (إعدادات إضافية للحمم)
# =============================================================================
LAVA_SETTINGS = {
    "agent_colors": {
        "sphere_droid": (1.0, 0.5, 0.0),   # برتقالي (مقاوم للنار)
        "robo_cube": (0.8, 0.2, 0.2),      # أحمر داكن
        "mini_drone": (1.0, 0.3, 0.0),     # برتقالي فاتح
        "crystal_alien": (1.0, 0.8, 0.0)   # أصفر برتقالي
    },
    "ember_count": 200,
    "rock_density": 0.7
}