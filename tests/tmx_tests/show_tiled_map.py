"""
Load a Tiled map file

Artwork from: http://kenney.nl
Tiled available from: http://www.mapeditor.org/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_tiled_map
"""

import arcade
import os
import time

TILE_SCALING = 0.5
PLAYER_SCALING = 1

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Tiled Map Example"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN_TOP = 60
VIEWPORT_MARGIN_BOTTOM = 60
VIEWPORT_RIGHT_MARGIN = 270
VIEWPORT_LEFT_MARGIN = 270

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = 23
GRAVITY = 1.1


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.tile_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None

        self.view_left = 0
        self.view_bottom = 0
        self.end_of_map = 0
        self.game_over = False
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None

    def setup(self):
        """ Set up the game and initialize the variables. """

        map_name = "../tmx_maps/rotation.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # --- Platforms ---
        self.wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites', TILE_SCALING)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.wall_list.draw()

def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
