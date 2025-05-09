"""
Scroll around a large screen.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_move_scrolling_shake
"""

import random
# import math
import arcade

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 1289
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Camera Shake Example"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 220

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1

# How fast the character moves
PLAYER_MOVEMENT_SPEED = 7

BOMB_COUNT = 50
PLAYING_FIELD_WIDTH = 1600
PLAYING_FIELD_HEIGHT = 1600


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__()

        # Sprite lists
        self.player_list = None
        self.wall_list = None
        self.bomb_list = None

        # Set up the player
        self.player_sprite = None

        # Physics engine so we don't run into walls.
        self.physics_engine = None

        # Create camera that will follow the player sprite.
        self.camera_sprites = arcade.Camera2D()

        self.camera_shake = arcade.camera.grips.ScreenShake2D(
            self.camera_sprites.view_data,
            max_amplitude=15.0,
            acceleration_duration=0.1,
            falloff_time=0.5,
            shake_frequency=10.0,
        )

        self.explosion_sound = arcade.load_sound(":resources:sounds/explosion1.wav")

    def setup(self):
        """Set up the game and initialize the variables."""

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bomb_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=0.4,
        )
        self.player_sprite.center_x = 512
        self.player_sprite.center_y = 512
        self.player_list.append(self.player_sprite)

        # -- Set up several columns of walls
        for x in range(200, PLAYING_FIELD_WIDTH, 210):
            for y in range(0, PLAYING_FIELD_HEIGHT, 64):
                # Randomly skip a box so the player can find a way through
                if random.randrange(5) > 0:
                    wall = arcade.Sprite(
                        ":resources:images/tiles/grassCenter.png",
                        scale=SPRITE_SCALING,
                    )
                    wall.center_x = x
                    wall.center_y = y
                    self.wall_list.append(wall)

        for i in range(BOMB_COUNT):
            bomb = arcade.Sprite(":resources:images/tiles/bomb.png", scale=0.25)
            placed = False
            while not placed:
                bomb.center_x = random.randrange(PLAYING_FIELD_WIDTH)
                bomb.center_y = random.randrange(PLAYING_FIELD_HEIGHT)
                if not arcade.check_for_collision_with_list(bomb, self.wall_list):
                    placed = True
            self.bomb_list.append(bomb)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Set the background color
        self.background_color = arcade.color.AMAZON

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Select the camera we'll use to draw all our sprites
        self.camera_shake.update_camera()
        self.camera_sprites.use()

        # Draw all the sprites.
        self.wall_list.draw()
        self.bomb_list.draw()
        self.player_list.draw()

        # Readjust the camera's screen_shake
        self.camera_shake.readjust_camera()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()
        self.camera_shake.update(delta_time)

        # Scroll the screen to the player
        self.scroll_to_player()

        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.bomb_list)
        for bomb in hit_list:
            # Remove the bomb and go 'boom'
            bomb.remove_from_sprite_lists()
            self.explosion_sound.play()

            self.camera_shake.start()

    def scroll_to_player(self):
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.
        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """

        position = (
            self.player_sprite.center_x,
            self.player_sprite.center_y
        )
        self.camera_sprites.position = arcade.math.lerp_2d(
            self.camera_sprites.position,
            position,
            CAMERA_SPEED,
        )

    def on_resize(self, width: int, height: int):
        """
        Resize window
        Handle the user grabbing the edge and resizing the window.
        """
        super().on_resize(width, height)
        self.camera_sprites.match_window()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=True)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
