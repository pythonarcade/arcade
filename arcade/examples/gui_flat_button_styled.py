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


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UIFlatButton Example", resizable=True)

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

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

        self.manager.add(ui_anchor_layout)

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = MyWindow()
arcade.run()
