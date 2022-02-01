"""
Example code showing how to style UIFlatButtons.
"""
import arcade
import arcade.gui


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

        red_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": None,
            "bg_color": arcade.color.REDWOOD,

            # used if button is pressed
            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.RED,  # also used when hovered
            "font_color_pressed": arcade.color.RED,
        }

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        # Create the buttons
        demo_button_1 = arcade.gui.UIFlatButton(text="Demo 1", width=200, style=default_style)
        demo_button_2 = arcade.gui.UIFlatButton(text="Demo 2", width=200, style=red_style)

        self.v_box.add(demo_button_1)
        self.v_box.add(demo_button_2)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = MyWindow()
arcade.run()
