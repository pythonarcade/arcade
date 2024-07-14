"""
Load a Tiled map file

Artwork from: https://kenney.nl
Tiled available from: https://www.mapeditor.org/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_tiled_map
"""

import time

import arcade

TILE_SCALING = 0.5
PLAYER_SCALING = 1

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Sprite Tiled Map Example"
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


class MyGame(arcade.Window):
    """Main application class."""

    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Tilemap Object
        self.tile_map = None

        # Sprite lists
        self.player_list = None
        self.wall_list = None
        self.coin_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None

        self.physics_engine = None
        self.end_of_map = 0
        self.game_over = False
        self.last_time = None
        self.frame_count = 0

        # Cameras
        self.camera = None
        self.gui_camera = None

        # Text
        self.fps_text = arcade.Text(
            "",
            x=10,
            y=40,
            color=arcade.color.BLACK,
            font_size=14
        )
        self.distance_text = arcade.Text(
            "0.0",
            x=10,
            y=20,
            color=arcade.color.BLACK,
            font_size=14,
        )

    def setup(self):
        """Set up the game and initialize the variables."""

        # Sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=PLAYER_SCALING,
        )

        # Starting position of the player
        self.player_sprite.center_x = 196
        self.player_sprite.center_y = 270
        self.player_list.append(self.player_sprite)

        map_name = ":resources:/tiled_maps/map.json"

        layer_options = {
            "Platforms": {"use_spatial_hash": True},
            "Coins": {"use_spatial_hash": True},
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(
            map_name, layer_options=layer_options, scaling=TILE_SCALING
        )
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # Set wall and coin SpriteLists
        self.wall_list = self.tile_map.sprite_lists["Platforms"]
        self.coin_list = self.tile_map.sprite_lists["Coins"]

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            self.background_color = self.tile_map.background_color

        # Keep player from running through the wall_list layer
        walls = [self.wall_list, ]
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls, gravity_constant=GRAVITY
        )

        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        # Center camera on user
        self.pan_camera_to_user()

        self.game_over = False

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.camera.use()
        self.clear()

        # Start counting frames
        self.frame_count += 1

        # Draw all the sprites.
        self.player_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()

        # Activate GUI camera for FPS, distance and hit boxes
        # This will adjust text position based on viewport
        self.gui_camera.use()

        # Calculate FPS if conditions are met
        if self.last_time and self.frame_count % 60 == 0:
            fps = round(1.0 / (time.time() - self.last_time) * 60)
            self.fps_text.text = f"FPS: {fps:3d}"

        # Draw FPS text
        self.fps_text.draw()

        # Get time for every 60 frames
        if self.frame_count % 60 == 0:
            self.last_time = time.time()

        # Enable to draw hit boxes
        # self.wall_list.draw_hit_boxes()
        # self.wall_list_objects.draw_hit_boxes()

        # Get distance and draw text
        distance = self.player_sprite.right
        self.distance_text.text = f"Distance: {distance}"
        self.distance_text.draw()

        # Draw game over text if condition met
        if self.game_over:
            arcade.draw_text(
                "Game Over",
                200,
                200,
                arcade.color.BLACK,
                30,
            )

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
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
        """Movement and game logic"""

        if self.player_sprite.right >= self.end_of_map:
            self.game_over = True

        # Call update on all sprites
        if not self.game_over:
            self.physics_engine.update()

        coins_hit = arcade.check_for_collision_with_list(
            self.player_sprite, self.coin_list
        )
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.score += 1

        # Pan to the user
        self.pan_camera_to_user(panning_fraction=0.12)

    def pan_camera_to_user(self, panning_fraction: float = 1.0):
        """ Manage Scrolling """

        # This spot would center on the user
        screen_center_x = self.player_sprite.center_x
        screen_center_y = self.player_sprite.center_y
        if screen_center_x - self.width/2 < 0:
            screen_center_x = self.width/2
        if screen_center_y - self.height/2 < 0:
            screen_center_y = self.height/2
        user_centered = screen_center_x, screen_center_y

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position,
            user_centered,
            panning_fraction,
        )


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
