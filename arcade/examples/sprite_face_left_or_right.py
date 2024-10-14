"""
Sprite Facing Left or Right
Face left or right depending on our direction

Simple program to show basic sprite usage.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_face_left_or_right
"""

import arcade

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sprite Face Left or Right Example"

MOVEMENT_SPEED = 5

# Index of textures, first element faces left, second faces right
TEXTURE_LEFT = 0
TEXTURE_RIGHT = 1


class Player(arcade.Sprite):

    def __init__(self, left_texture, right_texture):
        super().__init__(left_texture, scale=SPRITE_SCALING)
        self.textures.append(right_texture)

    def update(self, delta_time: float = 1/60):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Figure out if we should face left or right
        if self.change_x < 0:
            self.texture = self.textures[TEXTURE_LEFT]
        elif self.change_x > 0:
            self.texture = self.textures[TEXTURE_RIGHT]


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_sprite_list = None

        # Set up the player info
        self.player_sprite = None

        # Set the background color
        self.background_color = arcade.color.AMAZON

        # Textures for left and right facing sprites
        self.left_texture = arcade.load_texture(":resources:images/enemies/bee.png")
        self.right_texture = self.left_texture.flip_left_right()

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_sprite_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(self.left_texture, self.right_texture)
        self.player_sprite.center_x = WINDOW_WIDTH / 2
        self.player_sprite.center_y = WINDOW_HEIGHT / 2
        self.player_sprite_list.append(self.player_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # Clear the screen with the configured background color
        self.clear()

        # Draw all the sprites.
        self.player_sprite_list.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.player_sprite_list.update(delta_time)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key in (arcade.key.UP, arcade.key.W):
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.player_sprite.change_x = MOVEMENT_SPEED
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.W, arcade.key.S):
            self.player_sprite.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D):
            self.player_sprite.change_x = 0


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
