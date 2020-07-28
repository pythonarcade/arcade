"""
Load a Tiled map file

Artwork from: http://kenney.nl
Tiled available from: http://www.mapeditor.org/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_tiled_map
"""

import time
import arcade
from arcade.experimental.camera import Camera2D

TILE_SCALING = 0.5
PLAYER_SCALING = 0.5

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
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

        # Sprite lists
        self.wall_list = None
        self.player_list = None
        self.coin_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None

        self.physics_engine = None
        self.end_of_map = 0
        self.game_over = False
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None

        self.zoom = 0

        self.camera = Camera2D(
            viewport=(0, 0, self.width, self.height),
            projection=(0, self.width, 0, self.height),
        )

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                           PLAYER_SCALING)

        # Starting position of the player
        self.player_sprite.center_x = 196
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

        # Center camera on user
        user_centered = (
            self.player_sprite.center_x - self.width / 2,
            self.player_sprite.center_y - self.height / 2,
        )
        self.camera.scroll = user_centered

        map_name = ":resources:tmx_maps/level_1.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE

        # --- Platforms ---
        self.wall_list = arcade.tilemap.process_layer(my_map,
                                                      'Platforms',
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # --- Coins ---
        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      'Coins',
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Keep player from running through the wall_list layer
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY)

        self.game_over = False

    def on_resize(self, width, height):
        self.camera.viewport = 0, 0, width, height

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.zoom += scroll_y
        if self.zoom > 5:
            self.zoom = 5
        elif self.zoom < -5:
            self.zoom = -5

        self.camera.zoom = self.zoom * 20
        print(self.zoom)

    def on_draw(self):
        """ Render the screen. """

        self.camera.use()
        self.clear()

        self.frame_count += 1

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.player_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()

        # self.player_list.draw_hit_boxes(arcade.color.RED)
        # self.wall_list.draw_hit_boxes(arcade.color.RED)

        if self.last_time and self.frame_count % 60 == 0:
            fps = 1.0 / (time.time() - self.last_time) * 60
            self.fps_message = f"FPS: {fps:5.0f}"

        x = 10 + self.camera.scroll[0]
        y = 20 + self.camera.scroll[1]
        arcade.draw_text(f"Score: {self.score}", x, y, arcade.color.BLACK, 14)

        if self.fps_message:
            x = 10 + self.camera.scroll[0]
            y = 40 + self.camera.scroll[1]
            arcade.draw_text(self.fps_message, x, y, arcade.color.BLACK, 14)

        if self.frame_count % 60 == 0:
            self.last_time = time.time()

        if self.game_over:
            x = 200 + self.camera.scroll[0]
            y = 200 + self.camera.scroll[1]
            arcade.draw_text("Game Over", x, y, arcade.color.BLACK, 30)

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        if self.player_sprite.right >= self.end_of_map:
            self.game_over = True

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        if not self.game_over:
            self.physics_engine.update()

        coins_hit = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.score += 1

        # --- Manage Scrolling ---

        # This spot would center on the user
        user_centered = (
            self.player_sprite.center_x - SCREEN_WIDTH / 2,
            self.player_sprite.center_y - SCREEN_HEIGHT / 2,
        )
        # Center on user
        # self.camera.scroll = user_centered

        # Smooth scroll to user

        # Adjust this number between 0 to 1. Closer to 1, faster the pan.
        panning_fraction = 0.02

        cur_scroll = self.camera.scroll
        new_scroll = arcade.lerp(cur_scroll[0], user_centered[0], panning_fraction), \
            arcade.lerp(cur_scroll[1], user_centered[1], panning_fraction)
        self.camera.scroll = new_scroll


def main():
    """ Get this game started. """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
