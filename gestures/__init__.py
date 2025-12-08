"""
Hand gesture detection package
Contains all gesture recognition components
"""

from .VolumeController import VolumeController
from .MuteGestureDetector import MuteGestureDetector
from .DirectionGestureDetector import DirectionGestureDetector
from .HandGestureDetector import HandGestureDetector

__all__ = [
    'VolumeController',
    'MuteGestureDetector',
    'DirectionGestureDetector',
    'HandGestureDetector'
]

__version__ = "1.0.0"