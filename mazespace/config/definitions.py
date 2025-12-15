from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Dict, Any, Optional

@dataclass
class AgentConfig:
    key: str
    name: str
    desc: str
    color: Tuple[float, float, float] = (0.0, 1.0, 1.0)
    shape: str = "drone"
    scale: float = 1.0
    speed: float = 1.0

@dataclass
class ThemeConfig:
    key: str
    name: str
    desc: str
    background_color: Tuple[float, float, float, float] = (0.05, 0.05, 0.05, 1.0)
    hazard_damage: float = 0.0
    particle_density: int = 10

@dataclass
class AppConfig:
    width: int = 900
    height: int = 700
    fullscreen: bool = False
    default_theme: str = "DEFAULT"
    default_agent: str = "sphere_droid"
    default_algo: str = "A* search"

@dataclass
class GlobalConfig:
    app: AppConfig = field(default_factory=AppConfig)
    agents: List[AgentConfig] = field(default_factory=list)
    themes: List[ThemeConfig] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GlobalConfig':
        # Simple recursive dict to dataclass parser
        app_data = data.get("app", {})
        app_cfg = AppConfig(**app_data)
        
        agents_data = data.get("agents", [])
        agents_cfg = [AgentConfig(**a) for a in agents_data]
        
        themes_data = data.get("themes", [])
        themes_cfg = [ThemeConfig(**t) for t in themes_data]
        
        return cls(app=app_cfg, agents=agents_cfg, themes=themes_cfg)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
