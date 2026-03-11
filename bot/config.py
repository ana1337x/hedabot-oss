import os
import sys
from dotenv import load_dotenv

# Load the .env file when running locally. Cloud platforms (Railway, Fly.io)
# set environment variables through their dashboard instead, so we skip it there.
_is_cloud = any(os.environ.get(v) for v in ("RAILWAY_ENVIRONMENT", "FLY_APP_NAME"))
if not _is_cloud:
    load_dotenv()

REQUIRED = [
    "DISCORD_TOKEN",
    "DEEPGRAM_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
]

missing = [v for v in REQUIRED if not os.environ.get(v)]
if missing:
    print(f"[config] Missing required env vars: {missing}", file=sys.stderr)
    sys.exit(1)

DISCORD_TOKEN: str = os.environ["DISCORD_TOKEN"]

# discord.py can read the app ID out of the bot token itself, so you don't
# need to set this separately. It's here in case you ever need to override it.
DISCORD_CLIENT_ID: int = int(os.environ.get("DISCORD_CLIENT_ID") or "0")

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY: str = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

DEEPGRAM_API_KEY: str = os.environ["DEEPGRAM_API_KEY"]

VOICE_CONNECTION_TIMEOUT: int = int(os.environ.get("VOICE_CONNECTION_TIMEOUT", "15"))
