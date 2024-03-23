import pytest

import arcade


def test_text_instance_raise_multiline_error(window):
    with pytest.raises(ValueError) as e:
        _ = arcade.Text("Initial text", 0, 0, multiline=True)

    assert e.value.args[0] == "The 'width' parameter must be set when 'multiline' is True."


def test_text_function_raise_multiline_error(window):
    with pytest.raises(ValueError) as e:
        _ = arcade.draw_text("Initial text", 0, 0, multiline=True)

    assert e.value.args[0] == "The 'width' parameter must be set when 'multiline' is True."
