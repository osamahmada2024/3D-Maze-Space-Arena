"""
Forest theme package
Contains forest-specific scene and systems
"""

from .forest_scene import ForestScene
from .fog import FogSystem
from .particles import FireflyParticleSystem
from .audio_system import AudioSystem
from .slow_zones import SlowZoneManager
from .movable_objects import MovableObjectManager
from .environment_objects import EnvironmentObjectManager

__all__ = [
    'ForestScene',
    'FogSystem',
    'FireflyParticleSystem',
    'AudioSystem',
    'SlowZoneManager',
    'MovableObjectManager',
    'EnvironmentObjectManager'
]