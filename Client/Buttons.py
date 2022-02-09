import arcade
import arcade.gui

from Client import Sprites_
import Vector


class Button:
    def __init__(self, id_, text, center, size, idle_texture, hover_texture, click_texture, disabled_texture, alpha, on_click, text_colour, hover_text_colour, click_text_colour, text_size, enabled):
        self.id_ = id_
        self.text = text
        self.center = center
        self.size = size
        self.idle_texture = idle_texture
        self.hover_texture = hover_texture
        self.click_texture = click_texture
        self.disabled_texture = disabled_texture
        self.alpha = alpha
        self.on_click = on_click
        self.text_colour = text_colour
        self.hover_text_colour = hover_text_colour
        self.click_text_colour = click_text_colour
        self.text_size = text_size
        self.enabled = enabled


class ButtonManager:
    def __init__(self):
        self.buttons = {}
        self.hover_buttons = set()
        self.clicked_buttons = set()

    def append(self,
               id_: str,
               text: str,
               center: Vector,
               size: Vector,
               idle_texture: arcade.Texture = None,
               hover_texture: arcade.Texture = None,
               click_texture: arcade.Texture = None,
               alpha: int = 255,
               on_click=lambda: None,
               text_colour=(255, 255, 255, 255),
               hover_text_colour=None,
               click_text_colour=None,
               disabled_texture: arcade.Texture = None,
               text_size=22,
               enabled=True
               ):
        if hover_text_colour is None:
            hover_text_colour = text_colour
        if click_text_colour is None:
            click_text_colour = text_colour
        if not idle_texture:
            idle_texture = Sprites_.blank_button_dark
        if not hover_texture:
            hover_texture = Sprites_.blank_button_light
        if not click_texture:
            click_texture = Sprites_.blank_button_light_middle
        if not disabled_texture:
            disabled_texture = Sprites_.x
        self.buttons[id_] = Button(id_, text, center, size, idle_texture, hover_texture, click_texture, disabled_texture,
                                   alpha, on_click, text_colour, hover_text_colour, click_text_colour, text_size, enabled)

    def render(self):
        for button in self.buttons.values():
            if button.id_ not in self.hover_buttons and button.id_ not in self.clicked_buttons:
                texture = button.idle_texture
                text_colour = button.text_colour
            elif button.id_ not in self.clicked_buttons and button.enabled:
                texture = button.hover_texture
                text_colour = button.hover_text_colour
            else:
                if not button.enabled:
                    texture = button.click_texture
                    text_colour = button.click_text_colour
                else:
                    texture = button.idle_texture
                    text_colour = button.text_colour
            arcade.draw_texture_rectangle(
                button.center.x, button.center.y, button.size.x, button.size.y,
                texture, alpha=button.alpha
            )
            arcade.draw_text(
                button.text, button.center.x, button.center.y, text_colour, font_size=button.text_size,
                width=button.size.x, font_name='arial', anchor_x='center', anchor_y='center', align='center'
            )
            if not button.enabled:
                arcade.draw_texture_rectangle(button.center.x, button.center.y, button.size.x * 0.8, button.size.y * 0.8,
                                              button.disabled_texture, alpha=button.alpha)

    def remove(self, id_):
        if id_ in self.buttons:
            del self.buttons[id_]

    def disable(self, id_):
        if id_ in self.buttons:
            if self.buttons[id_].enabled:
                self.buttons[id_].enabled = False

    def enable(self, id_):
        if id_ in self.buttons:
            if not self.buttons[id_].enabled:
                self.buttons[id_].enabled = True

    def clear_all(self, confirm):
        if confirm:
            self.buttons.clear()
        else:
            return

    def on_click_check(self, x, y):
        self.check_hovered(x, y)
        for id_ in self.hover_buttons:
            if not self.buttons[id_].enabled:
                continue
            self.clicked_buttons.add(id_)

    def on_click_release(self):
        self.clicked_buttons.clear()
        for id_ in self.hover_buttons:
            if self.buttons[id_].on_click is not None:
                if not self.buttons[id_].enabled:
                    continue
                self.buttons[id_].on_click()

    def check_hovered(self, mouse_x, mouse_y):
        for button in self.buttons.values():
            if not button.enabled:
                continue
            if (
                    mouse_x in range(int(button.center.x - (button.size.x / 2)), int((button.center.x + (button.size.x / 2)) + 1))
                    and
                    mouse_y in range(int(button.center.y - (button.size.y / 2)), int((button.center.y + (button.size.y / 2)) + 1))
            ):
                self.hover_buttons.add(button.id_)
            else:
                self.hover_buttons.discard(button.id_)
