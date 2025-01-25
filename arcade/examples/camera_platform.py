"""
Camera Example

Artwork from: https://kenney.nl
Tiled available from: https://www.mapeditor.org/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.camera_platform
"""

import time

import arcade

TILE_SCALING = 0.5
PLAYER_SCALING = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

WINDOW_TITLE = "Camera Example"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

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

# Map Layers
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BOMBS = "Bombs"


class GameView(arcade.View):
    """Main application class."""

    def __init__(self):
        """
        Initializer
        """
        super().__init__()

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Set up the player
        self.score = 0
        self.player_sprite = None

        self.physics_engine = None
        self.top_of_map = 0
        self.end_of_map = 0
        self.game_over = False
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None

        # Cameras
        self.camera: arcade.camera.Camera2D = None
        self.gui_camera = None

        self.camera_shake = None

        self.shake_offset_1 = 0
        self.shake_offset_2 = 0
        self.shake_vel_1 = 0
        self.shake_vel_2 = 0

        # Text
        self.text_fps = arcade.Text(
            "",
            x=10,
            y=40,
            color=arcade.color.BLACK,
            font_size=14,
        )
        self.text_score = arcade.Text(
            f"Score: {self.score}",
            x=10,
            y=20,
            color=arcade.color.BLACK,
            font_size=14,
        )

    def setup(self):
        """Set up the game and initialize the variables."""

        # Map name
        map_name = ":resources:tiled_maps/level_1.json"

        # Layer Specific Options for the Tilemap
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_BOMBS: {
                "use_spatial_hash": True,
            },
        }

        # Load in TileMap
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initiate New Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set up the player
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=PLAYER_SCALING,
        )

        # Starting position of the player
        self.player_sprite.center_x = 196
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        self.camera = arcade.camera.Camera2D()

        self.camera_shake = arcade.camera.grips.ScreenShake2D(self.camera.view_data,
                                                              max_amplitude=12.5,
                                                              acceleration_duration=0.05,
                                                              falloff_time=0.20,
                                                              shake_frequency=15.0)

        # Center camera on user
        self.pan_camera_to_user()

        # Calculate the right edge of the my_map in pixels
        self.top_of_map = self.tile_map.height * GRID_PIXEL_SIZE
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            self.background_color = self.tile_map.background_color

        # Keep player from running through the wall_list layer
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            self.scene.get_sprite_list(LAYER_NAME_PLATFORMS),
            gravity_constant=GRAVITY,
        )

        self.game_over = False

    def on_resize(self, width, height):
        """Resize window"""
        super().on_resize(width, height)
        self.camera.match_window()

    def on_draw(self):
        """Render the screen."""
        self.clear()

        self.camera_shake.update_camera()
        with self.camera.activate():
            # Draw our Scene
            self.scene.draw()
        # Readjust the camera so the screen shake doesn't affect
        # the camera following algorithm.
        self.camera_shake.readjust_camera()

        with self.window.default_camera.activate():
            # Update fps text periodically
            if self.last_time and self.frame_count % 60 == 0:
                fps = 1.0 / (time.time() - self.last_time) * 60
                self.text_fps.text = f"FPS: {fps:5.2f}"

            self.text_fps.draw()

            if self.frame_count % 60 == 0:
                self.last_time = time.time()

            # Draw Score
            self.text_score.draw()

            # Draw game over
            if self.game_over:
                arcade.draw_text("Game Over", self.width/2, self.height/2, arcade.color.BLACK,
                                 30)

        self.frame_count += 1

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed
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

    def pan_camera_to_user(self, panning_fraction: float = 1.0):
        """
        Manage Scrolling

        Args:
            panning_fraction:
                Number from 0 to 1. Higher the number, faster we
                pan the camera to the user.
        """

        # This spot would center on the user
        screen_center_x, screen_center_y = self.player_sprite.position
        if screen_center_x < self.camera.viewport_width/2:
            screen_center_x = self.camera.viewport_width/2
        if screen_center_y < self.camera.viewport_height/2:
            screen_center_y = self.camera.viewport_height/2
        user_centered = screen_center_x, screen_center_y

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position,
            user_centered,
            panning_fraction,
        )

    def on_update(self, delta_time):
        """Movement and game logic"""

        if self.player_sprite.right >= self.end_of_map:
            self.game_over = True

        # Call update on all sprites
        if not self.game_over:
            self.physics_engine.update()
            self.camera_shake.update(delta_time)

        coins_hit = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene.get_sprite_list("Coins")
        )
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.score += 1

        # Bomb hits
        bombs_hit = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene.get_sprite_list("Bombs")
        )
        for bomb in bombs_hit:
            bomb.remove_from_sprite_lists()
            self.camera_shake.start()

        # Pan to the user
        self.pan_camera_to_user(panning_fraction=0.12)

        # Update score text
        self.text_score.text = f"Score: {self.score}"


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
