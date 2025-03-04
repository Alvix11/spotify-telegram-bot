from urllib.parse import urlparse, urlunparse

def clean_url(url):
    """Parse the URL into its components."""
    parsed_url = urlparse(url)
    # Rebuild the URL without query parameters and fragments
    url_clean = urlunparse((
        parsed_url.scheme,   # Protocol (https)
        parsed_url.netloc,   # Domain (open.spotify.com)
        parsed_url.path,     # Path (/track/...)
        "",                  # Parameters (not commonly used)
        "",                  # Query (delete ?if=...)
        ""                   # Fragment (remove #...)
    ))
    return url_clean
