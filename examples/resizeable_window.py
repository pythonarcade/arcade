"""
Example showing how to draw text to the screen.
"""
import arcade

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
START_Y = 0
END_Y = 2000
STEP_Y = 50

START_X = 0
END_X = 4000
STEP_X = 50


class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        super().__init__(width, height, title="Resizing Window Example", resizable=True)

        arcade.set_background_color(arcade.color.WHITE)
        self.text_angle = 0
        self.time_elapsed = 0

        self.y_list = []
        for y in range(START_Y, END_Y, STEP_Y):
            my_text = arcade.create_text(f"{y}", arcade.color.BLACK, 12, anchor_x="left", anchor_y="bottom")
            self.y_list.append(my_text)

        self.x_list = []
        for x in range(START_X, END_X, STEP_X):
            my_text = arcade.create_text(f"{x}", arcade.color.BLACK, 12, anchor_x="left", anchor_y="bottom")
            self.x_list.append(my_text)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        print(f"Window resized to: {width}, {height}")

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()
        i = 0
        for y in range(START_Y, END_Y, STEP_Y):
            arcade.draw_point(0, y, arcade.color.BLUE, 5)
            arcade.render_text(self.y_list[i], 5, y)
            i += 1

        i = 0
        for x in range(START_X, END_X, STEP_X):
            arcade.draw_point(x, 0, arcade.color.BLUE, 5)
            arcade.render_text(self.x_list[i], x, 5)
            i += 1


def main():
    window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)

    arcade.run()

main()
