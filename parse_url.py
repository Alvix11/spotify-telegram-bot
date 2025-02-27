from urllib.parse import urlparse, urlunparse

def limpiar_url(url):
    # Parsear la URL en sus componentes
    parsed_url = urlparse(url)
    # Reconstruir la URL sin parámetros de consulta ni fragmentos
    clean_url = urlunparse((
        parsed_url.scheme,   # Protocolo (https)
        parsed_url.netloc,   # Dominio (open.spotify.com)
        parsed_url.path,     # Ruta (/track/...)
        "",                  # Parámetros (no se usan comúnmente)
        "",                  # Consulta (eliminamos ?si=...)
        ""                   # Fragmento (eliminamos #...)
    ))
    return clean_url
