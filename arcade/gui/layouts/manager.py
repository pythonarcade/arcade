from _warnings import warn
from typing import Union

import arcade
from arcade import Sprite
from arcade.gui import UIElement, MOUSE_PRESS, MOUSE_MOTION, UIEvent, MOUSE_RELEASE
from arcade.gui.layouts import UIAbstractLayout
from arcade.gui.layouts.anchor import UIAnchorLayout
from arcade.gui.layouts.utils import valid
from arcade.gui.manager import UIAbstractManager


class UILayoutManager(UIAbstractManager):
    def __init__(self, window=None, attach_callbacks=True):
        super().__init__()
        self.window: arcade.Window = window if window else arcade.get_window()

        self._root_layout: UIAbstractLayout = UIAnchorLayout(
            self.window.width,
            self.window.height
        )
        self.do_layout()

        if attach_callbacks:
            self.register_handlers()

    def on_ui_event(self, event):
        self._handle_ui_event(event)
        self.root_layout.on_ui_event(event)

    def on_draw(self):
        self._root_layout.draw()

    def on_update(self, dt):
        # FIXME: This might be to slow, let's see
        self.do_layout()

    def pack(self, element: Union[Sprite, UIElement, 'UIAbstractLayout'], **kwargs):
        return self._root_layout.pack(element, **kwargs)

    def remove(self, element: Union[Sprite, UIElement, 'UIAbstractLayout']):
        return self._root_layout.remove(element)

    def _resize_root_layout(self):
        left, right, bottom, top = self.window.get_viewport()
        self.root_layout.top = top
        self.root_layout.left = left
        self.root_layout.width = right - left
        self.root_layout.height = top - bottom

    @property
    def root_layout(self):
        return self._root_layout

    @root_layout.setter
    def root_layout(self, layout: UIAbstractLayout):
        self._root_layout = layout
        self.do_layout()

    def do_layout(self):
        self._resize_root_layout()

        self._root_layout.do_layout()

        if not valid(self._root_layout):
            warn('Refresh produced invalid boundaries')

    def _handle_ui_event(self, event: UIEvent):
        """
        Care about hover and focus of elements
        """

        # if mouse event search for ui_elements at pos to handle hover and focus
        if event.type in (MOUSE_PRESS, MOUSE_MOTION, MOUSE_RELEASE):
            pos = event.get('x'), event.get('y')
            elements_at_pos = self.root_layout.get_elements_at(pos)

            # handle hover
            if event.type == MOUSE_MOTION:
                if len(elements_at_pos) > 0:
                    new_hovered_element = elements_at_pos[-1]
                    if new_hovered_element != self.hovered_element:
                        self.hovered_element = new_hovered_element
                else:
                    self.hovered_element = None

            # handle focus
            if event.type == MOUSE_PRESS:
                if len(elements_at_pos) > 0:
                    new_focused_element = elements_at_pos[-1]
                    if new_focused_element != self.focused_element:
                        self.focused_element = new_focused_element
                else:
                    self.focused_element = None
