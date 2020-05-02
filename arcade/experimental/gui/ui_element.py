import PIL.Image

import arcade

import logging
LOG = logging.getLogger(__name__)

class UIElement(arcade.Sprite):
    def __init__(self,
                 center_x = 0,
                 center_y = 0):
        super().__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.is_mouse_over = False
        self.is_mouse_pressed = False
        self.width = None
        self.height = None

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_over(self):
        pass

    def on_mouse_leave(self):
        pass
