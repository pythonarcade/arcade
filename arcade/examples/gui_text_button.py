"""
GUI Text Button

Simple program to show basic button usage.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gui_text_button
"""
import arcade
import random
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "GUI Text Button Example"


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Set window background
        arcade.set_background_color(arcade.color.AMAZON)

        # Variable that will hold state of game (pause/play)
        self.pause = False

        # Variable that will hold sprite lists
        self.coin_list = None

        # Variable that will hold buttons
        self.button_list = []

    def setup(self):
        """
        Set up the game and initialize the variables.
        """

        # Create random-located coins
        self.coin_list = arcade.SpriteList()
        for i in range(10):
            # Create coin
            coin = arcade.Sprite(":resources:images/items/coinGold.png", 0.25)
            # Set up random position of coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT)
            # Set up moving down for coin
            coin.change_y = -1
            # Add coin in list of coins
            self.coin_list.append(coin)

        # Create ours on-screen GUI buttons
        play_button = arcade.gui.TextButton(60, 570, 100, 40, "Start")
        # Set up function, that will be execute when the button be clicked
        play_button.click_action = self.resume_program
        self.button_list.append(play_button)

        stop_button = arcade.gui.TextButton(60, 515, 100, 40, "Stop")
        # Set up function, that will be execute when the button be clicked
        stop_button.click_action = self.pause_program
        self.button_list.append(stop_button)

    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()

        # Draw the coins
        self.coin_list.draw()

        # Draw the buttons
        for button in self.button_list:
            button.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        if not self.pause:
            self.coin_list.update()

            for coin in self.coin_list:
                if coin.top < 0:
                    coin.bottom = SCREEN_HEIGHT

    def pause_program(self):
        """
        Stop the game.
        """
        self.pause = True

    def resume_program(self):
        """
        Resume the game.
        """
        self.pause = False


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
