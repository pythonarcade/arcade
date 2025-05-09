"""
Platformer Template

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.template_platformer
"""
import arcade
from arcade.types import Color

# --- Constants
WINDOW_TITLE = "Platformer"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# Camera constants
FOLLOW_DECAY_CONST = 0.3  # get within 1% of the target position within 2 seconds


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__()

        # A Camera that can be used for scrolling the screen
        self.camera_sprites = arcade.Camera2D()

        # A rectangle that is used to constrain the camera's position.
        # we update it when we load the tilemap
        self.camera_bounds = self.window.rect

        # A non-scrolling camera that can be used to draw GUI elements
        self.camera_gui = arcade.Camera2D()

        # The scene which helps draw multiple spritelists in order.
        self.scene = self.create_scene()

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            scale=CHARACTER_SCALING,
        )

        # Our physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

        # Keep track of the score
        self.score = 0

        # What key is pressed down?
        self.left_key_down = False
        self.right_key_down = False

        # Text object to display the score
        self.score_display = arcade.Text(
            "Score: 0",
            x=10,
            y=10,
            color=arcade.csscolor.WHITE,
            font_size=18,
        )

    def create_scene(self) -> arcade.Scene:
        """Load the tilemap and create the scene object."""
        # Our TileMap Object
        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for collision detection.
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }
        tile_map = arcade.load_tilemap(
            ":resources:tiled_maps/map.json",
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        # Set the window background color to the same as the map if it has one
        if tile_map.background_color:
            self.window.background_color = Color.from_iterable(tile_map.background_color)

        # Use the tilemap's size to correctly set the camera's bounds.
        # Because how how shallow the map is we don't offset the bounds height
        self.camera_bounds = arcade.LRBT(
            self.window.width/2.0,
            tile_map.width * GRID_PIXEL_SIZE - self.window.width/2.0,
            self.window.height/2.0,
            tile_map.height * GRID_PIXEL_SIZE
        )


        # Our Scene Object
        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        return arcade.Scene.from_tilemap(tile_map)

    def reset(self):
        """Reset the game to the initial state."""
        self.score = 0
        # Load a fresh scene to get the coins back
        self.scene = self.create_scene()

        # Move the player to start position
        self.player_sprite.position = (128, 128)
        # Add the player to the scene
        self.scene.add_sprite("Player", self.player_sprite)

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Draw the map with the sprite camera
        with self.camera_sprites.activate():
            # Draw our Scene
            # Note, if you a want pixelated look, add pixelated=True to the parameters
            self.scene.draw()

        # Draw the score with the gui camera
        with self.camera_gui.activate():
            # Draw our score on the screen. The camera keeps it in place.
            self.score_display.text = f"Score: {self.score}"
            self.score_display.draw()

    def update_player_speed(self):
        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0

        if self.left_key_down and not self.right_key_down:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_key_down and not self.left_key_down:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        # Jump
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED

        # Left
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = True
            self.update_player_speed()

        # Right
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
            self.update_player_speed()

    def center_camera_to_player(self):
        # Move the camera to center on the player
        self.camera_sprites.position = arcade.math.smerp_2d(
            self.camera_sprites.position,
            self.player_sprite.position,
            self.window.delta_time,
            FOLLOW_DECAY_CONST,
        )

        # Constrain the camera's position to the camera bounds.
        self.camera_sprites.view_data.position = arcade.camera.grips.constrain_xy(
            self.camera_sprites.view_data, self.camera_bounds
        )

    def on_update(self, delta_time: float):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Add one to the score
            self.score += 1

        # Position the camera
        self.center_camera_to_player()

    def on_resize(self, width: int, height: int):
        """ Resize window """
        super().on_resize(width, height)
        # Update the cameras to match the new window size
        self.camera_sprites.match_window()
        # The position argument keeps `0, 0` in the bottom left corner.
        self.camera_gui.match_window(position=True)


def main():
    """Main function"""
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()
    game.reset()

    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
