from unittest.mock import Mock

import arcade
from tests.test_gui import MockButton


def test_ui_element_renders_on_style_change():
    render_mock: Mock = Mock()
    button = MockButton()
    button.render = render_mock

    button.set_style_attrs(color=arcade.color.BLUE)

    render_mock.assert_called_once()


def test_ui_element_not_renders_on_style_change_with_foreign_id():
    render_mock: Mock = Mock()
    button = MockButton(id='this-button')
    button.render = render_mock

    button.style.set_class_attrs('other-button', color=arcade.color.BLUE)

    render_mock.assert_not_called()


def test_ui_element_renders_on_style_change_with_own_id():
    this_button_id = 'this-button'
    render_mock: Mock = Mock()
    button = MockButton(id=this_button_id)
    button.render = render_mock

    button.style.set_class_attrs(this_button_id, color=arcade.color.BLUE)

    render_mock.assert_called_once()


