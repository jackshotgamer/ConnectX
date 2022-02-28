import arcade
from Client import Main_View, State
import random


window = arcade.Window(width=900, height=900, resizable=True, title='Connect X', antialiasing=False)
State.state.window = window
window.set_min_size(700, 800)
window.show_view(Main_View.MainMenu(7, 6, 4))
if __name__ == '__main__':
    arcade.run()
