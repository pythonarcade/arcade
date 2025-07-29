"""
Example demonstrating a grid layout with focusable buttons in an Arcade GUI.

This example shows how to create a grid layout with buttons
that can be navigated using a controller.
It includes a focus transition setup to allow smooth navigation between buttons in the grid.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.exp_controller_support_grid
"""

import arcade
from arcade.examples.gui.exp_controller_support import ControllerIndicator
from arcade.experimental.controller_window import ControllerView, ControllerWindow
from arcade.gui import (
    UIFlatButton,
    UIGridLayout,
    UIView,
    UIWidget,
)
from arcade.gui.experimental.focus import UIFocusable, UIFocusGroup


class FocusableButton(UIFocusable, UIFlatButton):
    pass


def setup_grid_focus_transition(grid: dict[tuple[int, int], UIWidget]):
    """Setup focus transition in grid.

    Connect focus transition between `Focusable` in grid.

    Args:
        grid: Dict[Tuple[int, int], Focusable]: grid of Focusable widgets.
        key represents position in grid (x,y)

    """

    cols = max(x for x, y in grid.keys()) + 1
    rows = max(y for x, y in grid.keys()) + 1
    for c in range(cols):
        for r in range(rows):
            btn = grid.get((c, r))
            if btn is None or not isinstance(btn, UIFocusable):
                continue

            if c > 0:
                btn.neighbor_left = grid.get((c - 1, r))
            else:
                btn.neighbor_left = grid.get((cols - 1, r))

            if c < cols - 1:
                btn.neighbor_right = grid.get((c + 1, r))
            else:
                btn.neighbor_right = grid.get((0, r))

            if r > 0:
                btn.neighbor_up = grid.get((c, r - 1))
            else:
                btn.neighbor_up = grid.get((c, rows - 1))

            if r < rows - 1:
                btn.neighbor_down = grid.get((c, r + 1))
            else:
                btn.neighbor_down = grid.get((c, 0))


class MyView(ControllerView, UIView):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)

        self.root = self.add_widget(ControllerIndicator())
        self.root = self.root.add(UIFocusGroup())
        grid = self.root.add(
            UIGridLayout(column_count=3, row_count=3, vertical_spacing=10, horizontal_spacing=10)
        )

        _grid = {}
        for i in range(9):
            btn = FocusableButton(text=f"Button {i}")
            _grid[(i % 3, i // 3)] = btn
            grid.add(btn, column=i % 3, row=i // 3)

        # connect focus transition in grid
        setup_grid_focus_transition(_grid)

        self.root.detect_focusable_widgets()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        # make the example close with the escape key
        if symbol == arcade.key.ESCAPE:
            self.window.close()
            return True
        return super().on_key_press(symbol, modifiers)


if __name__ == "__main__":
    window = ControllerWindow(title="Controller UI Example")
    window.show_view(MyView())
    arcade.run()
