from __future__ import annotations
import calendar
import dataclasses
import datetime
from typing import Optional, Any
from pytimeparse2 import parse as timeparse  # type: ignore[import]

import jwt

DEFAULT_TOKEN_TTL = datetime.timedelta(hours=6)


@dataclasses.dataclass
class VideoGrant:
    room_create: Optional[bool] = None
    room_join: Optional[bool] = None
    room_list: Optional[bool] = None
    room_record: Optional[bool] = None
    room_admin: Optional[bool] = None
    room: Optional[str] = None
    can_publish: Optional[bool] = None
    can_subscribe: Optional[bool] = None
    can_publish_data: Optional[bool] = None
    hidden: Optional[bool] = None


@dataclasses.dataclass
class AccessToken:
    api_key: str
    api_secret: str
    grant: VideoGrant = dataclasses.field(default_factory=VideoGrant)
    identity: Optional[str] = None
    name: Optional[str] = None
    ttl: datetime.timedelta = DEFAULT_TOKEN_TTL
    metadata: Optional[str] = None

    def __post_init__(self) -> None:
        if self.grant.room_join and self.identity is None:
            raise ValueError("identity is required for room_join grant")
        if self.ttl.total_seconds() <= 0:
            raise ValueError("AccessToken must expire in the future.")

    def to_jwt(self) -> str:
        payload = {
            "video": dataclasses.asdict(
                self.grant, dict_factory=self.camel_case_dict
            ),
            "iss": self.api_key,
            "nbf": calendar.timegm(datetime.datetime.utcnow().utctimetuple()),
            "exp": calendar.timegm(
                (datetime.datetime.utcnow() + self.ttl).utctimetuple()
            ),
        }
        if self.metadata is not None:
            payload["metadata"] = self.metadata
        if self.identity is not None:
            payload["sub"] = self.identity
        if self.name:
            payload["name"] = self.name
        return jwt.encode(payload, self.api_secret)

    @staticmethod
    def camel_case_dict(data: list[tuple[str, Any]]) -> dict[str, Any]:
        """
        Return dictionary with keys converted from snake_case to camelCase

        Example:
            dataclasses.asdict(my_data, dict_factory=camel_case_dict)
        """
        return {  # type: ignore[misc]
            "".join(
                word if i == 0 else word.title() for i, word in enumerate(key.split("_"))  # type: ignore[has-type]
            ): value  # type: ignore[has-type]
            for key, value in data
            if value is not None  # type: ignore[has-type]
        }


def print_access_token(
        room_name: str,
        api_key: str = "dev",
        api_secret: str = "devsecret",
        identity: str = "",
        name: str | None = None,
        ttl: str = "6h",
) -> None:
    print(create_access_token(room_name=room_name, api_key=api_key, api_secret=api_secret, identity=identity, name=name, ttl=ttl))


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

    grant = VideoGrant(room_join=True, room=room_name)
    token = AccessToken(api_key, api_secret, grant=grant, identity=identity, name=name, ttl=ttl)
    r: str = token.to_jwt()
    return r
