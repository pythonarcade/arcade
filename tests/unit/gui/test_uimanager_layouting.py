from contextlib import contextmanager

from pyglet.math import Vec2

from arcade.gui import UIManager, UIDummy


@contextmanager
def sized(window, width, height):
    old_size = window.get_size()
    window.set_size(width=width, height=height)
    yield window
    window.set_size(*old_size)


def test_supports_size_hint(window):
    manager = UIManager()

    widget1 = UIDummy()
    widget1.size_hint = (1, 1)

    widget2 = UIDummy()
    widget2.size_hint = (0.5, 0.25)

    widget3 = UIDummy()
    widget3.size_hint = (1, None)

    manager.add(widget1)
    manager.add(widget2)
    manager.add(widget3)

    with sized(window, 200, 300):
        manager.draw()

    assert widget1.size == Vec2(200, 300)
    assert widget2.size == Vec2(100, 75)
    assert widget3.size == Vec2(200, 100)


def test_supports_size_hint_min(window):
    manager = UIManager()

    widget1 = UIDummy()
    widget1.size_hint_min = (120, 200)

    manager.add(widget1)

    manager.draw()

    assert widget1.size == Vec2(120, 200)


def test_supports_size_hint_max(window):
    manager = UIManager()

    widget1 = UIDummy()
    widget1.size_hint_max = (50, 60)

    manager.add(widget1)

    manager.draw()

    assert widget1.size == Vec2(50, 60)
