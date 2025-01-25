import PIL.Image
import PIL.ImageDraw
import pytest

import arcade
from arcade import Texture, hitbox

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LINE_HEIGHT = 20
CHARACTER_SCALING = 0.5


def test_texture_constructor_hit_box_algo():
    """
    Test the different hitbox algorithms
    """
    image = PIL.Image.new("RGBA", (100, 100), color=(255, 255, 255, 255))
    Texture(name="default", image=image)
    Texture(name="simple", image=image, hit_box_algorithm=hitbox.algo_simple)
    Texture(name="detailed", image=image, hit_box_algorithm=hitbox.algo_detailed)
    Texture(name="allows_none_hitbox", image=image, hit_box_algorithm=hitbox.algo_bounding_box)
    Texture(name="old_behavior_preserved", image=image)

    with pytest.raises(TypeError):
        Texture(name="random", image=image, hit_box_algorithm="definitely invalid")


def test_load_texture():
    """Create texture with different """
    path = ":resources:images/test_textures/test_texture.png"
    # Basic loading
    tex = arcade.load_texture(path)
    assert tex.size == (128, 128)
    assert tex.width == 128
    assert tex.height == 128
    assert tex.size == (128, 128)
    assert tex.hit_box_points is not None

    with pytest.raises(FileNotFoundError):
        arcade.load_texture("moo")


def test_texture_equality():
    """Test the eq/ne operator for textures"""
    t1 = arcade.load_texture(":resources:images/test_textures/test_texture.png")
    t2 = arcade.load_texture(":resources:images/test_textures/test_texture.png")

    # They are equal to themselves
    assert t1 == t1
    assert t2 == t2
    # These are two separate instances with the same content
    assert t1 != t2


def test_crate_empty():
    """Create empty texture"""
    size = (256, 256)
    tex = Texture.create_empty("empty", size)
    assert tex.file_path is None
    assert tex.crop_values is None
    assert tex.size == size
    assert tex._hit_box_algorithm == hitbox.algo_bounding_box
    assert tex.hit_box_points == (
        (-128.0, -128.0),
        (128.0, -128.0),
        (128.0, 128.0),
        (-128.0, 128.0)
    )
