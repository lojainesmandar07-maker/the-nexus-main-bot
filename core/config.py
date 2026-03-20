import os
import json
from dotenv import load_dotenv

load_dotenv()

# Direct token-in-code setup requested by user.
DISCORD_TOKEN = ""
# Optional fallback if you clear DISCORD_TOKEN above:
if not DISCORD_TOKEN.strip():
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
GUILD_ID = os.getenv("GUILD_ID") # Optional, for testing sync commands faster

if not DISCORD_TOKEN:
    raise ValueError(
        "Missing Discord token. Set DISCORD_TOKEN in core/config.py or as an environment variable."
    )

# --- New config helpers ---
CONFIG_PATH = "data/config.json"

_DEFAULT_CONFIG = {
    "world_channels": {},
    "test_channel": None,
    "archetype_roles": {},
    "npc_channels": {}
}

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        save_config(_DEFAULT_CONFIG.copy())
        return _DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, val in _DEFAULT_CONFIG.items():
            data.setdefault(key, val)
        return data
    except Exception:
        return _DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_config(key: str, default=None):
    return load_config().get(key, default)
