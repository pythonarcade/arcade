"""Tests that Text only lays out its text again when something changes"""

import pytest
from pyglet.text import LinearGradient

import arcade

FONT = "Liberation Sans"


def _render(window, text: arcade.Text):
    """Draw a Text into an offscreen framebuffer and return its pixels"""
    ctx = window.ctx
    fbo = ctx.framebuffer(color_attachments=[ctx.texture((400, 200), components=4)])
    with fbo.activate():
        fbo.clear(color=(0, 0, 0, 0))
        text.draw()
    return fbo.read(components=4)


def _count_layouts(text: arcade.Text) -> list[int]:
    """Count the label's full layouts, which is what makes changes slow"""
    label = text.label
    count = [0]
    update = label._update

    def counting_update():
        # pyglet skips the layout while an update is in progress
        if label._update_enabled:
            count[0] += 1
        update()

    label._update = counting_update
    return count


# Each property with its current value, which setting again should not lay out
SAME_VALUES = (
    ("text", "Hello"),
    ("value", "Hello"),
    ("x", 10),
    ("y", 20),
    ("position", (10, 20)),
    ("font_name", (FONT,)),
    ("font_size", 20),
    ("color", (255, 255, 255)),
    ("bold", False),
    ("italic", False),
    ("anchor_x", "left"),
    ("anchor_y", "baseline"),
    ("rotation", 0),
    ("align", "left"),
    ("width", 300),
    ("height", None),
    ("multiline", True),
    ("tracking", 0),
    ("visible", True),
)


@pytest.fixture
def text(window) -> arcade.Text:
    text = arcade.Text("Hello", 10, 20, font_name=(FONT,), font_size=20, width=300, multiline=True)
    text.tracking = 0
    return text


@pytest.mark.parametrize(("name", "value"), SAME_VALUES)
def test_same_value_does_not_lay_out(text, name, value):
    layouts = _count_layouts(text)
    setattr(text, name, value)
    assert layouts[0] == 0


def test_same_gradient_does_not_lay_out(text):
    gradient = LinearGradient((255, 0, 0, 255), (0, 0, 255, 255))
    text.color = gradient
    layouts = _count_layouts(text)
    text.color = LinearGradient((255, 0, 0, 255), (0, 0, 255, 255))
    assert layouts[0] == 0


def test_font_name_list_matches_tuple(text):
    layouts = _count_layouts(text)
    text.font_name = [FONT]
    assert layouts[0] == 0


def test_font_name_changed_on_label_is_set_again(text):
    """Setting the same font name again works if the label was changed directly"""
    text.label.font_name = "Liberation Serif"
    text.font_name = (FONT,)
    assert text.label.font_name == FONT


def test_empty_with_block_does_not_lay_out(text):
    layouts = _count_layouts(text)
    with text:
        pass
    with text:
        for name, value in SAME_VALUES:
            setattr(text, name, value)
    assert layouts[0] == 0


def test_cheap_changes_in_with_block_do_not_lay_out(text):
    layouts = _count_layouts(text)
    with text:
        text.position = 50, 60
        text.color = arcade.color.RED
        text.rotation = 10
    assert layouts[0] == 0
    assert text.position == (50, 60)
    assert text.color == arcade.color.RED
    assert text.rotation == 10


def test_with_block_lays_out_once(text):
    layouts = _count_layouts(text)
    with text:
        text.text = "Changed text"
        text.font_size = 24
        text.bold = True
        text.italic = True
        text.width = 350
        text.align = "center"
    assert layouts[0] == 1


def test_nested_with_blocks_lay_out_once(text):
    layouts = _count_layouts(text)
    with text:
        text.text = "Changed"
        with text:
            text.font_size = 24
        assert layouts[0] == 0
    assert layouts[0] == 1


def test_with_block_ends_update_after_exception(text):
    with pytest.raises(ZeroDivisionError):
        with text:
            text.text = "Changed"
            raise ZeroDivisionError
    assert text.label._update_enabled
    layouts = _count_layouts(text)
    text.font_size = 30
    assert layouts[0] == 1


def test_changes_outside_with_block_lay_out_right_away(text):
    layouts = _count_layouts(text)
    text.font_size = 24
    assert layouts[0] == 1
    # pyglet replaces text by deleting it and inserting the new text,
    # which lays out twice, but the first layout is of empty text
    text.text = "Changed"
    assert layouts[0] > 1
    assert text.content_width > 0


def test_with_block_draws_like_new_text(window, text):
    with text:
        text.anchor_x = "center"
        text.color = arcade.color.YELLOW
        text.text = "A longer line of changed text"
        text.font_size = 16
        text.position = 200, 100
        text.italic = True
        text.align = "center"

    expected = arcade.Text(
        "A longer line of changed text",
        200,
        100,
        color=arcade.color.YELLOW,
        font_name=(FONT,),
        font_size=16,
        width=300,
        multiline=True,
        anchor_x="center",
        italic=True,
        align="center",
    )
    expected.tracking = 0
    assert _render(window, text) == _render(window, expected)


def test_text_pool_unchanged_does_not_lay_out(window):
    pool = arcade.TextPool(font_name=FONT)
    text = pool.get("score", "Score: 10", 10, 10, arcade.color.WHITE, 16, bold=True)
    layouts = _count_layouts(text)
    for _ in range(10):
        pool.get("score", "Score: 10", 10, 10, arcade.color.WHITE, 16, bold=True)
    assert layouts[0] == 0

    pool.get("score", "Score: 20", 30, 10, arcade.color.RED, 18, bold=True)
    assert layouts[0] == 1
    assert text.text == "Score: 20"
    assert text.font_size == 18
