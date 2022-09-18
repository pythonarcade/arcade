"""
This is the same as the examples for drawing text using the one-off draw_text function
as well as the Text objects example. This takes it one step further though. Here we are
creating Text objects, and then adding them to a Pyglet Batch object, and drawing them
all with one draw command.

Using this method, we can draw thousands and thousands of text objects with nearly the
same cost as drawing just one Text object directly.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.drawing_text_objects_batch
"""
import arcade
import pyglet.graphics

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

        self.batch = pyglet.graphics.Batch()

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
            batch=self.batch,
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
            batch=self.batch,
        )

        # Move the y value down to create another line of text
        start_y -= DEFAULT_LINE_HEIGHT
        self.font_default = arcade.Text(
            "Default Font (Arial)",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            batch=self.batch,    
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
            batch=self.batch,
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_future = arcade.Text(
            "Kenney Future Font",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Future",
            batch=self.batch,
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_high = arcade.Text(
            "Kenney High Font",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney High",
            batch=self.batch,
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_high_square = arcade.Text(
            "Kenney High Square Font",
            start_x,
            start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney High Square",
            batch=self.batch,
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_mini_square = arcade.Text(
            "Kenney Mini Square Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Mini Square",
            batch=self.batch,   
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_pixel = arcade.Text(
            "Kenney Pixel Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Pixel",
            batch=self.batch,
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_pixel_square = arcade.Text(
            "Kenney Pixel Square Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Pixel Square",
            batch=self.batch,
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_rocket = arcade.Text(
            "Kenney Rocket Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Rocket",
            batch=self.batch,    
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.font_kenney_rocket_square = arcade.Text(
            "Kenney Rocket Square Font",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name="Kenney Rocket Square",
            batch=self.batch,
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
            ),
            batch=self.batch,
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.multi_line_breaks = arcade.Text(
            "Multi-Line\ntext using\n\\n characters.",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE / 2,
            multiline=True,
            width=300,
            batch=self.batch,
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
            width=300,
            batch=self.batch,
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
            batch=self.batch,
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
            batch=self.batch,
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
            batch=self.batch,
        )

        start_y -= DEFAULT_LINE_HEIGHT
        self.top_left = arcade.Text(
            "'top' and 'left'",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            anchor_x="left",
            anchor_y="top",
            batch=self.batch,         
        )

        start_y -= DEFAULT_LINE_HEIGHT * 2
        self.basline_center = arcade.Text(
            "'baseline' and 'center'",
            start_x, start_y,
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            anchor_x="center",
            anchor_y="baseline",
            batch=self.batch,
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
            batch=self.batch,
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
            batch=self.batch,
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
            rotation=0,
            batch=self.batch,
        )

    def on_update(self, delta_time):
        self.text_angle += 1
        self.time_elapsed += delta_time
        self.rotating_text.rotation = self.text_angle

    def on_draw(self):
        """
        Render the screen.
        """
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Draw all the text objects
        with self.ctx.pyglet_rendering():
            self.batch.draw()

        arcade.draw_point(
            self.default_baseline_left.x,
            self.default_baseline_left.y,
            arcade.color.BARN_RED,
            5,
        )

        arcade.draw_point(
            self.bottom_left.x,
            self.bottom_left.y,
            arcade.color.BARN_RED,
            5,    
        )

        arcade.draw_point(
            self.top_left.x,
            self.top_left.y,
            arcade.color.BARN_RED,
            5,
        )

        arcade.draw_point(
            self.basline_center.x,
            self.basline_center.y,
            arcade.color.BARN_RED,
            5
        )

        arcade.draw_point(
            self.baseline_right.x,
            self.baseline_right.y,
            arcade.color.BARN_RED,
            5,
        )

        arcade.draw_point(
            self.center_center.x,
            self.center_center.y,
            arcade.color.BARN_RED,
            5,
        )

        arcade.draw_point(
            self.rotating_text.x,
            self.rotating_text.y,
            arcade.color.BARN_RED,
            5,
        )


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
