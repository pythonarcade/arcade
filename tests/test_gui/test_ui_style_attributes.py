import arcade
import pytest

from arcade.gui.ui_style import UIStyle
from . import MockButton

ELEMENT_STYLE_CLASS = 'uielement'

DEFAULT_COLOR = (114, 47, 55)  # arcade.color.WINE
EXPECTED_COLOR = (135, 255, 104)
EXPECTED_COLOR_STR = str(EXPECTED_COLOR)[1:-1]


@pytest.fixture()
def style() -> UIStyle:
    return UIStyle({
        'globals': {'font_color': arcade.color.BLACK},
        ELEMENT_STYLE_CLASS: {'normal_color': DEFAULT_COLOR}
    })


@pytest.fixture()
def element(mock_mng, style) -> MockButton:
    e = MockButton(style=style)
    e.style_classes.append(ELEMENT_STYLE_CLASS)
    mock_mng.add_ui_element(e)

    return e


def test_get_style_attribute_by_element_class(element):
    assert element.style_attr('normal_color') == DEFAULT_COLOR


def test_fallback_to_global_values(element):
    attr_not_set_in_class_style = 'font_color'
    assert element.style_attr(attr_not_set_in_class_style) == arcade.color.BLACK


def test_can_set_custom_style_attributes(element):
    element.set_style_attrs(normal_color=EXPECTED_COLOR)

    assert element.style_attr('normal_color') == EXPECTED_COLOR


def test_can_remove_custom_attributes(element):
    element.set_style_attrs(normal_color=arcade.color.BLACK)
    element.set_style_attrs(normal_color=None)

    assert element.style_attr('normal_color') == DEFAULT_COLOR


def test_ignores_del_of_attribute_if_they_are_set(element):
    element.set_style_attrs(normal_color=None)

    assert element.style_attr('normal_color') == DEFAULT_COLOR


def test_attr_loaded_from_second_class(element):
    element.style_classes.append('some_class')
    assert element.style_attr('normal_color') == DEFAULT_COLOR


def test_loads_id_style_attributes_first(style):
    element_id = 'my_lovely_element'

    element = MockButton(style=style)
    element.id = element_id

    style.data[element_id] = {'normal_color': EXPECTED_COLOR}

    assert element.style_attr('normal_color') == EXPECTED_COLOR
