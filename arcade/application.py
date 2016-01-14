from .window_commands import *

import pyglet

class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_window(self)
        set_viewport(0, self.width, 0, self.height)
        print("Set")
