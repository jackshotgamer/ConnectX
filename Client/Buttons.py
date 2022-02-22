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

    def get_actual_pos(self):
        if callable(self.center):
            return self.center()
        return self.center
    
    def update(self):
        pass


class TextInput:
    def __init__(self, id_, prompt, center, size, idle_texture, hover_texture, alpha, on_click, text_colour, disabled_texture, text_size, text, enabled, text_length):
        self.id_ = id_
        self.center = center
        self.prompt = arcade.Text(prompt, self.get_actual_pos().x, self.get_actual_pos().y, text_colour, text_size, size.x, anchor_x='center', anchor_y='center')
        self.size = size
        self.idle_texture = idle_texture
        self.hover_texture = hover_texture
        self.disabled_texture = disabled_texture
        self.alpha = alpha
        self.on_click = on_click
        self.text_colour = text_colour
        self.text_size = text_size
        self.text = arcade.Text(text, self.get_actual_pos().x, self.get_actual_pos().y, text_colour, text_size, size.x, font_name='Fonts/JetBrainsMono.ttf', anchor_x='center', anchor_y='center')
        self.enabled = enabled
        self.text_length = text_length

    def get_actual_pos(self):
        if callable(self.center):
            return self.center()
        return self.center
    
    def update(self):
        self.prompt.x, self.prompt.y = self.get_actual_pos().x, self.get_actual_pos().y
        self.text.x, self.text.y = self.get_actual_pos().x, self.get_actual_pos().y


class ButtonManager:
    def __init__(self):
        self.buttons = {}
        self.inputs = {}
        self.hover_buttons = set()
        self.hover_inputs = set()
        self.clicked_buttons = set()
        self.clicked_inputs = set()

    def append_button(self,
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

    def append_input(self,
                     id_: str,
                     prompt: str,
                     center: Vector,
                     size: Vector,
                     idle_texture: arcade.Texture = None,
                     hover_texture: arcade.Texture = None,
                     alpha: int = 255,
                     on_click=lambda: None,
                     text_colour=(255, 255, 255, 255),
                     disabled_texture: arcade.Texture = None,
                     text_size=22,
                     text: str = '',
                     enabled=True,
                     text_length=-1
                     ):
        if not idle_texture:
            idle_texture = Sprites_.blank_button_dark
        if not hover_texture:
            hover_texture = Sprites_.blank_button_light
        if not disabled_texture:
            disabled_texture = Sprites_.x
        self.inputs[id_] = TextInput(id_, prompt, center, size, idle_texture, hover_texture,
                                     alpha, on_click, text_colour, disabled_texture, text_size, text, enabled, text_length)

    def render(self):
        self._button_render()
        self._input_render()

    def _input_render(self):
        for input_ in self.inputs.values():
            render_prompt = True
            if input_.id_ not in self.hover_inputs and input_.id_ not in self.clicked_inputs:
                texture = input_.idle_texture
            elif input_.id_ not in self.clicked_inputs and input_.enabled:
                texture = input_.hover_texture
            else:
                texture = input_.hover_texture
                if input_.enabled:
                    render_prompt = False
            arcade.draw_texture_rectangle(
                input_.get_actual_pos().x, input_.get_actual_pos().y, input_.size.x, input_.size.y,
                texture, alpha=input_.alpha
            )
            input_.prompt.draw() if not input_.text.value and render_prompt else input_.text.draw()
            if not input_.enabled:
                arcade.draw_texture_rectangle(input_.get_actual_pos().x, input_.get_actual_pos().y, input_.size.x * 0.8, input_.size.y * 0.8,
                                              input_.disabled_texture, alpha=input_.alpha)

    def _button_render(self):
        for button in self.buttons.values():
            if button.id_ not in self.hover_buttons and button.id_ not in self.clicked_buttons:
                texture = button.idle_texture
                text_colour = button.text_colour
            elif button.id_ not in self.clicked_buttons and button.enabled:
                texture = button.hover_texture
                text_colour = button.hover_text_colour
            else:
                if button.enabled:
                    texture = button.click_texture
                    text_colour = button.click_text_colour
                else:
                    texture = button.idle_texture
                    text_colour = button.text_colour
            arcade.draw_texture_rectangle(
                button.get_actual_pos().x, button.get_actual_pos().y, button.size.x, button.size.y,
                texture, alpha=button.alpha
            )
            arcade.draw_text(
                button.text, button.get_actual_pos().x, button.get_actual_pos().y, text_colour, font_size=button.text_size,
                width=button.size.x, font_name='arial', anchor_x='center', anchor_y='center', align='center'
            )
            if not button.enabled:
                arcade.draw_texture_rectangle(button.get_actual_pos().x, button.get_actual_pos().y, button.size.x * 0.8, button.size.y * 0.8,
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

    def update_elements(self):
        for input_ in self.inputs.values():
            input_.update()
        for button_ in self.buttons.values():
            button_.update()

    def clear_all(self, confirm):
        if confirm:
            self.buttons.clear()
        else:
            return

    def on_key_press(self, symbol: int, modifier: int):
        if chr(symbol).isalnum():
            # TODO:
            # or symbol in {ord('!'), ord('^'), ord('*'), ord('('), ord(')'), ord('_'), ord('-'), ord('='), ord('+'), ord('.'), ord(','), ord('/'), ord('\\'),
            #                                        ord('|'), ord('?'), ord('{'), ord('}'), ord('['), ord(']'), ord(':'), ord(';'), ord('@'), ord("'"), ord('~'), ord('#'), ord('<'),
            #                                        ord('>'), ord('`')}:
            for id_ in self.clicked_inputs:
                if len(self.inputs[id_].text.value) + 1 <= self.inputs[id_].text_length or self.inputs[id_].text_length <= 0:
                    self.inputs[id_].text.value += chr(symbol) if not modifier & arcade.key.MOD_SHIFT else chr(symbol).upper()
        elif symbol == arcade.key.BACKSPACE:
            for id_ in self.clicked_inputs:
                self.inputs[id_].text.value = self.inputs[id_].text.value[:-1]

    def on_click_check(self, x, y):
        self.check_hovered(x, y)
        for id_ in self.hover_buttons:
            if not self.buttons[id_].enabled:
                continue
            self.clicked_buttons.add(id_)
        for id_ in self.hover_inputs:
            if not self.inputs[id_].enabled:
                continue
            self.clicked_inputs.add(id_)
        self.clicked_inputs = self.clicked_inputs & self.hover_inputs

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
                    mouse_x in range(int(button.get_actual_pos().x - (button.size.x / 2)), int((button.get_actual_pos().x + (button.size.x / 2)) + 1))
                    and
                    mouse_y in range(int(button.get_actual_pos().y - (button.size.y / 2)), int((button.get_actual_pos().y + (button.size.y / 2)) + 1))
            ):
                self.hover_buttons.add(button.id_)
            else:
                self.hover_buttons.discard(button.id_)
        for input_ in self.inputs.values():
            if not input_.enabled:
                continue
            if (
                    mouse_x in range(int(input_.get_actual_pos().x - (input_.size.x / 2)), int((input_.get_actual_pos().x + (input_.size.x / 2)) + 1))
                    and
                    mouse_y in range(int(input_.get_actual_pos().y - (input_.size.y / 2)), int((input_.get_actual_pos().y + (input_.size.y / 2)) + 1))
            ):
                self.hover_inputs.add(input_.id_)
            else:
                self.hover_inputs.discard(input_.id_)
