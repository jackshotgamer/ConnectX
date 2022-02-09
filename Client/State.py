import arcade
import Vector


class State:
    def __init__(self):
        self.window = None
        self.cell_size = Vector.Vector(150, 150)
        self.default_cell_size = Vector.Vector(150, 150)
        self.render_radius = 2
        self.default_window_size = Vector.Vector(1000, 800)

    def set_cell_size(self, slot_width, slot_height):
        temp = min(((self.window.width - (self.window.width * 0.1)) / slot_width), ((self.window.height - (self.window.height * 0.1)) / slot_height))
        self.cell_size = Vector.Vector(temp, temp)

    @property
    def screen_center(self):
        return Vector.Vector(self.window.width / 2, self.window.height / 2)

    @property
    def cell_render_size(self):
        aspect_ratio = min((self.window.width - (self.window.width * 0.1)) / self.default_window_size.x, (self.window.height - (self.window.height * 0.1)) / self.default_window_size.y)
        aspect_ratio = (aspect_ratio, aspect_ratio)
        return self.cell_size * aspect_ratio

    @staticmethod
    def generate_radius(radius):
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                yield x, y


state = State()
