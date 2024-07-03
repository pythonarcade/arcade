import arcade


def test_read_pixel(window):
    """Read zero pixel from active framebuffer."""
    window.clear(color=arcade.color.WHITE)
    px = arcade.get_pixel(0, 0)
    assert px == arcade.color.WHITE.rgb
    px = arcade.get_pixel(0, 0, components=4)
    assert px == arcade.color.WHITE


def test_get_image(window):
    """Get image from active framebuffer."""
    window.clear(color=arcade.color.WHITE)
    image = arcade.get_image()
    assert image.tobytes()[0:16] == b'\xff' * 16

    image = arcade.get_image(components=3)
    assert image.tobytes()[0:16] == b'\xff' * 16
