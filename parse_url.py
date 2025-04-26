from urllib.parse import urlparse, urlunparse

def clean_url(url):
    """Parse the URL into its components and clean it."""
    parsed_url = urlparse(url)
    
    # Remove 'intl-es' from the path if present
    path = parsed_url.path
    if path.startswith('/intl-'):
        # Split the path and keep only the parts after 'intl-xx'
        path_parts = path.split('/')
        path = '/' + '/'.join(path_parts[2:])  # Skip the first two parts (empty and 'intl-xx')
    
    # Rebuild the URL without query parameters, fragments, and intl-xx
    url_clean = urlunparse((
        parsed_url.scheme,   # Protocol (https)
        parsed_url.netloc,   # Domain (open.spotify.com)
        path,               # Modified path (without /intl-es)
        "",                 # Parameters (not commonly used)
        "",                 # Query (delete ?if=...)
        ""                  # Fragment (remove #...)
    ))
    return url_clean
