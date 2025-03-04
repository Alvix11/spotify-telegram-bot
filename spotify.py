import requests
import base64
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, LOGGER

def get_token():
    """Get the Spotify access token."""
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        LOGGER.error(f"Error obteniendo el token: {response.status_code}")
        return None

def get_info_song(url):
    """Gets information about a track given the Spotify link."""
    token = get_token()
    if not token:
        return None

    try:
        track_id = url.split("/track/")[1].split("?")[0]
    except IndexError:
        LOGGER.error("URL no válida para un track.")
        return None

    track_url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(track_url, headers=headers)
    
    if response.status_code == 200:
        track_data = response.json()
        name = track_data.get('name')
        artists = [artist['name'] for artist in track_data['artists']]
        album = track_data.get('album', {}).get('name')
        date = track_data.get('album', {}).get('release_date')
        image_url = track_data.get('album', {}).get('images', [{}])[0].get('url')
        if len(artists) > 1:
            various_artists = ", ".join(artists)
            if len(name) > 100:
                name = name[:97] + "..."
                return name, various_artists, album, date, image_url
            else:
                return name, various_artists, album, date, image_url
        else:
            artist = "".join(artists)
            if len(name) > 100:
                name = name[:97] + "..."
                return name, artist, album, date, image_url
            else:
                return name, artist, album, date, image_url
            
    else:
        LOGGER.error(f"Error obteniendo la información del track: {response.status_code}")
        return None

def get_info_album(url):
    """Gets information about an album given the Spotify link."""
    token = get_token()
    if not token:
        return None

    try:
        album_id = url.split("/album/")[1].split("?")[0]
    except IndexError:
        LOGGER.error("URL no válida para un álbum.")
        return None

    album_url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(album_url, headers=headers)
    
    if response.status_code == 200:
        album_data = response.json()
        name_album = album_data.get('name')
        artist = album_data.get('artists', [{}])[0].get('name')
        date = album_data.get('release_date')
        image_url = album_data.get('images', [{}])[0].get('url')
        songs = album_data.get('tracks', {}).get('items', [])
        return name_album, artist, date, image_url, songs
    else:
        LOGGER.error(f"Error obteniendo la información del álbum: {response.status_code}")
        return None