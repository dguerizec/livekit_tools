import typer


def main_token() -> None:
    from .livekit_token import print_access_token

    typer.run(print_access_token)


def main_url() -> None:
    from .livekit_url import print_livekit_server_url

    typer.run(print_livekit_server_url)


def main_peek() -> None:
    raise NotImplementedError("Not implemented yet")
    # from .livekit_frames import peek_on_livekit

    # typer.run(peek_on_livekit)


def main_decode() -> None:
    from .livekit_token import print_decode_jwt

    typer.run(print_decode_jwt)


def main_verify() -> None:
    from .livekit_token import print_verify_jwt

    typer.run(print_verify_jwt)
