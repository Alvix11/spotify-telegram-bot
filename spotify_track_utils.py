import requests
from spotify import obtener_token, obtener_info_cancion
import os
from config import LOGGER

def obtener_urls_album(url_album):
    """Gets the URLs of each song in an album from Spotify."""
    token = obtener_token()  
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
    
    # Create a set for already processed songs (avoid repeated calls)
    tracks_info = {}

    # Iterate over each URL of the song
    for url_track in url_tracks:
        # If the song information has already been processed, we get it from the dictionary.
        if url_track not in tracks_info:
            info_cancion = obtener_info_cancion(url_track)
            if info_cancion:
                name, artist = info_cancion[:2]
                name_song = f"{artist} - {name}.mp3"
                # Store the processed song in the dictionary to avoid recalculating it
                tracks_info[url_track] = name_song
            else:
                LOGGER.info(f"No se pudo obtener información de la URL: {url_track}")
                continue
        
        # Compare the name of the song with the file name
        if tracks_info[url_track] == name_file:
            LOGGER.info(f"Se encontró la canción: {tracks_info[url_track]}")
            return url_track

    return None



