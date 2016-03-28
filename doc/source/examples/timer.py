"""
Show a timer on-screen.

"""
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def setup(self):
        """
        Set up the application.
        """
        self.total_time = 0.0
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        """ Use this function to draw everything to the screen. """

        # Start the render. This must happen before any drawing
        # commands. We do NOT need an stop render command.
        arcade.start_render()

        # Calculate minutes
        minutes = int(self.total_time) // 60

        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.total_time) % 60

        output = "Time: {:02d}:{:02d}".format(minutes, seconds)
        arcade.draw_text(output, 300, 300, arcade.color.BLACK, 30)

    def animate(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        self.total_time += delta_time


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
window.setup()

arcade.run()
