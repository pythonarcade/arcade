import pytest
import arcade
from arcade import hitbox
from PIL import Image, ImageDraw


def test_create():
    texture = arcade.Texture(Image.new("RGBA", (10, 10)))
    assert texture.width == 10
    assert texture.height == 10
    assert texture.file_path is None
    assert texture.crop_values is None
    assert texture.image_data.hash == "7a12e561363385e9dfeeab326368731c030ed4b374e7f5897ac819159d2884c5"
    assert texture.cache_name == f"{texture.image_data.hash}|{texture._vertex_order}|{texture.hit_box_algorithm.cache_name}|"

    with pytest.raises(TypeError):
        _ = arcade.Texture("not valid image data")


def test_create_override_name():
    texture = arcade.Texture(Image.new("RGBA", (10, 10)), hash="test")
    assert texture.cache_name == f"test|{texture._vertex_order}|{texture.hit_box_algorithm.cache_name}|"


def test_hitbox_algo_selection():
    image = Image.new("RGBA", (10, 10), color=(255, 255, 255, 255))

    # Default algorithm
    texture = arcade.Texture(image)
    assert texture.hit_box_algorithm is hitbox.algo_default


def test_rotate():
    texture = arcade.Texture(Image.new("RGBA", (10, 10)))
    texture_rot90 = texture.rotate_90()

    assert texture._vertex_order != texture_rot90._vertex_order
    assert texture.cache_name != texture_rot90.cache_name
    assert texture.image_data == texture_rot90.image_data


def test_crop():
    # Create a texture with 4 sections with different colors
    image = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 4, 4), fill=(255, 0, 0, 255))
    draw.rectangle((5, 0, 9, 5), fill=(0, 255, 0, 255))
    draw.rectangle((0, 5, 5, 9), fill=(0, 0, 255, 255))
    draw.rectangle((5, 5, 9, 9), fill=(255, 255, 255, 255))
    texture = arcade.Texture(image)

    # Conditions returning th same texture (no crop, same size)
    assert texture == texture.crop(0, 0, 0, 0)
    assert texture == texture.crop(0, 0, 10, 10)

    with pytest.raises(ValueError):
        texture.crop(-1, -1, -1, -1)

    # Crop the four sections
    texture_red = texture.crop(0, 0, 5, 5)
    texture_green = texture.crop(5, 0, 5, 5)
    texture_blue = texture.crop(0, 5, 5, 5)
    texture_white = texture.crop(5, 5, 5, 5)

    assert texture_red.image.size == (5, 5)
    assert texture_green.image.size == (5, 5)
    assert texture_blue.image.size == (5, 5)
    assert texture_white.image.size == (5, 5)

    assert texture_red.image.tobytes() == b"\xff\x00\x00\xff" * 25
    assert texture_green.image.tobytes() == b"\x00\xff\x00\xff" * 25
    assert texture_blue.image.tobytes() == b"\x00\x00\xff\xff" * 25
    assert texture_white.image.tobytes() == b"\xff\xff\xff\xff" * 25
