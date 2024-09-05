import os
import urllib.parse

from .livekit_token import create_access_token


def parse_livekit_url(url: str) -> dict[str, int | str]:
    split = urllib.parse.urlparse(url)
    if split.scheme != "livekit":
        raise ValueError(f"Invalid url scheme: {url}")

    host = split.hostname or "localhost"
    port = int(split.port or 7880)
    ws = "wss" if port == 443 else "ws"
    url = f"{ws}://{host}:{port}" if port != 443 else f"{ws}://{host}"

    qs = urllib.parse.parse_qs(split.query)
    api_key = qs.get("api_key", ["devkey"])[0]
    api_secret = qs.get("api_secret", ["secret"])[0]
    ttl = qs.get("ttl", ["6h"])[0]
    identity = split.username or f"lkcli-{os.getpid()}"
    room = split.path[1:]

    token = create_access_token(api_key=api_key, api_secret=api_secret, room_name=room, identity=identity, ttl=ttl)
    d: dict[str, int | str] = {
        "url": url,
        "token": token,
        "api_key": api_key,
        "api_secret": api_secret,
        "room": room,
        "identity": identity,
        "ttl": ttl,
        "host": host,
        "port": port,
        "protocol": ws,
    }
    d["type"] = "livekit_sdk"
    return d


def get_livekit_test_ui_url(url: str) -> str:
    info = parse_livekit_url(url)
    return f"https://meet.livekit.io/custom?liveKitUrl={info['url']}&token={info['token']}"


def print_livekit_server_url(url: str, verbose: bool = False) -> None:
    info = parse_livekit_url(url)
    if verbose:
        print(f"# {info}")
    print(f"https://meet.livekit.io/custom?liveKitUrl={info['url']}&token={info['token']}")
