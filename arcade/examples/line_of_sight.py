"""
Line of Sight

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.line_of_sight
"""

import arcade
import random

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Line of Sight"

MOVEMENT_SPEED = 5

VIEWPORT_MARGIN = 250
HORIZONTAL_BOUNDARY = WINDOW_WIDTH / 2.0 - VIEWPORT_MARGIN
VERTICAL_BOUNDARY = WINDOW_HEIGHT / 2.0 - VIEWPORT_MARGIN
# If the player moves further than this boundary away from
# the camera we use a constraint to move the camera
CAMERA_BOUNDARY = arcade.LRBT(
    -HORIZONTAL_BOUNDARY,
    HORIZONTAL_BOUNDARY,
    -VERTICAL_BOUNDARY,
    VERTICAL_BOUNDARY,
)


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
        self.player_list = None
        self.wall_list = None
        self.enemy_list = None

        # Set up the player info
        self.player = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.physics_engine = None

        # Camera for scrolling
        self.camera = None

        # Set the background color
        self.background_color = arcade.color.AMAZON

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Camera
        self.camera = arcade.Camera2D()

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()

        # Set up the player
        self.player = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=SPRITE_SCALING,
        )
        self.player.center_x = 50
        self.player.center_y = 350
        self.player_list.append(self.player)

        # Set enemies
        enemy = arcade.Sprite(
            ":resources:images/animated_characters/zombie/zombie_idle.png",
            scale=SPRITE_SCALING,
        )
        enemy.center_x = 350
        enemy.center_y = 350
        self.enemy_list.append(enemy)

        spacing = 200
        for column in range(10):
            for row in range(10):
                sprite = arcade.Sprite(
                    ":resources:images/tiles/grassCenter.png",
                    scale=SPRITE_SCALING,
                )

                x = (column + 1) * spacing
                y = (row + 1) * sprite.height

                sprite.center_x = x
                sprite.center_y = y
                if random.randrange(100) > 20:
                    self.wall_list.append(sprite)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.wall_list,
        )

    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()
        self.wall_list.draw()
        self.enemy_list.draw()

        for enemy in self.enemy_list:
            if arcade.has_line_of_sight(
                self.player.position, enemy.position, self.wall_list
            ):
                color = arcade.color.RED
            else:
                color = arcade.color.WHITE
            arcade.draw_line(self.player.center_x,
                             self.player.center_y,
                             enemy.center_x,
                             enemy.center_y,
                             color,
                             2)

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Calculate speed based on the keys pressed
        self.player.change_x = 0
        self.player.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player.change_y = -MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = MOVEMENT_SPEED

        self.physics_engine.update()

        # --- Manage Scrolling ---
        self.camera.position = arcade.camera.grips.constrain_boundary_xy(
            self.camera.view_data, CAMERA_BOUNDARY, self.player.position
        )
        self.camera.use()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False


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
