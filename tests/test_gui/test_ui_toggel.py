import pytest

from arcade.gui.elements.toggel import UIToggel


@pytest.fixture()
def toggel(mock_mng) -> UIToggel:
    b = UIToggel(
        center_x=30,
        center_y=40,
        height=30
    )
    mock_mng.add_ui_element(b)
    return b


def test_toggel_off_via_click(toggel, mock_mng):
    last_called_with = None

    @toggel.event('on_toggel')
    def on_toggel(value):
        nonlocal last_called_with
        last_called_with = value

    mock_mng.click(toggel.center_x, toggel.center_y)

    assert last_called_with is False


def test_toggel_off_via_toggel(toggel, mock_mng):
    last_called_with = None

    @toggel.event('on_toggel')
    def on_toggel(value):
        nonlocal last_called_with
        last_called_with = value

    toggel.toggel()

    assert last_called_with is False
