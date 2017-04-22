import arcade

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600


class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        super().__init__(width, height)

        arcade.set_background_color(arcade.color.WHITE)


    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)

arcade.run()
