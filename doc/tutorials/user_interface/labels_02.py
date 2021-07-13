import arcade
import arcade.gui

LABEL_LINE_HEIGHT = 60


class MyView(arcade.View):
    def __init__(self, my_window: arcade.Window):
        super().__init__(my_window)

        # This creates a "manager" for all our UI elements
        self.ui_manager = arcade.gui.UIManager(self.window, attach_callbacks=False)

        style_data = {"label": {"font_size": 40,
                                "font_color": arcade.color.WHITE,
                                "font_name": ["CENSCBK", "Arial"]
                                },
                      }

        style = arcade.gui.UIStyle(style_data)

        center_x = self.window.width / 2
        center_y = self.window.height - 40

        for text in ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]:

            # Add in a simple label element.
            self.ui_manager.add_ui_element(
                arcade.gui.UILabel(
                    text=text,
                    align="center",
                    width=self.window.width,
                    center_x=center_x,
                    center_y=center_y,
                    style=style
                )
            )

            center_y -= LABEL_LINE_HEIGHT

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
    window = arcade.Window(title="Arcade GUI Example")
    window.show_view(MyView(window))
    arcade.run()
