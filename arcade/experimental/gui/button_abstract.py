"""
Abstract button class
"""
from .ui_element import UIElement

import logging
LOG = logging.getLogger(__name__)

class ButtonAbstract(UIElement):
    """ Abstract button to be used as a base class for other button types. """
    def __init__(self,
                 center_x=0,
                 center_y=0):
        super().__init__(center_x=center_x, center_y=center_y)

        self.normal_texture = None
        self.mouse_over_texture = None
        self.mouse_press_texture = None

    def set_proper_texture(self):
        """ Set normal, mouse-over, or clicked texture. """
        if self.is_mouse_pressed:
            self.texture = self.mouse_press_texture
        elif self.is_mouse_over:
            self.texture = self.mouse_over_texture
        else:
            self.texture = self.normal_texture

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """ Handle mouse down event. """
        LOG.debug("UIElement mouse press")
        self.set_proper_texture()
        return True

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Handle mouse release event. """
        LOG.debug("UIElement mouse release")
        self.set_proper_texture()

        # If we mouse up, while still over item, call -click-
        if self.is_mouse_over:
            self.on_click()

        return True

    def on_mouse_over(self):
        """ Handle mouse over. """
        LOG.debug("UIElement mouse over")
        self.set_proper_texture()

    def on_mouse_leave(self):
        """ Mouse leaves element. """
        LOG.debug("UIElement mouse leave")
        self.set_proper_texture()

    def on_click(self):
        """ Handle a mouse click """
        pass
