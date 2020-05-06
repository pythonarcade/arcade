"""
User Interface Element Manager
"""
import typing

from pyglet.window import Window
import arcade

import logging
LOG = logging.getLogger(__name__)

class UIManager:
    """
    User Interface Element Manager
    """

    def __init__(self, window: Window):
        """ Create manager """
        self.window: Window = window

        self.ui_elements: arcade.SpriteList = arcade.SpriteList(use_spatial_hash=True)

        self.window.push_handlers(self.on_mouse_press)
        self.window.push_handlers(self.on_mouse_drag)
        self.window.push_handlers(self.on_mouse_release)
        self.window.push_handlers(self.on_mouse_motion)

    def append(self, ui_element):
        """ Add a new element. """
        self.ui_elements.append(ui_element)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """ Handle a mouse press. """
        LOG.debug("Click UIManager")
        matching_ui_elements = arcade.get_sprites_at_point((x, y), self.ui_elements)
        if len(matching_ui_elements) > 0:
            matching_ui_element2 = typing.cast(arcade.experimental.gui.UIElement, matching_ui_elements[0])
            matching_ui_element2.is_mouse_pressed = True
            return matching_ui_element2.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Handle a mouse release. """
        for ui_element in self.ui_elements:
            ui_element2 = typing.cast(arcade.experimental.gui.UIElement, ui_element)
            if ui_element2.is_mouse_pressed:
                ui_element2.is_mouse_pressed = False
                return ui_element2.on_mouse_release(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """ Handle mouse motion """
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ Handle mouse motion """

        matching_ui_elements = arcade.get_sprites_at_point((x, y), self.ui_elements)
        for matching_ui_element in matching_ui_elements:
            matching_ui_element2 = typing.cast(arcade.experimental.gui.UIElement, matching_ui_element)
            if not matching_ui_element2.is_mouse_over:
                matching_ui_element2.is_mouse_over = True
                matching_ui_element2.on_mouse_over()

        for ui_element in self.ui_elements:
            ui_element2 = typing.cast(arcade.experimental.gui.UIElement, ui_element)
            if ui_element2.is_mouse_over and ui_element not in matching_ui_elements:
                ui_element2.is_mouse_over = False
                ui_element2.on_mouse_leave()

    def draw(self):
        """ Draw all the UI Elements """
        self.ui_elements.draw()
