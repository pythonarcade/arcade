import pytest
from pyglet import gl
from arcade import window_commands
import numpy as np
from ctypes import POINTER
from arcade.buffered_draw_commands import (
    create_line,
    create_line_generic_with_colors,
    create_line_generic,
    create_line_strip,
    create_line_loop,
    create_lines,
    create_polygon,
    create_rectangle,
    create_rectangle_outline,
    create_rectangle_filled,
    get_rectangle_points,
    create_rectangle_filled_with_colors,
    create_triangles_filled_with_colors,
    create_ellipse,
    create_ellipse_filled,
    create_ellipse_outline,
    create_ellipse_filled_with_colors,
)


@pytest.fixture(autouse=True)
def set_projection():
    window_commands._projection = window_commands.create_orthogonal_projection(
        left=0, right=800, bottom=0, top=600, near=-0, far=100
    )


buffer_type = np.dtype([("vertex", "2f4"), ("color", "4B")])


def get_data_from_vbo(vbo, count, stride):
    data = np.zeros(count, dtype=buffer_type)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo.buffer_id)
    gl.glGetBufferSubData(gl.GL_ARRAY_BUFFER, 0, count * stride,
                          data.ctypes.data_as(POINTER(gl.GLvoid)))
    return data


def test_create_line():
    line = create_line(
        start_x=10, start_y=20, end_x=30, end_y=40,
        color=(100, 110, 120), line_width=5
    )
    assert line.mode == gl.GL_LINE_STRIP
    assert line.line_width == 5

    data = get_data_from_vbo(line.vbo, 2, 12)
    expected = np.zeros(2, dtype=buffer_type)
    expected["vertex"] = [10, 20], [30, 40]
    expected["color"] = [100, 110, 120, 255], [100, 110, 120, 255]
    np.testing.assert_array_equal(data, expected)


def test_create_line_generic_with_colors():
    line = create_line_generic_with_colors(
        point_list=[(10, 20), (30, 40), (50, 60)],
        color_list=[(100, 110, 120), (130, 140, 150), (160, 170, 180)],
        shape_mode=gl.GL_LINE_STRIP,
        line_width=2
    )
    assert line.mode == gl.GL_LINE_STRIP
    assert line.line_width == 2

    data = get_data_from_vbo(line.vbo, 3, 12)
    expected = np.zeros(3, dtype=buffer_type)
    expected["vertex"] = [(10, 20), (30, 40), (50, 60)]
    expected["color"] = [(100, 110, 120, 255),
                         (130, 140, 150, 255),
                         (160, 170, 180, 255)]
    np.testing.assert_array_equal(data, expected)


def test_create_line_generic(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    create_line_generic(
        point_list=[(10, 20), (30, 40), (50, 60)],
        color=(100, 110, 120),
        shape_mode=gl.GL_LINE_STRIP,
        line_width=2
    )
    mock.assert_called_with(
        [(10, 20), (30, 40), (50, 60)],
        [(100, 110, 120, 255), (100, 110, 120, 255), (100, 110, 120, 255)],
        gl.GL_LINE_STRIP,
        2
    )


def test_create_line_strip(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    create_line_strip(
        point_list=[(10, 20), (30, 40), (50, 60)],
        color=(100, 110, 120),
        line_width=2
    )
    mock.assert_called_with(
        [(10, 20), (30, 40), (50, 60)],
        [(100, 110, 120, 255), (100, 110, 120, 255), (100, 110, 120, 255)],
        gl.GL_LINE_STRIP,
        2
    )


def test_create_line_loop(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    create_line_loop(
        point_list=[(10, 20), (30, 40), (50, 60)],
        color=(100, 110, 120),
        line_width=2
    )
    mock.assert_called_with(
        [(10, 20), (30, 40), (50, 60), (10, 20)],
        [(100, 110, 120, 255), (100, 110, 120, 255),
         (100, 110, 120, 255), (100, 110, 120, 255)],
        gl.GL_LINE_STRIP,
        2
    )


def test_create_lines(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    create_lines(
        point_list=[(10, 20), (30, 40), (50, 60), (70, 80)],
        color=(100, 110, 120),
        line_width=2
    )
    mock.assert_called_with(
        [(10, 20), (30, 40), (50, 60), (70, 80)],
        [(100, 110, 120, 255), (100, 110, 120, 255),
         (100, 110, 120, 255), (100, 110, 120, 255)],
        gl.GL_LINES,
        2
    )


def test_create_polygon(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    create_polygon(
        point_list=[(30, 20), (10, 40), (50, 80), (90, 40), (50, 20)],
        color=(100, 110, 120),
        border_width=2
    )
    mock.assert_called_with(
        [(30, 20), (50, 20), (10, 40), (90, 40), (50, 80)],
        [(100, 110, 120, 255), (100, 110, 120, 255), (100, 110, 120, 255),
         (100, 110, 120, 255), (100, 110, 120, 255)],
        gl.GL_TRIANGLE_STRIP,
        2
    )


def test_create_rectangle(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    create_rectangle(
        center_x=200, center_y=200, width=50, height=50,
        color=(0, 255, 0), border_width=3, tilt_angle=0
    )
    mock.assert_called_with(
        [(175, 175), (175, 225), (225, 175), (225, 225)],
        [(0, 255, 0, 255), (0, 255, 0, 255), (0, 255, 0, 255), (0, 255, 0, 255)],
        gl.GL_TRIANGLE_STRIP,
        3
    )


def test_create_rectangle_outline(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    create_rectangle_outline(
        center_x=200, center_y=200, width=50, height=50,
        color=(0, 255, 0), border_width=3, tilt_angle=0
    )
    mock.assert_called_with(
        [(175, 175), (175, 225), (225, 225), (225, 175), (175, 175)],
        [(0, 255, 0, 255), (0, 255, 0, 255), (0, 255, 0, 255),
         (0, 255, 0, 255), (0, 255, 0, 255)],
        gl.GL_LINE_STRIP,
        3
    )


def test_create_rectangle_filled(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_rectangle")
    create_rectangle_filled(
        center_x=200, center_y=200, width=50, height=50,
        color=(0, 255, 0), tilt_angle=0
    )
    mock.assert_called_with(
        200, 200, 50, 50, (0, 255, 0), tilt_angle=0
    )


def test_get_rectangle_points():
    side = 2 * 10 / (2 ** 0.5)  # diagonal length will be 2 * 10
    points = get_rectangle_points(
        center_x=0, center_y=0, width=side, height=side, tilt_angle=45
    )
    assert points == [(0, -10), (-10, 0), (0, 10), (10, 0)]


def test_create_rectangle_filled_with_colors(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    create_rectangle_filled_with_colors(
        point_list=[(0, 0), (100, 0), (100, 100), (0, 100)],
        color_list=[(100, 110, 120), (130, 140, 150),
                    (160, 170, 180), (190, 200, 210)]
    )
    mock.assert_called_with(
        [(0, 0), (100, 0), (0, 100), (100, 100)],
        [(100, 110, 120), (130, 140, 150),
         (190, 200, 210), (160, 170, 180)],
        gl.GL_TRIANGLE_STRIP
    )


def test_create_triangles_filled_with_colors(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    create_triangles_filled_with_colors(
        point_list=[(0, 0), (100, 0), (0, 100)],
        color_list=[(100, 110, 120), (130, 140, 150), (190, 200, 210)]
    )
    mock.assert_called_with(
        [(0, 0), (100, 0), (0, 100)],
        [(100, 110, 120), (130, 140, 150), (190, 200, 210)],
        gl.GL_TRIANGLE_STRIP
    )


def test_create_ellipse(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic")
    create_ellipse(
        center_x=100, center_y=100, width=50, height=80,
        color=(200, 150, 100), num_segments=10
    )
    mock.assert_called_with(
        [(150.0, 100.0),
         (140.45084688381107, 52.977173573474644),
         (140.45085003374027, 147.022819489717),
         (115.45084564139354, 23.915476576687922),
         (115.4508507380858, 176.08452077368725),
         (84.54914671356813, 23.915480551125484),
         (84.54915181026028, 176.08452209849975),
         (59.54914839129532, 52.97718397868734),
         (59.54915154122427, 147.02282295812122),
         (50.00000000000007, 100.00000428718346)],
        (200, 150, 100),
        gl.GL_TRIANGLE_STRIP,
        1
    )


def test_create_ellipse_outline(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic")
    create_ellipse_outline(
        center_x=100, center_y=100, width=50, height=80,
        color=(200, 150, 100), num_segments=10
    )
    mock.assert_called_with(
        [(150.0, 100.0),
         (140.45085003374027, 147.022819489717),
         (115.4508507380858, 176.08452077368725),
         (84.54915181026028, 176.08452209849975),
         (59.54915154122427, 147.02282295812122),
         (50.00000000000007, 100.00000428718346),
         (59.54914839129532, 52.97718397868734),
         (84.54914671356813, 23.915480551125484),
         (115.45084564139354, 23.915476576687922),
         (140.45084688381107, 52.977173573474644),
         (150.0, 100.0)],
        (200, 150, 100),
        gl.GL_LINE_STRIP,
        1
    )


def test_create_ellipse_filled(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_ellipse")
    create_ellipse_filled(center_x=100, center_y=100, width=50, height=80,
                          color=(200, 150, 100))
    border_width = 1
    tilt_angle = 0
    num_segments = 128
    mock.assert_called_with(
        100, 100, 50, 80, (200, 150, 100),
        border_width, tilt_angle, num_segments, filled=True
    )


def test_create_ellipse_filled_with_colors(mocker):
    mock = mocker.patch("arcade.buffered_draw_commands.create_line_generic_with_colors")
    num_segments = 10
    create_ellipse_filled_with_colors(
        center_x=100, center_y=100, width=50, height=80,
        outside_color=(200, 150, 100), inside_color=(0, 50, 100),
        num_segments=num_segments
    )
    mock.assert_called_with(
        [(100, 100),
         (150.0, 100.0),
         (140.45085003374027, 147.022819489717),
         (115.4508507380858, 176.08452077368725),
         (84.54915181026028, 176.08452209849975),
         (59.54915154122427, 147.02282295812122),
         (50.00000000000007, 100.00000428718346),
         (59.54914839129532, 52.97718397868734),
         (84.54914671356813, 23.915480551125484),
         (115.45084564139354, 23.915476576687922),
         (140.45084688381107, 52.977173573474644),
         (150.0, 100.0)],
        [(0, 50, 100)] + [(200, 150, 100)] * (num_segments + 1),
        gl.GL_TRIANGLE_FAN
    )
