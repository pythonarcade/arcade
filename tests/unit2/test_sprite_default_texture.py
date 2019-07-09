import os
import random

import arcade
import pytest


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5

FRAMES = 50


class GeneralTestWindow(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Test Window")

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.AMAZON)

        self.all_sprites = arcade.SpriteList()

        self.setup()

    def setup(self):
        """To be overridden by specific test windows"""
        pass

    def on_draw(self):
        arcade.start_render()
        self.all_sprites.draw()

    def update(self, delta_time):
        self.all_sprites.update()


def test_no_image_no_dimensions_raises_value_error():
    """When no dimensions are given, raise ValueError."""
    with pytest.raises(ValueError):
        self.character_sprite = arcade.Sprite()


def test_no_image_with_dimensions_draws_default_texture():
    """Use a default rectangle texture when no texture is given.
    Random color if not specified."""
    class SpecificTestWindow(GeneralTestWindow):
        def setup(self):
            self.character_sprite = arcade.Sprite(
                width=100,
                height=100,
                color=arcade.color.BLUE)
            self.character_sprite.center_x = 50
            self.character_sprite.center_y = 50
            self.character_sprite.change_x = 5
            self.character_sprite.change_y = 5
            self.all_sprites.append(self.character_sprite)

            for _ in range(100):
                sprite = arcade.Sprite(width=20, height=20)
                sprite.center_x = random.randrange(10, SCREEN_WIDTH-10)
                sprite.center_y = random.randrange(10, SCREEN_HEIGHT-10)
                while sprite.change_x == 0 and sprite.change_y == 0:
                    sprite.change_x = random.randrange(-4, 5)
                    sprite.change_y = random.randrange(-4, 5)

                self.all_sprites.append(sprite)

    window = SpecificTestWindow()
    window.test(frames=FRAMES)
    window.close()
