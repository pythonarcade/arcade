from pathlib import Path

import pytest

from arcade.gui.utils import parse_value


def test_parse_rgb():
    assert parse_value("21,19,21") == (21, 19, 21)
    assert parse_value("21, 19, 21") == (21, 19, 21)


def test_parse_hex():
    assert parse_value("fff") == (255, 255, 255)
    assert parse_value("ffffff") == (255, 255, 255)


def test_parse_font_name():
    assert parse_value(["Calibri", "Arial"]) == ["Calibri", "Arial"]


def test_parse_empty_value():
    assert parse_value(None) is None
    assert parse_value("None") is None
    assert parse_value("") is None


def test_parse_path():
    assert parse_value(".") == Path(".")


def test_parsing_unknown():
    with pytest.warns(UserWarning):
        assert parse_value("not parsable") == "not parsable"
