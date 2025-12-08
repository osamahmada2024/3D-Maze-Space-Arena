"""
Rendering systems package
Contains all visual rendering components
"""

from .AgentRender import AgentRender
from .PathRender import PathRender
from .GoalRender import GoalRender
from .ParticleSystem import ParticleSystem

# Model loader is optional
try:
    from .model_loader import (
        load_model, 
        load_texture,
        SimpleGLTFModel,
        SimpleOBJModel
    )
    __all__ = [
        'AgentRender',
        'PathRender',
        'GoalRender',
        'ParticleSystem',
        'load_model',
        'load_texture',
        'SimpleGLTFModel',
        'SimpleOBJModel'
    ]
except ImportError:
    __all__ = [
        'AgentRender',
        'PathRender',
        'GoalRender',
        'ParticleSystem'
    ]

__version__ = "1.0.0"