from typing import TYPE_CHECKING, Generator
import asyncio
import signal
import sys
import logging
import contextlib
import threading

if TYPE_CHECKING:
    from .http_conn import HTTPConn


HANDLED_SIGNALS = {
    signal.SIGINT: "SIGINT",
    signal.SIGTERM: "SIGTERM",
}
if sys.platform == "win32":
    HANDLED_SIGNALS[signal.SIGBREAK] = "SIGBREAK"


logger = logging.getLogger(__name__)

class ServerState:
    """
    Shared servers state that is available b/w all protocol instances (from uvicorn)
    """
    def __init__(self):
        self.total_requests = 0
        self.connections: set[HTTPConn] = set()
        self.tasks: set[asyncio.Task[None]] = set()
        self.default_headers = list[tuple[bytes, bytes]] = []



class Server:
    def __init__(self):
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