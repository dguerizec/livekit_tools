from __future__ import annotations

import base64
import calendar
import dataclasses
import datetime
import json
from typing import Any, Optional

import jwt
from livekit import api
from pytimeparse2 import parse as timeparse  # type: ignore[import]

DEFAULT_TOKEN_TTL = datetime.timedelta(hours=6)


def print_access_token(
    room_name: str,
    api_key: str = "dev",
    api_secret: str = "devsecret",
    identity: str = "",
    name: str | None = None,
    ttl: str = "6h",
) -> None:
    token = create_access_token(
        room_name=room_name, api_key=api_key, api_secret=api_secret, identity=identity, name=name, ttl=ttl
    )
    print(f"Access token for room {room_name}: {token}")


def create_access_token(
    room_name: str,
    api_key: str = "dev",
    api_secret: str = "devsecret",
    identity: str = "",
    name: str | None = None,
    ttl: datetime.timedelta | str = datetime.timedelta(hours=6),
) -> str:
    if isinstance(ttl, str):
        ttl = datetime.timedelta(seconds=timeparse(ttl))

    grant = api.VideoGrants(
        room_create=True,
        room_join=True,
        room_list=False,
        room_record=False,
        room_admin=False,
        can_update_own_metadata=True,
        can_publish=True,
        can_publish_sources=[],
        can_subscribe=True,
        can_publish_data=True,
        room=room_name,
    )
    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_name(name or "")
        .with_ttl(ttl)
        .with_grants(grant)
    )
    r: str = token.to_jwt()
    return r




def decode_jwt(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid token")

    header = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
    payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))

    return {"header": header, "payload": payload}


def verify_jwt(token: str, api_secret: str) -> tuple[bool, str]:
    try:
        # Décodage et vérification du token
        payload = jwt.decode(token, api_secret, algorithms=["HS256"])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token expired"
    except jwt.InvalidSignatureError:
        return False, "Invalid token signature"
    except jwt.DecodeError:
        return False, "Invalid token"
    except Exception as e:
        return False, f"Error: {e}"


def print_decode_jwt(token: str) -> None:
    if "token=" in token:
        token = token.split("token=")[-1]
        token = token.split("&")[0]
        print(f"Token: {token}")
    decoded = decode_jwt(token)
    print(json.dumps(decoded, indent=2))


def print_verify_jwt(token: str, api_secret: str) -> None:
    verified, payload = verify_jwt(token, api_secret)
    print(f"Token verified: {verified}")
    if not verified:
        print(f"Error: {payload}")
    print(json.dumps(payload, indent=2))
