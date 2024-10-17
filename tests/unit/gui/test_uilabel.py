from unittest.mock import Mock

import pytest
from pyglet.math import Vec2

from arcade.gui import UILabel
from arcade.types import Color, LBWH


def test_constructor_only_text_no_size(window):
    """Should fit text"""
    label = UILabel(text="Example", font_name="Kenney Pixel")

    assert label.rect.width == 43
    assert label.rect.height == 12


def test_constructor_text_and_size(window):
    label = UILabel(text="Example", width=100, height=50)
    assert label.rect == LBWH(0, 0, 100, 50)


def test_constructor_size_smaller_then_text(window):
    label = UILabel(text="Example", width=20, height=50)
    assert label.rect == LBWH(0, 0, 20, 50)


def test_constructor_fix_width_and_multiline(window):
    label = UILabel(text="E x a m p l e", width=10, multiline=True, font_name="Kenney Pixel")
    assert label.rect.left == 0
    assert label.rect.bottom == 0
    assert label.rect.width == 10
    assert label.rect.height == 84


def test_constructor_adaptive_width_support_for_multiline_text(window):
    """
    This test is a bit tricky. Enabling multiline without a width
    should fit the size to the text. This is not natively supported by either arcade.Text or pyglet.Label.
    Because text length variates between different os, we can only test boundaries, which indicate a proper implementation.
    """
    label = UILabel(text="Multiline\ntext\nwhich\n", multiline=True)
    assert label.width < 100
    assert label.height > 20


def test_with_border_keeps_previous_size(window):
    label = UILabel(text="Example", font_name="Kenney Pixel")
    assert label.rect.width == 43
    assert label.rect.height == 12

    label.with_border()
    assert label.rect.width == 43
    assert label.rect.height == 12


def test_with_padding_keeps_previous_size(window):
    label = UILabel(text="Example", font_name="Kenney Pixel")
    assert label.rect.width == 43
    assert label.rect.height == 12

    label.with_padding(all=2)
    assert label.rect.width == 43
    assert label.rect.height == 12


def test_internals_text_placed_at_0_0(window):
    label = UILabel(text="Example")
    assert label._label.position == (0, 0)
    assert label.position == Vec2(0, 0)

    label = UILabel(text="Example", x=10, y=10)
    assert label._label.position == (0, 0)
    assert label.position == Vec2(10, 10)


def test_change_text_triggers_full_render_without_background(window):
    """
    This test is a bit tricky. Enabling multiline without a width
    should fit the size to the text. This is not natively supported by either arcade.Text or pyglet.Label.
    Because text length variates between different os, we can only test boundaries, which indicate a proper implementation.
    """

    label = UILabel(text="First Text")
    label.parent = Mock()

    label.text = "Second Text"
    label.parent.trigger_render.assert_called_once()


def test_change_text_triggers_render_with_background(window):
    """
    This test is a bit tricky. Enabling multiline without a width
    should fit the size to the text. This is not natively supported by either arcade.Text or pyglet.Label.
    Because text length variates between different os, we can only test boundaries, which indicate a proper implementation.
    """

    label = UILabel(text="First Text").with_background(color=Color(255, 255, 255, 255))
    label.parent = Mock()

    label.text = "Second Text"
    label.parent.trigger_render.assert_not_called()


def test_size_hint_min_contains_border_and_updated(window):
    label = UILabel(text="Example")

    size_hint_min = label.size_hint_min

    label.with_border(width=2)
    assert label.size_hint_min == (size_hint_min[0] + 4, size_hint_min[1] + 4)


def test_size_hint_min_contains_padding_and_updated(window):
    label = UILabel(text="Example")

    size_hint_min = label.size_hint_min

    label.with_padding(all=3)
    assert label.size_hint_min == (size_hint_min[0] + 6, size_hint_min[1] + 6)


def test_multiline_exposed_as_property(window):
    label = UILabel(text="Example")
    assert not label.multiline

    label = UILabel(text="Example", multiline=True)
    assert label.multiline


def test_size_hint_min_adapts_to_new_text(window):
    label = UILabel(text="First Text")

    # WHEN, text is changed and layout is executed
    shm_w, shm_h = label.size_hint_min
    label.text = "Second Text, which is way longer"

    assert label.size_hint_min[0] > shm_w
    assert label.size_hint_min[1] == shm_h


def test_size_hint_min_adapts_to_bigger_font(window):
    label = UILabel(text="First Text")

    # WHEN, text is changed and layout is executed
    shm_w, shm_h = label.size_hint_min
    label.update_font(font_size=20)

    assert label.size_hint_min[0] > shm_w
    assert label.size_hint_min[1] > shm_h


def test_size_hint_min_adapts_to_smaller_font(window):
    label = UILabel(text="First Text")

    # WHEN, text is changed and layout is executed
    shm_w, shm_h = label.size_hint_min
    label.update_font(font_size=2)

    assert label.size_hint_min[0] < shm_w
    assert label.size_hint_min[1] < shm_h


def test_multiline_enabled_size_hint_min_adapts_to_new_text(window):
    """Tests multiline with auto size. It should adapt to new text.

    Due to the multiline, and the preset width, the height should change.
    The width might change, but only if the text wrap shortens the longest line.
    """
    label = UILabel(text="First Text", multiline=True)

    # WHEN, text is changed and layout is executed
    shm_w, shm_h = label.size_hint_min
    label.text = "Second Text, which is way longer"

    assert label.size_hint_min[0] < shm_w
    assert label.size_hint_min[1] > shm_h


def test_integration_with_layout_fit_to_content(ui):
    """Tests multiple integrations with layout/uimanager and auto size.

    Just to be sure, it really works as expected.
    """
    label = UILabel(
        text="Example",
        size_hint=(0, 0),  # default, enables auto size
        font_name="Kenney Pixel",
    )

    ui.add(label)
    ui.execute_layout()

    # auto size should fit the text
    assert label.rect.width == 44
    assert label.rect.height == 12

    # even when text changed
    label.text = "Example, which is way longer"
    ui.execute_layout()

    assert label.rect.width > 63
    assert label.rect.height == 12

    # or font
    label.text = "Example"
    label.update_font(font_size=20)
    ui.execute_layout()

    assert label.rect.width > 63
    assert label.rect.height > 12


def test_fit_content_overrides_width(ui):
    label = UILabel(
        text="Example",
        width=100,
        height=50,
        font_name="Kenney Pixel",
    )

    label.fit_content()

    assert label.rect.width == 44
    assert label.rect.height == 12


def test_fit_content_uses_adaptive_multiline_width(ui):
    label = UILabel(
        text="Example with multiline enabled",
        width=70,
        multiline=True,
    )
    shm_w, shm_h = label.size_hint_min

    label.fit_content()

    assert label.rect.width > 70
    assert label.rect.height < 25

    # check size_hint_min updated
    assert label.size_hint_min[0] > shm_w
    assert label.size_hint_min[1] < shm_h
