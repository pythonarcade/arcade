import pytest

from arcade.gui import UILabel, Rect


def test_uilabel_inits_with_text_size(window):
    label = UILabel(text="Example")

    assert label.rect.width == pytest.approx(63, abs=6)  # on windows the width differs about 6 pixel
    assert label.rect.height == 19


def test_uilabel_uses_size_parameter(window):
    label = UILabel(text="Example", width=100, height=50)
    assert label.rect == Rect(0, 0, 100, 50)


def test_uilabel_uses_smaller_size_parameter(window):
    label = UILabel(text="Example", width=20, height=50)
    assert label.rect == Rect(0, 0, 20, 50)


def test_uilabel_allow_multiline_and_uses_text_height(window):
    label = UILabel(text="E x a m p l e", width=10, multiline=True)
    assert label.rect == Rect(0, 0, 10, 133)


def test_uilabel_with_border_keeps_previous_size(window):
    label = UILabel(text="Example")
    assert label.rect.width == pytest.approx(63, abs=6)
    assert label.rect.height == 19

    label.with_border()
    assert label.rect.width == pytest.approx(63, abs=6)
    assert label.rect.height == 19


def test_uilabel_with_padding_keeps_previous_size(window):
    label = UILabel(text="Example")
    assert label.rect.width == pytest.approx(63, abs=6)
    assert label.rect.height == 19

    label.with_padding(all=2)
    assert label.rect.width == pytest.approx(63, abs=6)
    assert label.rect.height == 19


def test_uilabel_fixes_internal_text_to_pos_0_0(window):
    label = UILabel(text="Example")
    assert label.label.position == (0, 0)
    assert label.position == (0, 0)

    label = UILabel(text="Example", x=10, y=10)
    assert label.label.position == (0, 0)
    assert label.position == (10, 10)
