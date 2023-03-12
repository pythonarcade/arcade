from pathlib import Path
import pytest
from PIL import Image
import arcade

SPRITE_SHEET_RESOURCE = ":resources:images/spritesheets/codepage_437.png"
SPRITE_SHEET_PATH = arcade.resources.resolve_resource_path(SPRITE_SHEET_RESOURCE)


@pytest.fixture
def image():
    return Image.new("RGBA", (10, 10))


def test_create_from_path():
    ss = arcade.SpriteSheet(SPRITE_SHEET_RESOURCE)
    assert ss.flip_flags == (False, False)
    assert ss.image is not None
    assert ss.path == SPRITE_SHEET_PATH


def test_create_from_image(image):
    ss = arcade.SpriteSheet(image=image)
    assert ss.flip_flags == (False, False)
    assert ss.image == image
    assert ss.path is None


def test_flip():
    ss = arcade.SpriteSheet(SPRITE_SHEET_RESOURCE)
    im = Image.open(SPRITE_SHEET_PATH).convert("RGBA")
    assert ss.image == im
    assert ss.flip_flags == (False, False)

    ss.flip_left_right()
    assert ss.flip_flags == (True, False)
    assert ss.image != im
    im = im.transpose(Image.FLIP_LEFT_RIGHT)
    assert ss.image == im

    ss.flip_top_bottom()
    assert ss.flip_flags == (True, True)
    assert ss.image != im
    im = im.transpose(Image.FLIP_TOP_BOTTOM)
    assert ss.image == im

    # Flip back to original
    ss.flip_left_right()
    ss.flip_top_bottom()
    assert ss.flip_flags == (False, False)


def test_crop():
    pass


def test_crop_grid():
    pass
