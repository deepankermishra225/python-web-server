# python-web-server

A minimal web server built in Python using **only built-in libraries** (and the pure-Python `h11` library) to understand how HTTP works at a low level.

---

## What is a Socket?

A **socket** is a software construct that enables **communication between two computers** over a network. It is the basis for most network communication.

---

## Challenges of Using Raw Sockets in Servers

Implementing a server with raw sockets requires handling many complex issues manually:

1. **Partial Reads/Writes**  
   `recv(1024)` might return only part of a message (e.g., 100 bytes or a fragmented message).
2. **Manual Buffering**  
   You must manage your own buffers and parse streams yourself.
3. **Backpressure / Flow Control**  
   If the receiver is slow, `send()` may block or drop data.
4. **Non-blocking Setup**  
   Requires calling `sock.setblocking(False)` and using `select()` or `epoll()` manually.
5. **Clean Connection Lifecycle**  
   You must detect when the peer closes and clean up resources.
6. **Concurrency / Threading**  
   Requires threads or event loops like `select()` to handle multiple clients.
7. **Parsing / Message Framing**  
   Messages may arrive split across multiple packets or several messages may come in a single chunk.

---

## Why Use `h11`?

This project uses [`h11`](https://github.com/python-hyper/h11), a pure-Python implementation of the HTTP/1.1 protocol.

###  Benefits of `h11`:

- `h11` is a **synchronous state machine**.
- You feed it raw bytes and it returns high-level HTTP events like `Request`, `Data`, or `Response`.
- It **does not touch the network**—you are in full control of reading from or writing to sockets.
- This separation makes it easier to reason about and debug high-level HTTP logic.

> **Note:** `h11` is written in pure Python and might be **slower** than C-based libraries like `httpcore`.

---

##  Goal

This project is designed for **educational purposes**—to explore the **internals of HTTP/1.1 servers**, **socket programming**, and **manual protocol parsing** in Python.

---
