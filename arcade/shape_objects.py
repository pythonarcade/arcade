from .draw_commands import *

#### OBJECTS ####

import arcade.color

class Shape():
    
    def __init__(self, center_x, center_y, color = arcade.color.GREEN, tilt_angle = 0):
        self.color = color
        self.center_x = center_x
        self.center_y = center_y
        self.tilt_angle = tilt_angle

        self.change_x = 0
        self.change_y = 0
        self.change_angle = 0

    def draw(self):   
        print("Cannot draw an object of type Shape. Use the subclasses of Shape: Rectangle, etc.")

    def move(self):   
        print("Cannot move an object of type Shape. Use the subclasses of Shape: Rectangle, etc.")

    def update(self):        
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.tilt_angle += self.change_angle


class Rectangle(Shape):
    
    def __init__(self, center_x, center_y, width, height, color = arcade.color.GREEN, border_width = 0, tilt_angle = 0):
        
        super().__init__(center_x, center_y, color)
        
        self.width = width
        self.height = height
        self.border_width = border_width
        self.tilt_angle = tilt_angle

    def draw(self):
        draw_rectangle(self.center_x, self.center_y, self.width, self.height, self.color, self.border_width, self.tilt_angle)


class Square(Rectangle):
    def __init__(self, center_x, center_y, width_and_height, color = arcade.color.GREEN, border_width = 0, tilt_angle = 0):

        super().__init__(center_x, center_y, width_and_height, width_and_height, color, border_width, tilt_angle)

        self.width_and_height = width_and_height

    def draw(self):
        draw_rectangle(self.center_x, self.center_y, self.width_and_height, self.width_and_height, self.color, self.border_width, self.tilt_angle)

class Oval(Shape):
    def __init__(self, center_x, center_y, width, height, color = arcade.color.GREEN, border_width = 0, tilt_angle = 0):
        
        super().__init__(center_x, center_y, color)

        self.width = width
        self.height = height
        self.border_width = border_width
        self.tilt_angle = tilt_angle

    def draw(self):
        draw_oval(self.center_x, self.center_y, self.width, self.height, self.color, self.border_width, self.tilt_angle)

class Circle(Shape):
    def __init__(self, center_x, center_y, radius, color = arcade.color.GREEN, border_width = 0):
        
        super().__init__(center_x, center_y, color)

        self.radius = radius
        self.border_width = border_width

    def draw(self):
        draw_circle(self.center_x, self.center_y, self.radius, self.color, self.border_width)
        
class Point(Shape):
    def __init__(self, center_x, center_y, size, color = arcade.color.GREEN):
    
        super().__init__(center_x, center_y, color)

        self.size = size

    def draw(self):
        draw_point(self.center_x, self.center_y, self.color, self.size)

class Text(Shape):
    def __init__(self, text, center_x, center_y, size, color = arcade.color.GREEN):
        
        super().__init__(center_x, center_y, color)

        self.size = size
        self.text = text

    def draw(self):
        draw_text(self.text, self.center_x, self.center_y, self.color, self.size)

def master_draw(object):
    object.draw()

def draw_all(list):
    for item in list:
        item.draw()

def update_all(list):
    for item in list:
        item.update()


#### END OBJECTS ####


