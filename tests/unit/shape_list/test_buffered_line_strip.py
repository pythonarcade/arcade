import arcade
from arcade import shape_list


def test_buffered_lines(window):
    window.background_color = arcade.color.WHITE
    window.clear()

    point_list = ([0, 100],
                    [100, 100],
                    [100, 300],
                    [300, 300])
    line_strip = shape_list.create_line_strip(point_list, arcade.csscolor.BLACK, 10)

    line_strip.draw()
    p = arcade.get_pixel(0, 100)
    assert p == (0, 0, 0)
    p = arcade.get_pixel(0, 96)
    assert p == (0, 0, 0)
    p = arcade.get_pixel(0, 94)
    assert p == (255, 255, 255)
    p = arcade.get_pixel(50, 100)
    assert p == (0, 0, 0)
    p = arcade.get_pixel(100, 200)
    assert p == (0, 0, 0)
    p = arcade.get_pixel(150, 300)
    assert p == (0, 0, 0)
    p = arcade.get_pixel(301, 300)
    assert p == (255, 255, 255)
