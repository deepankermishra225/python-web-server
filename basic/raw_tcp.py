import socket
import time

def create(host, port):

    raw_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # specify that I want a tcp socket and want to use ipv4
    raw_tcp_socket.bind((host, port))
    raw_tcp_socket.listen(5) # set backlog as 5

    print("Server is ready!")
    try:
        while True:
            conn, address = raw_tcp_socket.accept()
            request = conn.recv(1024).decode()
            print("Recieved request\n", request)
            time.sleep(2)
            response = b"""HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello"""
            conn.sendall(response)
            conn.close()
    except KeyboardInterrupt:
        print("Shutting down server!")

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080

    create(host=host, port=port)