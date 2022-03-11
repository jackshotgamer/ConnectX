import sys
import arcade
from arcade import gui
from Client import Sprites_, State, Game_View, Event_Base, Buttons
import Vector
import itertools


# # noinspection PyUnresolvedReferences,PyProtectedMember,PyAttributeOutsideInit
# class LimitText(gui.elements.inputbox._KeyAdapter):
#     @property
#     def text(self):
#         return self._text
#
#     @text.setter
#     def text(self, text):
#         if text != self._text:
#             self.state_changed = True
#
#         self._text = text[:15]


class MainMenu(Event_Base.EventBase):
    def __init__(self, slot_width, slot_height, win_length):
        super().__init__()
        self.ui_manager = gui.UIManager(self.window)
        arcade.set_background_color((23, 93, 150))
        self.invalid_colour = False
        self.times = 1
        self.socket = None
        self.disabled_buttons = []
        self.error = ''
        self.started = False
        self.full_lobby = False
        self.ui_manager.enable()
        # self.username = gui.UIInputText(State.state.screen_center.x - 85, State.state.screen_center.y + 10, 300, 50, 'Enter Username:', font_size=18, text_color=arcade.color.GOLD)  # 300, 50
        # self.username.text_adapter = LimitText()
        from functools import partial
        # self.ui_manager.add(self.username)
        self.button_manager.append_button('Enter', 'Enter', lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y), Vector.Vector(250, 50), on_click=self.enter_button)
        self.button_manager.append_button('Quit', 'Quit', lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y - 50), Vector.Vector(100, 50), on_click=self.exit_button)
        self.button_manager.append_input('username', 'Username: ', lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y+50), Vector.Vector(300, 50),
                                         text_colour=(255, 215, 0), text_length=13)
        self.button_manager.append_input('room_id', 'Room Name: ', lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y+101+25), Vector.Vector(200, 50),
                                         text_colour=(215, 215, 215), text_length=6)
        self.room_id = self.button_manager.inputs['room_id'].text.value
        self.slot_width = slot_width
        self.slot_height = slot_height
        self.win_length = win_length
        
        center = lambda: Vector.Vector(State.state.screen_center.x, State.state.screen_center.y - 250)
        self.center = center
        self.no_colour = False
        self.no_name = False
        self.button_manager.append_button('red', 'Red', lambda: Vector.Vector(center().x, center().y + 100), Vector.Vector(100, 100), on_click=partial(self.colour, 'red'), idle_texture=Sprites_.red_disc,
                                          hover_texture=Sprites_.red_disc, click_texture=Sprites_.red_disc, text_size=16, text_colour=(0, 0, 0), hover_text_colour=(100, 100, 100),
                                          click_text_colour=(200, 200, 200))
        self.button_manager.append_button('yellow', 'Yellow', lambda: Vector.Vector(center().x, center().y - 100), Vector.Vector(100, 100), on_click=partial(self.colour, 'yellow'),
                                          idle_texture=Sprites_.yellow_disc,
                                          hover_texture=Sprites_.yellow_disc, click_texture=Sprites_.yellow_disc, text_size=16, text_colour=(0, 0, 0), hover_text_colour=(100, 100, 100),
                                          click_text_colour=(200, 200, 200))
        self.button_manager.append_button('green', 'Green', lambda: Vector.Vector(center().x + 100, center().y), Vector.Vector(100, 100), on_click=partial(self.colour, 'green'), idle_texture=Sprites_.green_disc,
                                          hover_texture=Sprites_.green_disc, click_texture=Sprites_.green_disc, text_size=16, text_colour=(0, 0, 0), hover_text_colour=(100, 100, 100),
                                          click_text_colour=(200, 200, 200))
        self.button_manager.append_button('blue', 'Blue', lambda: Vector.Vector(center().x - 100, center().y), Vector.Vector(100, 100), on_click=partial(self.colour, 'blue'), idle_texture=Sprites_.blue_disc,
                                          hover_texture=Sprites_.blue_disc, click_texture=Sprites_.blue_disc, text_size=16, text_colour=(0, 0, 0), hover_text_colour=(100, 100, 100),
                                          click_text_colour=(200, 200, 200))
        self.button_manager.append_button('pink', 'Pink', lambda: Vector.Vector(center().x + 100, center().y + 100), Vector.Vector(100, 100), on_click=partial(self.colour, 'pink'),
                                          idle_texture=Sprites_.pink_disc,
                                          hover_texture=Sprites_.pink_disc, click_texture=Sprites_.pink_disc, text_size=16, text_colour=(0, 0, 0), hover_text_colour=(100, 100, 100),
                                          click_text_colour=(200, 200, 200))
        self.button_manager.append_button('lime', 'Lime', lambda: Vector.Vector(center().x - 100, center().y + 100), Vector.Vector(100, 100), on_click=partial(self.colour, 'lime'),
                                          idle_texture=Sprites_.lime_disc,
                                          hover_texture=Sprites_.lime_disc, click_texture=Sprites_.lime_disc, text_size=16, text_colour=(0, 0, 0), hover_text_colour=(100, 100, 100),
                                          click_text_colour=(200, 200, 200))
        self.button_manager.append_button('orange', 'Orange', lambda: Vector.Vector(center().x + 100, center().y - 100), Vector.Vector(100, 100), on_click=partial(self.colour, 'orange'),
                                          idle_texture=Sprites_.orange_disc, hover_texture=Sprites_.orange_disc, click_texture=Sprites_.orange_disc, text_size=16, text_colour=(0, 0, 0),
                                          hover_text_colour=(100, 100, 100), click_text_colour=(200, 200, 200))
        self.button_manager.append_button('purple', 'Purple', lambda: Vector.Vector(center().x - 100, center().y - 100), Vector.Vector(100, 100), on_click=partial(self.colour, 'purple'),
                                          idle_texture=Sprites_.purple_disc, hover_texture=Sprites_.purple_disc, click_texture=Sprites_.purple_disc, text_size=16, text_colour=(0, 0, 0),
                                          hover_text_colour=(100, 100, 100), click_text_colour=(200, 200, 200))
        self.colour_buttons = ['red', 'yellow', 'green', 'blue', 'pink', 'lime', 'orange', 'purple']
        self.current_colour = 'None'
        self.preview_texture = Sprites_.disc_slot

    def colour(self, colour):
        self.current_colour = colour
        self.preview_texture = Sprites_.__dict__.get(f'{self.current_colour}_disc', Sprites_.disc_slot)

    def on_draw(self):
        super().on_draw()
        # arcade.draw_rectangle_filled(450, 450 + 50, 250, 50, (0, 0, 0))
        arcade.draw_texture_rectangle(self.center().x, self.center().y, 100, 100, self.preview_texture)
        arcade.draw_text(f'Selected:\n{self.current_colour.upper()}', self.center().x, self.center().y, (0, 0, 0), 11, 100, align='center', bold=True,
                         anchor_x='center', anchor_y='center', multiline=True)
        if self.started:
            arcade.draw_text('Game has started, please join another.', State.state.screen_center.x, State.state.screen_center.y + 200, (255, 0, 0), 30, bold=True, anchor_x='center', anchor_y='center')
            self.errors()
        elif self.full_lobby:
            arcade.draw_text('Game is full, please join another.', State.state.screen_center.x, State.state.screen_center.y + 200, (255, 0, 0), 30, bold=True, anchor_x='center', anchor_y='center')
            self.errors()
        elif self.invalid_colour:
            arcade.draw_text('Invalid colour, please select another.', State.state.screen_center.x, State.state.screen_center.y + 200, (255, 0, 0), 30, bold=True, anchor_x='center', anchor_y='center')
            self.errors()
        elif self.no_name:
            arcade.draw_text('Please input a name.', State.state.screen_center.x, State.state.screen_center.y + 200, (255, 0, 0), 30, bold=True, anchor_x='center', anchor_y='center')
            self.errors()
        elif self.no_colour:
            arcade.draw_text('Please select a colour.', State.state.screen_center.x, State.state.screen_center.y + 200, (255, 0, 0), 30, bold=True, anchor_x='center', anchor_y='center')
            self.errors()
        elif self.error:
            arcade.draw_text(self.error, State.state.screen_center.x, State.state.screen_center.y + 200, (255, 0, 0), 25, 750, bold=True, align='center', anchor_x='center', anchor_y='center',
                             multiline=True)
            self.errors()
        else:
            self.times = 1
        self.ui_manager.draw()

    def on_update(self, delta_time: float):
        super().on_update(delta_time)
        if self.room_id != self.button_manager.inputs['room_id'].text.value:
            for button in (self.button_manager.buttons[id_] for id_ in self.colour_buttons):
                self.button_manager.apply_state(button.id_, self.button_manager.action_enabled, True)
            self.room_id = self.button_manager.inputs['room_id'].text.value

    def errors(self):
        self.times += 1
        if not self.times % 50:
            self.times = 1
            self.started = False
            self.full_lobby = False
            self.invalid_colour = False
            self.no_name = False
            self.no_colour = False
            self.error = ''

    def enter_button(self):
        player_username = self.button_manager.inputs['username'].text.value
        if self.no_name:
            self.no_colour = False
        if player_username == 'Enter Username:':
            player_username = 'None'
        if player_username == 'None' or not player_username:
            self.no_name = True
            return
        if self.current_colour == 'None':
            if not self.no_name:
                self.no_colour = True
            return
        if self.establish_connection():
            from Client.Lobby_View import LobbyView
            self.window.show_view(LobbyView(self.button_manager.inputs['room_id'].text, self.socket, player_username, self.current_colour))

    def establish_connection(self):
        import socket as s
        import socket_util
        import json
        success = True
        self.socket = s.socket()
        # self.socket.connect(('127.0.0.1', 2819))
        self.socket.connect(('proxy.wumpus.host', 10049))
        socket_util.send_str(self.socket, json.dumps({'room_id': self.button_manager.inputs['room_id'].text.value}))
        import time
        time.sleep(.5)
        string = {
            'type': 'command',
            'command': 'join',
            'args': [f'{self.button_manager.inputs["username"].text.value}', f'{self.current_colour}'],
        }
        try:
            socket_util.send_str(self.socket, json.dumps(string))
        except ConnectionResetError:
            self.error = 'Connection Error\nPlease check internet'
            return
        read = json.loads(socket_util.read_str(self.socket).strip('|||'))
        if read.get('error') == 'DupeCol':
            if len(read.get('invalidCol', [])) >= 8:
                success = False
                self.full_lobby = True
            else:
                self.invalid_colour = True
                for colour in read.get('invalidCol', []):
                    self.button_manager.apply_state(colour, self.button_manager.action_enabled, False)
                    self.disabled_buttons.append(colour)
                    success = False
        elif read.get('error') == 'GameStarted':
            self.started = True
            success = False
        return success

    @staticmethod
    def exit_button():
        arcade.close_window()
