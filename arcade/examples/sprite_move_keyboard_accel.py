"""
Acceleration and Friction

Demonstrate how to implement simple acceleration and friction without a
physics engine.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the
command line with:
python -m arcade.examples.sprite_move_keyboard_accel
"""

import arcade

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Better Move Sprite with Keyboard Example"

# Important constants for this example

# Speed limit
MAX_SPEED = 3.0

# How fast we accelerate
ACCELERATION_RATE = 0.1

# How fast to slow down after we let off the key
FRICTION = 0.02


class Player(arcade.Sprite):

    def update(self, delta_time: float = 1/60):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check to see if we hit the screen edge
        if self.left < 0:
            self.left = 0
            self.change_x = 0  # Zero x speed
        elif self.right > WINDOW_WIDTH - 1:
            self.right = WINDOW_WIDTH - 1
            self.change_x = 0

        if self.bottom < 0:
            self.bottom = 0
            self.change_y = 0
        elif self.top > WINDOW_HEIGHT - 1:
            self.top = WINDOW_HEIGHT - 1
            self.change_y = 0


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

        # Variable to will hold the player sprite list
        self.player_list = None

        # Create a place to store the player sprite
        # so it can be  accessed directly.
        self.player_sprite = None

        # Create places to store the speed display Text objects
        self.x_speed_display = None
        self.y_speed_display = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Set the background color
        self.background_color = arcade.color.AMAZON

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Create a sprite list
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=SPRITE_SCALING,
        )
        self.player_sprite.position = self.width / 2, self.height / 2
        self.player_list.append(self.player_sprite)

        # Create the speed display objects with initial text
        self.x_speed_display = arcade.Text(
            f"X Speed: {self.player_sprite.change_x:6.3f}",
            10, 50, arcade.color.BLACK, font_size=15,
        )

        self.y_speed_display = arcade.Text(
            f"Y Speed: {self.player_sprite.change_y:6.3f}",
            10, 70, color=arcade.color.BLACK, font_size=15,
        )

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()

        # Draw the speed indicators
        self.x_speed_display.draw()
        self.y_speed_display.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Add some friction
        if self.player_sprite.change_x > FRICTION:
            self.player_sprite.change_x -= FRICTION
        elif self.player_sprite.change_x < -FRICTION:
            self.player_sprite.change_x += FRICTION
        else:
            self.player_sprite.change_x = 0

        if self.player_sprite.change_y > FRICTION:
            self.player_sprite.change_y -= FRICTION
        elif self.player_sprite.change_y < -FRICTION:
            self.player_sprite.change_y += FRICTION
        else:
            self.player_sprite.change_y = 0

        # Apply acceleration based on the keys pressed
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y += ACCELERATION_RATE
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y += -ACCELERATION_RATE
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x += -ACCELERATION_RATE
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x += ACCELERATION_RATE

        if self.player_sprite.change_x > MAX_SPEED:
            self.player_sprite.change_x = MAX_SPEED
        elif self.player_sprite.change_x < -MAX_SPEED:
            self.player_sprite.change_x = -MAX_SPEED
        if self.player_sprite.change_y > MAX_SPEED:
            self.player_sprite.change_y = MAX_SPEED
        elif self.player_sprite.change_y < -MAX_SPEED:
            self.player_sprite.change_y = -MAX_SPEED

        # Call update to move the sprite
        # IMPORTANT: If using a physics engine, you need to call update
        # on it instead of the sprite list!
        self.player_list.update(delta_time)

        # Update the speed displays based on the final speed
        self.x_speed_display.text = f"X Speed: {self.player_sprite.change_x:6.3f}"
        self.y_speed_display.text = f"Y Speed: {self.player_sprite.change_y:6.3f}"

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
