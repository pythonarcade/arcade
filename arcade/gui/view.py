from typing import TypeVar

from arcade import View
from arcade.gui.ui_manager import UIManager
from arcade.gui.widgets import UIWidget

W = TypeVar("W", bound=UIWidget)


class UIView(View):
    """This view provides basic GUI setup.

    This is a convenience class, which adds the UIManager to the view under `self.ui`.
    The UIManager is enabled when the view is shown and disabled when the view is hidden.

    This class provides two draw callbacks: on_draw_before_ui and on_draw_after_ui.
    Use these to draw custom elements before or after the UI elements are drawn.

    The screen is cleared before on_draw_before_ui is called
    with the background color of the window.

    If you override ``on_show_view`` or ``on_hide_view``,
    don't forget to call super().on_show_view() or super().on_hide_view().

    """

    def __init__(self):
        super().__init__()
        self.ui = UIManager()
        """
        The UIManager of this view.
        """

    def add_widget(self, widget: W) -> W:
        """Add a widget to the UIManager of this view."""
        return self.ui.add(widget)

    def on_show_view(self):
        """If subclassing UIView, don't forget to call super().on_show_view()."""
        self.ui.enable()

    def on_hide_view(self):
        """If subclassing UIView, don't forget to call super().on_hide_view()."""
        self.ui.disable()

    def on_draw(self):
        """To subclass UIView and add custom drawing, override on_draw_before_ui
        and on_draw_after_ui.
        """
        self.clear()
        self.on_draw_before_ui()
        self.ui.draw()
        self.on_draw_after_ui()

    def on_draw_before_ui(self):
        """Use this method to draw custom elements before the UI elements are drawn."""
        pass

    def on_draw_after_ui(self):
        """Use this method to draw custom elements after the UI elements are drawn."""
        pass
