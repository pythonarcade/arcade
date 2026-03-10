"""Tests that layouts warn when explicit width/height conflicts with active size_hint."""
import warnings

import pytest

from arcade.gui import UIBoxLayout
from arcade.gui.widgets.layout import UIAnchorLayout, UIGridLayout


def test_anchor_layout_warns_when_width_given_with_default_size_hint(window):
    """UIAnchorLayout should warn when width is given but size_hint_x is active."""
    with pytest.warns(UserWarning, match="size_hint_x"):
        UIAnchorLayout(width=500)


def test_anchor_layout_warns_when_height_given_with_default_size_hint(window):
    """UIAnchorLayout should warn when height is given but size_hint_y is active."""
    with pytest.warns(UserWarning, match="size_hint_y"):
        UIAnchorLayout(height=500)


def test_anchor_layout_no_warning_when_size_hint_none(window):
    """UIAnchorLayout should not warn when size_hint=None is explicitly set."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        UIAnchorLayout(width=500, height=500, size_hint=None)


def test_anchor_layout_no_warning_when_no_explicit_size(window):
    """UIAnchorLayout should not warn when width/height are not explicitly given."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        UIAnchorLayout(size_hint=(1, 1))


def test_anchor_layout_no_warning_when_size_hint_x_none(window):
    """UIAnchorLayout should not warn for width when size_hint_x is None."""
    # No width warning expected (only height warning)
    with pytest.warns(UserWarning, match="size_hint_y"):
        UIAnchorLayout(width=500, height=500, size_hint=(None, 1))


def test_anchor_layout_no_warning_when_size_hint_y_none(window):
    """UIAnchorLayout should not warn for height when size_hint_y is None."""
    # No height warning expected (only width warning)
    with pytest.warns(UserWarning, match="size_hint_x"):
        UIAnchorLayout(width=500, height=500, size_hint=(1, None))


def test_box_layout_warns_when_width_given_with_default_size_hint(window):
    """UIBoxLayout should warn when width is given but size_hint_x is active."""
    with pytest.warns(UserWarning, match="size_hint_x"):
        UIBoxLayout(width=200)


def test_box_layout_warns_when_height_given_with_default_size_hint(window):
    """UIBoxLayout should warn when height is given but size_hint_y is active."""
    with pytest.warns(UserWarning, match="size_hint_y"):
        UIBoxLayout(height=200)


def test_box_layout_no_warning_when_size_hint_none(window):
    """UIBoxLayout should not warn when size_hint=None is explicitly set."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        UIBoxLayout(width=200, height=200, size_hint=None)


def test_box_layout_no_warning_when_no_explicit_size(window):
    """UIBoxLayout should not warn when width/height are not explicitly given."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        UIBoxLayout(size_hint=(0, 0))


def test_grid_layout_warns_when_width_given_with_default_size_hint(window):
    """UIGridLayout should warn when width is given but size_hint_x is active."""
    with pytest.warns(UserWarning, match="size_hint_x"):
        UIGridLayout(width=200)


def test_grid_layout_warns_when_height_given_with_default_size_hint(window):
    """UIGridLayout should warn when height is given but size_hint_y is active."""
    with pytest.warns(UserWarning, match="size_hint_y"):
        UIGridLayout(height=200)


def test_grid_layout_no_warning_when_size_hint_none(window):
    """UIGridLayout should not warn when size_hint=None is explicitly set."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        UIGridLayout(width=200, height=200, size_hint=None)


def test_grid_layout_no_warning_when_no_explicit_size(window):
    """UIGridLayout should not warn when width/height are not explicitly given."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        UIGridLayout(size_hint=(0, 0))


def test_warning_message_includes_class_name(window):
    """Warning should include the layout class name for clear identification."""
    with pytest.warns(UserWarning, match="UIBoxLayout"):
        UIBoxLayout(width=200)

    with pytest.warns(UserWarning, match="UIAnchorLayout"):
        UIAnchorLayout(width=200)

    with pytest.warns(UserWarning, match="UIGridLayout"):
        UIGridLayout(width=200)
