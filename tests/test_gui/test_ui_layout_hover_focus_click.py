from arcade.gui.layouts.box import UIBoxLayout


def test_move_layout_hover(mock_layout_mng, mock_button):
    layout = UIBoxLayout(vertical=False, align='left')
    mock_layout_mng.root_layout = layout

    layout.pack(mock_button)

    mock_layout_mng.move_mouse(50, 50)

    assert mock_button.on_hover_called
    assert mock_button.hovered


def test_move_layout_focus(mock_layout_mng, mock_button):
    layout = UIBoxLayout(vertical=False, align='left')
    mock_layout_mng.root_layout = layout

    layout.pack(mock_button)

    mock_layout_mng.click_and_hold(50, 50)

    assert mock_button.on_focus_called
    assert mock_button.focused


def test_move_layout_click_and_hold(mock_layout_mng, mock_button):
    layout = UIBoxLayout(vertical=False, align='left')
    mock_layout_mng.root_layout = layout

    layout.pack(mock_button)

    mock_layout_mng.click_and_hold(50, 50)

    assert mock_button.on_press_called
    assert not mock_button.on_click_called


def test_move_layout_click(mock_layout_mng, mock_button):
    layout = UIBoxLayout(vertical=False, align='left')
    mock_layout_mng.root_layout = layout

    layout.pack(mock_button)

    mock_layout_mng.click(50, 50)

    assert mock_button.on_press_called
    assert mock_button.on_release_called
    assert mock_button.on_click_called


def test_move_layout_hover_move_release(mock_layout_mng, mock_button):
    layout = UIBoxLayout(vertical=False, align='left')
    mock_layout_mng.root_layout = layout

    layout.pack(mock_button)

    mock_layout_mng.click_and_hold(50, 50)
    mock_layout_mng.move_mouse(250, 50)
    mock_layout_mng.release(250, 50)

    assert not mock_button.hovered
    assert mock_button.focused
    assert not mock_button.on_click_called
