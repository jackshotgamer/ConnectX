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
        self.is_owner = True
        self.players = {}
        self.ready_players = set()
        self.everyone_ready = True
        self.name = name
        self.colour = colour
        self.width_text = arcade.Text('', 0, 0, anchor_x='center', anchor_y='center')
        self.height_text = arcade.Text('', 0, 0, anchor_x='center', anchor_y='center')
        self.win_length_text = arcade.Text('', 0, 0, anchor_x='center', anchor_y='center')
        self.button_manager.append_button('Ready', 'Ready', lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y - 200), Vector.Vector(100, 50), on_click=self.ready_button)
        self.button_manager.append_input('input_x', 'Width:', lambda: Vector.Vector(State.state.screen_center.x - 56, State.state.screen_center.y + 152 + 50), Vector.Vector(110, 50),
                                         text_length=2, visible=False)
        self.button_manager.append_input('input_y', 'Height:', lambda: Vector.Vector(State.state.screen_center.x + 56, State.state.screen_center.y + 152 + 50), Vector.Vector(110, 50),
                                         text_length=2, visible=False)
        self.button_manager.append_input('win_length', 'Win Length:', lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y + 203 + 50), Vector.Vector(200, 50),
                                         text_length=2, visible=False)
        self.button_manager.append_button('confirm', 'Confirm', lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y + 101 + 50), Vector.Vector(200, 50),
                                          on_click=self.confirm_button, visible=False)

    def on_draw(self):
        super().on_draw()
        self.width_text.draw()
        self.height_text.draw()
        self.win_length_text.draw()

    def confirm_button(self):
        import json
        string = {
            'type': 'command',
            'command': 'set_board',
            'args': self.get_board_info()
        }
        socket_util.send_str(self.socket, json.dumps(string))

    socket_interval = 1 / 16
    elapsed_delta = 0

    def get_board_info(self):
        if self.width_text.value:
            input_x = self.width_text.value
        else:
            input_x = self.button_manager.inputs['input_x'].text.value

        if self.height_text.value:
            input_y = self.height_text.value
        else:
            input_y = self.button_manager.inputs['input_y'].text.value

        if self.win_length_text.value:
            win_length = self.win_length_text.value
        else:
            win_length = self.button_manager.inputs['win_length'].text.value

        input_x = int(input_x) if input_x and input_x.isdigit() else 7
        input_y = int(input_y) if input_y and input_y.isdigit() else 6
        win_length = int(win_length) if win_length and win_length.isdigit() else 4
        return input_x, input_y, win_length

    def ready_button(self):
        board_info = self.get_board_info()
        if self.everyone_ready:
            State.state.window.show_view(Game_View.GameView(board_info[0], board_info[1], board_info[2], self.name, self.colour, self.socket))

    def owner_update(self):
        if self.is_owner:
            self.button_manager.apply_state('input_x', self.button_manager.action_visible, force=True)
            self.button_manager.apply_state('input_y', self.button_manager.action_visible, force=True)
            self.button_manager.apply_state('win_length', self.button_manager.action_visible, force=True)
            self.button_manager.apply_state('confirm', self.button_manager.action_visible, force=True)
            self.width_text = arcade.Text('', 0, 0, anchor_x='center', anchor_y='center')
            self.height_text = arcade.Text('', 0, 0, anchor_x='center', anchor_y='center')
            self.win_length_text = arcade.Text('', 0, 0, anchor_x='center', anchor_y='center')
        else:
            self.width_text = arcade.Text(f'Width: {self.button_manager.buttons["input_x"].text.value if self.button_manager.buttons["input_x"].text.value else "7"}',
                                          State.state.screen_center.x - 56, State.state.screen_center.y + 152 + 50, anchor_x='center', anchor_y='center')
            self.height_text = arcade.Text(f'Height: {self.button_manager.buttons["input_y"].text.value if self.button_manager.buttons["input_y"].text.value else "6"}',
                                           State.state.screen_center.x + 56, State.state.screen_center.y + 152 + 50, anchor_x='center', anchor_y='center')
            self.win_length_text = arcade.Text(f'Win Length: {self.button_manager.buttons["win_length"].text.value if self.button_manager.buttons["win_length"].text.value else "4"}',
                                               State.state.screen_center.x, State.state.screen_center.y + 203 + 50, anchor_x='center', anchor_y='center')
            self.button_manager.apply_state('input_x', self.button_manager.action_visible, force=False)
            self.button_manager.apply_state('input_y', self.button_manager.action_visible, force=False)
            self.button_manager.apply_state('win_length', self.button_manager.action_visible, force=False)
            self.button_manager.apply_state('confirm', self.button_manager.action_visible, force=False)

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
                    if alert['type'] == 'board_update':
                        self.width_text.value = str(alert['args'][0])
                        self.height_text.value = str(alert['args'][1])
                        self.win_length_text.value = str(alert['args'][2])
                    self.owner_update()
            self.elapsed_delta = 0
