"""
Move Sprite with Controller

An example of one way to use controller and controller input to move a
sprite.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the
command line with:
python -m arcade.examples.sprite_move_controller
"""
import arcade

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Move Sprite with Controller Example"

MOVEMENT_SPEED = 5
DEAD_ZONE = 0.05


class Player(arcade.Sprite):
    """ Player sprite """

    def __init__(self, filename, scale):
        super().__init__(filename, scale=scale)

        self.controller = None

        controllers = arcade.get_controllers()

        # If we have any...
        if controllers:
            # Grab the first one in  the list
            self.controller = controllers[0]

            # Open it for input
            self.controller.open()

            # Push this object as a handler for controller events.
            # Required for the controller events to be called.
            self.controller.push_handlers(self)

    def update(self, delta_time: float = 1 / 60):
        """ Move the player """

        # If there is a controller, grab the speed.
        if self.controller:

            # x-axis
            movement_x = self.controller.leftx
            if abs(movement_x) < DEAD_ZONE:
                self.change_x = 0
            else:
                self.change_x = movement_x * MOVEMENT_SPEED

            # y-axis
            movement_y = self.controller.lefty
            if abs(movement_y) < DEAD_ZONE:
                self.change_y = 0
            else:
                self.change_y = movement_y * MOVEMENT_SPEED

        # Move the player
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Keep from moving off-screen
        if self.left < 0:
            self.left = 0
        elif self.right > WINDOW_WIDTH - 1:
            self.right = WINDOW_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > WINDOW_HEIGHT - 1:
            self.top = WINDOW_HEIGHT - 1

    def on_button_press(self, controller, button_name):
        """ Handle button-down event for the controller """
        print(f"Button {button_name} down")

    def on_button_release(self, controller, button_name):
        """ Handle button-up event for the controller """
        print(f"Button {button_name} up")

    def on_stick_motion(self, controller, stick_name, x, y):
        """ Handle hat events """
        print(f"Movement on stick {stick_name}: ({x}, {y})")


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
        self.all_sprites_list = None

        # Set up the player info
        self.player_sprite = None

        # Set the background color
        self.background_color = arcade.color.AMAZON

        self.error_text = arcade.Text(
            "There are no controllers, plug in a controller and run again.",
            10,
            10,
            arcade.color.WHITE,
            22,
            width=WINDOW_WIDTH,
            align="center",
        )

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(
            ":resources:images/animated_characters/female_person/"
            "femalePerson_idle.png",
            SPRITE_SCALING,
        )
        self.player_sprite.position = self.width / 2, self.height / 2
        self.all_sprites_list.append(self.player_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Draw all the sprites.
        self.all_sprites_list.draw()

        # Print an error if there is no controller
        if not self.player_sprite.controller:
            self.error_text.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.all_sprites_list.update(delta_time)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0


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
