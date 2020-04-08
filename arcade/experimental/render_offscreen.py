"""
Render scene to offscreen buffer and scroll the texture coordinates
"""
import random
import arcade
import os
import pyglet
import pyglet.gl as gl
import numpy
import time

from arcade import get_image
from arcade import shader
from arcade.experimental import geometry

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

        # Offscreen stuff
        program = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 v_uv;

                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_uv = in_uv;
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D tex;
                uniform float time;

                in vec2 v_uv;
                out vec4 f_color;

                void main() {
                    f_color = texture(tex, v_uv + vec2(sin(time), cos(time)));
                }
            ''',
        )
        self.color_attachment = self.ctx.texture((SCREEN_WIDTH, SCREEN_HEIGHT), 4)
        self.offscreen = self.ctx.framebuffer(color_attachments=[self.color_attachment])
        self.quad_fs = geometry.quad_fs(program, size=(2.0, 2.0))
        # self.quad_fs.program['tex'] = 0

        self.start_time = time.time()

    def on_draw(self):
        """ Draw everything """
        try:
            # Render to offscreen
            self.offscreen.use()
            self.offscreen.clear()
            self.coin_list.draw()
            output = f"Score: {self.score}"
            arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

            # Render back to window
            self.use()
            arcade.start_render()
            self.color_attachment.use(0)
            self.quad_fs.program['time'] = self.current_time() / 4
            self.quad_fs.render()
        except Exception as ex:
            print(ex)

    def current_time(self):
        return time.time() - self.start_time


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
