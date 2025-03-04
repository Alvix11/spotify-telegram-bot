import requests
from spotify import get_token, get_info_song
import os
from config import LOGGER

def get_urls_album(url_album):
    """Gets the URLs of each song in an album from Spotify."""
    token = get_token()  
    if not token:
        LOGGER.warning(f"Error no se pudo obtener el token de Spotify: {token}")
        return None

    try:
        album_id = url_album.split("/album/")[1].split("?")[0]
    except IndexError:
        LOGGER.warning(f"Error la URL del álbum no válida: {album_id}")
        return None

    album_url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(album_url, headers=headers)

    if response.status_code == 200:
        album_data = response.json()
        track_urls = [track['external_urls']['spotify'] for track in album_data.get('tracks', {}).get('items', [])]
        return track_urls
    else:
        LOGGER.warning(f"Error obteniendo las canciones del álbum: {response.status_code}")
        return None
    
def match_track_with_file(archivo, url):
    """Compare each track in the album with the files to be sent so that the data is saved correctly."""
    name_file = os.path.basename(archivo)
    url_tracks = get_urls_album(url)
    
    # Create a set for already processed songs (avoid repeated calls)
    tracks_info = {}

    # Iterate over each URL of the song
    for url_track in url_tracks:
        # If the song information has already been processed, we get it from the dictionary.
        if url_track not in tracks_info:
            info_song = get_info_song(url_track)
            if info_song:
                name, artist = info_song[:2]
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



