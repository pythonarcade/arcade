"""
Turn and Move Example.

Right-click to cause the tank to move to that point.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.turn_and_move
"""
import math
import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Turn and Move Example"

# Image might not be lined up right, set this to offset
IMAGE_ROTATION = -90


class Player(arcade.Sprite):
    """
    Sprite that turns and moves
    """
    def __init__(self):
        super().__init__(":resources:images/topdown_tanks/tank_green.png")

        # Destination point is where we are going
        self._destination_point = None

        # Max speed px / s
        self.speed = 300

        # what percent of the angle do we move by each frame
        self.rot_speed = 0.1

    @property
    def destination_point(self):
        return self._destination_point

    @destination_point.setter
    def destination_point(self, destination_point):
        self._destination_point = destination_point
        self.change_x = 0.0
        self.change_y = 0.0

    def update(self, delta_time: float = 1 / 60):
        """ Update the player """

        # If we have no destination, don't go anywhere.
        if not self._destination_point:
            self.change_x = 0
            self.change_y = 0
            return

        # Position the start at our current location
        start_x = self.center_x
        start_y = self.center_y

        # Get the destination location
        dest_x = self._destination_point[0]
        dest_y = self._destination_point[1]

        # Do math to calculate how to get the sprite to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the player will travel.
        target_angle = arcade.math.get_angle_degrees(start_x, start_y, dest_x, dest_y)
        current_angle = self.angle - IMAGE_ROTATION

        new_angle = arcade.math.lerp_angle(current_angle, target_angle, self.rot_speed)

        self.angle = new_angle + IMAGE_ROTATION
        angle_diff = abs(target_angle - new_angle)
        if  angle_diff < 0.1 or 359.9 < angle_diff:
            self.angle = target_angle + IMAGE_ROTATION
            target_radians = math.radians(target_angle)
            self.change_x = math.cos(-target_radians) * self.speed
            self.change_y = math.sin(-target_radians) * self.speed

        # Fine-tune our change_x/change_y if we are really close to destination
        # point and just need to set to that location.
        traveling = False
        if abs(self.center_x - dest_x) < abs(self.change_x * delta_time):
            self.center_x = dest_x
        else:
            self.center_x += self.change_x * delta_time
            traveling = True

        if abs(self.center_y - dest_y) < abs(self.change_y * delta_time):
            self.center_y = dest_y
        else:
            self.center_y += self.change_y * delta_time
            traveling = True

        # If we have arrived, then cancel our destination point
        if not traveling:
            self._destination_point = None


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.SAND

        self.player_sprite = None

        # Sprite Lists
        self.player_list = None

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """

        # Sprite Lists
        self.player_list = arcade.SpriteList()
        self.player_sprite = Player()
        self.player_sprite.center_x = 300
        self.player_sprite.center_y = 300
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        self.player_list.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        self.player_list.update(delta_time)

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player_sprite.destination_point = x, y


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
