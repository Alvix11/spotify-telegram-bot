from dotenv import load_dotenv
import logging
import os

# Loads the variables from the .env file into the system environment.
load_dotenv()

# --- Telegram settings ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# --- Spotify settings ---
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# --- Database settings ---
DB_NAME = "music_cache"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = "localhost"
DB_PORT = "5432"

#Maximum allowed size of telegram to send files through bots.
MAX_SIZE = 50 * 1024 * 1024  # 50 MB

# --- Logging settings ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)
