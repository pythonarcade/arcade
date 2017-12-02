"""
Use sprites to scroll around a large screen.

Simple program to show basic sprite usage.

Artwork from http://kenney.nl
"""
import random
import arcade

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 40

MOVEMENT_SPEED = 5


class MyApplication(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen=True)
        self.is_full_screen = True

    def setup(self):
        """ Set up the game and initialize the variables. """


        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()
        screen_width, screen_height = self.get_size()
        arcade.draw_text("Press F to toggle between full screen and windowed mode.", screen_width // 2, screen_height // 2, arcade.color.WHITE, 24, width=400, anchor_x="center")


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.F:
            self.is_full_screen = not self.is_full_screen
            self.set_fullscreen(self.is_full_screen)




    def update(self, delta_time):
        """ Movement and game logic """
        pass



def main():
    """ Main method """
    window = MyApplication()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
