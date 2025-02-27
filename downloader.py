# downloader.py

import os
import glob
from config import LOGGER

def descargar_musica(url):
    """
    Descarga la música utilizando spotdl y retorna la lista de archivos .mp3 generados.
    """
    try:
        os.system(f"spotdl {url}")
        return glob.glob("*.mp3")
    except Exception as e:
        LOGGER.error(f"Error al descargar música: {e}")
        return None