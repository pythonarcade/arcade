import PIL.Image

import arcade

import logging
LOG = logging.getLogger(__name__)

class UIElement(arcade.Sprite):
    def __init__(self,
                 center_x = 0,
                 center_y = 0,
                 width = 60,
                 height = 40):
        super().__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.is_mouse_over = False
        self.is_mouse_pressed = False
        self.normal_texture = None
        self.mouse_over_texture = None
        self.mouse_press_texture = None

        color = (127, 127, 127)
        image = PIL.Image.new('RGBA', (width, height), color)
        self.texture = arcade.Texture(f"Solid-{color[0]}-{color[1]}-{color[2]}", image)
        self._points = self.texture.hit_box_points

        self.normal_texture = self.texture

        color = (80, 80, 80)
        image = PIL.Image.new('RGBA', (width, height), color)
        self.mouse_over_texture = arcade.Texture(f"Solid-{color[0]}-{color[1]}-{color[2]}", image)

        color = (127, 0, 0)
        image = PIL.Image.new('RGBA', (width, height), color)
        self.mouse_press_texture = arcade.Texture(f"Solid-{color[0]}-{color[1]}-{color[2]}", image)

    def set_proper_texture(self):
        if self.is_mouse_pressed:
            self.texture = self.mouse_press_texture
        elif self.is_mouse_over:
            self.texture = self.mouse_over_texture
        else:
            self.texture = self.normal_texture

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        LOG.debug("UIElement mouse press")
        self.set_proper_texture()
        return True

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        LOG.debug("UIElement mouse release")
        self.set_proper_texture()

        return True

    def on_mouse_over(self):
        LOG.debug("UIElement mouse over")
        self.set_proper_texture()


    def on_mouse_leave(self):
        LOG.debug("UIElement mouse leave")
        self.set_proper_texture()
