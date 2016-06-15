"""

Various shapes for arcade games.

"""
# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods

from typing import Iterable

from arcade.color import GREEN
from arcade.draw_commands import draw_rectangle_filled
from arcade.draw_commands import draw_ellipse_filled
from arcade.draw_commands import draw_circle_filled
from arcade.draw_commands import draw_point, draw_text
from arcade.draw_commands import draw_triangle_filled
from arcade.draw_commands import draw_polygon_filled
from arcade.draw_commands import draw_line
from arcade.draw_commands import draw_arc_outline
from arcade.arcade_types import Color
from arcade.arcade_types import PointList


class Shape:

    def __init__(self, center_x: float, center_y: float,
                 color: Color = GREEN, tilt_angle: float = 0):
        self.color = color
        self.center_x = center_x
        self.center_y = center_y
        self.tilt_angle = tilt_angle

        self.change_x = 0
        self.change_y = 0
        self.change_tilt_angle = 0

    def draw(self):
        print("Cannot draw an object of type Shape. Use the subclasses of "
              "Shape: Rectangle, etc.")

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.tilt_angle += self.change_tilt_angle


class Rectangle(Shape):

    def __init__(self, center_x: float, center_y: float,
                 width: float, height: float,
                 color: Color = GREEN,
                 border_width: float = 0, tilt_angle: float = 0):

        """

        Args:
            center_x (float):
            center_y (float):
            width (float):
            height (float):
            border_width (float):
            tilt_angle (float):
        """
        super().__init__(center_x, center_y, color)

        self.width = width
        self.height = height
        self.border_width = border_width
        self.tilt_angle = tilt_angle

    def draw(self):
        draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height,
                              self.color, self.tilt_angle)


class Square(Rectangle):
    def __init__(self, center_x: float, center_y: float,
                 width_and_height: float,
                 color: Color = GREEN,
                 border_width: float = 0, tilt_angle: float = 0):

        super().__init__(center_x, center_y, width_and_height,
                         width_and_height, color, border_width, tilt_angle)

        self.width_and_height = width_and_height

    def draw(self):
        draw_rectangle_filled(self.center_x, self.center_y, self.width_and_height,
                              self.width_and_height, self.color, self.tilt_angle)


class Ellipse(Shape):
    """ Class that represents an Ellipse. """

    def __init__(self, center_x: float, center_y: float, width: float,
                 height: float, color: Color = GREEN,
                 tilt_angle: float = 0):

        super().__init__(center_x, center_y, color, tilt_angle)
        self.width = width
        self.height = height

    def draw(self):
        draw_ellipse_filled(self.center_x, self.center_y, self.width, self.height,
                            self.color, self.tilt_angle)


class Circle(Shape):
    """ Class that represents an Circle. """

    def __init__(self, center_x: float, center_y: float, radius: float,
                 color: Color = GREEN,
                 border_width: float = 0):

        super().__init__(center_x, center_y, color)

        self.radius = radius
        self.border_width = border_width

    def draw(self):
        draw_circle_filled(self.center_x, self.center_y, self.radius, self.color)


class Point(Shape):
    """ Class that represents an Point. """

    def __init__(self, center_x: float, center_y: float, size: float,
                 color: Color = GREEN):

        super().__init__(center_x, center_y, color)

        self.size = size

    def draw(self):
        draw_point(self.center_x, self.center_y, self.color, self.size)


class Text(Shape):
    """ Class that represents a text label. """

    def __init__(self, text: str, center_x: float, center_y: float,
                 size: float, color: Color = GREEN):

        super().__init__(center_x, center_y, color)

        self.size = size
        self.text = text

    def draw(self):
        draw_text(self.text, self.center_x, self.center_y, self.color,
                  self.size)


class Triangle(Shape):
    """ Class that represents a triangle. """

    def __init__(self, first_x: float, first_y: float, second_x: float,
                 second_y: float, third_x: float, third_y: float,
                 color: Color = GREEN,
                 border_width: float = 0):
        center_x = (first_x + second_x + third_x) / 3
        center_y = (first_y + second_y + third_y) / 3
        super().__init__(center_x, center_y, color)
        self.first_x = first_x
        self.first_y = first_y
        self.second_x = second_x
        self.second_y = second_y
        self.third_x = third_x
        self.third_y = third_y

        self.color = color
        self.border_width = border_width

    def draw(self):
        draw_triangle_filled(self.first_x, self.first_y,
                             self.second_x, self.second_y,
                             self.third_x, self.third_y,
                             self.color)


class Polygon(Shape):

    def __init__(self, point_list: PointList,
                 color: Color = GREEN,
                 border_width: float = 0):

        total_x = 0
        total_y = 0
        for point in point_list:
            total_x += point[0]
            total_y += point[1]
        super().__init__(total_x / len(point_list), total_y / len(point_list), color)

        self.point_list = point_list
        self.color = color
        self.border_width = border_width

        self.change_x = 0
        self.change_y = 0

    def draw(self):
        draw_polygon_filled(self.point_list, self.color)

    def update(self):
        for point in self.point_list:
            point[0] += self.change_x
            point[1] += self.change_y


class Parabola(Shape):

    def __init__(self, start_x: float, start_y: float, end_x: float,
                 height: float,
                 color: Color = GREEN,
                 border_width: float = 0, tilt_angle: float = 0):
        super().__init__((start_x + end_x) / 2, (start_y + height) / 2, color)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.height = height
        self.color = color
        self.border_width = border_width
        self.tilt_angle = tilt_angle

        self.change_x = 0
        self.change_y = 0
        self.change_tilt_angle = 0


class Line(Shape):

    def __init__(self, start_x: float, start_y: float, end_x: float,
                 end_y: float,
                 color: Color = GREEN,
                 width: float = 1):
        super().__init__((start_x + end_x) / 2, (start_y + end_y) / 2, color)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.color = color
        self.width = width

        self.change_x = 0
        self.change_y = 0

    def draw(self):
        draw_line(self.start_x, self.start_y, self.end_x, self.end_y,
                  self.color, self.width)

    def update(self):
        self.start_x += self.change_x
        self.start_y += self.change_y
        self.end_x += self.change_x
        self.end_y += self.change_y


class Arc(Shape):
    def __init__(self, center_x: float, center_y: float, width: float,
                 height: float, color: Color=GREEN,
                 start_angle: float=0, end_angle: float=180,
                 border_width: float=0, tilt_angle: float=0):

        super().__init__(center_x, center_y, color)
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.color = color
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.border_width = border_width
        self.tilt_angle = tilt_angle

        self.change_x = 0
        self.change_y = 0
        self.change_tilt_angle = 0
        self.change_start_angle = 0
        self.change_end_angle = 0

    def draw(self):
        draw_arc_outline(self.center_x, self.center_y, self.width, self.height,
                         self.color, self.start_angle, self.end_angle,
                         self.border_width, self.tilt_angle)

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.tilt_angle += self.change_tilt_angle
        self.start_angle += self.change_start_angle
        self.end_angle += self.change_end_angle


def master_draw(shape_object: Shape):
    shape_object.draw()


def draw_all(shape_list: Iterable[Shape]):
    for item in shape_list:
        item.draw()


def update_all(shape_list: Iterable[Shape]):
    for item in shape_list:
        item.update()
