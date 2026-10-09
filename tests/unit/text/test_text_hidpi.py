"""On a scaled (HiDPI) display, Text lays out at the screen's resolution.

The tests run with a pixel ratio of 1, so they pretend the display is scaled
by patching the scale Text lays out at. Patching the window's
get_pixel_ratio would also change the viewport.
"""

import pyglet
import pytest

import arcade
from arcade.text import _UnscaledText

RATIO = 2.0


def pretend_scaled(monkeypatch):
    monkeypatch.setattr(arcade.Text, "_render_scale", lambda self, window: RATIO)
    # create_text_sprite opts out, like on a real scaled display
    monkeypatch.setattr(_UnscaledText, "_render_scale", lambda self, window: 1.0)


@pytest.fixture
def scaled(window, monkeypatch):
    pretend_scaled(monkeypatch)


def text(**kwargs):
    return arcade.Text("The quick brown fox", 100, 50, arcade.color.BLACK, 14, **kwargs)


def dark_bounds():
    """The left, bottom, right and top of the dark pixels on screen."""
    image = arcade.get_image().convert("L")
    box = image.point([255 if value < 128 else 0 for value in range(256)]).getbbox()
    assert box, "Nothing was drawn"
    left, top, right, bottom = box
    height = image.height
    return left, height - bottom, right, height - top


@pytest.mark.usefixtures("scaled")
def test_glyphs_are_rasterized_at_the_screen_resolution():
    assert text().label.dpi == 96 * RATIO


@pytest.mark.usefixtures("scaled")
def test_positions_and_sizes_are_in_window_units():
    plain_scale_text = text()
    assert plain_scale_text.x == 100
    assert plain_scale_text.y == 50
    assert plain_scale_text.position == (100, 50)
    assert plain_scale_text.left == pytest.approx(100)

    plain_scale_text.position = 20, 30
    assert plain_scale_text.position == (20, 30)
    plain_scale_text.x = 40
    assert plain_scale_text.x == 40

    wrapped = text(width=150, multiline=True)
    assert wrapped.width == 150
    wrapped.width = 200
    assert wrapped.width == 200


def test_content_size_matches_unscaled_text(window, monkeypatch):
    unscaled = text()
    pretend_scaled(monkeypatch)
    scaled_text = text()
    # Fonts are hinted at each size, so the widths differ a little
    assert scaled_text.content_width == pytest.approx(unscaled.content_width, rel=0.1)
    assert scaled_text.content_height == pytest.approx(unscaled.content_height, rel=0.1)


@pytest.mark.parametrize("use_batch", [False, True], ids=["draw", "batch"])
def test_drawn_where_unscaled_text_is(window, monkeypatch, use_batch):
    window.background_color = arcade.color.WHITE

    window.clear()
    text().draw()
    expected = dark_bounds()

    pretend_scaled(monkeypatch)
    window.clear()
    if use_batch:
        batch = pyglet.graphics.Batch()
        scaled_text = text(batch=batch)
        batch.draw()
    else:
        scaled_text = text()
        scaled_text.draw()
    actual = dark_bounds()

    # Same place and about the same size, not twice as big
    assert actual[0] == pytest.approx(expected[0], abs=3)
    assert actual[1] == pytest.approx(expected[1], abs=3)
    assert actual[2] - actual[0] == pytest.approx(expected[2] - expected[0], rel=0.1)
    assert actual[3] - actual[1] == pytest.approx(expected[3] - expected[1], rel=0.15)
    assert scaled_text.label.dpi == 96 * RATIO


def test_text_sprites_are_unchanged(window, monkeypatch):
    unscaled = arcade.create_text_sprite("The quick brown fox", arcade.color.BLACK, 14)
    pretend_scaled(monkeypatch)
    scaled_sprite = arcade.create_text_sprite("The quick brown fox", arcade.color.BLACK, 14)
    assert scaled_sprite.size == unscaled.size


def test_unscaled_display_is_unchanged(window):
    assert window.get_pixel_ratio() == 1
    plain = text()
    assert plain.label.dpi == 96
    assert plain.label.x == 100
