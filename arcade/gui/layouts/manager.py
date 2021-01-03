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
            self.window.height,
            parent=self)
        self._resize_root_layout()

        if attach_callbacks:
            self.register_handlers()

    def on_ui_event(self, event):
        self._handle_ui_event(event)
        self.root_layout.on_ui_event(event)

    def on_draw(self):
        self._root_layout.draw()

    def on_update(self, dt):
        self._resize_root_layout()

        # Relayout all children, this might be to slow, let's see
        self.refresh()

    def pack(self, element: Union[Sprite, UIElement, 'UIAbstractLayout'], **kwargs):
        self._root_layout.pack(element, **kwargs)

    def _resize_root_layout(self):
        self.root_layout.top = self._top
        self.root_layout.left = self._left
        self.root_layout.width = self.window.width
        self.root_layout.height = self.window.height

    @property
    def root_layout(self):
        return self._root_layout

    @root_layout.setter
    def root_layout(self, layout: UIAbstractLayout):
        self._root_layout = layout
        self.refresh()

    def refresh(self):
        self._root_layout.refresh()

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

    # UILayoutManager always fills the whole view
    @property
    def _left(self):
        return self.window.get_viewport()[0]

    @property
    def _right(self):
        return self.window.get_viewport()[1]

    @property
    def _bottom(self):
        return self.window.get_viewport()[2]

    @property
    def _top(self):
        return self.window.get_viewport()[3]
