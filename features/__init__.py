"""
Additional game features package
Contains optional gameplay features
"""

# Lucky blocks system (optional)
try:
    from .lucky_blocks import (
        LuckyBlock,
        TeleportPoint,
        EffectType,
        ActiveEffect,
        LuckyBlockTeleportSystem,
        GameFlowIntegration
    )
    __all__ = [
        'LuckyBlock',
        'TeleportPoint',
        'EffectType',
        'ActiveEffect',
        'LuckyBlockTeleportSystem',
        'GameFlowIntegration'
    ]
except ImportError:
    __all__ = []

__version__ = "1.0.0"