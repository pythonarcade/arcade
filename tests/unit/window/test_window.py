import pytest
import time

import arcade


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

    def f():
        pass

    arcade.schedule(f, 1/60)
    time.sleep(0.01)
    arcade.unschedule(f)
    window.test()

def test_window_with_view_arg(window: arcade.Window):
    class TestView(arcade.View):
        def __init__(self):
            super().__init__()
            self.on_show_called = False

        def on_show_view(self):
            self.on_show_called = True
    v = TestView()
    window.run(view=v)

    assert v.on_show_called
    assert window.current_view is v

def test_start_finish_render(window):
    """Test start and finish render"""
    # start_render must be called first
    with pytest.raises(RuntimeError):
        arcade.finish_render()

    arcade.start_render()
    assert window._start_finish_render_data is not None

    # Draw something into the buffer
    arcade.draw_lbwh_rectangle_filled(0, 0, 100, 100, arcade.color.RED)

    # Only allowed to call start_render once
    with pytest.raises(RuntimeError):
        arcade.start_render()

    arcade.finish_render()

    # Make sure we rendered something to the screen
    window._start_finish_render_data.draw()
    assert arcade.get_pixel(50, 50) == arcade.color.RED.rgb

    # Only allowed to call finish_render once
    with pytest.raises(RuntimeError):
        arcade.finish_render()
