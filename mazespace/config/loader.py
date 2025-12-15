import yaml
import json
import os
from .definitions import GlobalConfig

def load_config(path: str) -> GlobalConfig:
    """Load configuration from a YAML or JSON file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
        
    with open(path, 'r') as f:
        if path.endswith('.json'):
            data = json.load(f)
        elif path.endswith('.yaml') or path.endswith('.yml'):
            data = yaml.safe_load(f)
        else:
            raise ValueError("Unsupported config format. Use .yaml, .yml or .json")
            
    return GlobalConfig.from_dict(data)

def save_config(config: GlobalConfig, path: str):
    """Save configuration to a YAML or JSON file."""
    data = config.to_dict()
    with open(path, 'w') as f:
        if path.endswith('.json'):
            json.dump(data, f, indent=4)
        elif path.endswith('.yaml') or path.endswith('.yml'):
            yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError("Unsupported config format. Use .yaml, .yml or .json")

def load_defaults() -> GlobalConfig:
    """Load built-in defaults or return hardcoded object if file missing."""
    # Look for defaults.yaml in package or specific path
    # For now, we'll return a sensible default object if file logic is complex
    # But let's try to load from adjacent defaults.yaml
    base_dir = os.path.dirname(__file__)
    defaults_path = os.path.join(base_dir, "defaults.yaml")
    
    if os.path.exists(defaults_path):
        return load_config(defaults_path)
    
    # Fallback to hardcoded defaults
    # Minimal fallback
    from .definitions import GlobalConfig, AppConfig, ThemeConfig, AgentConfig
    return GlobalConfig(
        app=AppConfig(),
        themes=[
            ThemeConfig(key="DEFAULT", name="Standard (Space)", desc="Classic space", background_color=(0.05, 0.05, 0.1, 1.0)),
            ThemeConfig(key="LAVA", name="Lava Maze", desc="Hot lava", background_color=(0.2, 0.05, 0.0, 1.0), hazard_damage=10.0)
        ],
        agents=[
            AgentConfig(key="sphere_droid", name="Sphere Droid", desc="Simple sphere", shape="sphere", color=(0, 1, 1))
        ]
    )
