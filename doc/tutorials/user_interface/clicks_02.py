import arcade
import arcade.gui


class MyView(arcade.View):
    def __init__(self, my_window: arcade.Window):
        super().__init__(my_window)

        # This creates a "manager" for all our UI elements
        self.ui_manager = arcade.gui.UIManager(self.window, attach_callbacks=False)

        # Style our button. Styles can also be stored/loaded from default.yaml
        style_data = {"flatbutton": {"font_size": 40,
                                     "border_width": 2,
                                     "border_color_hover": arcade.color.WHITE,
                                     "border_color_press": arcade.color.WHITE,
                                     "font_color": arcade.color.BLACK,
                                     "font_color_hover": arcade.color.BLACK,
                                     "bg_color": (40, 40, 40),
                                     "bg_color_hover": (40, 40, 40),
                                     "bg_color_press": arcade.color.DARK_GRAY,
                                     "font_name": ["Calibri", "Arial"]
                                     },
                      }

        style = arcade.gui.UIStyle(style_data)

        # Create our button
        self.my_button = arcade.gui.UIFlatButton(
            text="Start Game",
            center_x=self.window.width / 2,
            center_y=self.window.height / 2,
            style=style,
            width=300,
            height=70
        )

        # Map that button's on_click method to this view's on_button_click method.
        self.my_button.on_click = self.on_button_click

        # Add in our element.
        self.ui_manager.add_ui_element(self.my_button)

    def on_button_click(self):
        print("Button has been clicked!")
        if self.my_button.text == "Start Game":
            self.my_button.text = "Stop Game"
        else:
            self.my_button.text = "Start Game"

    def on_draw(self):
        arcade.start_render()

        # This draws our elements
        self.ui_manager.on_draw()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

        # Registers handlers for GUI button clicks, etc.
        # We don't really use them in this example.
        self.ui_manager.enable()

    def on_hide_view(self):
        # This unregisters the manager's UI handlers,
        # Handlers respond to GUI button clicks, etc.
        self.ui_manager.disable()


if __name__ == "__main__":
    window = arcade.Window(title="Arcade GUI Tutorial")
    window.show_view(MyView(window))
    arcade.run()
