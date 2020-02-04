import os
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5


class MyTestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.texture = arcade.load_texture(":resources:images/space_shooter/playerShip1_orange.png")
        assert self.texture.width == 99
        assert self.texture.height == 75

        self.circle_texture = arcade.make_circle_texture(10, arcade.color.RED)
        self.soft_circle_texture = arcade.make_soft_circle_texture(10, arcade.color.RED, 255, 0)
        self.soft_square_texture = arcade.make_soft_square_texture(10, arcade.color.RED, 255, 0)

        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256
        file_name = ":resources:images/spritesheets/explosion.png"

        # Load the explosions from a sprite sheet
        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, count)

    def on_draw(self):
        arcade.start_render()

        self.texture.draw_scaled(50, 50, 1)
        self.texture.draw_sized(150, 50, 99, 75)


def test_textures():
    window = MyTestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Textures")
    window.test()
    window.close()
    arcade.cleanup_texture_cache()