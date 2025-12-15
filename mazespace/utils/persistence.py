import json
import os
from mazespace.config.definitions import GlobalConfig
from mazespace.config.loader import load_config

SESSION_FILE = ".last_session.json"

def save_session(config: GlobalConfig):
    """Save the current configuration as the last session."""
    try:
        data = config.to_dict()
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Session saved to {SESSION_FILE}")
    except Exception as e:
        print(f"Failed to save session: {e}")

def load_session() -> GlobalConfig:
    """Load the last session if available."""
    if os.path.exists(SESSION_FILE):
        try:
            return load_config(SESSION_FILE)
        except Exception as e:
            print(f"Failed to load last session: {e}")
    return None
