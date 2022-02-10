import socket as s
from dataclasses import dataclass
from typing import Deque, NamedTuple, Optional

import socket_util
import threading
import collections
import time

socket = s.socket(s.AF_INET, s.SOCK_STREAM)
socket.bind(('0.0.0.0', 10049))
socket.listen(6)
ERROR_broad_scope = 1
ERROR_missing_obj = 2
ERROR_invalid_obj = 3
ERROR_invalid_json = 4

"""
. . . . .
. . - Y .
. . Y R .
. Y Y R .
# Y R R R
"""


def _command(name='', func=None):
    import functools
    if func is None:
        return functools.partial(_command, name)
    else:
        func._command_name = name
    return func


@dataclass
class GameClient:
    sockt_: s.socket
    colour: str


"""
INPUT NAME
JOIN
WAIT   <---------------┓
ON READY               |
CHECK IF ALL ARE READY-┫
                       ↓
SEND OUT SIGNAL TO START TO ALL
STARTING TURN
RECEIVE INPUT <-----------┓
UPDATE ALL INTERFACES     |
WIN CHECK---┳-----┓       |
WIN <-------┛     |       |
CHANGE TURN <-----┛       |
        ┗-----------------┛
"""
neutral_colour = 'gray'


class ClientThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.game_clients: Deque[GameClient] = collections.deque()
        self.running = False
        self.slot_width = 7
        self.slot_height = 6
        self.win_length = 4
        self.wcenter = int((self.slot_width - 1) / 2)
        self.hcenter = int((self.slot_height - 1) / 2)
        weven = True if not self.slot_width % 2 else False
        heven = True if not self.slot_height % 2 else False
        self.current_turn = None
        self.first_join = False
        self.turn_order = []
        self.slots = {
            (self.wcenter - num1, self.hcenter - num2): neutral_colour
            for num1 in range(- (1 if weven else 0), self.slot_width - (1 if weven else 0))
            for num2 in range(- (1 if heven else 0), self.slot_height - (1 if heven else 0))
        }
        self._commands = {}
        import inspect
        for item in self.__class__.__dict__.values():
            if inspect.isfunction(item):
                if hasattr(item, '_command_name'):
                    if item._command_name not in self._commands:
                        self._commands[item._command_name] = item.__get__(self)

    @property
    def sockets(self):
        return [x.sockt_ for x in self.game_clients if x.sockt_ is not None]

    @_command('drop')
    def cmd_drop(self, data, socket_: s.socket, args):
        import json
        if tuple(args[0]) in self.slots:
            drop_pos = args[0]
            current_team = args[1]
            if current_team == self.current_turn:
                self.slots[(drop_pos[0], drop_pos[1])] = current_team
                from Win_Checker import win_check
                winner = win_check(self.slots, drop_pos[0], drop_pos[1], self.win_length)
                for client in self.sockets:
                    socket_util.send_str(client, json.dumps({'type': 'drop_confirm', 'coords': drop_pos, 'drop_team': current_team, 'winner': winner}))
                turn = False
                done_once = False
                print(self.current_turn)

                for c in self.turn_order:
                    if turn:
                        self.turn_order.remove(self.current_turn)
                        self.turn_order.append(self.current_turn)
                        self.current_turn = c
                        turn = False
                        done_once = True
                    if self.current_turn == c and not done_once:
                        turn = True

    @_command('join')
    def cmd_join(self, data, socket_: s.socket, args):
        import json
        colour = args[1]
        if not self.first_join:
            self.current_turn = colour
            self.first_join = True
        self.turn_order.append(colour)
        self.slot_width, self.slot_height = args[2]
        self.win_length = args[3]
        """
        current:red
        
        [client:red client:orange] <- 0, 1, 0, 1
        """
        for client in self.game_clients:
            if client.colour == colour:
                error = {
                    'error': 'DupeCol',
                    'invalidCol': [client1.colour for client1 in self.game_clients]
                }
                socket_util.send_str(socket_, json.dumps(error))
                return
        self.game_client_from_socket(socket_).colour = colour
        print(args)
        socket_util.send_str(socket_, json.dumps(data))

    def game_client_from_socket(self, socket_: s.socket) -> Optional[GameClient]:
        for client in self.game_clients:
            if client.sockt_ is not None and socket_.fileno() == client.sockt_.fileno():
                return client
        return None

    def run(self):
        self.running = True
        import json
        while self.running:
            if self.sockets:
                # for connection_ in socket_util.get_writeable_sockets(self.sockets):
                #     socket_util.send(connection_, (b"This connection is sponsored by NordVPN. "
                #                                    b"Staying safe online is an ever growing difficulty and you could be exploited by hackers. "
                #                                    b"NordVPN allows you to change your IP address, making you harder to track, securing your privacy. "
                #                                    b"Check out the link in the connection to get 20% off for the first two months and thank you to NordVPN for sponsoring this connection. "
                #                                    b"link: www.totallynotafakeaddress.com"))
                #     connection_.close()
                #     self.sockets.remove(connection_)
                for connection_ in socket_util.get_readable_sockets(self.sockets):
                    try:
                        strings = self.parse_json(connection_)
                        for data in strings:
                            if data is not None:
                                if (response := self.handle_command(data, connection_)) is not None:
                                    socket_util.send_str(connection_, json.dumps(response))
                            else:
                                socket_util.send_str(connection_, json.dumps((ERROR_invalid_json, 'Error: Not JSON')))
                    except socket_util.SOCKET_ERRORS:
                        connection_.close()
                        self.game_clients.remove(self.game_client_from_socket(connection_))
            time.sleep(0.0001)

    def handle_command(self, data, socket_):
        print(data)
        if 'type' in data:
            type_ = data['type'].lower()
            if type_ == 'command':
                if 'command' not in data:
                    return ERROR_missing_obj, 'Error: No command'

                command = data['command'].lower()
                if 'args' not in data:
                    return ERROR_missing_obj, 'Error: No args'

                args = data['args']
                if command not in self._commands:
                    return ERROR_invalid_obj, 'Error: Invalid command'
                command = self._commands[command]
                command(data, socket_, args)

    def add_client(self, socket_: s.socket):
        self.game_clients.append(GameClient(socket_, ''))

    @staticmethod
    def parse_json(socket_: s.socket):
        import json
        for packet in socket_util.read_str(socket_).split('|||'):
            try:
                yield json.loads(packet)
            except json.JSONDecodeError:
                pass


thread = ClientThread()
thread.start()
while True:
    connection, address = socket.accept()
    thread.add_client(connection)
