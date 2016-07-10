"""
Sprite Collect Coins

Simple program to show basic sprite usage.

Artwork from http://kenney.nl
"""
import arcade
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

COIN_SCALE = 0.5
COIN_COUNT = 50

MOVEMENT_SPEED = 5


class MyAppWindow(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        """
        Initializer
        :param width:
        :param height:
        """
        super().__init__(width, height)

        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player = arcade.AnimatedWalkingSprite()

        filename = "images/character_sheet.png"

        image_location_list = [[0, 6, 59, 92]]
        self.player.stand_right_textures = \
            arcade.load_textures(filename, image_location_list, False)
        self.player.stand_left_textures = \
            arcade.load_textures(filename, image_location_list, True)

        image_location_list = [[591, 5, 64, 93],
                               [655, 10, 75, 88],
                               [730, 7, 54, 91],
                               [784, 3, 59, 95],
                               [843, 6, 56, 92]]
        self.player.walk_right_textures = \
            arcade.load_textures(filename, image_location_list, False)
        self.player.walk_left_textures = \
            arcade.load_textures(filename, image_location_list, True)

        self.player.texture_change_distance = 20

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player.scale = 0.8

        self.all_sprites_list.append(self.player)

        for i in range(COIN_COUNT):
            coin = arcade.AnimatedTimeSprite(scale=0.5)
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT)
            coin.textures = []
            coin.textures.append(arcade.load_texture("images/gold_1.png",
                                                     scale=COIN_SCALE))
            coin.textures.append(arcade.load_texture("images/gold_2.png",
                                                     scale=COIN_SCALE))
            coin.textures.append(arcade.load_texture("images/gold_3.png",
                                                     scale=COIN_SCALE))
            coin.textures.append(arcade.load_texture("images/gold_4.png",
                                                     scale=COIN_SCALE))
            coin.textures.append(arcade.load_texture("images/gold_3.png",
                                                     scale=COIN_SCALE))
            coin.textures.append(arcade.load_texture("images/gold_2.png",
                                                     scale=COIN_SCALE))
            coin.cur_texture_index = random.randrange(len(coin.textures))
            self.coin_list.append(coin)
            self.all_sprites_list.append(coin)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

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

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcade.key.UP:
            self.player.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0

    def animate(self, delta_time):
        """ Movement and game logic """

        self.all_sprites_list.update()
        self.all_sprites_list.update_animation()

        # Generate a list of all sprites that collided with the player.
        hit_list = \
            arcade.check_for_collision_with_list(self.player,
                                                 self.coin_list)

        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in hit_list:
            coin.kill()
            self.score += 1


def main():
    MyAppWindow(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()


if __name__ == "__main__":
    main()
