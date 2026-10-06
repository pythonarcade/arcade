import PIL.Image
import PIL.ImageChops
import pytest
from pyglet.text import LinearGradient

import arcade


@pytest.mark.parametrize("color", (arcade.color.WHITE, (255, 255, 255), (255, 255, 255, 255)))
def test_create(window, color):
    sprite = arcade.create_text_sprite("Hello World", color)
    assert isinstance(sprite, arcade.Sprite)
    assert sprite.width == pytest.approx(75, rel=10)
    assert sprite.height == pytest.approx(20, rel=5)


def _ink(image):
    """Total alpha of an image, as a measure of how much was drawn"""
    return sum(value * count for value, count in enumerate(image.getchannel("A").histogram()))


def _sprite_bounds(sprite):
    return sprite.left, sprite.right, sprite.bottom, sprite.top


def _text_bounds(text):
    return text.left, text.right, text.bottom, text.top


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"anchor_x": "center"},
        {"anchor_x": "right"},
        {"font_size": 40},
        {"multiline": True, "width": 120},
        {"multiline": True, "width": 90, "align": "center", "anchor_x": "center"},
    ],
)
def test_position_matches_text(window, kwargs):
    """The sprite covers the same area as a Text object at the same position"""
    text = "Two lines of text gj"
    sprite = arcade.create_text_sprite(text, **kwargs)
    text_object = arcade.Text(text, 0, 0, anchor_y="baseline", **kwargs)
    assert _sprite_bounds(sprite) == pytest.approx(_text_bounds(text_object), abs=1)


@pytest.mark.parametrize("anchor_x", ["left", "center", "right"])
def test_anchor_draws_all_text(window, anchor_x):
    """Every anchor puts all of the text inside the texture"""
    atlas = window.ctx.default_atlas
    # Read each image right away, so this doesn't depend on the sprites
    # having separate images (tested below)
    anchored = arcade.create_text_sprite("Hello World", font_size=20, anchor_x=anchor_x)
    actual = _ink(atlas.read_texture_image_from_atlas(anchored.texture))
    left = arcade.create_text_sprite("Hello World", font_size=20)
    expected = _ink(atlas.read_texture_image_from_atlas(left.texture))
    assert expected > 0
    assert actual == pytest.approx(expected, rel=0.01)


def test_same_text_different_style(window):
    """Sprites with the same text keep their own images"""
    atlas = window.ctx.default_atlas
    small_red = arcade.create_text_sprite("Same", color=arcade.color.RED, font_size=20)
    red_image = atlas.read_texture_image_from_atlas(small_red.texture)

    big_blue = arcade.create_text_sprite("Same", color=arcade.color.BLUE, font_size=40)

    # Each texture has an atlas region of its own size
    for sprite in (small_red, big_blue):
        region = atlas.get_texture_region_info(sprite.texture.atlas_name)
        assert (region.width, region.height) == sprite.texture.size
    assert big_blue.texture.size != small_red.texture.size

    # Creating the second sprite didn't change the first one's image
    assert atlas.read_texture_image_from_atlas(small_red.texture).tobytes() == red_image.tobytes()
    red, _green, blue, _alpha = red_image.getextrema()
    assert red[1] > 200 and blue[1] == 0


def test_survives_atlas_rebuild(window):
    """The text is kept when the atlas rebuilds itself from the textures' images"""
    atlas = window.ctx.default_atlas
    sprite = arcade.create_text_sprite("Hello World", color=arcade.color.RED, font_size=20)
    image = atlas.read_texture_image_from_atlas(sprite.texture)
    assert _ink(image) > 0
    # The texture's own image has the text too
    assert sprite.texture.image.tobytes() == image.tobytes()

    atlas.rebuild()
    assert atlas.read_texture_image_from_atlas(sprite.texture).tobytes() == image.tobytes()


def test_empty_text(window):
    """An empty string makes a transparent sprite instead of failing"""
    sprite = arcade.create_text_sprite("")
    assert sprite.texture.width >= 1
    assert sprite.texture.height >= 1
    image = window.ctx.default_atlas.read_texture_image_from_atlas(sprite.texture)
    assert _ink(image) == 0


BACKGROUND = (40, 80, 160, 255)


def _pixels(image) -> list[tuple[int, int, int, int]]:
    data = image.convert("RGBA").tobytes()
    return [tuple(data[i : i + 4]) for i in range(0, len(data), 4)]


def _direct_over_background(window, text: arcade.Text, size):
    """Draw a Text directly over an opaque background, the size of its sprite"""
    text.x = -text.left
    text.y = -text.bottom
    ctx = window.ctx
    fbo = ctx.framebuffer(color_attachments=[ctx.texture(size, components=4)])
    with fbo.activate():
        fbo.clear(color=BACKGROUND)
        text.draw()
    image = PIL.Image.frombytes("RGBA", size, fbo.read(components=4))
    # Atlas images are stored upside down compared to framebuffer reads
    return image.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)


@pytest.mark.parametrize(
    "color",
    [
        arcade.color.WHITE,
        (255, 50, 50, 255),
        (255, 255, 255, 128),
        (50, 255, 50, 60),
        LinearGradient((255, 0, 0, 255), (0, 0, 255, 128)),
    ],
)
def test_texture_matches_text_drawn_directly(window, color):
    """
    The sprite's texture, drawn over a background, looks like the text drawn
    directly. Text with partial alpha used to get its alpha squared and its
    color multiplied by its alpha, so sprites were drawn too faint.
    """
    kwargs = dict(font_name="Liberation Sans", font_size=30, color=color)
    sprite = arcade.create_text_sprite("Hello World", **kwargs)
    image = sprite.texture.image
    background = PIL.Image.new("RGBA", image.size, BACKGROUND)
    via_sprite = PIL.Image.alpha_composite(background, image)
    direct = _direct_over_background(window, arcade.Text("Hello World", 0, 0, **kwargs), image.size)

    diff = PIL.ImageChops.difference(via_sprite.convert("RGB"), direct.convert("RGB"))
    assert max(high for _low, high in diff.getextrema()) <= 2


def test_opaque_text_is_opaque(window):
    sprite = arcade.create_text_sprite("Hello", font_name="Liberation Sans", font_size=30)
    alpha = sprite.texture.image.getchannel("A")
    assert alpha.getextrema() == (0, 255)
    # Edge pixels keep the text's own color, not a darker one. Dividing out
    # an 8 bit alpha can be off by a little.
    colors = {pixel[:3] for pixel in _pixels(sprite.texture.image) if pixel[3] > 0}
    assert min(min(color) for color in colors) >= 253


def test_alpha_text_keeps_its_alpha(window):
    sprite = arcade.create_text_sprite(
        "Hello", font_name="Liberation Sans", font_size=30, color=(255, 255, 255, 128)
    )
    # Used to be 64: the alpha was squared
    assert sprite.texture.image.getchannel("A").getextrema()[1] in (127, 128, 129)


def test_partly_transparent_background(window):
    sprite = arcade.create_text_sprite(
        "Hello", font_name="Liberation Sans", font_size=30, background_color=(0, 0, 0, 128)
    )
    image = sprite.texture.image
    # Away from the text, the background is unchanged
    assert image.getpixel((0, 0)) == (0, 0, 0, 128)
    # Over the text it's covered by opaque white text
    assert (255, 255, 255, 255) in set(_pixels(image))


def test_opaque_background(window):
    sprite = arcade.create_text_sprite(
        "Hello", font_name="Liberation Sans", font_size=30, background_color=arcade.color.BLUE
    )
    image = sprite.texture.image
    assert image.getchannel("A").getextrema() == (255, 255)
    assert image.getpixel((0, 0)) == (0, 0, 255, 255)
