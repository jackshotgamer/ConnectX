import sys
import arcade
from arcade import gui
from Client import Sprites_, State, Game_View, Event_Base, Buttons
import Vector
import itertools
import socket as s
import socket_util
import numpy as np
import dataclasses


class LobbyView(Event_Base.EventBase):
    def __init__(self, room_id, socket, name, colour):
        super().__init__()
        self.room_id = room_id
        self.socket = socket
        self.is_owner = False
        self.players = {}
        self.ready_players = set()
        self.everyone_ready = False
        self.name = name
        self.colour = colour
        self.button_manager.append_button('Ready', 'Ready', lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y - 200), Vector.Vector(100, 50), on_click=self.ready_button())

    def on_draw(self):
        super().on_draw()

    socket_interval = 1 / 16
    elapsed_delta = 0

    def ready_button(self):
        State.state.window.show_view(Game_View.GameView(7, 6, 4, self.name, self.colour, self.socket))

    def on_update(self, delta_time: float):
        super().update(delta_time)
        self.elapsed_delta += delta_time
        if self.elapsed_delta > self.socket_interval:
            if socket_alerts := socket_util.get_readable_sockets([self.socket]):
                import json
                raw = socket_util.read_str(socket_alerts[0])
                for alert1 in raw.split('|||'):
                    if not alert1.strip():
                        continue
                    alert = json.loads(alert1)
                    if alert['type'] == 'ready':
                        pass
                    if alert['type'] == 'start':
                        pass
                    if alert['type'] == 'join':
                        pass
                    if alert['type'] == 'leave':
                        pass
            self.elapsed_delta = 0
