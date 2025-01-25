"""
Example showing how to draw localized text to the screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.text_loc_example_start
"""
import arcade

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
WINDOW_TITLE = "Localizing Text Example"


class GameView(arcade.View):
    """
    Main application class.
    """
    def __init__(self):
        super().__init__()
        self.window.background_color = arcade.color.WHITE
        self.text = arcade.Text(
            "Simple line of text in 12 point",
            50.0, 450.0, arcade.color.BLACK, 12
        )

    def on_draw(self):
        """
        Render the screen.
        """
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # We draw a dot to make it clear how the text relates to the text
        arcade.draw_point(self.text.x, self.text.y, arcade.color.BLUE, 5)
        self.text.draw()


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()

    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
