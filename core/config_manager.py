import json
import os
import logging
from typing import Any, Dict

CONFIG_FILE = "data/config.json"

# Default config structure based on requirements
DEFAULT_CONFIG = {
    "world_channels": {}, # e.g. "fantasy": 123
    "test_channel": None,
    "archetype_roles": {}, # e.g. "strategist": 111
    "npc_channels": {} # e.g. "fantasy": 321
}

def load_config() -> Dict[str, Any]:
    """Load configuration from the JSON file, creating it with defaults if missing."""
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(CONFIG_FILE):
        logging.warning(f"Config file not found at {CONFIG_FILE}. Creating with defaults.")
        _save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Merge with defaults to ensure all keys exist
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except json.JSONDecodeError:
        logging.error(f"Error decoding {CONFIG_FILE}. Using default config.")
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        logging.error(f"Unexpected error loading config: {e}. Using default config.")
        return DEFAULT_CONFIG.copy()

def _save_config(config: Dict[str, Any]) -> None:
    """Save configuration to the JSON file."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to save config: {e}")

def get_config(key: str, default: Any = None) -> Any:
    """Safely get a configuration value."""
    config = load_config()
    return config.get(key, default)

def set_config(key: str, value: Any) -> None:
    """Update a configuration value and save."""
    config = load_config()
    config[key] = value
    _save_config(config)

def update_nested_config(main_key: str, sub_key: str, value: Any) -> None:
    """Update a nested dictionary in the configuration and save."""
    config = load_config()
    if main_key not in config or not isinstance(config[main_key], dict):
        config[main_key] = {}
    config[main_key][sub_key] = value
    _save_config(config)
