from typing import TYPE_CHECKING
import asyncio
if TYPE_CHECKING:
    from .http_conn import HTTPConn

class ServerState:
    """
    Shared servers state that is available b/w all protocol instances (from uvicorn)
    """
    def __init__(self):
        """
        Each H11Protocol instance represents a single client connection and is responsible for parsing incoming HTTP requests, sending responses, and managing the state of 
        that specific connection.
        """
        self.connections: set[HTTPConn] = set()
        """
        These are background asyncio.Task objects that Uvicorn itself creates and manages.
        A primary example is the task that is created for each incoming HTTP request to handle the ASGI application's response. When a new HTTP request comes in, Uvicorn creates 
        an asyncio.Task to run your ASGI application (e.g., a FastAPI endpoint) and process the response. This task is added to self.server_state.tasks.
        """
        self.tasks: set[asyncio.Task[None]] = set()