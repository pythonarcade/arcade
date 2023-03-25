"""
Menu.

Shows the usage of almost every gui widget, switching views and making a modal.
"""
import arcade

# Screen title and size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Making a Menu"


class MainView(arcade.View):
    """ Main application class."""

    def __init__(self):
        super().__init__()

    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
    main_view = MainView()
    window.show_view(main_view)
    arcade.run()


if __name__ == "__main__":
    main()
