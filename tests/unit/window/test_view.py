from unittest.mock import Mock

from arcade import Window, View, color, get_image


def test_on_show_view_called(window):
    view = View(window)
    show_mock = Mock()
    view.on_show_view = show_mock

    window.show_view(view)

    show_mock.assert_called_once()


def test_on_hide_view_called(window):
    view1 = View(window)
    view2 = View(window)
    window.show_view(view1)

    hide_mock = Mock()
    view1.on_hide_view = hide_mock

    window.show_view(view2)

    hide_mock.assert_called_once()
    
def test_view_background_color(window):
    view = View(window, color.ARCADE_GREEN)
    assert view.background_color == color.ARCADE_GREEN
    window.clear()
    # assert get_image(0, 0, 1, 1).getpixel((0, 0)) == color.BLACK
    view.clear()
    # assert get_image(0, 0, 1, 1).getpixel((0, 0)) == color.ARCADE_GREEN
