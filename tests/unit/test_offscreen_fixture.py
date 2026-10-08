"""The offscreen fixture's pixel readers return one value per channel."""

from arcade import LBWH


def test_read_pixel(offscreen):
    offscreen.fbo.clear(color=(10, 20, 30, 40))
    assert offscreen.read_pixel(5, 6) == (10, 20, 30)
    assert offscreen.read_pixel(5, 6, components=4) == (10, 20, 30, 40)


def test_read_region(offscreen):
    offscreen.fbo.clear(color=(10, 20, 30, 40))
    offscreen.fbo.clear(color=(200, 100, 50, 255), viewport=(1, 0, 1, 1))
    # Bottom row first, left to right
    assert offscreen.read_region(LBWH(0, 0, 2, 2)) == [
        (10, 20, 30, 40),
        (200, 100, 50, 255),
        (10, 20, 30, 40),
        (10, 20, 30, 40),
    ]
