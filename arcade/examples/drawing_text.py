"""
Example showing how to draw text to the screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.drawing_text
"""
import arcade

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        super().__init__(width, height, title="Drawing Text Example")

        arcade.set_background_color(arcade.color.WHITE)
        self.text_angle = 0
        self.time_elapsed = 0.0

    def update(self, delta_time):
        self.text_angle += 1
        self.time_elapsed += delta_time

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        # start_x and start_y make the start point for the text. We draw a dot to make it easy too see
        # the text in relation to its start x and y.
        start_x = 50
        start_y = 450
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)

        arcade.draw_text("Simple line of text in 12 point", start_x, start_y, arcade.color.BLACK, 12, )

        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        start_x = 50
        start_y = 400
        arcade.draw_text("Text anchored 'top' and 'left'.",
                         start_x, start_y, arcade.color.BLACK, 12, anchor_x="left", anchor_y="top")

        start_y = 350
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("14 point multi\nline\ntext",
                         start_x, start_y, arcade.color.BLACK, 14, anchor_y="top")

        start_y = 450
        start_x = 300
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("Set of text\nthat\nis centered.",
                         start_x, start_y, arcade.color.BLACK, 14, width=200, align="center", anchor_y="top")

        start_y = 250
        start_x = 300
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("Text centered on\na point",
                         start_x, start_y, arcade.color.BLACK, 14, width=200, align="center",
                         anchor_x="center", anchor_y="center")

        start_y = 150
        start_x = 300
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("Text rotated on\na point", start_x, start_y,
                         arcade.color.BLACK, 14, width=200, align="center", anchor_x="center",
                         anchor_y="center", rotation=self.text_angle)

        start_y = 150
        start_x = 20
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text("Sideways text", start_x, start_y,
                         arcade.color.BLACK, 14, width=200, align="center",
                         anchor_x="center", anchor_y="center", rotation=90.0)

        start_y = 20
        start_x = 50
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.draw_text(f"Time elapsed: {self.time_elapsed:7.1f}",
                         start_x, start_y, arcade.color.BLACK, 14)


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()


if __name__ == "__main__":
    main()
