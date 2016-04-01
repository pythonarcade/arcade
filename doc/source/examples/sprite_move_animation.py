"""
Sprite Collect Coins

Simple program to show basic sprite usage.

Artwork from http://kenney.nl
"""
import random
import arcade

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

MOVEMENT_SPEED = 5

window = None


class MyApplication(arcade.Window):
    """ Main application class. """

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player = arcade.AnimatedSprite()

        image_location_list = [
                               [0, 6, 59, 92],
                               [59, 6, 63, 92],
                               [122, 4, 76, 94],
                               [198, 0, 91, 98],
                               [289, 17, 65, 81],
                               [354, 6, 80, 92],
                               [434, 5, 76, 93],
                               [510, 6, 81, 92],
                               [591, 5, 64, 93],
                               [655, 10, 75, 88],
                               [730, 7, 54, 91],
                               [784, 3, 59, 95],
                               [843, 6, 56, 92],
                               [899, 7, 91, 91],
                               [990, 1, 91, 97],
                               [1081, 2, 91, 96],
                               [1172, 5, 68, 93],
                               [1240, 6, 69, 92],
                               [1309, 10, 67, 88]]
        filename = "images/character_sheet.png"

        texture_info_list = arcade.load_textures(filename, image_location_list)
        for texture_info in texture_info_list:
            texture = texture_info
            self.player.append_texture(texture)

        texture_info_list = arcade.load_textures(filename, image_location_list, True)
        for texture_info in texture_info_list:
            texture = texture_info
            self.player.append_texture(texture)

        flip = len(image_location_list)
        self.player.set_right_stand_textures([0])
        self.player.set_left_stand_textures([0 + flip])
        self.player.set_right_walk_textures([8, 9, 10, 11, 12])
        self.player.set_left_walk_textures([8 + flip, 9 + flip, 10 + flip, 11 + flip, 12 + flip])
        self.player.texture_change_distance = 20

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2
        self.player.set_texture(0)
        self.player.scale = 0.8
        self.player.draw()

        self.all_sprites_list.append(self.player)

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
        output = "Frame: {}".format(self.player.get_texture())
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcade.key.UP:
            self.player .change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player .change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player .change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player .change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player .change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player .change_x = 0

    def animate(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.all_sprites_list.update()


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
window.setup()

arcade.run()
