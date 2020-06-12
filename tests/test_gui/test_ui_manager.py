from uuid import uuid4

import pytest

from arcade.gui import UIException, UIElement, UIEvent
from . import MockButton


def test_ui_manager_dispatch_ui_event(mock_mng):
    # GIVEN
    test_event = UIEvent('some-ui-event')
    catched_event = None

    def on_ui_event(event):
        nonlocal catched_event
        catched_event = event

    mock_mng.push_handlers(on_ui_event)

    # WHEN
    mock_mng.disptach_ui_event(test_event)

    # THEN
    assert catched_event == test_event


def test_ui_elements_get_reference_to_mng(mock_mng):
    ui_element = MockButton()

    mock_mng.add_ui_element(ui_element)

    assert ui_element.mng == mock_mng


def test_can_search_ui_elements_by_id(mock_mng):
    mock_button = MockButton(id=str(uuid4()))

    mock_mng.add_ui_element(mock_button)

    assert mock_mng.find_by_id(mock_button.id) == mock_button


def test_can_set_id_after_creation(mock_mng, mock_button):
    mock_button.id = str(uuid4())

    mock_mng.add_ui_element(mock_button)

    assert mock_mng.find_by_id(mock_button.id) == mock_button


def test_find_by_id_returns_none(mock_mng):
    assert mock_mng.find_by_id('no element here') is None


def test_duplicate_ids_raise_an_ui_exception(mock_mng):
    ui_element_1 = MockButton(id='element1')
    ui_element_2 = MockButton(id='element1')
    mock_mng.add_ui_element(ui_element_1)

    with pytest.raises(UIException) as e:
        mock_mng.add_ui_element(ui_element_2)

    assert 'duplicate id "element1"' in str(e.value)


def test_broken_ui_element_raises(mock_mng):
    # noinspection PyMissingConstructor
    class BrokenUIElement(UIElement):
        def __init__(self):
            pass

    with pytest.raises(UIException) as e:
        mock_mng.add_ui_element(BrokenUIElement())

    assert 'super().__init__' in str(e.value)


def test_no_id_duplication_exception_after_purge(mock_mng):
    # GIVEN
    mock_mng.add_ui_element(MockButton(id='dream'))

    # WHEN
    mock_mng.purge_ui_elements()

    # THEN
    mock_mng.add_ui_element(MockButton(id='dream'))
