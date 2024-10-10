"""
Sprites with Properties Example

Simple program to show how to store properties on sprites.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_properties
"""
import arcade

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprites with Properties Example"


INSTRUCTIONS1 = (
    "Touch a coin to set its intensity property to 'bright'."
    "Press 'R' to reset the sprites"
)
INSTRUCTIONS2 = "Touch the trigger at the bottom-right to destroy all 'bright' sprites."


class GameView(arcade.View):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_list = None
        self.coin_list = None

        # Set up the player info
        self.player_sprite = None

        # Set up sprite that will serve as trigger
        self.trigger_sprite = None

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)

        self.background_color = arcade.color.AMAZON

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        # Character image from kenney.nl
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=0.75,
        )
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 150
        self.player_list.append(self.player_sprite)

        # Create the sprites
        for x in range(180, 1100, 100):
            coin = arcade.Sprite(
                ":resources:images/items/coinGold.png",
                scale=0.3,
                center_x=x,
                center_y=400,
            )
            coin.intensity = 'dim'
            coin.alpha = 64
            self.coin_list.append(coin)

        # Create trigger
        self.trigger_sprite = arcade.Sprite(
            ":resources:images/pinball/bumper.png", scale=0.5,
            center_x=750, center_y=50,
        )

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.R:
            self.setup()

    def on_draw(self):
        """ Draw everything """
        self.clear()
        self.coin_list.draw()
        arcade.draw_sprite(self.trigger_sprite)
        self.player_list.draw()

        # Put the instructions on the screen.
        arcade.draw_text(INSTRUCTIONS1, 10, 90, arcade.color.WHITE, 14)
        arcade.draw_text(INSTRUCTIONS2, 10, 70, arcade.color.WHITE, 14)

        # Query the property on the coins and show results.
        coins_are_bright = [coin.intensity == 'bright' for coin in self.coin_list]
        output_any = f"Any sprites have intensity=bright? : {any(coins_are_bright)}"
        arcade.draw_text(output_any, 10, 40, arcade.color.WHITE, 14)
        output_all = f"All sprites have intensity=bright? : {all(coins_are_bright)}"
        arcade.draw_text(output_all, 10, 20, arcade.color.WHITE, 14)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the center of the player sprite to match the mouse x, y
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.coin_list.update()

        # Generate a list of all sprites that collided with the player.
        coins_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.coin_list,
        )

        # Loop through each colliding sprite to set intensity=bright
        for coin in coins_hit_list:
            coin.intensity = 'bright'
            coin.alpha = 255

        hit_trigger = arcade.check_for_collision(self.player_sprite, self.trigger_sprite)
        if hit_trigger:
            intense_sprites = [
                sprite for sprite in self.coin_list if sprite.intensity == 'bright'
            ]
            for coin in intense_sprites:
                coin.remove_from_sprite_lists()


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
