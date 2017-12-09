"""
Sprite Bullets

Simple program to show basic sprite usage.

Artwork from http://kenney.nl
"""
import random
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class MyWindow(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Shape Demo")

        self.rect1 = arcade.create_rectangle_filled(100, 100, 50, 50, arcade.color.AFRICAN_VIOLET)
        self.rect2 = arcade.create_rectangle_filled(200, 200, 50, 50, arcade.color.RADICAL_RED)
        self.rect3 = arcade.create_rectangle_filled(300, 300, 50, 50, arcade.color.ALLOY_ORANGE)
        self.line1 = arcade.create_line(400, 400, 500, 500, arcade.color.ASH_GREY, 10)

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):

        """ Set up the game and initialize the variables. """



    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        arcade.render(self.rect1)
        arcade.render(self.rect2)
        arcade.render(self.rect3)
        arcade.render(self.line1)



    def update(self, delta_time):
        """ Movement and game logic """



def main():
    window = MyWindow()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
