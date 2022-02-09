import socket
import select
from typing import Collection

SOCKET_ERRORS = (ConnectionAbortedError, socket.gaierror, socket.error)


def read(socket_: socket.socket, buffer_size=1024):
    return socket_.recv(buffer_size)


def read_str(socket_: socket.socket, buffer_size=1024):
    return read(socket_, buffer_size).decode()


def get_readable_sockets(sockets_: Collection[socket.socket]):
    if not sockets_:
        return []
    else:
        return select.select(sockets_, [], [], 0.001)[0]


def get_writeable_sockets(sockets_: Collection[socket.socket]):
    if not sockets_:
        return []
    else:
        return select.select([], sockets_, [], 0.001)[1]


def send(socket_: socket.socket, bytes_: bytes):
    return socket_.sendall(bytes_ + bytes('|||', 'utf8'))


def send_str(socket_: socket.socket, data: str):
    return send(socket_, data.encode())
