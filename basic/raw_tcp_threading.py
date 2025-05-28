import socket
import time
from concurrent.futures import ThreadPoolExecutor



def handle_connect(conn):
    request = conn.recv(1024).decode()
    print("Recieved request\n", request)
    time.sleep(2)
    response = b"""HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello"""
    conn.sendall(response)
    conn.close()


def create(host, port):

    raw_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # specify that I want a tcp socket and want to use ipv4
    raw_tcp_socket.bind((host, port))
    raw_tcp_socket.listen(10) # set backlog as 5

    executor = ThreadPoolExecutor(max_workers=50)

    print("Server is ready!")
    try:
        while True:
            conn, address = raw_tcp_socket.accept()
            executor.submit(handle_connect, conn)
    except KeyboardInterrupt:
        print("Shutting down server!")

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080

    create(host=host, port=port)