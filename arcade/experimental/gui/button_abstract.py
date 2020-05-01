from .ui_element import UIElement

import logging
LOG = logging.getLogger(__name__)

class ButtonAbstract(UIElement):
    def __init__(self,
                 center_x=0,
                 center_y=0,
                 width=60,
                 height=40):
        super().__init__(center_x=center_x, center_y=center_y, width=width, height=height)

        self.normal_texture = None
        self.mouse_over_texture = None
        self.mouse_press_texture = None

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
