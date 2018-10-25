def test_window():
    import arcade
    width = 800
    height = 600
    title = "My Title"
    resizable = True
    arcade.open_window(width, height, title, resizable)

    arcade.set_background_color(arcade.color.AMAZON)
    w = arcade.get_window()
    assert w is not None
    arcade.set_window(w)

    p = arcade.get_projection()
    assert p is not None

    v = arcade.get_viewport()
    assert v[0] == 0
    assert v[1] == width - 1
    assert v[2] == 0
    assert v[3] == height - 1

    arcade.start_render()
    arcade.finish_render()

    def f():
        pass

    arcade.schedule(f, 1/60)

    arcade.pause(0.01)

    arcade.close_window()

    arcade.open_window(width, height, title, resizable)
    arcade.quick_run(0.01)

