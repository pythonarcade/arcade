import pytest
import PIL.Image
import PIL.ImageDraw

import arcade
from arcade import Texture
from arcade import hitbox

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
    image = PIL.Image.new("RGBA", (100, 100), color=(255, 255, 255, 255))
    Texture(name="default", image=image)
    Texture(name="simple", image=image, hit_box_algorithm=hitbox.algo_simple)
    Texture(name="detailed", image=image, hit_box_algorithm=hitbox.algo_detailed)
    Texture(name="allows_none_hitbox", image=image, hit_box_algorithm=hitbox.algo_bounding_box)
    Texture(name="old_behavior_preserved", image=image)

    with pytest.raises(ValueError):
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
    # cache_name = ":resources:images/test_textures/test_texture.png-0-0-0-0-False-False-False-Simple "
    # assert tex.name == cache_name
    assert tex.hit_box_points is not None
    assert tex._sprite is None
    assert tex._sprite_list is None

    with pytest.raises(FileNotFoundError):
        arcade.load_texture("moo")


def test_load_textures(window):
    """Test load_textures with various parameters"""
    arcade.cleanup_texture_cache()
    path = ":resources:images/test_textures/test_texture.png"
    def _load(mirrored=False, flipped=False):
        return arcade.load_textures(
            path,
            image_location_list=[
                (0, 0, 64, 64),
                (64, 0, 64, 64),
                (0, 64, 64, 64),
                (64, 64, 64, 64),
            ],
            mirrored=mirrored,
            flipped=flipped,
        )
    # Load twice to load from disk and then resolve from cache
    textures = _load()
    textures = _load()
    assert len(textures) == 4
    # Check The contents of the upper right pixel in each texture
    assert textures[0].image.getpixel((0, 0)) == (255, 0, 0, 255)
    assert textures[1].image.getpixel((0, 0)) == (0, 255, 0, 255)
    assert textures[2].image.getpixel((0, 0)) == (0, 0, 255, 255)
    assert textures[3].image.getpixel((0, 0)) == (255, 0, 255, 255)

    # Load textures with with transforms
    _load(mirrored=True)
    _load(flipped=True)
    _load(mirrored=True, flipped=True)

    # Attempt to load with illegal regions
    with pytest.raises(ValueError):
        arcade.load_textures(path, image_location_list=[(129, 0, 64, 64)])
    with pytest.raises(ValueError):
        arcade.load_textures(path, image_location_list=[(64, 129, 64, 64)])
    with pytest.raises(ValueError):
        arcade.load_textures(path, image_location_list=[(65, 0, 64, 64)])
    with pytest.raises(ValueError):
        arcade.load_textures(path, image_location_list=[(0, 65, 64, 64)])

    with pytest.raises(ValueError):
        arcade.load_textures(path, image_location_list=[(0, 0, 0, 0, 0)])


def test_load_texture_pair():
    """Load texture pair inspecting contents"""
    a, b = arcade.load_texture_pair(":resources:images/test_textures/test_texture.png")
    # Red pixel in upper left corner
    # assert a.image.getpixel((0, 0)) == (255, 0, 0, 255)
    # assert a.size == (128, 128)
    # Green pixel in upper left when mirrored
    # assert b.image.getpixel((0, 0)) == (0, 255, 0, 255)
    # assert b.size == (128, 128)
    assert a._vertex_order != b._vertex_order


def test_texture_equality():
    """Test the eq/ne operator for textures"""
    t1 = arcade.load_texture(":resources:images/test_textures/test_texture.png")
    t2 = arcade.load_texture(":resources:images/test_textures/test_texture.png")

    # They are equal to themselves
    assert t1 == t1
    assert t2 == t2
    assert (t1 != t1) is False
    # Texture with the same path/name are equal
    assert t1 == t2
    # Should reference the same underlying PIL image
    assert t1.image == t2.image
    assert id(t1.image) == id(t2.image)
    # Handle comparing with other objects
    assert t1 != "moo"
    assert t1 != None
    assert (t1 == None) is False
    assert (t1 == "moo") is False


def test_crate_empty():
    """Create empty texture"""
    size = (256, 256)
    tex = Texture.create_empty("empty", size)
    assert tex.origin is None
    assert tex.size == size
    assert tex._hit_box_algorithm == hitbox.algo_bounding_box
    assert tex.hit_box_points == (
        (-128.0, -128.0),
        (128.0, -128.0),
        (128.0, 128.0),
        (-128.0, 128.0)
    )
