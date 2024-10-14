"""
Sprite Collect Coins

A simple game demonstrating an easy way to create and use sprites.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the
command line with:
python -m arcade.examples.sprite_collect_coins
"""

import random
import arcade

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.4
COIN_COUNT = 50

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprite Collect Coins Example"


class GameView(arcade.View):

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_list = None
        self.coin_list = None

        # Create a variable to hold the player sprite
        self.player_sprite = None

        # Variables to hold the score and the Text object displaying it
        self.score = 0
        self.score_display = None

        # Hide the mouse cursor while it's over the window
        self.window.set_mouse_visible(False)

        self.background_color = arcade.color.AMAZON

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Create the sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Reset the score and the score display
        self.score = 0
        self.score_display = arcade.Text(
            text="Score: 0", x=10, y=20,
            color=arcade.color.WHITE, font_size=14)

        # Set up the player
        # Character image from kenney.nl
        img = ":resources:images/animated_characters/female_person/femalePerson_idle.png"
        self.player_sprite = arcade.Sprite(img, scale=SPRITE_SCALING_PLAYER)
        self.player_sprite.position = 50, 50
        self.player_list.append(self.player_sprite)

        # Create the coins
        for i in range(COIN_COUNT):

            # Create the coin instance
            # Coin image from kenney.nl
            coin = arcade.Sprite(":resources:images/items/coinGold.png",
                                 scale=SPRITE_SCALING_COIN)

            # Position the coin
            coin.center_x = random.randrange(WINDOW_WIDTH)
            coin.center_y = random.randrange(WINDOW_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def on_draw(self):
        """ Draw everything """

        # Clear the screen to only show the background color
        self.clear()

        # Draw the sprites
        self.coin_list.draw()
        self.player_list.draw()

        # Draw the score Text object on the screen
        self.score_display.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the player sprite to place its center on the mouse x, y
        self.player_sprite.position = x, y

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Generate a list of all sprites that collided with the player.
        coins_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                              self.coin_list)

        # Keep track of the score from before collisions occur
        old_score = self.score

        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1

        # Update the score display if the score changed this tick
        if old_score != self.score:
            self.score_display.text = f"Score: {self.score}"


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
