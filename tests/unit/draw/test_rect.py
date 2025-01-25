from PIL import Image, ImageDraw

import arcade
from arcade import LBWH

IMAGE = Image.new("RGBA", (2, 2), (0, 0, 0, 0))
draw = ImageDraw.Draw(IMAGE)
draw.point((0, 0), fill=(255, 0, 0, 255))  # upper left
draw.point((1, 0), fill=(0, 255, 0, 255))  # upper right
draw.point((0, 1), fill=(0, 0, 255, 255))  # lower left
draw.point((1, 1), fill=(255, 255, 255, 255))  # lower right

TEXTURE = arcade.Texture(IMAGE)


def test_draw_texture_rect(window, offscreen):
    """Draw a texture rect and compare it to the expected image."""
    region = LBWH(0, 0, *TEXTURE.size)
    arcade.draw_texture_rect(TEXTURE, region, blend=False, pixelated=True) 

    screen_image = offscreen.read_region_image(region, components=3)
    expected_image = TEXTURE.image.convert("RGB")
    offscreen.assert_images_almost_equal(screen_image, expected_image)


def test_draw_sprite(offscreen):
    """Draw a sprite and compare it to the expected image."""
    sprite = arcade.Sprite(TEXTURE, center_x=1.0, center_y=1.0)
    region = LBWH(0, 0, *TEXTURE.size)

    arcade.draw_sprite(sprite, blend=False, pixelated=True)

    screen_image = offscreen.read_region_image(region, components=3)
    expected_image = TEXTURE.image.convert("RGB")
    offscreen.assert_images_almost_equal(screen_image, expected_image, abs=1)


def test_draw_sprite_rect(offscreen):
    """Draw a sprite and compare it to the expected image."""
    sprite = arcade.Sprite(TEXTURE, center_x=64, center_y=64)
    region = LBWH(0, 0, *TEXTURE.size)

    arcade.draw_sprite_rect(sprite, region, blend=False, pixelated=True)

    screen_image = offscreen.read_region_image(region, components=3)
    expected_image = TEXTURE.image.convert("RGB")
    offscreen.assert_images_almost_equal(screen_image, expected_image, abs=1)
