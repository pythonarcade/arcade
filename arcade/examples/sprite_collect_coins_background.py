"""
Sprite Collect Coins with Background

Simple program to show basic sprite usage.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_collect_coins_background
"""
import random
import arcade

PLAYER_SCALING = 0.75
COIN_SCALING = 0.4

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprite Collect Coins with Background Example"


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        """ Initializer """

        # Call the parent class initializer
        super().__init__()

        # Background image will be stored in this variable
        self.background = arcade.load_texture(":resources:images/backgrounds/abstract_1.jpg")

        # Variables that will hold sprite lists
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=PLAYER_SCALING,
        )
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)
        self.coin_list = arcade.SpriteList()

        # Set up the player info
        self.score = 0
        self.score_text = arcade.Text("Score: 0", 10, 20, arcade.color.WHITE, 14)

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

        # Set the background color
        self.background_color = arcade.color.AMAZON

    def reset(self):
        """Restart the game."""
        # Sprite lists
        self.coin_list.clear()

        # Set up the player
        self.score = 0
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50

        for i in range(50):
            # Create the coin instance
            coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=COIN_SCALING)

            # Position the coin
            coin.center_x = random.randrange(WINDOW_WIDTH)
            coin.center_y = random.randrange(WINDOW_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw the background texture
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        )

        # Draw all the sprites.
        self.coin_list.draw()
        self.player_list.draw()

        # Update the score text and draw it
        self.score_text.text = f"Score: {self.score}"
        self.score_text.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on the coin sprites (The sprites don't do much in this
        # example though.)
        self.coin_list.update()

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.R:
            self.reset()
        elif symbol == arcade.key.ESCAPE:
            self.window.close()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.reset()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
