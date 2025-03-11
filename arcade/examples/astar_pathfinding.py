"""
A-Star Path-finding

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.astar_pathfinding
"""

import arcade
from arcade import camera
import random

SPRITE_IMAGE_SIZE = 128
SPRITE_SCALING = 0.25
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING)

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "A-Star Path-finding"

MOVEMENT_SPEED = 5

VIEWPORT_MARGIN = 100
HORIZONTAL_BOUNDARY = WINDOW_WIDTH / 2.0 - VIEWPORT_MARGIN
VERTICAL_BOUNDARY = WINDOW_HEIGHT / 2.0 - VIEWPORT_MARGIN

# If the player moves further than this boundary away from the camera we use a
# constraint to move the camera
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

        # --- Related to paths
        # List of points that makes up a path between two points
        self.path = None
        # List of points we checked to see if there is a barrier there
        self.barrier_list = None

        # Set the window background color
        self.background_color = arcade.color.AMAZON

        # Camera
        self.camera = None

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True,
                                           spatial_hash_cell_size=128)
        self.enemy_list = arcade.SpriteList()

        # Set up the player
        resource = ":resources:images/animated_characters/" \
                   "female_person/femalePerson_idle.png"
        self.player = arcade.Sprite(resource, scale=SPRITE_SCALING)
        self.player.center_x = SPRITE_SIZE * 5
        self.player.center_y = SPRITE_SIZE * 1
        self.player_list.append(self.player)

        # Set enemies
        resource = ":resources:images/animated_characters/zombie/zombie_idle.png"
        enemy = arcade.Sprite(resource, scale=SPRITE_SCALING)
        enemy.center_x = SPRITE_SIZE * 4
        enemy.center_y = SPRITE_SIZE * 7
        self.enemy_list.append(enemy)

        spacing = SPRITE_SIZE * 3
        for column in range(10):
            for row in range(15):
                sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png",
                                       scale=SPRITE_SCALING)

                x = (column + 1) * spacing
                y = (row + 1) * sprite.height

                sprite.center_x = x
                sprite.center_y = y
                if random.randrange(100) > 30:
                    self.wall_list.append(sprite)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player,
                                                         self.wall_list)

        # --- Path related
        # This variable holds the travel-path. We keep it as an attribute so
        # we can calculate it in on_update, and draw it in on_draw.
        self.path = None
        # Grid size for calculations. The smaller the grid, the longer the time
        # for calculations. Make sure the grid aligns with the sprite wall grid,
        # or some openings might be missed.
        grid_size = SPRITE_SIZE

        # Calculate the playing field size. We can't generate paths outside of
        # this.
        playing_field_left_boundary = -SPRITE_SIZE * 2
        playing_field_right_boundary = SPRITE_SIZE * 35
        playing_field_top_boundary = SPRITE_SIZE * 17
        playing_field_bottom_boundary = -SPRITE_SIZE * 2

        # This calculates a list of barriers. By calculating it here in the
        # init, we are assuming this list does not change. In this example,
        # our walls don't move, so that is ok. If we want moving barriers (such as
        # moving platforms or enemies) we need to recalculate. This can be an
        # time-intensive process depending on the playing field size and grid
        # resolution.

        # Note: If the enemy sprites are the same size, we only need to calculate
        # one of these. We do NOT need a different one for each enemy. The sprite
        # is just used for a size calculation.
        self.barrier_list = arcade.AStarBarrierList(enemy,
                                                    self.wall_list,
                                                    grid_size,
                                                    playing_field_left_boundary,
                                                    playing_field_right_boundary,
                                                    playing_field_bottom_boundary,
                                                    playing_field_top_boundary)

        self.camera = camera.Camera2D()

    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        self.clear()

        with self.camera.activate():
            # Draw all the sprites.
            self.player_list.draw()
            self.wall_list.draw()
            self.enemy_list.draw()

            if self.path:
                arcade.draw_line_strip(self.path, arcade.color.BLUE, 2)

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

        # Update the character
        self.physics_engine.update()

        # Calculate a path to the player
        enemy = self.enemy_list[0]
        # Set to True if we can move diagonally. Note that diagonal movement
        # might cause the enemy to clip corners.
        self.path = arcade.astar_calculate_path(enemy.position,
                                                self.player.position,
                                                self.barrier_list,
                                                diagonal_movement=False)
        # print(self.path,"->", self.player.position)

        # --- Manage Scrolling ---
        self.camera.position = camera.grips.constrain_boundary_xy(
            self.camera.view_data, CAMERA_BOUNDARY, self.player.position
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = True
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        # Close the window / exit game
        elif key == arcade.key.ESCAPE:
            self.window.close()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
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
