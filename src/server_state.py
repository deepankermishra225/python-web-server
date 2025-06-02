from typing import TYPE_CHECKING
import asyncio
if TYPE_CHECKING:
    from .http_conn import HTTPConn

class ServerState:
    """
    Shared servers state that is available b/w all protocol instances (from uvicorn)
    """
    def __init__(self):
        self.total_requests = 0
        self.connections: set[HTTPConn] = set()
        self.tasks: set[asyncio.Task[None]] = set()
        self.default_headers = list[tuple[bytes, bytes]] = []