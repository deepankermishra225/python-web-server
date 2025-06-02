from typing import Generator
import asyncio
import signal
import sys
import logging
import contextlib
import threading
import click
from .server_state import ServerState
from .http_conn import HTTPConn
import time


HANDLED_SIGNALS = {
    signal.SIGINT: "SIGINT",
    signal.SIGTERM: "SIGTERM",
}
if sys.platform == "win32":
    HANDLED_SIGNALS[signal.SIGBREAK] = "SIGBREAK"


logger = logging.getLogger(__name__)

class Config:

    def __init__(
            self,
            host,
            port,
            ssl,
            backlog,
            timeout_graceful_shutdown
    ):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.backlog = backlog
        self.timeout_graceful_shutdown = timeout_graceful_shutdown


class Server:
    def __init__(self, config: Config):
        self.config = config
        self.server_state = ServerState()
        self.started = False
        self.should_exit = False
        self.force_exit = False
        self._captured_signals: list[int] = []
    
    def run(self) -> None:
        return asyncio.run(self.serve())
    
    async def serve(self) -> None:
        with self.capture_signals():
            await self._serve()

    async def _serve(self):
        logger.info("Starting server...")
        await self.startup()
        if self.should_exit:
            return
        await self.main_loop()
        await self.shutdown()
        logger.info("Server shutdown complete!")


    async def startup(self) -> None:
        try:
            loop = asyncio.get_running_loop()
            server = await loop.create_server(HTTPConn, 
                                              host=self.config.host,
                                              port=self.config.port,
                                              ssl=self.config.ssl,
                                              backlog=self.config.backlog
                                              )
            self._log_startup_message(server.sockets[0])

        except OSError as exc:
            logger.error(exc)
            sys.exit(1)

    def _log_startup_message(self, listener):
        addr_format = "%s://%s:%d"
        host = "0.0.0.0" if self.config.host is None else self.config.host
        if ":" in host:
            # It's an IPv6 address.
            addr_format = "%s://[%s]:%d"

        port = self.config.port
        if port==0:
            port = listener.getsockname()[1]

        protocol_name = "https" if self.config.ssl else "http"
        message = f"Uvicorn running on {addr_format} (Press CTRL+C to quit)"
        color_message = "Uvicorn running on " + click.style(addr_format, bold=True) + " (Press CTRL+C to quit)"
        logger.info(
            message,
            protocol_name,
            host,
            port,
            extra={"color_message": color_message},
        )


    async def main_loop(self) -> None:
        """
        instead of using 
        async with server:
            await server.serve_forever()
        we use a custom loop to allow for graceful shutdown and signal handling.
        """
        while not self.should_exit:
            """
            While main_loop is paused, the asyncio event loop is free to do other work. This includes:
            Accepting new client connections.
            Processing data on existing connections (running Uvicorn's H11Protocol or HttpToolsProtocol instances).
            Handling background tasks.
            Responding to signals (like SIGINT or SIGTERM which would then set self.should_exit = True via the handle_exit method).
            """
            await asyncio.sleep(0.1)
        
    

    async def shutdown(self)-> None:
        ...

    # signal handling
    @contextlib.contextmanager
    def capture_signals(self) -> Generator[None, None, None]:
        """
        Signals can only be listened to from the main thread
        """
        if threading.current_thread() is not threading.main_thread():
            yield
            return
        original_handlers = {sig: signal.signal(sig, self.handle_exit) for sig in HANDLED_SIGNALS.keys()}
        try:
            yield
        finally:
            # Restore original signal handlers
            for sig, handler in original_handlers.items():
                signal.signal(sig, handler)
            # Raise captured signals in reverse order to ensure proper handling
            for captured_signal in reversed(self._captured_signals):
                signal.raise_signal(captured_signal)

    def handle_exit(self, sig: int, frame: signal.FrameType | None) -> None:
        self._captured_signals.append(sig)
        if self.should_exit and sig==signal.SIGINT:
            self.force_exit = True
        else:
            self.should_exit = True