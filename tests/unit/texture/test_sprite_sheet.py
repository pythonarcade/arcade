from arcade.types.rect import LBWH
import pytest
from PIL import Image
import arcade

# 32x8 grid of 8x16 sprites
SPRITE_SHEET_RESOURCE = ":resources:images/spritesheets/codepage_437.png"
SPRITE_SHEET_PATH = arcade.resources.resolve(SPRITE_SHEET_RESOURCE)


def get_dollar_sign(sprite_sheet: arcade.SpriteSheet):
    """
    Crop out the dollar sign from the sprite sheet.
    """
    # left, upper, right, and lower
    return sprite_sheet.image.crop((
        9 * 4,  # left: 4th column
        16,  # upper: second row
        9 * 4 + 8,  # right: 8 pixels wide
        16 + 16  # lower: 16 pixels tall
    ))


@pytest.fixture(scope="module")
def image():
    return Image.new("RGBA", (10, 10))


@pytest.fixture(scope="module")
def sprite_sheet():
    return arcade.SpriteSheet(SPRITE_SHEET_RESOURCE)


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


def test_get_image(sprite_sheet):
    """Get an image from the sprite sheet."""
    dollar_sign = get_dollar_sign(sprite_sheet)

    # Crop out the dollar sign using upper left origin
    im = sprite_sheet.get_image(
        LBWH(9 * 4,  # 4th column
        16,  # second row
        8, 16))
    assert isinstance(im, Image.Image)
    assert im.size == (8, 16)
    assert im.tobytes() == dollar_sign.tobytes()

    # Crop out the dollar sign using lower left origin
    im = sprite_sheet.get_image(
        LBWH(9 * 4,  # 4th column
        16 * 6,  # 6th row
        8,16), True)
    assert isinstance(im, Image.Image)
    assert im.size == (8, 16)
    assert im.tobytes() == dollar_sign.tobytes()


def test_get_texture(sprite_sheet):
    """Get a texture from the sprite sheet."""
    texture = sprite_sheet.get_texture(LBWH(0, 0, 8, 16))
    assert isinstance(texture, arcade.Texture)
    assert texture.image.size == (8, 16)


def test_image_grid(sprite_sheet):
    """Get a grid of images from the sprite sheet."""
    images = sprite_sheet.get_image_grid(
        size=(8, 16),
        margin=(0, 1, 0, 0),
        columns=32,
        count=255,
    )
    assert len(images) == 255
    for im in images:
        assert im.size == (8, 16)

    assert images[36].tobytes() == get_dollar_sign(sprite_sheet).tobytes()


def test_get_texture_grid(sprite_sheet):
    """Get a grid of textures from the sprite sheet."""
    textures = sprite_sheet.get_texture_grid(
        size=(8, 16),
        margin=(0, 1, 0, 0),
        columns=32,
        count=255,
    )
    assert len(textures) == 255
    for texture in textures:
        assert texture.image.size == (8, 16)
    
    assert textures[36].image.tobytes() == get_dollar_sign(sprite_sheet).tobytes()
