"""
Sprite with Moving Platforms

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_moving_platforms
"""
import arcade
from pyglet.math import Vec2

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite with Moving Platforms Example"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * SPRITE_SCALING)

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = SPRITE_PIXEL_SIZE * SPRITE_SCALING
RIGHT_MARGIN = 4 * SPRITE_PIXEL_SIZE * SPRITE_SCALING

# Physics
MOVEMENT_SPEED = 10 * SPRITE_SCALING
JUMP_SPEED = 28 * SPRITE_SCALING
GRAVITY = .9 * SPRITE_SCALING

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """ Initializer """

        # Call the parent init
        super().__init__(width, height, title)

        # Sprite lists

        # Drawing non-moving walls separate from moving walls improves performance.
        self.static_wall_list = None
        self.moving_wall_list = None

        self.player_list = None

        # Set up the player
        self.player_sprite = None
        self.physics_engine = None
        self.game_over = False

        # Create the cameras. One for the GUI, one for the sprites.
        # We scroll the 'sprite world' but not the GUI.
        self.camera_sprites = arcade.SimpleCamera()
        self.camera_gui = arcade.SimpleCamera()

        self.left_down = False
        self.right_down = False

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.static_wall_list = arcade.SpriteList()
        self.moving_wall_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/"
                                           "femalePerson_idle.png",
                                           SPRITE_SCALING)
        self.player_sprite.center_x = 2 * GRID_PIXEL_SIZE
        self.player_sprite.center_y = 3 * GRID_PIXEL_SIZE
        self.player_list.append(self.player_sprite)

        # Create floor
        for i in range(30):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", SPRITE_SCALING)
            wall.bottom = 0
            wall.center_x = i * GRID_PIXEL_SIZE
            self.static_wall_list.append(wall)

        # Create platform side to side
        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", SPRITE_SCALING)
        wall.center_y = 3 * GRID_PIXEL_SIZE
        wall.center_x = 3 * GRID_PIXEL_SIZE
        wall.boundary_left = 2 * GRID_PIXEL_SIZE
        wall.boundary_right = 5 * GRID_PIXEL_SIZE
        wall.change_x = 2 * SPRITE_SCALING
        self.moving_wall_list.append(wall)

        # Create platform side to side
        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", SPRITE_SCALING)
        wall.center_y = 3 * GRID_PIXEL_SIZE
        wall.center_x = 7 * GRID_PIXEL_SIZE
        wall.boundary_left = 5 * GRID_PIXEL_SIZE
        wall.boundary_right = 9 * GRID_PIXEL_SIZE
        wall.change_x = -2 * SPRITE_SCALING
        self.moving_wall_list.append(wall)

        # Create platform moving up and down
        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", SPRITE_SCALING)
        wall.center_y = 5 * GRID_PIXEL_SIZE
        wall.center_x = 5 * GRID_PIXEL_SIZE
        wall.boundary_top = 8 * GRID_PIXEL_SIZE
        wall.boundary_bottom = 4 * GRID_PIXEL_SIZE
        wall.change_y = 2 * SPRITE_SCALING
        self.moving_wall_list.append(wall)

        # Create platform moving diagonally
        wall = arcade.Sprite(":resources:images/tiles/grassMid.png", SPRITE_SCALING)
        wall.center_y = 5 * GRID_PIXEL_SIZE
        wall.center_x = 8 * GRID_PIXEL_SIZE
        wall.boundary_left = 7 * GRID_PIXEL_SIZE
        wall.boundary_right = 9 * GRID_PIXEL_SIZE
        wall.boundary_top = 8 * GRID_PIXEL_SIZE
        wall.boundary_bottom = 4 * GRID_PIXEL_SIZE
        wall.change_x = 2 * SPRITE_SCALING
        wall.change_y = 2 * SPRITE_SCALING
        self.moving_wall_list.append(wall)

        # Create our physics engine
        self.physics_engine = \
            arcade.PhysicsEnginePlatformer(self.player_sprite,
                                           [self.static_wall_list, self.moving_wall_list],
                                           gravity_constant=GRAVITY)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        self.game_over = False

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()

        # Draw the sprites.
        self.static_wall_list.draw()
        self.moving_wall_list.draw()
        self.player_list.draw()

        self.camera_gui.use()

        # Put the text on the screen.
        distance = self.player_sprite.right
        output = f"Distance: {distance}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def set_x_speed(self):
        if self.left_down and not self.right_down:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_down and not self.left_down:
            self.player_sprite.change_x = MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """ Called whenever the mouse moves. """
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.left_down = True
            self.set_x_speed()
        elif key == arcade.key.RIGHT:
            self.right_down = True
            self.set_x_speed()

    def on_key_release(self, key, modifiers):
        """ Called when the user presses a mouse button. """
        if key == arcade.key.LEFT:
            self.left_down = False
            self.set_x_speed()
        elif key == arcade.key.RIGHT:
            self.right_down = False
            self.set_x_speed()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites
        self.physics_engine.update()

        # Scroll the screen to the player
        self.scroll_to_player()

    def scroll_to_player(self):
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.
        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """

        position = Vec2(self.player_sprite.center_x - self.width / 2,
                        self.player_sprite.center_y - self.height / 2)
        self.camera_sprites.move_to(position, CAMERA_SPEED)


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
