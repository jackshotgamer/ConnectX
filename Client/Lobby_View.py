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
        self.everyone_ready = True
        self.name = name
        self.colour = colour
        self.width = None
        self.height = None
        self.win_length = None
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
        self.button_manager.append_button('set_owner', 'Toggle Owner', lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y + 50 + 50), Vector.Vector(200, 50),
                                          on_click=self.toggle_owner, visible=True)
        self.owner_update()

    def on_draw(self):
        super().on_draw()
        self.width_text.draw()
        self.height_text.draw()
        self.win_length_text.draw()

    def toggle_owner(self):
        self.is_owner = not self.is_owner
        self.owner_update()

    def confirm_button(self):
        import json
        self.set_board_info()
        print(f'A: {self.width, self.height, self.win_length}')
        string = {
            'type': 'command',
            'command': 'set_board',
            'args': (self.width, self.height, self.win_length)
        }
        socket_util.send_str(self.socket, json.dumps(string))

    socket_interval = 1 / 16
    elapsed_delta = 0

    def set_board_info(self):
        # self.owner_update()
        print(f'Stuff2: {self.width, self.height, self.win_length}')

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
        print(f'Things: {input_x, input_y, win_length}')
        try:
            input_x = int(input_x) if input_x else 7
            input_y = int(input_y) if input_y else 6
            win_length = int(win_length) if win_length else 4
        except ValueError:
            input_x = 7
            input_y = 6
            win_length = 4
        board_info2 = [self.width, self.height, self.win_length]
        board_info1 = [input_x, input_y, win_length]
        print(f'Board info1: {board_info1}')

        for index, item in enumerate(zip(board_info1, board_info2)):
            if not item[0]:
                if item[1]:
                    board_info1[index] = item[1]
                else:
                    if index == 0:
                        board_info1[index] = 7
                    elif index == 1:
                        board_info1[index] = 6
                    else:
                        board_info1[index] = 4
        self.width = board_info1[0]
        self.height = board_info1[1]
        self.win_length = board_info1[2]
        print(f'Board info2: {board_info1}')

    def ready_button(self):
        if self.everyone_ready:
            self.set_board_info()
            State.state.window.show_view(Game_View.GameView(self.width, self.height, self.win_length, self.name, self.colour, self.socket))

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
            self.width_text = arcade.Text(f'Width: {self.button_manager.inputs["input_x"].text.value if self.button_manager.inputs["input_x"].text.value else "7"}',
                                          State.state.screen_center.x - 56, State.state.screen_center.y + 152 + 50, anchor_x='center', anchor_y='center')
            self.height_text = arcade.Text(f'Height: {self.button_manager.inputs["input_y"].text.value if self.button_manager.inputs["input_y"].text.value else "6"}',
                                           State.state.screen_center.x + 56, State.state.screen_center.y + 152 + 50, anchor_x='center', anchor_y='center')
            self.win_length_text = arcade.Text(f'Win Length: {self.button_manager.inputs["win_length"].text.value if self.button_manager.inputs["win_length"].text.value else "4"}',
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
                        print(alert)
                        self.width_text.value = f"Width: {str(alert['args'][0])}"
                        self.height_text.value = f"Height: {str(alert['args'][1])}"
                        self.win_length_text.value = f"Win Length: {str(alert['args'][2])}"
                        self.width = alert['args'][0]
                        self.height = alert['args'][1]
                        self.win_length = alert['args'][2]
                        print(f'Stuff1: {self.width, self.height, self.win_length}')
                        self.set_board_info()
                        self.owner_update()
            self.elapsed_delta = 0
