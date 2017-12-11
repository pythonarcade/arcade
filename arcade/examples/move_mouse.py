"""
This simple animation example shows how to move an item with the mouse, and
handle mouse clicks.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.move_mouse
"""

import arcade

# Set up the constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RECT_WIDTH = 50
RECT_HEIGHT = 50


class Rectangle:
    """ Class to represent a rectangle on the screen """

    def __init__(self, x, y, width, height, angle, color):
        """ Initialize our rectangle variables """

        # Position
        self.x = x
        self.y = y

        # Size and rotation
        self.width = width
        self.height = height
        self.angle = angle

        # Color
        self.color = color

    def draw(self):
        """ Draw our rectangle """
        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height,
                                     self.color, self.angle)


class MyGame(arcade.Window):
    """ Main application class. """
    def __init__(self, width, height):
        super().__init__(width, height, title="Keyboard control")
        self.player = None
        self.left_down = False

    def setup(self):
        """ Set up the game and initialize the variables. """
        width = RECT_WIDTH
        height = RECT_HEIGHT
        x = 0
        y = RECT_HEIGHT
        angle = 0
        color = arcade.color.WHITE
        self.player = Rectangle(x, y, width, height, angle, color)
        self.left_down = False

    def update(self, dt):
        """ Move everything """
        if self.left_down:
            self.player.angle += 2

    def on_draw(self):
        """
        Render the screen.
        """
        arcade.start_render()

        self.player.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        self.player.x = x
        self.player.y = y

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """
        print(button)
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_down = True

    def on_mouse_release(self, x, y, button, modifiers):
        """
        Called when a user releases a mouse button.
        """
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_down = False


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
