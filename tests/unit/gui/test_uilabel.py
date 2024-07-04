from unittest.mock import Mock

import pytest
from pyglet.math import Vec2

from arcade.gui import UILabel
from arcade.types import Color, LBWH


def test_uilabel_inits_with_text_size(window):
    label = UILabel(text="Example")

    assert label.rect.width == pytest.approx(
        63, abs=6
    )  # on windows the width differs about 6 pixel
    assert label.rect.height == pytest.approx(19, abs=1)


def test_uilabel_uses_size_parameter(window):
    label = UILabel(text="Example", width=100, height=50)
    assert label.rect == LBWH(0, 0, 100, 50)


def test_uilabel_uses_smaller_size_parameter(window):
    label = UILabel(text="Example", width=20, height=50)
    assert label.rect == LBWH(0, 0, 20, 50)


def test_uilabel_allow_multiline_and_uses_text_height(window):
    label = UILabel(text="E x a m p l e", width=10, multiline=True)
    assert label.rect.left == pytest.approx(0, abs=2)
    assert label.rect.bottom == pytest.approx(0, abs=2)
    assert label.rect.width == pytest.approx(10, abs=2)
    assert label.rect.height == pytest.approx(133, abs=7)


def test_uilabel_with_border_keeps_previous_size(window):
    label = UILabel(text="Example")
    assert label.rect.width == pytest.approx(63, abs=6)
    assert label.rect.height == pytest.approx(19, abs=6)

    label.with_border()
    assert label.rect.width == pytest.approx(63, abs=6)
    assert label.rect.height == pytest.approx(19, abs=6)


def test_uilabel_with_padding_keeps_previous_size(window):
    label = UILabel(text="Example")
    assert label.rect.width == pytest.approx(63, abs=6)
    assert label.rect.height == pytest.approx(19, abs=6)

    label.with_padding(all=2)
    assert label.rect.width == pytest.approx(63, abs=6)
    assert label.rect.height == pytest.approx(19, abs=6)


def test_uilabel_fixes_internal_text_to_pos_0_0(window):
    label = UILabel(text="Example")
    assert label.label.position == (0, 0)
    assert label.position == Vec2(0, 0)

    label = UILabel(text="Example", x=10, y=10)
    assert label.label.position == (0, 0)
    assert label.position == Vec2(10, 10)


def test_adaptive_width_support_for_multiline_text(window):
    """
    This test is a bit tricky. Enabling multiline without a width
    should fit the size to the text. This is not natively supported by either arcade.Text or pyglet.Label.
    Because text length variates between different os, we can only test boundaries, which indicate a proper implementation.
    """
    label = UILabel(text="Multiline\ntext\nwhich\n", multiline=True)
    assert label.width < 100
    assert label.height > 20


def test_change_text_does_full_render_without_background(window):
    """
    This test is a bit tricky. Enabling multiline without a width
    should fit the size to the text. This is not natively supported by either arcade.Text or pyglet.Label.
    Because text length variates between different os, we can only test boundaries, which indicate a proper implementation.
    """

    label = UILabel(text="First Text")
    label.parent = Mock()

    label.text = "Second Text"
    label.parent.trigger_render.assert_called_once()


def test_change_text_does_normal_render_with_background(window):
    """
    This test is a bit tricky. Enabling multiline without a width
    should fit the size to the text. This is not natively supported by either arcade.Text or pyglet.Label.
    Because text length variates between different os, we can only test boundaries, which indicate a proper implementation.
    """

    label = UILabel(text="First Text").with_background(color=Color(255, 255, 255, 255))
    label.parent = Mock()

    label.text = "Second Text"
    label.parent.trigger_render.assert_not_called()


def test_size_hint_contains_border_and_updated(window):
    label = UILabel(text="Example")

    size_hint_min = label.size_hint_min

    label.with_border(width=2)
    assert label.size_hint_min == (size_hint_min[0] + 4, size_hint_min[1] + 4)


def test_size_hint_contains_padding_and_updated(window):
    label = UILabel(text="Example")

    size_hint_min = label.size_hint_min

    label.with_padding(all=3)
    assert label.size_hint_min == (size_hint_min[0] + 6, size_hint_min[1] + 6)


def test_uilabel_automatically_fit_content(uimanager):
    label = UILabel(text="First Text")
    uimanager.add(label)
    start_width = label.rect.width

    label.text = "Second Text, which is way longer"
    uimanager.execute_layout()

    assert label.rect.width > start_width
