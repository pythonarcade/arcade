"""
Example showing how to draw text to the screen using Text objects.
This is much faster than using draw_text

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.drawing_text_objects
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

        # Add the screen title
        start_x = 0
        start_y = SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 1.5
        self.title = arcade.Text(
            "Text Drawing Examples",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE * 2,
            width=SCREEN_WIDTH,
            align="center",
        )

        # start_x and start_y make the start point for the text. We draw a dot to make it
        # easy too see the text in relation to its start x and y.
        start_x = 10
        start_y = SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 3
        self.fonts = arcade.Text(
            "Fonts:",
            start_x,
            start_y,
            arcade.color.FRENCH_WINE,
            DEFAULT_FONT_SIZE, bold=True,
        )

        # Move the y value down to create another line of text
        start_y -= DEFAULT_LINE_HEIGHT
        self.font_default = arcade.Text(
            "Default Font (Arial)",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE    
        )

        # Show some built-in fonts
        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_blocks = arcade.Text(
            "Kenney Blocks Font",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Blocks",
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_future = arcade.Text(
            "Kenney Future Font",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Future",
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_high = arcade.Text(
            "Kenney High Font",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney High"
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_high_square = arcade.Text(
            "Kenney High Square Font",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney High Square",
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_mini_square = arcade.Text(
            "Kenney Mini Square Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Mini Square",   
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_pixel = arcade.Text(
            "Kenney Pixel Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Pixel",
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_pixel_square = arcade.Text(
            "Kenney Pixel Square Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Pixel Square",
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_rocket = arcade.Text(
            "Kenney Rocket Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Rocket",    
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_rocket_square = arcade.Text(
            "Kenney Rocket Square Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Rocket Square",
        )

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
        self.font_times_new_roman = arcade.Text(
            "Times New Roman (Or closest match on system)",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name=(
                "Times New Roman",  # Comes with Windows
                "Times",  # MacOS may sometimes have this variant
                "Liberation Serif"  # Common on Linux systems
            )
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.multi_line_breaks = arcade.Text(
            "Multi-Line\ntext using\n\\n characters.",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE / 2,
            multiline=True,
            width=300,
        )

        start_y -= DEFAULT_LINE_HEIGHT * 1.5
        self.multiline_wrap = arcade.Text(
            "Wrapping really long text automatically to a new line. "
            "The quick brown fox jumped over the lazy dogs.",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE / 2,
            multiline=True,
            width=300
        )

        # --- Column 2 ---
        start_x = 750
        start_y = SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 3
        self.text_positioning = arcade.Text(
            "Text Positioning:",
            start_x,
            start_y,
            arcade.color.FRENCH_WINE,
            DEFAULT_FONT_SIZE,
            bold=True,
        )

        # start_x and start_y make the start point for the text.
        # We draw a dot to make it easy too see the text in relation to
        # its start x and y.
        start_y -= DEFAULT_LINE_HEIGHT

        self.default_baseline_left = arcade.Text(
            "Default of 'baseline' and 'Left'",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.bottom_left = arcade.Text(
            "'bottom' and 'left'",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            anchor_x="left",
            anchor_y="bottom",
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.top_left = arcade.Text(
            "'top' and 'left'",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            anchor_x="left",
            anchor_y="top",            
        )

        start_y -= DEFAULT_LINE_HEIGHT * 2
        self.basline_center = arcade.Text(
            "'baseline' and 'center'",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            anchor_x="center",
            anchor_y="baseline",
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.baseline_right = arcade.Text(
            "'baseline' and 'right'",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            anchor_x="right",
            anchor_y="baseline",
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.center_center = arcade.Text(
            "'center' and 'center'",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            anchor_x="center",
            anchor_y="center",
        )

        start_y -= DEFAULT_LINE_HEIGHT * 4
        # start_x = 0
        # start_y = 0
        self.rotating_text = arcade.Text(
            "Rotating Text",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            anchor_x="center",
            anchor_y="center",
            rotation=self.text_angle
        )

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

        # Draw all the text objects
        # Column 1
        self.title.draw()
        self.fonts.draw()
        self.font_default.draw()
        self.font_kenney_blocks.draw()
        self.font_kenney_future.draw()
        self.font_kenney_high.draw()
        self.font_kenney_high_square.draw()
        self.font_kenney_mini_square.draw()
        self.font_kenney_pixel.draw()
        self.font_kenney_pixel_square.draw()
        self.font_kenney_rocket.draw()
        self.font_kenney_rocket_square.draw()
        self.font_times_new_roman.draw()
        self.multi_line_breaks.draw()
        self.multiline_wrap.draw()

        # Column 2
        self.text_positioning.draw()

        arcade.draw_point(
            self.default_baseline_left.x,
            self.default_baseline_left.y,
            arcade.color.BARN_RED,
            5,
        )
        self.default_baseline_left.draw()

        arcade.draw_point(
            self.bottom_left.x,
            self.bottom_left.y,
            arcade.color.BARN_RED,
            5,    
        )
        self.bottom_left.draw()

        arcade.draw_point(
            self.top_left.x,
            self.top_left.y,
            arcade.color.BARN_RED,
            5,
        )
        self.top_left.draw()

        arcade.draw_point(
            self.basline_center.x,
            self.basline_center.y,
            arcade.color.BARN_RED,
            5
        )
        self.basline_center.draw()

        arcade.draw_point(
            self.baseline_right.x,
            self.baseline_right.y,
            arcade.color.BARN_RED,
            5,
        )
        self.baseline_right.draw()

        arcade.draw_point(
            self.center_center.x,
            self.center_center.y,
            arcade.color.BARN_RED,
            5,
        )
        self.center_center.draw()

        arcade.draw_point(
            self.rotating_text.x,
            self.rotating_text.y,
            arcade.color.BARN_RED,
            5,
        )
        self.rotating_text.rotation = self.text_angle
        self.rotating_text.draw()


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
