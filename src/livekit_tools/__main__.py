import typer
from .livekit_token import print_access_token
from .livekit_url import print_livekit_server_url


def main_token() -> None:
    typer.run(print_access_token)

def main_url() -> None:
    typer.run(print_livekit_server_url)

def main_peek() -> None:
    from .livekit_frames import peek_on_livekit
    typer.run(peek_on_livekit)