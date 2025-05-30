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
from .flow_control import FlowControl

logger = logging.getLogger(__name__)

class Server(asyncio.Protocol):

    def __init__(self):
        self.transport: asyncio.Transport | None = None
        self.flow_control = None

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        self.flow_control = FlowControl(transport)
        logger.debug(f"Connection made with {transport.get_extra_info('peername')}")

        transport.set_write_buffer_limits(
            high=transport.get_write_buffer_limits()[1],
            low=transport.get_write_buffer_limits()[0]
        )

    def data_recieved(self, data: bytes):
        logger.debug(f"Data received: {data.decode()}")
        self.flow_control.drain()
        # Echo the data back to the client
        if self.transport:
            self.transport.write(data)
            logger.debug(f"Data sent: {data.decode()}")

    def pause_writing(self):
        """
        Called by transport when the write buffer exceeds the high water mark
        """
        logger.debug("Pausing reading")
        if self.flow_control:
            self.flow_control.pause_writing()

    def resume_writing(self):
        """
        Called by the transport when the write buffer falls below the low water mark
        """
        logger.debug("Resuming reading")
        if self.flow_control:
            self.flow_control.resume_writing()


async def main():
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: Server(),
        host='127.0.0.1',
        port=8081
    )
    logger.info("Server is ready!")
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
