"""
Sprite Collect Coins

Simple program to show basic sprite usage.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_collect_coins
"""

import random
import arcade
import os
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

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.player_list = None
        self.coin_list = None

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        self.color_attachment = None
        self.offscreen = None
        self.quad_fs = None
        self.mini_map_quad = None

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Offscreen stuff
        program = shader.program(
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

                in vec2 v_uv;
                out vec4 f_color;
                uniform int blur;
                uniform float weight =1;
                uniform int my_size = 20;
                uniform int step_size = 1;
                
                void main() {
                    vec2 tex_offset = vec2(1.0 / 800.0, 1.0 / 600.0);
                    if(blur == 1) {
                        vec4 result = texture(tex, v_uv);
                        for(int x = -my_size; x < my_size; x += step_size)
                        {
                            for(int y = -my_size; y < my_size; y += step_size)
                            {                                
                                vec2 p2 = v_uv - vec2(tex_offset.x * x, tex_offset.y * y);
                                float d = distance(v_uv, p2);
                                float ratio = 0.0;
                                if(d != 0) {
                                    ratio = 1.0 / ((d * 800) * (d * 600)) * weight;
                                }
                                    
                                result += texture(tex, p2) * ratio;
                                // result += texture(tex, v_uv - vec2(tex_offset.x * x, tex_offset.y * y)) * weight;
                            }
                        }
                        f_color = result;
                    } else {
                        f_color = texture(tex, v_uv);
                    }
                }
            ''',
        )
        self.color_attachment = shader.texture((SCREEN_WIDTH, SCREEN_HEIGHT), 4)
        self.offscreen = shader.framebuffer(color_attachments=[self.color_attachment])
        self.blur_fs = geometry.quad_fs(program, size=(2.0, 2.0))
        self.quad_fs = geometry.quad_fs(program, size=(2.0, 2.0), pos=(0.0, 0.0))

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Score
        self.score = 0

        # Set up the player
        # Character image from kenney.nl
        color = random.randrange(255), random.randrange(255), random.randrange(255)
        self.player_sprite = arcade.SpriteSolidColor(30, 30, arcade.color.WHITE)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        # Create the coins
        for i in range(COIN_COUNT):

            # Create the coin instance
            # Coin image from kenney.nl
            color = random.randrange(255), random.randrange(255), random.randrange(255)
            coin = arcade.Sprite("circle16.png")

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()

        self.offscreen.use()
        self.offscreen.clear()

        self.coin_list.draw()

        self.use()

        self.color_attachment.use(0)
        self.blur_fs.program['blur'] = 1
        self.blur_fs.render()

        # self.color_attachment.use(0)
        # self.quad_fs.program['blur'] = 0
        # self.quad_fs.render()

        self.player_list.draw()

        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)


    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the center of the player sprite to match the mouse x, y
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.coin_list.update()

        # Generate a list of all sprites that collided with the player.
        coins_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
