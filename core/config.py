import os
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
