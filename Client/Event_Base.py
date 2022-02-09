import arcade
import arcade.gui

from Client import Buttons

symbols = []
held_modifiers = 0


class EventBase(arcade.View):
    def __init__(self):
        super().__init__()
        self.button_manager = Buttons.ButtonManager()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.button_manager.check_hovered(x, y)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.button_manager.on_click_check(x, y)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.button_manager.on_click_release()

    def on_draw(self):
        arcade.start_render()
        super().on_draw()
        self.button_manager.render()

    def on_key_press(self, symbol: int, modifiers: int):
        global symbols
        global held_modifiers
        symbols.append(symbol)
        held_modifiers |= modifiers

    def on_key_release(self, _symbol: int, _modifiers: int):
        global symbols
        global held_modifiers
        if _symbol in symbols:
            symbols.remove(_symbol)
        held_modifiers &= _modifiers
        # 01101 - 4 = 01001
        #


"""
100 shift
010 ctrl

press a + shift
held_modifiers = 0b100

release shift
press b

"""
# () [] <> != == & ^ % * @ ! : " ' . , / // | {} async from def match case import from for in as int str print open with class __init__ ; '' '''''' "" """""" ~ + = - global if elif else while self
# &= |= bin ord memoryview pass remove join encode lower format split splitlines index center count isnumeric strip
