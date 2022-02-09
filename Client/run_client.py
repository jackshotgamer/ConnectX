import socket as s
import socket_util
import json

socket = s.socket()
socket.connect(('127.0.0.1', 2819))
string = {

    'type': 'command',
    'command': 'join',
    'args': ['name'],
}
print('hi')
socket_util.send_str(socket, json.dumps(string))
print(socket_util.read_str(socket))
