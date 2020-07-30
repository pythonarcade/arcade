import pytest

from arcade.gui.elements.toggle import UIToggle


@pytest.fixture()
def toggle(mock_mng) -> UIToggle:
    b = UIToggle(
        center_x=30,
        center_y=40,
        height=30
    )
    mock_mng.add_ui_element(b)
    return b


def test_toggle_off_via_click(toggle, mock_mng):
    last_called_with = None

    @toggle.event('on_toggle')
    def on_toggle(value):
        nonlocal last_called_with
        last_called_with = value

    mock_mng.click(toggle.center_x, toggle.center_y)

    assert last_called_with is False


def test_toggle_off_via_toggle(toggle, mock_mng):
    last_called_with = None

    @toggle.event('on_toggle')
    def on_toggle(value):
        nonlocal last_called_with
        last_called_with = value

    toggle.toggle()

    assert last_called_with is False
