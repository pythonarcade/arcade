import pytest

import arcade


def test_text_instance_raise_multiline_error(window):
    with pytest.raises(ValueError) as e:
        _ = arcade.Text("Initial text", 0, 0, width=0, multiline=True)

    assert e.value.args[0] == "The 'width' parameter must be set to a non-zero value when 'multiline' is True, but got 0."

    with pytest.raises(ValueError) as e:
        _ = arcade.Text("Initial text", 0, 0, width=None, multiline=True)

    assert e.value.args[0] == "The 'width' parameter must be set to a non-zero value when 'multiline' is True, but got None."


def test_text_function_raise_multiline_error(window):
    with pytest.raises(ValueError) as e:
        _ = arcade.draw_text("Initial text", 0, 0, width=0, multiline=True)

    assert e.value.args[0] == "The 'width' parameter must be set to a non-zero value when 'multiline' is True, but got 0."

    with pytest.raises(ValueError) as e:
        _ = arcade.draw_text("Initial text", 0, 0, width=None, multiline=True)

    assert e.value.args[0] == "The 'width' parameter must be set to a non-zero value when 'multiline' is True, but got None."
