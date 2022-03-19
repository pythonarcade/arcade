"""
Camera Example

Artwork from: https://kenney.nl
Tiled available from: https://www.mapeditor.org/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.camera_example
"""

import time

import arcade

TILE_SCALING = 0.5
PLAYER_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_TITLE = "Camera Example"
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


class MyGame(arcade.Window):
    """Main application class."""

    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

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
        self.camera = None
        self.gui_camera = None

        self.shake_offset_1 = 0
        self.shake_offset_2 = 0
        self.shake_vel_1 = 0
        self.shake_vel_2 = 0

        # Text
        self.text_fps = arcade.Text(
            "",
            start_x=10,
            start_y=40,
            color=arcade.color.BLACK,
            font_size=14,
        )
        self.text_score = arcade.Text(
            f"Score: {self.score}",
            start_x=10,
            start_y=20,
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
            PLAYER_SCALING,
        )

        # Starting position of the player
        self.player_sprite.center_x = 196
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

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
        self.camera.resize(width, height)
        self.gui_camera.resize(width, height)

    def on_draw(self):
        """Render the screen."""
        self.clear()

        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        self.gui_camera.use()

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
            x = 200 + self.camera.position[0]
            y = 200 + self.camera.position[1]
            arcade.draw_text("Game Over", x, y, arcade.color.BLACK, 30)

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

        :param panning_fraction: Number from 0 to 1. Higher the number, faster we
                                 pan the camera to the user.
        """

        # This spot would center on the user
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        user_centered = screen_center_x, screen_center_y

        self.camera.move_to(user_centered, panning_fraction)

    def on_update(self, delta_time):
        """Movement and game logic"""

        if self.player_sprite.right >= self.end_of_map:
            self.game_over = True

        # Call update on all sprites
        if not self.game_over:
            self.physics_engine.update()

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
            print("Pow")
            self.camera.shake((4, 7))

        # Pan to the user
        self.pan_camera_to_user(panning_fraction=0.12)

        # Update score text
        self.text_score.text = f"Score: {self.score}"


def main():
    """Get this game started."""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
