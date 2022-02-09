import arcade
import socket as s
import socket_util
import numpy as np
from Client import Sprites_, State, Event_Base
import Vector
import itertools
import dataclasses

neutral_colour = 'Gray'


class GameView(Event_Base.EventBase):
    def __init__(self, slot_width, slot_height, win_length, name, colour, socket: s.socket):
        super().__init__()
        arcade.set_background_color((23, 93, 150))
        self.slot_width = abs(slot_width)
        self.slot_height = abs(slot_height)
        self.win_length = abs(win_length)
        self.slot_width = min(25, max(3, self.slot_width))
        self.slot_height = min(25, max(3, self.slot_height))
        self.win_length = min(25, max(3, self.win_length))
        self.total_slots = self.slot_width * self.slot_height
        self.socket = socket
        self.name = name
        self.winner = ''
        self.username_text = arcade.Text(f'Name: {self.name}', State.state.screen_center.x, State.state.window.height - 20, arcade.color.BLACK, 18, anchor_x='center', anchor_y='center',
                                         multiline=False)
        self.winner_text1 = arcade.Text(f'Winner:', State.state.screen_center.x, State.state.screen_center.y + (max(State.state.cell_render_size.x, State.state.cell_render_size.y)),
                                        arcade.color.DARK_BLUE, 50, bold=True, anchor_x='center', anchor_y='center', multiline=False)
        self.winner_text2 = arcade.Text(f'{self.winner.upper()}!', State.state.screen_center.x, State.state.screen_center.y, arcade.color.DARK_BLUE,
                                        50, bold=True, anchor_x='center', anchor_y='center', multiline=False)
        State.state.set_cell_size(self.slot_width, self.slot_height)
        self.wcenter = int((self.slot_width - 1) / 2)
        self.hcenter = int((self.slot_height - 1) / 2)
        weven = True if not self.slot_width % 2 else False
        heven = True if not self.slot_height % 2 else False
        self.slots = {
            (self.wcenter - num1, self.hcenter - num2): neutral_colour
            for num1 in range(- (1 if weven else 0), self.slot_width - (1 if weven else 0))
            for num2 in range(- (1 if heven else 0), self.slot_height - (1 if heven else 0))
        }
        self.current_team = colour
        self.drop_pos = None
        self.w_offset, self.h_offset = 0, 0

    def colour_at_coords(self, x, y):
        if (x, y) in self.slots:
            return self.slots[(x, y)]
        else:
            return None

    @staticmethod
    def convert_colour_to_sprite(colour):
        if colour == 'red':
            return Sprites_.red_disc
        if colour == 'yellow':
            return Sprites_.yellow_disc
        if colour == 'green':
            return Sprites_.green_disc
        if colour == 'blue':
            return Sprites_.blue_disc
        if colour == 'pink':
            return Sprites_.pink_disc
        if colour == 'lime':
            return Sprites_.lime_disc
        if colour == 'orange':
            return Sprites_.orange_disc
        if colour == 'purple':
            return Sprites_.purple_disc
        return Sprites_.disc_slot

    @staticmethod
    def convert_colour_to_rgb(colour):
        if colour == 'red':
            return 217, 38, 38
        if colour == 'yellow':
            return 255, 255, 38
        if colour == 'green':
            return 15, 136, 47
        if colour == 'blue':
            return 3, 6, 255
        if colour == 'pink':
            return 232, 84, 178
        if colour == 'lime':
            return 78, 238, 52
        if colour == 'orange':
            return 236, 120, 9
        if colour == 'purple':
            return 104, 49, 177
        return 127, 127, 127

    @property
    def is_even_slots(self):
        return

    """
    -1, 2   0, 2   1, 2   2, 2
    -1, 1   0, 1   1, 1   2, 1
    -1, 0   0, 0   1, 0   2, 0
    -1,-1   0,-1   1,-1   3,-1
    3 
    for num in slots:
        if num.x == clicked_x:
            if current in filled_slots:
                current += 1
                slots.add((clicked_x,current), f'{team_colour}')
            current = min(num.y,current)
    """

    def on_draw(self):
        super().on_draw()
        if (not (self.slot_width & 1)) | ((not (self.slot_height & 1)) << 1) != 0:
            if (not (self.slot_width & 1)) | ((not (self.slot_height & 1)) << 1) == 1:
                self.w_offset = -(State.state.cell_render_size.xf / 2)
            elif (not (self.slot_width & 1)) | ((not (self.slot_height & 1)) << 1) == 2:
                self.h_offset = -(State.state.cell_render_size.yf / 2)
            else:
                self.w_offset = -(State.state.cell_render_size.xf / 2)
                self.h_offset = -(State.state.cell_render_size.yf / 2)
        # for index, slot in np.ndenumerate(self.slots):
        render_center = Vector.Vector(State.state.screen_center.xf + self.w_offset, State.state.screen_center.yf + self.h_offset)
        # arcade.draw_texture_rectangle(render_center.x, render_center.y, State.state.cell_render_size.xf, State.state.cell_render_size.yf,
        #                               Sprites_.disc_slot, alpha=100)
        for (x, y), team in self.slots.items():
            current_render_center = Vector.Vector((State.state.cell_render_size.xf * x) + render_center.x, (State.state.cell_render_size.yf * y) + render_center.y)
            arcade.draw_texture_rectangle(current_render_center.x, current_render_center.y, State.state.cell_render_size.xf, State.state.cell_render_size.yf,
                                          self.convert_colour_to_sprite(team))
        if self.drop_pos:
            droppos = self.convert_grid_pos_into_render_pos(self.drop_pos[0], self.drop_pos[1])
            arcade.draw_texture_rectangle(droppos.xf, droppos.yf, State.state.cell_render_size.x, State.state.cell_render_size.y,
                                          self.convert_colour_to_sprite(self.current_team), alpha=100)
        arcade.draw_point(State.state.screen_center.x, State.state.screen_center.y, arcade.color.BLACK, 10)
        arcade.draw_point(render_center.x, render_center.y, arcade.color.BLACK, 10)
        arcade.draw_point((State.state.cell_render_size.x + self.w_offset) + State.state.screen_center.x,
                          (State.state.cell_render_size.y + self.h_offset) + State.state.screen_center.y,
                          arcade.color.GOLD, 10)
        if self.winner:
            arcade.draw_circle_filled(State.state.screen_center.x, State.state.screen_center.y + (State.state.screen_center.y * 0.1), 200, (50, 120, 255))
            self.winner_text1.draw()
            self.winner_text2.draw()
        self.username_text.draw()

    def convert_grid_pos_into_render_pos(self, x, y):
        render_center = Vector.Vector(State.state.screen_center.xf + self.w_offset, State.state.screen_center.yf + self.h_offset)
        return Vector.Vector((State.state.cell_render_size.xf * x) + render_center.x, (State.state.cell_render_size.yf * y) + render_center.y)

    # noinspection PyProtectedMember
    def hovered_lane(self):
        mouse_pos = Vector.Vector(self.window._mouse_x, self.window._mouse_y)
        return Vector.Vector(((mouse_pos.x - (State.state.screen_center.xf - (State.state.cell_render_size.x * (self.slot_width / 2))))
                              // State.state.cell_render_size.xf) - self.wcenter,
                             ((mouse_pos.y - (State.state.screen_center.yf - (State.state.cell_render_size.y * (self.slot_height / 2))))
                              // State.state.cell_render_size.yf) - self.hcenter, )
    """
    {...}|||{...}
    """
    socket_interval = 1 / 16
    elapsed_delta = 0
    # noinspection PyProtectedMember
    def update(self, delta_time: float):
        self.elapsed_delta += delta_time
        if self.elapsed_delta > self.socket_interval:
            if socket_alerts := socket_util.get_readable_sockets([self.socket]):
                import json
                raw = socket_util.read_str(socket_alerts[0])
                print(raw)
                for alert1 in raw.split('|||'):
                    if not alert1.strip():
                        continue
                    print(alert1)
                    alert = json.loads(alert1)
                    if alert['type'] == 'drop_confirm':
                        self.slots[tuple(alert['coords'])] = alert['drop_team']
                        if not self.winner:
                            self.winner = alert['winner']
                            if self.winner:
                                self.winner_text2.color = self.convert_colour_to_rgb(self.winner)
                                self.winner_text1.color = self.convert_colour_to_rgb(self.winner)
                                self.winner_text2.value = f'{self.winner.upper()}!'
            self.elapsed_delta = 0
        hovered = (self.hovered_lane())
        self.username_text.x = State.state.screen_center.x
        self.username_text.y = State.state.window.height - 20
        self.winner_text1.x = State.state.screen_center.x
        self.winner_text1.y = State.state.screen_center.y + (max(State.state.cell_render_size.x, State.state.cell_render_size.y))
        self.winner_text2.x = State.state.screen_center.x
        self.winner_text2.y = State.state.screen_center.y
        hovered_colours = [(x, y) for (x, y), team in self.slots.items() if x == hovered.x and team == neutral_colour]
        if hovered_colours:
            self.drop_pos = min(hovered_colours, key=lambda arg: arg[1])
        else:
            self.drop_pos = None
        # for (x, y), team in self.slots.items():
        #     if x == hovered.x:
        #         if self.colour_at_coords(x, current) or current == -(self.slot_height // 2):
        #             self.slots[(hovered.x, current)] =
        #         current = min(y, current)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        if button == 1:
            if self.drop_pos:
                import json
                string = {
                    'type': 'command',
                    'command': 'drop',
                    'args': [(self.drop_pos[0], self.drop_pos[1]), f'{self.current_team}'],
                }
                socket_util.send_str(self.socket, json.dumps(string))

    def on_key_release(self, _symbol: int, _modifiers: int):
        if _symbol == arcade.key.ESCAPE:
            exit()
        if _symbol == arcade.key.Y:
            self.current_team = 'yellow'
        elif _symbol == arcade.key.R:
            self.current_team = 'red'
