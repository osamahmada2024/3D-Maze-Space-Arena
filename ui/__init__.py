"""
User interface systems package
Contains menu and camera control systems
"""

from .MenuManager import MenuManager
from .CameraController import CameraController

# Alternative camera module
try:
    from .camera import Camera, CameraController as CameraController2
    __all__ = [
        'MenuManager',
        'CameraController',
        'Camera',
        'CameraController2'
    ]
except ImportError:
    __all__ = [
        'MenuManager',
        'CameraController'
    ]

__version__ = "1.0.0"