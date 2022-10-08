"""
Example showing how to draw text to the screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.drawing_text
"""
import arcade

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Drawing Text Example"
DEFAULT_LINE_HEIGHT = 45
DEFAULT_FONT_SIZE = 20


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.background_color = arcade.color.BEIGE
        self.text_angle = 0
        self.time_elapsed = 0.0

    def on_update(self, delta_time):
        self.text_angle += 1
        self.time_elapsed += delta_time

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Add the screen title
        start_x = 0
        start_y = SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 1.5
        arcade.draw_text("Text Drawing Examples",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE * 2,
                         width=SCREEN_WIDTH,
                         align="center")

        # start_x and start_y make the start point for the text. We draw a dot to make it
        # easy too see the text in relation to its start x and y.
        start_x = 10
        start_y = SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 3
        arcade.draw_text("Fonts:",
                         start_x,
                         start_y,
                         arcade.color.FRENCH_WINE,
                         DEFAULT_FONT_SIZE, bold=True)

        # Move the y value down to create another line of text
        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Default Font (Arial)",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE)

        # Show some built-in fonts
        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Kenney Blocks Font",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name="Kenney Blocks")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Kenney Future Font",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name="Kenney Future")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Kenney High Font",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name="Kenney High")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Kenney High Square Font",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name="Kenney High Square")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Kenney Mini Square Font",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name="Kenney Mini Square")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Kenney Pixel Font",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name="Kenney Pixel")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Kenney Pixel Square Font",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name="Kenney Pixel Square")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Kenney Rocket Font",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name="Kenney Rocket")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Kenney Rocket Square Font",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name="Kenney Rocket Square")

        start_y -= DEFAULT_LINE_HEIGHT
        # When trying to use system fonts, it can be risky to specify
        # only a single font because someone else's computer might not
        # have it installed. This is especially true if they run a
        # different operating system. For example, if you are on Windows
        # and a friend has a mac or Linux, they might not have the same
        # fonts. Your game could look different or broken on their computer.
        # One way around that is to provide multiple options for draw_text
        # to try. It will use the first one it finds, and use Arial as a
        # default if it can't find any of them.
        # In the example below, draw_text is given a tuple of names for very
        # similar fonts, each of which is common on a different major
        # operating systems.
        arcade.draw_text("Times New Roman (Or closest match on system)",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         font_name=(
                             "Times New Roman",  # Comes with Windows
                             "Times",  # MacOS may sometimes have this variant
                             "Liberation Serif"  # Common on Linux systems
                         ))

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_text("Multi-Line\ntext using\n\\n characters.",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE / 2,
                         multiline=True,
                         width=300)

        start_y -= DEFAULT_LINE_HEIGHT * 1.5
        arcade.draw_text("Wrapping really long text automatically to a new line. "
                         "The quick brown fox jumped over the lazy dogs.",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE / 2,
                         multiline=True,
                         width=300)

        # --- Column 2 ---
        start_x = 750
        start_y = SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 3
        arcade.draw_text("Text Positioning:",
                         start_x,
                         start_y,
                         arcade.color.FRENCH_WINE,
                         DEFAULT_FONT_SIZE,
                         bold=True)

        # start_x and start_y make the start point for the text.
        # We draw a dot to make it easy too see the text in relation to
        # its start x and y.
        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_point(start_x, start_y, arcade.color.BARN_RED, 5)
        arcade.draw_text("Default of 'baseline' and 'Left'",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE)

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_point(start_x, start_y, arcade.color.BARN_RED, 5)
        arcade.draw_text("'bottom' and 'left'",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         anchor_x="left",
                         anchor_y="bottom")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_point(start_x, start_y, arcade.color.BARN_RED, 5)
        arcade.draw_text("'top' and 'left'",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         anchor_x="left",
                         anchor_y="top")

        start_y -= DEFAULT_LINE_HEIGHT * 2
        arcade.draw_point(start_x, start_y, arcade.color.BARN_RED, 5)
        arcade.draw_text("'baseline' and 'center'",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="baseline")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_point(start_x, start_y, arcade.color.BARN_RED, 5)
        arcade.draw_text("'baseline' and 'right'",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         anchor_x="right",
                         anchor_y="baseline")

        start_y -= DEFAULT_LINE_HEIGHT
        arcade.draw_point(start_x, start_y, arcade.color.BARN_RED, 5)
        arcade.draw_text("'center' and 'center'",
                         start_x,
                         start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="center")

        start_y -= DEFAULT_LINE_HEIGHT * 4
        # start_x = 0
        # start_y = 0
        arcade.draw_point(start_x, start_y, arcade.color.BARN_RED, 5)
        arcade.draw_text("Rotating Text",
                         start_x, start_y,
                         arcade.color.BLACK,
                         DEFAULT_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="center",
                         rotation=self.text_angle)


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
