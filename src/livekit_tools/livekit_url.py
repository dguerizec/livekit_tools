import os
import urllib.parse

from .livekit_token import create_access_token


def parse_livekit_url(url: str) -> dict[str, str]:
    split = urllib.parse.urlparse(url)
    if split.scheme != 'livekit':
        raise ValueError(f"Invalid url scheme: {url}")

    port = split.port or 7880
    ws = 'wss' if port == 443 else 'ws'
    url = f"{ws}://{split.hostname}:{port}" if port != 443 else f"{ws}://{split.hostname}"

    qs = urllib.parse.parse_qs(split.query)
    api_key = qs.get('api_key', ['devkey'])[0]
    api_secret = qs.get('api_secret', ['secret'])[0]
    ttl = qs.get('ttl', ['6h'])[0]
    identity = split.username or f'lkcli-{os.getpid()}'
    room = split.path[1:]

    token = create_access_token(api_key=api_key, api_secret=api_secret, room_name=room, identity=identity, ttl=ttl)
    return {'url': url, 'token': token, 'api_key': api_key, 'api_secret': api_secret, 'room': room, 'identity': identity, 'ttl': ttl}

def print_livekit_server_url(url: str, verbose: bool = False) -> None:
    info = parse_livekit_url(url)
    if verbose:
        print(f'# {info}')
    print(f"https://meet.livekit.io/custom?liveKitUrl={info['url']}&token={info['token']}")


if __name__ == "__main__":
    import typer
    typer.run(print_livekit_server_url)
