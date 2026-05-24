import requests
from requests.adapters import HTTPAdapter


_openrouter_session = requests.Session()
_openrouter_session.trust_env = False
_openrouter_session.mount('https://', HTTPAdapter(pool_connections=100, pool_maxsize=100))
_openrouter_session.mount('http://', HTTPAdapter(pool_connections=100, pool_maxsize=100))


def post_openrouter(url, **kwargs):
    return _openrouter_session.post(url, **kwargs)
