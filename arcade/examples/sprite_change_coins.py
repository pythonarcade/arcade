"""
Sprite Change Coins

This shows how you can change a sprite once it is hit, rather than eliminate it.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_change_coins
"""

import random
import arcade

SPRITE_SCALING = 0.4

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprite Change Coins"


class Collectable(arcade.Sprite):
    """ This class represents something the player collects. """

    def __init__(self, filename, scale):
        super().__init__(filename, scale=scale)
        # Flip this once the coin has been collected.
        self.changed = False


class GameView(arcade.View):
    """
    Main application class.a
    """

    def __init__(self):
        super().__init__()

        # Sprite lists
        self.player_list = None
        self.coin_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None
        self.bumper_texture = arcade.load_texture(":resources:images/pinball/bumper.png")

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=0.75,
        )
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        for i in range(50):
            # Create the coin instance
            coin = Collectable(
                ":resources:images/items/coinGold.png",
                scale=SPRITE_SCALING,
            )

            # Position the coin
            coin.center_x = random.randrange(WINDOW_WIDTH)
            coin.center_y = random.randrange(WINDOW_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

        # Set the background color
        self.background_color = arcade.color.AMAZON

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.coin_list.draw()
        self.player_list.draw()

        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.player_list.update()
        self.coin_list.update()

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        # Loop through each colliding sprite, change it, and add to the score.
        for coin in hit_list:
            # Have we collected this?
            if not coin.changed:
                # No? Then do so
                coin.texture = self.bumper_texture
                coin.changed = True
                coin.width = 30
                coin.height = 30
                self.score += 1


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
