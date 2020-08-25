from arcade.gui import UIClickable
from tests.test_gui import MockButton


def test_has_normal_state(mock_button):
    assert not mock_button.hovered
    assert not mock_button.pressed
    assert not mock_button.focused


def test_change_state_on_hover(mock_button):
    mock_button.on_hover()
    assert mock_button.hovered


def test_change_state_on_press(mock_button):
    mock_button.on_press()
    assert mock_button.pressed


def test_change_state_on_focus(mock_button):
    mock_button.on_focus()
    assert mock_button.focused


def test_uibutton_is_pressed(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.click_and_hold(50, 50)

    assert mock_button.on_press_called
    assert not mock_button.on_click_called


def test_uibutton_clicked(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.click(50, 50)

    assert mock_button.on_release
    assert mock_button.on_click_called


def test_uibutton_click_dispatch_event(mock_mng, mock_button):
    # GIVEN
    mock_mng.add_ui_element(mock_button)
    clicked = False

    @mock_button.event('on_click')
    def callback(*args):
        nonlocal clicked
        clicked = True

    # WHEN
    mock_mng.click(50, 50)

    # THEN
    assert clicked


def test_uibutton_has_on_click_event_type(mock_button):
    # THEN
    assert 'on_click' in mock_button.event_types


def test_uibutton_not_clicked_if_released_beside(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.click_and_hold(50, 50)
    mock_mng.release(100, 100)

    assert not mock_button.on_click_called


def test_uibutton_send_custom_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.click(50, 50)

    assert mock_mng.last_event.type == UIClickable.CLICKED
    assert mock_mng.last_event.get('ui_element') == mock_button


def test_hover_over_last_rendered_element(mock_mng):
    button1 = MockButton(center_x=50, center_y=50, width=400, height=400, id='button1')
    button2 = MockButton(center_x=50, center_y=50, width=40, height=40, id='button2')
    mock_mng.add_ui_element(button1)
    mock_mng.add_ui_element(button2)

    mock_mng.move_mouse(50, 50)

    assert mock_mng.hovered_element == button2


def test_focus_over_last_rendered_element(mock_mng):
    button1 = MockButton(center_x=50, center_y=50, width=400, height=400, id='button1')
    button2 = MockButton(center_x=50, center_y=50, width=40, height=40, id='button2')
    mock_mng.add_ui_element(button1)
    mock_mng.add_ui_element(button2)

    mock_mng.click_and_hold(50, 50)

    assert mock_mng.focused_element == button2


def test_click_hits_last_rendered_element(mock_mng):
    button1 = MockButton(center_x=50, center_y=50, width=400, height=400, id='button1')
    button2 = MockButton(center_x=50, center_y=50, width=40, height=40, id='button2')
    mock_mng.add_ui_element(button1)
    mock_mng.add_ui_element(button2)

    mock_mng.click(50, 50)

    # second button clicked
    assert button2.on_click_called

    # but first button NOT
    assert not button1.on_click_called

    # last event triggered from button2
    assert mock_mng.last_event.type == UIClickable.CLICKED
    assert mock_mng.last_event.get('ui_element') == button2
