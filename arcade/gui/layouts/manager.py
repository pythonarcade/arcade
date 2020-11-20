from _warnings import warn

import arcade
from arcade.gui.layouts import UIAbstractLayout
from arcade.gui.layouts.anchor import UIAnchorLayout
from arcade.gui.layouts.utils import valid
from arcade.gui.manager import UIAbstractManager


class UILayoutManager(UIAbstractManager):
    def __init__(self, window=None):
        super().__init__()
        self.window: arcade.Window = window if window else arcade.get_window()

        self._root_layout: UIAbstractLayout = UIAnchorLayout(
            self.window.width,
            self.window.height,
            parent=self)
        self._resize_root_layout()

        self.register_handlers()

    def on_ui_event(self, event):
        pass
        # TODO pass

    def on_draw(self):
        self._root_layout.draw()

    def on_update(self, dt):
        self._resize_root_layout()

        # Relayout all children, this might be to slow, let's see
        self.refresh()

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
