import os

import pytest
import arcade
from arcade import Texture

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5


def test_main(window: arcade.Window):
    arcade.set_background_color(arcade.color.AMAZON)

    texture = arcade.load_texture(":resources:images/space_shooter/playerShip1_orange.png")
    assert texture.width == 99
    assert texture.height == 75

    circle_texture = arcade.make_circle_texture(10, arcade.color.RED)
    soft_circle_texture = arcade.make_soft_circle_texture(10, arcade.color.RED, 255, 0)
    soft_square_texture = arcade.make_soft_square_texture(10, arcade.color.RED, 255, 0)

    columns = 16
    count = 60
    sprite_width = 256
    sprite_height = 256
    file_name = ":resources:images/spritesheets/explosion.png"

    # Load the explosions from a sprite sheet
    explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, count)

    def on_draw():
        arcade.start_render()
        texture.draw_scaled(50, 50, 1)
        texture.draw_sized(150, 50, 99, 75)

    window.on_draw = on_draw
    window.test()
    arcade.cleanup_texture_cache()


def test_texture_constructor_hit_box_algo():
    """
    Test the different hitbox algorithms
    """
    Texture(name="default")
    Texture(name="simple", hit_box_algorithm="Simple")
    Texture(name="detailed", hit_box_algorithm="Detailed")
    Texture(name="allowsnonehitbox", hit_box_algorithm=None)
    Texture(name="old_behavior_preserved", hit_box_algorithm="None")

    with pytest.raises(ValueError):
        Texture(name="random", hit_box_algorithm="definitely invalid")

    arcade.cleanup_texture_cache()


def test_load_texture_pair(window):
    """Load texture pair inspecting contents"""
    a, b = arcade.load_texture_pair(":resources:images/test_textures/test_texture.png")
    # Red pixel in upper left corner
    assert a.image.getpixel((0, 0)) == (255, 0, 0, 255)
    assert a.size == (128, 128)
    # Green pixel in upper left when mirrored
    assert b.image.getpixel((0, 0)) == (0, 255, 0, 255)
    assert b.size == (128, 128)


def test_missing_image():
    """Texture without image raises ValueError when accessing properties"""
    tex = Texture("empty")

    with pytest.raises(ValueError):
        tex.width

    with pytest.raises(ValueError):
        tex.height

    with pytest.raises(ValueError):
        tex.size

    with pytest.raises(ValueError):
        tex.hit_box_points


def test_crate_empty():
    """Create empty texture"""
    size = (256, 256)
    tex = Texture.create_empty("empty", size)
    assert tex.name == "empty"
    assert tex.size == size
    assert tex._hit_box_algorithm == 'None'
    assert tex.hit_box_points == (
        (-128.0, -128.0),
        (128.0, -128.0),
        (128.0, 128.0),
        (-128.0, 128.0)
    )
