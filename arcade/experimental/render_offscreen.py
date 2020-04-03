import random
import arcade
import os
import pyglet
import pyglet.gl as gl

from arcade.shader import Texture
from arcade.framebuffer import Framebuffer

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = .25
COIN_COUNT = 50

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Collect Coins Example"


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Create some color attachments and a framebuffer
        # Ensure all properties are working
        self.color_attachment1 = Texture((SCREEN_WIDTH, SCREEN_HEIGHT), 4)
        self.color_attachment1.build_mipmaps()
        self.color_attachment1.filter = gl.GL_NEAREST, gl.GL_NEAREST

        self.color_attachment2 = Texture((SCREEN_WIDTH, SCREEN_HEIGHT), 4)
        self.color_attachment2.build_mipmaps()
        self.color_attachment2.filter = gl.GL_NEAREST, gl.GL_NEAREST

        self.offscreen = Framebuffer(color_attachments=[self.color_attachment1, self.color_attachment2])
        self.offscreen.use()
        self.offscreen.clear()
        print('id', self.offscreen.glo)
        print('viewport', self.offscreen.viewport)
        print('width', self.offscreen.width)
        print('height', self.offscreen.height)
        print('size', self.offscreen.size)
        print('samples', self.offscreen.samples)
        print('color attachments', self.offscreen.color_attachments)
        print('depth_attachment', self.offscreen.depth_attachment)

        self.use()

        # Variables that will hold sprite lists
        self.coin_list = None

        # Set up the player info
        self.score = 0

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.coin_list = arcade.SpriteList()

        # Create the coins
        for i in range(COIN_COUNT):
            coin = arcade.Sprite(":resources:images/items/coinGold.png",
                                 SPRITE_SCALING_COIN)

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def on_draw(self):
        """ Draw everything """

        # Render to offscreen
        self.offscreen.use()

        arcade.start_render()
        self.coin_list.draw()
        self.player_list.draw()
        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

        # Render to window again
        self.use()
        # ...


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
