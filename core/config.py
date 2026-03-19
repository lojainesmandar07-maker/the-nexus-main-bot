import os
from dotenv import load_dotenv

load_dotenv()

# Paste your Discord bot token between the quotes:
HARDCODED_DISCORD_TOKEN = "PASTE_YOUR_DISCORD_TOKEN_HERE"

DISCORD_TOKEN = (
    HARDCODED_DISCORD_TOKEN.strip()
    or os.getenv("DISCORD_TOKEN")
    or os.getenv("TOKEN")
)

GUILD_ID = os.getenv("GUILD_ID")  # Optional, for faster guild-only command sync

if not DISCORD_TOKEN:
    raise ValueError(
        "Missing Discord token. Either set HARDCODED_DISCORD_TOKEN in core/config.py "
        "or set DISCORD_TOKEN/TOKEN in environment variables."
    )
