"""
Core game systems package
Contains fundamental game components
"""

from .Agent import Agent
from .GridGenerator import GridGenerator
from .GridUtils import GridUtils
from .PathfindingEngine import PathfindingEngine

# Player is optional (for multiplayer)
try:
    from .Player import Player
    __all__ = [
        'Agent',
        'GridGenerator',
        'GridUtils',
        'PathfindingEngine',
        'Player'
    ]
except ImportError:
    __all__ = [
        'Agent',
        'GridGenerator',
        'GridUtils',
        'PathfindingEngine'
    ]

__version__ = "1.0.0"