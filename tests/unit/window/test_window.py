import pytest

import arcade
import pyglet

from pyglet.math import Mat4


def test_window(window: arcade.Window):
    width = window.width
    height = window.height
    title = "Window Test"
    window.set_caption(title)

    arcade.set_background_color(arcade.color.AMAZON)
    w = arcade.get_window()
    assert w is not None

    for not_a_view in ("string", 1, ("not", "a", "view")):
        with pytest.raises(TypeError):
            w.show_view(not_a_view)

    # NOTE: Window managers can enforce difference sizes
    # Make sure the arguments get passed to the window
    # assert w.width == width
    # assert w.height == height

    assert w.caption == title
    assert w.resizeable is False
    assert w.current_view is None

    arcade.set_window(w)

    w.background_color = 255, 255, 255, 255
    assert w.background_color == (255, 255, 255, 255)
    w.set_mouse_visible(True)
    w.set_size(width, height)

    v = window.ctx.viewport
    assert v[0] == 0
    assert v[1] == 0
    assert v[2] == width
    assert v[3] == height

    factor = window.get_pixel_ratio()
    assert isinstance(factor, float) 
    assert factor > 0

    arcade.start_render()
    arcade.finish_render()

    def f():
        pass

    arcade.schedule(f, 1/60)
    arcade.pause(0.01)
    arcade.unschedule(f)
    window.test()
