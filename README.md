# python-web-server
Create a web-server in python with just built-in libraries to understand web-server implementation in python.

Q- What is a socket ?
A- Socket is a software construct for communication b/w two computers. 

Using raw socket in a server has lots of challanges:

1. Partial Reads/Writes - recv(1024) might return 100 or 300 byte or split a message mid-way
2. Manual Buffering - have to maintain your own buffers and manage stream parsing
3. Backpressure/Flow Control - If the other side is slow send() can block or drop data
4. Non-blocking setup - Must call sock.setblocking(False) use select or epoll manually
5. Clean Connection Lifecycle - Need to detect when peer closes and ensure cleanup
6. Concurrency/Threading - Threads or select() loops are required
7. Parsing Message Framing - You may receive part of a message or multiple messages in one chunk
