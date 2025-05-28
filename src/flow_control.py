"""
This class implements flow control for an asyncio transport, allowing for pausing and resuming reading and writing operations.
# It uses asyncio.Event to manage the state of writing operations, ensuring that writes can be paused and resumed as needed.
We need asyncio.Event to manage the state of writing operations, allowing us to pause and resume writes.
Read rate is dependent on the asgi application's ability to process incoming data, while write rate is controlled by the
internal state of the Transport class. 
"""


import asyncio


class FlowControl:

    def __init__(self, transport: asyncio):
        self._read_paused = False
        self._write_paused = False
        self._write_event: asyncio.Event = asyncio.Event()
        self._write_event.set() # Set the event to allow writing initially
        self._transport = transport

    async def drain(self):
        await self._write_event.wait()  # Wait until the write event is set

    def pause_reading(self):
        if not self._read_paused:
            self._read_paused = True
            self._transport.pause_reading()

    def resume_reading(self):
        if self._read_paused:
            self._read_paused = False
            self._transport.resume_reading()

    def pause_writing(self):
        if not self._write_paused:
            self._write_paused = True
            self._write_event.clear()

    def resume_writing(self):
        if self._write_paused:
            self._write_paused = False
            self._write_event.set()

