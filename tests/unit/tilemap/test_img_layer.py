import PIL.Image
from pytiled_parser import Color

import arcade
from arcade.tilemap.tilemap import _make_color_transparent


def test_image_layer():
    # Read in the tiled map
    tile_map = arcade.load_tilemap(":fixtures:tilemaps/image_layer.json")

    # --- Platforms ---
    assert "img" in tile_map.sprite_lists
    assert len(tile_map.sprite_lists["img"]) == 1

    image = tile_map.sprite_lists["img"][0]

    assert image.width == 1024
    assert image.height == 600
    assert image.left == 0
    assert image.top == 1920

    assert "img-offset" in tile_map.sprite_lists
    assert len(tile_map.sprite_lists["img-offset"]) == 1
    image = tile_map.sprite_lists["img-offset"][0]

    assert image.width == 1024
    assert image.height == 600
    assert image.left == 1280
    assert image.top == 1408


def test_image_layer_with_scaling():
    # Read in the tiled map
    tile_map = arcade.load_tilemap(":fixtures:tilemaps/image_layer.json", 0.5)

    # --- Platforms ---
    assert "img" in tile_map.sprite_lists
    assert len(tile_map.sprite_lists["img"]) == 1
    image = tile_map.sprite_lists["img"][0]

    assert image.width == 512
    assert image.height == 300
    assert image.left == 0
    assert image.top == 960

    assert "img-offset" in tile_map.sprite_lists
    assert len(tile_map.sprite_lists["img-offset"]) == 1
    image = tile_map.sprite_lists["img-offset"][0]

    assert image.width == 512
    assert image.height == 300
    assert image.left == 640
    assert image.top == 704


def test_image_layer_transparent_color():
    """Pixels of the layer's transparent color become transparent"""
    tile_map = arcade.load_tilemap(":fixtures:tilemaps/image_layer_transparent.json")
    image = tile_map.sprite_lists["img"][0].texture.image
    original = PIL.Image.open(
        arcade.resources.resolve(":resources:images/spritesheets/number_sheet.png")
    ).convert("RGBA")

    data = image.tobytes()
    original_data = original.tobytes()
    white = 0
    for i in range(0, len(data), 4):
        pixel = tuple(data[i : i + 4])
        original_pixel = tuple(original_data[i : i + 4])
        if original_pixel[:3] == (255, 255, 255):
            white += 1
            assert pixel == (255, 255, 255, 0)
        else:
            assert pixel == original_pixel
    assert white > 0


def test_make_color_transparent():
    image = PIL.Image.new("RGBA", (4, 1))
    image.putpixel((0, 0), (10, 20, 30, 255))
    image.putpixel((1, 0), (10, 20, 30, 128))  # Alpha doesn't matter
    image.putpixel((2, 0), (10, 20, 31, 255))  # One band differs
    image.putpixel((3, 0), (0, 0, 0, 255))
    _make_color_transparent(image, Color(10, 20, 30, 255))
    assert [image.getpixel((x, 0)) for x in range(4)] == [
        (255, 255, 255, 0),
        (255, 255, 255, 0),
        (10, 20, 31, 255),
        (0, 0, 0, 255),
    ]
