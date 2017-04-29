"""
Example showing how to draw text to the screen.
"""
import arcade

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500


class MyApplication(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height):
        super().__init__(width, height, title="Drawing Text Example")

        arcade.set_background_color(arcade.color.WHITE)
        self.text_angle = 0
        self.time_elapsed = 0
        self.t1 = arcade.create_text("Simple line of text in 12 point", arcade.color.BLACK, 12)
        self.t2 = arcade.create_text("Text anchored 'top' and 'left'.", arcade.color.BLACK, 12, anchor_x="left", anchor_y="top")
        self.t3 = arcade.create_text("14 point multi\nline\ntext", arcade.color.BLACK, 14, anchor_y="top")
        self.t4 = arcade.create_text("Set of text\nthat\nis centered.", arcade.color.BLACK, 14, width=200, align="center", anchor_y="top")
        self.t5 = arcade.create_text("Text centered on\na point", arcade.color.BLACK, 14, width=200, align="center", anchor_x="center", anchor_y="center")
        self.t6 = arcade.create_text("Text rotated on\na point", arcade.color.BLACK, 14, width=200, align="center", anchor_x="center", anchor_y="center")
        self.t7 = arcade.create_text("Sideways text", arcade.color.BLACK, 14, width=200, align="center", anchor_x="center", anchor_y="center")
        self.t8 = arcade.create_text("Time elapsed: {:5.1f}".format(self.time_elapsed), arcade.color.BLACK, 14)


    def animate(self, delta_time):
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
        cache = False

        arcade.render_text(self.t1, start_x, start_y)

        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        start_x = 50
        start_y = 400
        arcade.render_text(self.t2, start_x, start_y)

        start_y = 350
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.render_text(self.t3, start_x, start_y)

        start_y = 450
        start_x = 300
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.render_text(self.t4, start_x, start_y)


        start_y = 250
        start_x = 300
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.render_text(self.t5, start_x, start_y)

        start_y = 150
        start_x = 300
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.render_text(self.t6, start_x, start_y, rotation=self.text_angle)

        start_y = 150
        start_x = 20
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        arcade.render_text(self.t7, start_x, start_y, rotation=90.0)

        start_y = 20
        start_x = 50
        arcade.draw_point(start_x, start_y, arcade.color.BLUE, 5)
        text = "Time elapsed: {:5.1f}".format(self.time_elapsed)
        if text != self.t8.text:
            self.t8 = arcade.create_text(text, arcade.color.BLACK, 14)
        arcade.render_text(self.t8, start_x, start_y)


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)

arcade.run()
