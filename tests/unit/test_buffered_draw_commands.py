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
        [(10, 20), (30, 40), (50, 60)],
        [(100, 110, 120, 255), (100, 110, 120, 255), (100, 110, 120, 255)],
        gl.GL_LINE_LOOP,
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
        point_list=[(10, 20), (30, 40), (50, 60), (70, 80)],
        color=(100, 110, 120),
        border_width=2
    )
    mock.assert_called_with(
        [(10, 20), (30, 40), (50, 60), (70, 80)],
        [(100, 110, 120, 255), (100, 110, 120, 255),
         (100, 110, 120, 255), (100, 110, 120, 255)],
        gl.GL_POLYGON,
        2
    )
