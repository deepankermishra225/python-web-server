"""
asyncio provides a higher level StreamReader/StreamWriter API for working with streams, which is often more convenient than using Protocol and Transport directly.
However, since asyncio.Protocol and Transport provide more control over the connection and data flow, they are often used in more complex scenarios where you need to manage the connection state or implement custom protocols.

When using asyncio.Protocol, requried methods include:
- connection_made(transport): Called when a connection is made. The transport object represents the connection.
- data_received(data): Called when data is received. The data parameter contains the bytes received.
- connection_list(exc): Called when the connection is closed or list exc is an Exception or (None).
- [OPTIONAL]connection_lost(exc): Called when the connection is lost. The exc parameter contains the exception if the connection was closed with an error.
- eof_recieved(): Called when the end of the file (EOF) is received. This is typically used to handle the end of a stream.
- pause_writing(): Called when the transport's buffer goes over a high water mark
- resume_writing(): Called when the transport's buffer goes below a low water mark
"""
import logging
import asyncio
import http
from typing import Literal
from ._types import ASGIVersions, HTTPScope
from .flow_control import FlowControl
from .server_state import SeverState
from .config import Config
import h11
from .util import get_local_addr, get_remote_addr, is_ssl

logger = logging.getLogger(__name__)

def _get_status_phrase(status_code: int) -> bytes:
    try:
        return http.HTTPStatus(status_code).phrase.encode()
    except ValueError:
        return b""

STATUS_PHRASES = {status_code: _get_status_phrase(status_code) for status_code in range(100, 600)}

class RequestResponseCycle:

    def __init__(self,
                 scope: HTTPScope,
                 conn: h11.Connection,
                 transport: asyncio.Transport,
                 flow: FlowControl,
                 message_event: asyncio.Event):
        self.scope = scope
        self.conn = conn
        self.transport = transport
        self.flow = flow
        self.message_event = message_event
        self.response_complete = False
        self.disconnected = False


class HTTPConn(asyncio.Protocol):

    def __init__(self, 
                 config: Config,
                 server_state: SeverState,
                 loop: asyncio.AbstractEventLoop | None = None):
        self.loop = loop or asyncio.get_event_loop()
        self.config = config
        self.conn = h11.Connection(h11.SERVER)

        # Per-connection state
        self.transport: asyncio.Transport | None = None
        self.flow_control: FlowControl| None = None
        self.client: tuple[str, int] | None = None
        self.server: tuple[str, int] | None = None
        self.scheme = Literal["http", "https"] | None = None

        # Shared server state
        self.server_state = server_state
        self.connections = server_state.connections
        self.tasks = server_state.tasks
        
        self.cycle: RequestResponseCycle | None = None

    def connection_made(self, transport: asyncio.Transport):
        self.connections.append(self)
        self.transport = transport
        self.flow_control = FlowControl(transport)
        self.client = get_remote_addr(transport)
        self.server = get_local_addr(transport)
        self.scheme = "https" if is_ssl(transport) else "http"

    def connection_lost(self, exc: Exception | None = None) -> None:
        """
        This method is called when:
        1. peer closes connection (gracefully), or when the server closes connection (gracefully)
        2. network error / abrupt disconnect.


        Completing an HTTP Request does not necessarily call connection_lost (depends if connection is keep-alive or close).
        """
        self.connections.discard(self)

        if self.cycle and not self.cycle.response_complete:
            self.cycle.disconnected = True
        if self.conn.our_state != h11.ERROR:
            event = h11.ConnectionClosed()
            try:
                self.conn.send(event)
            except h11.LocalProtocolError:
                pass
        if self.cycle:
            self.cycle.message_event.set()
        if self.flow is not None:
            self.flow.resume_writing()  # avoid deadlock or 'stalled' tasks.

        """
        when exception occurs, the underlying transport is already considerd broken or closed by the asyncio event loop
        """
        if exc is None: # graceful shutdown when client closes connection or server closes connection by calling transport.close()
            self.transport.close()  # idempotent call

    def eof_received(self):
        return None

    def data_received(self, data: bytes):
        logger.debug(f"Data received: {data.decode()}")
        self.conn.receive_data(data)
        self.handle_events()
        

    def handle_events(self):
        while True:
            try:
                event = self.conn.next_event()
            except h11.RemoteProtocolError:
                msg = "Invalid HTTP request recieved"
                logger.error(msg)
                self.send_400_response(msg)

            if event is h11.NEED_DATA:
                return
            
            if isinstance(event, h11.PAUSED):
                """
                Ocurrs during HTTP pipeling -> multiple requests back-to-back on the same TCP connection without waiting for previous response. Server, however is 
                expected to reply in the same order as requests were received.
                E.g. - Server receives GET /foo and starts responding. The second request GET /bar has already arrived and is buffered.
                But the server must not start processing GET /bar until it finishes responding to GET /foo
                """
                self.flow.pause_reading()
                return
            
            if isinstance(event, h11.Data):
                if self.conn.our_state is h11.DONE:
                    continue

            if isinstance(event, h11.EndOfMessage):
                if self.conn.our_state is h11.DONE:
                    self.transport.resume_reading()
                    self.conn.start_next_cycle()
                    continue
                self.cycle.more_body = False
                self.cycle.message_event.set()
                if self.conn.their_state == h11.MUST_CLOSE:
                    break

    
    def send_400_response(self, msg: str):
        reason = STATUS_PHRASES[400]
        headers = [
            (b"content-type", b"text/plain; charset=utf-8"),
            (b"connection", "close"),
        ]
        event = h11.Response(status_code=400, headers=headers, reason=reason)
        output = self.conn.send(event)
        self.transport.write(output)

        output = self.conn.send(event=h11.Data(data=msg.encode("ascii")))
        self.transport.write(output)

        output = self.conn.send(event=h11.EndOfMessage())
        self.transport.write(output)

        self.transport.close()


async def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: HTTPConn(), 
        host='127.0.0.1',
        port=8081
    )
    logger.info("Server is ready!")
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
