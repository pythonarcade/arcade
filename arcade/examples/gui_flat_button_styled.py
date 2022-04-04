"""
Example code showing how to style UIFlatButtons.
"""
import arcade
import arcade.gui
import arcade.gui.widgets.buttons
import arcade.gui.widgets.layout
from arcade.experimental.uistyle import UIFlatButtonStyle


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
        default_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": (21, 19, 21),
            # used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.WHITE,  # also used when hovered
            "font_color_pressed": arcade.color.BLACK,
        }

        red_style = UIFlatButtonStyle(
            normal_font_name=("calibri", "arial"),
            normal_font_size=15,
            normal_font_color=arcade.color.WHITE,
            normal_border_width=2,
            normal_border=None,
            normal_bg=arcade.color.REDWOOD,
            hovered_font_name=("calibri", "arial"),
            hovered_font_size=17,
            hovered_font_color=arcade.color.WHITE,
            hovered_border_width=2,
            hovered_border=arcade.color.WHITE,
            hovered_bg=arcade.color.REDWOOD,
            pressed_bg=arcade.color.WHITE,
            pressed_border=arcade.color.RED,
            pressed_font_color=arcade.color.RED,
        )

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.widgets.layout.UIBoxLayout(space_between=20)

        # Create the buttons
        demo_button_1 = arcade.gui.widgets.buttons.UIFlatButton(
            text="Demo 1", width=200, style=default_style
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
