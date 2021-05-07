import pyglet


def test_window(twm):
    import arcade
    width = 800
    height = 600
    title = "My Title"
    resizable = True
    arcade.open_window(width, height, title, resizable)

    arcade.set_background_color(arcade.color.AMAZON)
    w = arcade.get_window()
    assert w is not None

    # Make sure the arguments get passed to the window
    if not twm:
        assert w.width == width
        assert w.height == height
    assert w.caption == title
    assert w.resizeable is resizable
    assert w.current_view is None

    arcade.set_window(w)

    w.background_color = 255, 255, 255, 255
    assert w.background_color == (255, 255, 255, 255)
    w.set_mouse_visible(True)
    w.set_size(width, height)

    p = arcade.get_projection()
    assert isinstance(p, pyglet.math.Mat4)

    v = arcade.get_viewport()
    if not twm:
        assert v[0] == 0
        assert v[1] == width
        assert v[2] == 0
        assert v[3] == height

    factor = arcade.get_scaling_factor()
    assert factor > 0
    factor = arcade.get_scaling_factor(w)
    assert factor > 0

    arcade.start_render()
    arcade.finish_render()

    def f():
        pass

    arcade.schedule(f, 1/60)

    arcade.pause(0.01)

    arcade.close_window()

    arcade.open_window(width, height, title, resizable)
    arcade.quick_run(0.01)
