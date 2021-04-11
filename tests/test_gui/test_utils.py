from arcade import set_viewport
from arcade.gui.utils import center_on_viewport


def test_center_on_viewport(window, mock_button):
    # GIVEN
    set_viewport(100, 400, 300, 600)
    # WHEN
    center_on_viewport(mock_button)

    # THEN
    assert mock_button.center_x == 250
    assert mock_button.center_y == 450
