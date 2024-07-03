import pytest
import arcade
from arcade import LBWH

TEXTURE = arcade.load_texture(":resources:images/items/coinGold.png")


def test_draw_texture_rect(offscreen):
    """Draw a texture rect and compare it to the expected image."""
    region = LBWH(0, 0, *TEXTURE.size)
    arcade.draw_texture_rect(TEXTURE, region, blend=False, pixelated=True) 

    screen_image = offscreen.read_region_image(region, components=3)
    expected_image = TEXTURE.image.convert("RGB")
    offscreen.assert_images_almost_equal(screen_image, expected_image)


def test_draw_sprite(offscreen):
    """Draw a sprite and compare it to the expected image."""
    sprite = arcade.Sprite(TEXTURE, center_x=64, center_y=64)
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
