import os
import glob
from config import LOGGER

def music_download(url):
    """Download the song using spotdl and return the list of generated .mp3 files."""
    try:
        os.system(f"spotdl {url}")
        return glob.glob("*.mp3")
    except Exception as e:
        LOGGER.error(f"Error al descargar música: {e}")
        return None