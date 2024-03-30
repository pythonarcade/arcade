from arcade import View
from arcade.gui import UIManager


class UIView(View):
    """This view provides basic GUI setup.

    This is a convenience class, which adds the UIManager to the view under `self.ui`.
    The UIManager is enabled when the view is shown and disabled when the view is hidden.

    If you override ``on_show_view`` or ``on_show_view``,
    don't forget to call super().on_show_view() or super().on_hide_view().

    """

    def __init__(self):
        super().__init__()
        self.ui = UIManager()

    def on_show_view(self):
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()
