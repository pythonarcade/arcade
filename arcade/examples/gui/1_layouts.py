"""Demonstrates the use of layouts.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.1_layouts

Content:
- Create a view with a description of layouts
- Use UIAnchorLayout to position widgets relative to the screen edges
- Use UIBoxLayout to position widgets in a horizontal or vertical line
- Use UIGridLayout to position widgets in a grid

"""

from datetime import datetime

import arcade
from arcade.gui import UIAnchorLayout

arcade.resources.load_system_fonts()

DESCRIPTION = """How to place widgets on the screen?

Widgets can be manually placed on the screen by using the `add` method of the UIManager
and setting the rect of a widget. This is useful for simple ui setups.

This approach requires to manually calculate the position of the
widgets and handling screen resizes.

Another approach is to use layouts. Layouts are containers that automatically
position widgets based on the layout rules. This example shows how to use
the UIAnchorLayout, UIBoxLayout, and UIGridLayout.

UIAnchorLayout:
- UIAnchorLayout is a layout that positions widgets relative to the screen edges.
- Widgets can be anchored to the top, bottom, left, right, center, or any combination of these.
- Widgets can be aligned to the anchor position with a pixel offset.

UIBoxLayout:
- UIBoxLayout is a layout that positions widgets in a horizontal or vertical line.
- Widgets can be aligned on the orthogonal axis.
- Widgets can have a space between them.

UIGridLayout:
- UIGridLayout is a layout that positions widgets in a grid.
- Widgets can be placed in rows and columns.
- Widgets can have a vertical and horizontal spacing.

The layouts calculate the size of the widgets based on the size_hint,
size_hint_min, and size_hint_max.

- size_hint: A tuple of two floats that represent the relative size of the widget.
- size_hint_min: A tuple of two floats that represent the minimum size of the widget.
- size_hint_max: A tuple of two floats that represent the maximum size of the widget.

Layouts only resize widgets if the size_hint is set for the resprecitve axis.
If the size_hint is not set, the widget will use its current size.

Some widgets calculate their minimum size based on their content like UILabel
and layouts in general.
"""


class LayoutView(arcade.gui.UIView):
    """This view demonstrates the use of layouts."""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_PETER_RIVER

        # Create a anchor layout, which can be used to position widgets on screen
        self.anchor = self.add_widget(UIAnchorLayout())

        # Add describing text in center
        text_area = arcade.gui.UITextArea(
            text=DESCRIPTION,
            text_color=arcade.uicolor.WHITE_CLOUDS,
            font_name=("Lato", "proxima-nova", "Helvetica Neue", "Arial", "sans-serif"),
            font_size=12,
            size_hint=(0.5, 0.8),
        )
        self.anchor.add(text_area, anchor_x="center_x", anchor_y="center_y")
        text_area.with_border(color=arcade.uicolor.GRAY_CONCRETE)
        text_area.with_background(color=arcade.uicolor.GRAY_CONCRETE.replace(a=125))
        text_area.with_padding(left=5)

        # add a grid layout with the window and grid size and grid position
        self.grid = arcade.gui.UIGridLayout(
            column_count=2,
            row_count=2,
            align_horizontal="left",
        )
        self.grid.with_background(color=arcade.uicolor.GRAY_CONCRETE)
        self.grid.with_border(color=arcade.uicolor.GRAY_ASBESTOS)
        self.grid.with_padding(all=10)
        self.anchor.add(self.grid, anchor_x="left", anchor_y="top", align_x=10, align_y=-10)
        self.grid.add(
            arcade.gui.UILabel(text="Arcade: "),
            row=0,
            column=0,
        )
        self.grid.add(
            arcade.gui.UILabel(text=arcade.VERSION),
            row=0,
            column=1,
        )
        self.grid.add(
            arcade.gui.UILabel(text="Today: "),
            row=1,
            column=0,
        )
        self.grid.add(
            arcade.gui.UILabel(text=datetime.utcnow().isoformat()[:10]),
            row=1,
            column=1,
        )

        # add a horizontal boxlayout with buttons
        h_box = arcade.gui.UIBoxLayout(space_between=20, vertical=False)
        self.anchor.add(h_box, anchor_x="center_x", anchor_y="bottom", align_y=5)

        # Add a button to move the grid layout to top_right
        # top left
        move_left_button = arcade.gui.UIFlatButton(text="Top Left", width=150)
        move_left_button.disabled = True
        h_box.add(move_left_button)

        @move_left_button.event("on_click")
        def _(event):
            self.anchor.remove(self.grid)
            self.anchor.add(self.grid, anchor_x="left", anchor_y="top", align_x=10, align_y=-10)
            move_left_button.disabled = True
            move_right_button.disabled = False

        move_right_button = arcade.gui.UIFlatButton(text="Top Right", width=150)
        h_box.add(move_right_button)

        @move_right_button.event("on_click")
        def _(event):
            self.anchor.remove(self.grid)
            self.anchor.add(self.grid, anchor_x="right", anchor_y="top", align_x=-10, align_y=-10)
            move_right_button.disabled = True
            move_left_button.disabled = False

    def on_draw_before_ui(self):
        # Add draw commands that should be below the UI
        pass

    def on_draw_after_ui(self):
        # Add draw commands that should be on top of the UI (uncommon)
        pass


if __name__ == "__main__":
    window = arcade.Window(title="GUI Example: Layouts")
    window.show_view(LayoutView())
    window.run()
