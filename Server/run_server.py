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


class PingManager:
    def __init__(self, room: "RoomThread"):
        self.room = room
        self.pending_pings = {}
        self.erroneous_clients = []

    def send_ping(self):
        import time
        for client in self.room.game_clients:
            if client.colour not in self.pending_pings:
                try:
                    socket_util.send_str(client.sockt_, json.dumps({'type': 'ping', 'args': ['typing?']}))
                    self.pending_pings[f'{client.colour}'] = (time.time(), client)
                except socket_util.SOCKET_ERRORS:
                    self.erroneous_clients.append(client)

    def receive_pong(self, colour):
        if colour in self.pending_pings:
            del self.pending_pings[colour]

    def check_pings(self):
        for colour, (time_point, client) in tuple(self.pending_pings.items()):
            if time.time() - time_point > 3:
                del self.pending_pings[colour]
                self.remove_stuff(client)
        for index in range(len(self.erroneous_clients) - 1, -1, -1):
            client2 = self.erroneous_clients[index]
            del self.erroneous_clients[index]
            self.remove_stuff(client2)

    def remove_stuff(self, client):
        for connection_ in socket_util.get_writeable_sockets(self.room.sockets):
            string = {
                'type': 'command',
                'command': 'leave',
                'args': [f'{client.colour}'],
            }
            try:
                socket_util.send_str(connection_, json.dumps(string))
            except BrokenPipeError:
                pass
        for index in range(len(self.room.game_clients) - 1, -1, -1):
            if client.colour == self.room.game_clients[index].colour:
                del self.room.game_clients[index]
                if client.colour in self.room.turn_order:
                    self.room.turn_order.remove(client.colour)
                if not self.room.turn_order:
                    self.room.game_over = True
                    return
                return


class ManagerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.rooms: dict[str, 'RoomThread'] = {}

    def get_or_create_room(self, room_id):
        return self.rooms[room_id] if room_id in self.rooms else self.create_room(room_id)

    def create_room(self, room_id):
        client = RoomThread()
        self.rooms[room_id] = client
        client.start()
        return client

    def run(self):
        import time
        while True:
            time.sleep(0.1)
            rooms = tuple(self.rooms.items())
            for key, value in rooms:
                if value.game_over:
                    del self.rooms[key]


neutral_colour = 'gray'


class RoomThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.game_clients: Deque[GameClient] = collections.deque()
        self.slot_width = None
        self.slot_height = None
        self.win_length = None
        self.wcenter = 0
        self.hcenter = 0
        self.current_turn = None
        self.first_join = False
        self.populated_slots = False
        self.turn_order = []
        self.slots = {}
        self._commands = {}
        self.started = False
        self.game_over = False
        self.ping_manager = PingManager(self)
        import inspect
        for item in self.__class__.__dict__.values():
            if inspect.isfunction(item):
                if hasattr(item, '_command_name'):
                    if item._command_name not in self._commands:
                        self._commands[item._command_name] = item.__get__(self)

    @property
    def sockets(self):
        return [x.sockt_ for x in self.game_clients if x.sockt_ is not None]

    def populate_slots(self):
        self.wcenter = int((self.slot_width - 1) / 2)
        self.hcenter = int((self.slot_height - 1) / 2)
        weven = True if not self.slot_width % 2 else False
        heven = True if not self.slot_height % 2 else False
        self.slots = {}
        self.slots = {
            (self.wcenter - num1, self.hcenter - num2): neutral_colour
            for num1 in range(- (1 if weven else 0), self.slot_width - (1 if weven else 0))
            for num2 in range(- (1 if heven else 0), self.slot_height - (1 if heven else 0))
        }
        print('')
        print(f'Slots = {self.slots}')
        print('')

    @_command('set_board')
    def cmd_set_board(self, data, socket_: s.socket, args):
        print(f'Args: {args}')
        self.slot_width, self.slot_height, self.win_length = args[0], args[1], args[2]
        print(f'Slot Width: {self.slot_width}, Slot Height: {self.slot_height}')
        if not self.populated_slots or args[3]:
            self.populate_slots()
            if not args[3]:
                self.populated_slots = True
        socket_util.send_str(socket_, json.dumps(data))
        for client in self.game_clients:
            socket_util.send_str(client.sockt_, json.dumps({'type': 'board_update', 'args': (self.slot_width, self.slot_height, self.win_length)}))

    @_command('start')
    def cmd_ready(self, data, socket_: s.socket, args):
        # TODO
        # do ready command
        # \/ being for if owner presses ready
        for client in self.game_clients:
            socket_util.send_str(client.sockt_, json.dumps({'type': 'start', 'args': []}))
        time.sleep(0.001)
        for client in self.game_clients:
            socket_util.send_str(client.sockt_, json.dumps({'type': 'set_turn', 'turn': self.current_turn}))
        self.started = True

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
                self.next_turn()
                for client in self.sockets:
                    socket_util.send_str(client, json.dumps({'type': 'drop_confirm', 'coords': drop_pos, 'drop_team': current_team, 'winner': winner, 'turn': self.current_turn}))
                if winner:
                    for client in self.sockets:
                        socket_util.send_str(client, json.dumps({'type': 'dc'}))
                    for client in self.sockets:
                        try:
                            client.close()
                        except Exception as e:
                            print(e)
                    self.game_over = True

    def next_turn(self):
        turn = False
        done_once = False
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
        name = args[0]
        colour = args[1]
        if not self.first_join:
            self.current_turn = colour
            self.first_join = True
        if self.started:
            error = {
                'error': 'GameStarted',
                'GameStarted': True
            }
            socket_util.send_str(socket_, json.dumps(error))
            return
        for client in self.game_clients:
            if client.colour == colour:
                error = {
                    'error': 'DupeCol',
                    'invalidCol': [client1.colour for client1 in self.game_clients]
                }
                socket_util.send_str(socket_, json.dumps(error))
                return
        self.turn_order.append(colour)
        self.game_client_from_socket(socket_).colour = colour
        print(args)
        for client in self.game_clients:
            socket_util.send_str(client.sockt_, json.dumps({'type': 'join', 'args': [name, colour, [self.slot_width, self.slot_height, self.win_length]]}))
        time.sleep(0.001)
        for client in self.game_clients:
            socket_util.send_str(client.sockt_, json.dumps({'type': 'set_owner', 'args': [self.current_turn]}))

    def game_client_from_socket(self, socket_: s.socket) -> Optional[GameClient]:
        for client in self.game_clients:
            if client.sockt_ is not None and socket_.fileno() == client.sockt_.fileno():
                return client
        return None

    @_command('pong')
    def cmd_pong(self, data, socket_: s.socket, args):
        self.ping_manager.receive_pong(args[0])

    def run(self):
        import json
        import time
        time_ = time.time()
        while not self.game_over:
            if self.sockets:
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
                if time.time() - time_ >= 5:
                    time_ = time.time()
                    self.ping_manager.send_ping()
                    self.ping_manager.check_pings()
            time.sleep(0.0001)
        print('closed for business!')

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


room_mngr = ManagerThread()
room_mngr.start()
while True:
    connection, address = socket.accept()
    import json

    raw = socket_util.read_str(connection).strip('|')
    print(raw)
    packet = json.loads(raw)
    room_id = packet['room_id']
    room_mngr.get_or_create_room(room_id).add_client(connection)
