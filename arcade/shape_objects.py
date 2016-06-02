from .draw_commands import *

import arcade.color


class Shape:

    def __init__(self, center_x, center_y, color=arcade.color.GREEN,
                 tilt_angle=0):
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

    def __init__(self, center_x, center_y, width, height,
                 color=arcade.color.GREEN, border_width=0, tilt_angle=0):

        super().__init__(center_x, center_y, color)

        self.width = width
        self.height = height
        self.border_width = border_width
        self.tilt_angle = tilt_angle

    def draw(self):
        draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height,
                              self.color, self.tilt_angle)


class Square(Rectangle):
    def __init__(self, center_x, center_y, width_and_height,
                 color=arcade.color.GREEN, border_width=0, tilt_angle=0):

        super().__init__(center_x, center_y, width_and_height,
                         width_and_height, color, border_width, tilt_angle)

        self.width_and_height = width_and_height

    def draw(self):
        draw_rectangle_filled(self.center_x, self.center_y, self.width_and_height,
                              self.width_and_height, self.color, self.tilt_angle)


class Ellipse(Shape):
    """ Class that represents an Ellipse. """

    def __init__(self, center_x, center_y, width, height,
                 color=arcade.color.GREEN, tilt_angle=0):

        super().__init__(center_x, center_y, color, tilt_angle)
        self.width = width
        self.height = height

    def draw(self):
        draw_ellipse_filled(self.center_x, self.center_y, self.width, self.height,
                            self.color, self.tilt_angle)


class Circle(Shape):
    """ Class that represents an Circle. """

    def __init__(self, center_x, center_y, radius,
                 color=arcade.color.GREEN, border_width=0):

        super().__init__(center_x, center_y, color)

        self.radius = radius
        self.border_width = border_width

    def draw(self):
        draw_circle_filled(self.center_x, self.center_y, self.radius, self.color)


class Point(Shape):
    """ Class that represents an Point. """

    def __init__(self, center_x, center_y, size, color=arcade.color.GREEN):

        super().__init__(center_x, center_y, color)

        self.size = size

    def draw(self):
        draw_point(self.center_x, self.center_y, self.color, self.size)


class Text(Shape):
    """ Class that represents a text label. """

    def __init__(self, text, center_x, center_y, size,
                 color=arcade.color.GREEN):

        super().__init__(center_x, center_y, color)

        self.size = size
        self.text = text

    def draw(self):
        draw_text(self.text, self.center_x, self.center_y, self.color,
                  self.size)


class Triangle:
    """ Class that represents a triangle. """

    def __init__(self, first_x, first_y, second_x, second_y, third_x, third_y,
                 color=arcade.color.GREEN, border_width=0):
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


class Polygon():

    def __init__(self, point_list, color=arcade.color.GREEN, border_width=0):
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


class Parabola():

    def __init__(self, start_x, start_y, end_x, height,
                 color=arcade.color.GREEN, border_width=0, tilt_angle=0):
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


class Line():

    def __init__(self, start_x, start_y, end_x, end_y,
                 color=arcade.color.GREEN, width=1):
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


class Arc():
    def __init__(self, center_x, center_y, width, height,
                 color=arcade.color.GREEN, start_angle=0, end_angle=180,
                 border_width=0, tilt_angle=0):
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


def master_draw(shape_object):
    shape_object.draw()


def draw_all(shape_list):
    for item in shape_list:
        item.draw()


def update_all(shape_list):
    for item in shape_list:
        item.update()
