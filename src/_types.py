from typing import TypedDict, Literal, Iterable


class ASGIVersions(TypedDict):
    spec_version: str
    version: Literal["2.0"] | Literal["3.0"]

class HTTPScope(TypedDict):
    type: Literal["http"]
    http_version: str
    method: str
    scheme: str
    path: str
    raw_path: bytes
    query_string: bytes
    root_path: str
    headers: Iterable[tuple[bytes, bytes]]
    client: tuple[str, int] | None
    server: tuple[str, int | None] | None