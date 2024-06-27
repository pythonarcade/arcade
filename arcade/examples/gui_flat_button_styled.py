"""
Example code showing how to style UIFlatButtons.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_flat_button_styled
"""
import arcade
import arcade.gui
import arcade.gui.widgets.buttons
import arcade.gui.widgets.layout
from arcade.gui import UIFlatButton


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.ui = arcade.gui.UIManager()

        # Render button
        red_style = {
            "normal": UIFlatButton.UIStyle(
                font_size=12,
                font_name=("calibri", "arial"),
                font_color=arcade.color.WHITE,
                bg=arcade.color.RED,
                border=None,
                border_width=0,
            ),
            "hover": UIFlatButton.UIStyle(
                font_size=12,
                font_name=("calibri", "arial"),
                font_color=arcade.color.WHITE,
                bg=arcade.color.REDWOOD,
                border=arcade.color.RED,
                border_width=2,
            ),
            "press": UIFlatButton.UIStyle(
                font_size=12,
                font_name=("calibri", "arial"),
                font_color=arcade.color.WHITE,
                bg=arcade.color.RED_BROWN,
                border=arcade.color.REDWOOD,
                border_width=2,
            ),
            "disabled": UIFlatButton.UIStyle(
                font_size=12,
                font_name=("calibri", "arial"),
                font_color=arcade.color.WHITE,
                bg=arcade.color.COOL_GREY,
                border=arcade.color.ASH_GREY,
                border_width=2,
            )
        }

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.widgets.layout.UIBoxLayout(space_between=20)

        # Create the buttons
        demo_button_1 = arcade.gui.widgets.buttons.UIFlatButton(
            text="Demo 1", width=200, style=UIFlatButton.DEFAULT_STYLE
        )
        demo_button_2 = arcade.gui.widgets.buttons.UIFlatButton(
            text="Demo 2", width=200, style=red_style
        )

        self.v_box.add(demo_button_1)
        self.v_box.add(demo_button_2)

        # Create a widget to hold the v_box widget, that will center the buttons
        ui_anchor_layout = arcade.gui.widgets.layout.UIAnchorLayout()
        ui_anchor_layout.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")

        self.ui.add(ui_anchor_layout)

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        # Disable UIManager when view gets inactive
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.window.close()


if __name__ == '__main__':
    window = arcade.Window(1280, 720, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
