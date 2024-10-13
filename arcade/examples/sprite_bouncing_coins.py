"""
Sprite Simple Bouncing

Simple program to show how to bounce items.
This only works for straight vertical and horizontal angles.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_bouncing_coins
"""

import arcade
import random

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 832
WINDOW_HEIGHT = 640
WINDOW_TITLE = "Sprite Bouncing Coins"

MOVEMENT_SPEED = 5


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__()

        # Sprite lists
        self.coin_list = None
        self.wall_list = None

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # -- Set up the walls

        # Create horizontal rows of boxes
        for x in range(32, WINDOW_WIDTH, 64):
            # Bottom edge
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png",
                scale=SPRITE_SCALING,
            )
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

            # Top edge
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png",
                scale=SPRITE_SCALING,
            )
            wall.center_x = x
            wall.center_y = WINDOW_HEIGHT - 32
            self.wall_list.append(wall)

        # Create vertical columns of boxes
        for y in range(96, WINDOW_HEIGHT, 64):
            # Left
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png",
                scale=SPRITE_SCALING,
            )
            wall.center_x = 32
            wall.center_y = y
            self.wall_list.append(wall)

            # Right
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png",
                scale=SPRITE_SCALING,
                )
            wall.center_x = WINDOW_WIDTH - 32
            wall.center_y = y
            self.wall_list.append(wall)

        # Create boxes in the middle
        for x in range(128, WINDOW_WIDTH, 196):
            for y in range(128, WINDOW_HEIGHT, 196):
                wall = arcade.Sprite(
                    ":resources:images/tiles/boxCrate_double.png",
                    scale=SPRITE_SCALING,
                )
                wall.center_x = x
                wall.center_y = y
                # wall.angle = 45
                self.wall_list.append(wall)

        # Create coins
        for i in range(10):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=0.25)
            coin.center_x = random.randrange(100, 700)
            coin.center_y = random.randrange(100, 500)
            while coin.change_x == 0 and coin.change_y == 0:
                coin.change_x = random.randrange(-4, 5)
                coin.change_y = random.randrange(-4, 5)

            self.coin_list.append(coin)

        # Set the background color
        self.background_color = arcade.color.AMAZON

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.wall_list.draw()
        self.coin_list.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        for coin in self.coin_list:

            coin.center_x += coin.change_x
            walls_hit = arcade.check_for_collision_with_list(coin, self.wall_list)
            for wall in walls_hit:
                if coin.change_x > 0:
                    coin.right = wall.left
                elif coin.change_x < 0:
                    coin.left = wall.right
            if len(walls_hit) > 0:
                coin.change_x *= -1

            coin.center_y += coin.change_y
            walls_hit = arcade.check_for_collision_with_list(coin, self.wall_list)
            for wall in walls_hit:
                if coin.change_y > 0:
                    coin.top = wall.bottom
                elif coin.change_y < 0:
                    coin.bottom = wall.top
            if len(walls_hit) > 0:
                coin.change_y *= -1


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
