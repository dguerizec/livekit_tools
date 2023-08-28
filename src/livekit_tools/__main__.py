from .livekit_token import print_access_token
import typer

from .livekit_url import print_livekit_server_url


def main_token() -> None:
    typer.run(print_access_token)

def main_url() -> None:
    typer.run(print_livekit_server_url)
