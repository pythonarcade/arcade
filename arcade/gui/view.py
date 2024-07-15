from arcade import View
from arcade.gui import UIManager


class UIView(View):
    """This view provides basic GUI setup.

    This is a convenience class, which adds the UIManager to the view under `self.ui`.
    The UIManager is enabled when the view is shown and disabled when the view is hidden.

    This class provides two draw callbacks: on_draw_before_ui and on_draw_after_ui.
    Use these to draw custom elements before or after the UI elements are drawn.

    If you override ``on_show_view`` or ``on_show_view``,
    don't forget to call super().on_show_view() or super().on_hide_view().

    """

    def __init__(self):
        super().__init__()
        self.ui = UIManager()

    def on_show_view(self):
        """If subclassing UIView, don't forget to call super().on_show_view()."""
        self.ui.enable()

    def on_hide_view(self):
        """If subclassing UIView, don't forget to call super().on_hide_view()."""
        self.ui.disable()

    def on_draw(self):
        """
        To subclass UIView and add custom drawing, override on_draw_before_ui
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
