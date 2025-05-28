"""
A TCP echo server is a basic network program that:

Listens for incoming TCP connections.

When a client sends a message, it sends the exact same message back.

An echo client:

Connects to the server.

Sends a message.

Waits for the same message to be echoed back.

This setup is often used to test or demonstrate basic networking behavior.

TCP - Transmission Control Protocol - a layer 4 protocol of the OSI model that ensures reliable, ordered and error-checked delivery
of data b/w programs

asyncio.Transport - The Wire
This represents the connection. (e.g. a TCP socket)
Handles the sending and receiving of bytes, connection state, etc.

asyncio.Protocol: Your logic to define what to do when the data arrives when the connection is made. Subclass
it do define your own protocol behaviour.

Together - Transport provides the i/o and protocol defines how to respond to it.
"""

import asyncio

class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        print(f"Connected to {peername}")

    def data_received(self, data):
        message = data.decode()
        print(f"Received: {message}")
        self.transport.write(data)  # Echo it back

    def connection_lost(self, exc):
        print("Client disconnected")

async def main():
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: EchoServerProtocol(),  # Factory
        '127.0.0.1', 8888
    )

    print("Serving on port 8888")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
