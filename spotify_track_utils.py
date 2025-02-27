import requests
from spotify import obtener_token, obtener_info_cancion
import os
from config import LOGGER

def obtener_urls_album(url_album):
    """
    Obtiene las URLs de cada canción de un álbum de Spotify.
    """
    token = obtener_token()  # Asegúrate de tener una función que obtenga el token de Spotify
    if not token:
        print("Error: No se pudo obtener el token de Spotify.")
        return None

    try:
        album_id = url_album.split("/album/")[1].split("?")[0]
    except IndexError:
        print("Error: URL del álbum no válida.")
        return None

    album_url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(album_url, headers=headers)

    if response.status_code == 200:
        album_data = response.json()
        track_urls = [track['external_urls']['spotify'] for track in album_data.get('tracks', {}).get('items', [])]
        return track_urls
    else:
        print(f"Error obteniendo las canciones del álbum: {response.status_code}")
        return None
    
def match_track_with_file(archivo, url):
    name_file = os.path.basename(archivo)
    url_tracks = obtener_urls_album(url)
    
    # Crear un set para las canciones ya procesadas (evitar llamadas repetidas)
    tracks_info = {}

    # Iterar sobre cada URL de la canción
    for url_track in url_tracks:
        # Si la información de la canción ya fue procesada, la obtenemos del diccionario
        if url_track not in tracks_info:
            info_cancion = obtener_info_cancion(url_track)
            if info_cancion:
                name, artist = info_cancion[:2]
                name_song = f"{artist} - {name}.mp3"
                # Almacenar la canción procesada en el diccionario para evitar recalcularla
                tracks_info[url_track] = name_song
            else:
                LOGGER.info(f"No se pudo obtener información de la URL: {url_track}")
                continue
        
        # Comparar el nombre de la canción con el nombre del archivo
        if tracks_info[url_track] == name_file:
            LOGGER.info(f"Se encontró la canción: {tracks_info[url_track]}")
            return url_track

    return None



