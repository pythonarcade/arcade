"""
Move Sprite With Keyboard or Controller using InputManager

Simple program to show moving a sprite with the keyboard or controller via InputManager.
This is similar to the behavior in sprite_move_controller and sprite_move_keyboard
but combining the devices using Arcade's advanced input system.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_move_input_manager
"""

import arcade

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Move Sprite with InputManager Example"

MOVEMENT_SPEED = 5


class Player(arcade.Sprite):

    def update(self, delta_time: float = 1/60):
        """ Move the player """
        # Move player.
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > WINDOW_WIDTH - 1:
            self.right = WINDOW_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > WINDOW_HEIGHT - 1:
            self.top = WINDOW_HEIGHT - 1


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

        # Set our controller to None, this will get changed if we find a connected controller
        controller = None

        # Ask arcade for a list of connected controllers
        controllers = arcade.get_controllers()
        if controllers:
            # Just use the first one in the list for now
            controller = controllers[0]

        # Create a new InputManager, and assign our controller to it(if we have one)
        self.input_manager = arcade.InputManager(controller)

        # Add a new horizontal movement axis to the input manager.
        # Also assign the LEFT/RIGHT arrow keys and left thumbstick to it
        self.input_manager.new_axis("MoveHorizontal")
        self.input_manager.add_axis_input_combined(
            "MoveHorizontal",
            arcade.Keys.RIGHT,
            arcade.Keys.LEFT
        )
        self.input_manager.add_axis_input("MoveHorizontal", arcade.ControllerSticks.LEFT_STICK_X)

        # Same thing for vertical movement axis
        self.input_manager.new_axis("MoveVertical")
        self.input_manager.add_axis_input_combined(
            "MoveVertical",
            arcade.Keys.UP,
            arcade.Keys.DOWN
        )
        self.input_manager.add_axis_input("MoveVertical", arcade.ControllerSticks.LEFT_STICK_Y)

        # Variables that will hold sprite lists
        self.player_list = None

        # Set up the player info
        self.player_sprite = None

        # Set the background color
        self.background_color = arcade.color.AMAZON

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=SPRITE_SCALING,
        )
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen
        self.clear()

        # Draw all the sprites.
        self.player_list.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Update the input manager so it has the latest values from our devices
        self.input_manager.update()

        # Apply the input axes to the player
        self.player_sprite.change_x = self.input_manager.axis("MoveHorizontal") * MOVEMENT_SPEED
        self.player_sprite.change_y = self.input_manager.axis("MoveVertical") * MOVEMENT_SPEED

        # Call update to move the sprite
        # If using a physics engine, call update player to rely on physics engine
        # for movement, and call physics engine here.
        self.player_list.update(delta_time)


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
