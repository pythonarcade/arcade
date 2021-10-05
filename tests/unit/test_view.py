from unittest.mock import Mock

from arcade import Window, View


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
