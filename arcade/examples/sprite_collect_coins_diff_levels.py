"""
Sprite Collect Coins with Different Levels

Simple program to show basic sprite usage.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_collect_coins_diff_levels
"""

import random
import arcade
import os

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Collect Coins with Different Levels Example"


class FallingCoin(arcade.Sprite):
    """ Simple sprite that falls down """

    def update(self):
        """ Move the coin """

        # Fall down
        self.center_y -= 2

        # Did we go off the screen? If so, pop back to the top.
        if self.top < 0:
            self.bottom = SCREEN_HEIGHT


class RisingCoin(arcade.Sprite):
    """ Simple sprite that falls up """

    def update(self):
        """ Move the coin """

        # Move up
        self.center_y += 2

        # Did we go off the screen? If so, pop back to the bottom.
        if self.bottom > SCREEN_HEIGHT:
            self.top = 0


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """ Initialize """

        # Call the parent class initializer
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.player_list = None
        self.coin_list = None

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        self.level = 1

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def level_1(self):
        for i in range(20):

            # Create the coin instance
            coin = arcade.Sprite("images/coin_01.png", SPRITE_SCALING / 3)

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def level_2(self):
        for i in range(30):

            # Create the coin instance
            coin = FallingCoin("images/gold_1.png", SPRITE_SCALING / 2)

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT, SCREEN_HEIGHT * 2)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def level_3(self):
        for i in range(30):

            # Create the coin instance
            coin = RisingCoin("images/gold_1.png", SPRITE_SCALING / 2)

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(-SCREEN_HEIGHT, 0)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def setup(self):
        """ Set up the game and initialize the variables. """

        self.score = 0
        self.level = 1

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite("images/character.png",
                                           SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        self.level_1()

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.player_sprite.draw()
        self.coin_list.draw()

        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 15)

        output = f"Level: {self.level}"
        arcade.draw_text(output, 10, 35, arcade.color.WHITE, 15)

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.coin_list.update()

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in hit_list:
            coin.kill()
            self.score += 1

        # See if we should go to level 2
        if len(self.coin_list) == 0 and self.level == 1:
            self.level += 1
            self.level_2()
        # See if we should go to level 3
        elif len(self.coin_list) == 0 and self.level == 2:
            self.level += 1
            self.level_3()


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
