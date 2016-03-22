"""
Sprite Collect Blocks

Simple program to show basic sprite usage.

Artwork from http://kenney.nl
"""
import random
import math
import arcade

SCALE = 0.5

window = None


class MyApplication(arcade.Window):
    """ Main application class. """

    def setup(self):
        """ Set up the game and initialize the variables. """

        self.frame_count = 0
        self.game_over = False

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = arcade.Sprite("images/character.png", SCALE)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.all_sprites_list.append(self.player_sprite)

        for i in range(50):
            coin = arcade.Sprite("images/coin_01.png", SCALE / 3)
            coin.center_x = random.randrange(800)
            coin.center_y = random.randrange(600)
            self.all_sprites_list.append(coin)
            self.coin_list.append(coin)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.all_sprites_list.draw()

        # Put the text on the screen.
        output = "Score: {}".format(self.score)
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def animate(self, delta_time):
        """ Move everything """

        if not self.game_over:
            self.all_sprites_list.update()
            hit_list = \
                    arcade.check_for_collision_with_list(self.player_sprite,
                                                         self.coin_list)
            for coin in hit_list:
                coin.kill()
                self.score += 1



window = MyApplication(800, 600)
window.setup()

arcade.run()
