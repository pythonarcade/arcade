"""Tests for the Text color, bold, and italic properties, and constructor errors"""

import pytest
from pyglet.enums import Style, Weight
from pyglet.text import LinearGradient

import arcade
from arcade.exceptions import NoArcadeWindowError

FONT = "Liberation Sans"
GRADIENT = LinearGradient((255, 0, 0, 255), (0, 0, 255, 255))


def _render(window, text: arcade.Text):
    """Draw a Text into an offscreen framebuffer and return its pixels"""
    ctx = window.ctx
    fbo = ctx.framebuffer(color_attachments=[ctx.texture((400, 100), components=4)])
    with fbo.activate():
        fbo.clear(color=(0, 0, 0, 0))
        text.draw()
    return fbo.read(components=4)


def _make(**kwargs) -> arcade.Text:
    return arcade.Text("Hello World", 10, 30, font_name=FONT, font_size=30, **kwargs)


def test_italic_setter_changes_font(window):
    normal = _render(window, _make())
    italic = _render(window, _make(italic=True))
    assert normal != italic

    text = _make()
    text.italic = True
    assert text.italic is True
    assert _render(window, text) == italic

    text.italic = False
    assert text.italic is False
    assert _render(window, text) == normal


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (False, False),
        (True, True),
        ("normal", False),
        ("italic", True),
        (Style.ITALIC, True),
        ("oblique", "oblique"),
    ),
)
def test_italic_values(window, value, expected):
    assert _make(italic=value).italic == expected

    text = _make()
    text.italic = value
    assert text.italic == expected


@pytest.mark.parametrize(
    ("value", "expected_bold", "expected_weight"),
    (
        (False, False, "normal"),
        (True, True, "bold"),
        ("normal", False, "normal"),
        ("bold", True, "bold"),
        (Weight.BOLD, True, "bold"),
        ("light", "light", "light"),
        ("semibold", "semibold", "semibold"),
        (Weight.BLACK, "black", "black"),
    ),
)
def test_bold_values(window, value, expected_bold, expected_weight):
    text = _make(bold=value)
    assert text.bold == expected_bold
    assert text.label.weight == expected_weight

    text = _make()
    text.bold = value
    assert text.bold == expected_bold
    assert text.label.weight == expected_weight


def test_bold_normal_string_draws_normal(window):
    """bold="normal" used to be treated as True, since it's a non-empty string"""
    normal = _render(window, _make())
    assert _render(window, _make(bold="normal")) == normal
    assert _render(window, _make(bold=True)) != normal


def test_gradient_color(window):
    text = _make(color=GRADIENT)
    assert text.color == GRADIENT

    text = _make()
    text.color = GRADIENT
    assert text.color == GRADIENT
    assert text.label.color == GRADIENT

    # Setting a plain color again works, and returns a Color
    text.color = (0, 255, 0)
    assert text.color == arcade.types.Color(0, 255, 0, 255)
    assert isinstance(text.color, arcade.types.Color)


def _red_blue_totals(pixels):
    """Sum of red in the left half and blue in the right half, and the reverse"""
    width = 400
    left_red = right_red = left_blue = right_blue = 0
    for i in range(0, len(pixels), 4):
        x = (i // 4) % width
        if x < width // 2:
            left_red += pixels[i]
            left_blue += pixels[i + 2]
        else:
            right_red += pixels[i]
            right_blue += pixels[i + 2]
    return left_red, right_red, left_blue, right_blue


def test_gradient_draws_left_to_right(window):
    pixels = _render(window, _make(color=GRADIENT, width=380, align="center"))
    left_red, right_red, left_blue, right_blue = _red_blue_totals(pixels)
    assert left_red > right_red
    assert right_blue > left_blue


# Tests draw_text, which warns that it's slow
@pytest.mark.filterwarnings("ignore::arcade.exceptions.PerformanceWarning")
def test_draw_text_gradient(window):
    window.ctx.label_cache.clear()
    arcade.draw_text("Hello", 10, 10, color=GRADIENT)
    arcade.draw_text("Hello", 10, 10, color=arcade.color.RED)
    arcade.draw_text("Hello", 10, 10, color=GRADIENT)
    (label,) = window.ctx.label_cache.values()
    assert label.color == GRADIENT


def test_bad_arguments_raise_in_constructor(window):
    """These used to be swallowed, then raised later when the text was first used"""
    with pytest.raises(TypeError):
        arcade.Text("Hello", 0, 0, font_name=123)  # type: ignore


def test_lazy_init_without_window(window, monkeypatch):
    """Creating a Text before there's a window still works, and creates the label later"""

    def no_window():
        raise NoArcadeWindowError("No window")

    with monkeypatch.context() as patch:
        patch.setattr(arcade, "get_window", no_window)
        text = arcade.Text("Hello", 0, 0, italic=True, bold="light", color=GRADIENT)
        assert not text._initialized

    assert text.italic is True
    assert text.bold == "light"
    assert text.color == GRADIENT
    assert text._initialized
