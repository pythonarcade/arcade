import arcade
import arcade.gui


class MyView(arcade.View):
    def __init__(self, my_window: arcade.Window):
        super().__init__(my_window)

        # This creates a "manager" for all our UI elements
        self.ui_manager = arcade.gui.UIManager(self.window)

        # Add in a simple label element.
        self.ui_manager.add_ui_element(
            arcade.gui.UILabel(
                text="Hello world",
                center_x=self.window.width / 2,
                center_y=self.window.height / 2,
            )
        )

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
