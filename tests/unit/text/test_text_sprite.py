import pytest
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
