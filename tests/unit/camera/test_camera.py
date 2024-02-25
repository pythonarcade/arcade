import arcade


def test_camera(window):
    c1 = arcade.SimpleCamera()
    assert c1.viewport == (0, 0, *window.size)
    assert c1.projection == (0, window.width, 0, window.height)

    c2 = arcade.Camera()
    assert c2.viewport == (0, 0, *window.size)
    assert c2.projection == (0, window.width, 0, window.height)
