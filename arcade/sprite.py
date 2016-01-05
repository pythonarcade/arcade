from .draw_commands import *
from .geometry import *


class SpriteList():
    """
    List of sprites.

    :Example:

    >>> import arcade
    >>> import random
    >>> arcade.open_window("Sprite Example", 600, 600)
    >>> scale = 0.002
    >>> meteor_list = arcade.SpriteList()
    >>> for i in range(100):
    ...     meteor = arcade.Sprite("examples/images/meteorGrey_big1.png", \
scale)
    ...     meteor.center_x = random.random() * 2 - 1
    ...     meteor.center_y = random.random() * 2 - 1
    ...     meteor_list.append(meteor)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> meteor_list.draw()
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
    """
    def __init__(self):
        self.sprite_list = []

    def append(self, item):
        """
        Add a new sprite to the list.
        """
        self.sprite_list.append(item)
        item._register_sprite_list(self)

    def remove(self, item):
        """
        Remove a specific sprite from the list.
        """
        self.sprite_list.remove(item)

    def update(self):
        """
        Call the update() method on each sprite in the list.
        """
        for sprite in self.sprite_list:
            sprite.update()

    def draw(self):
        """
        Call the draw() method on each sprite in the list.
        """
        for sprite in self.sprite_list:
            sprite.draw()

    def __len__(self):
        return len(self.sprite_list)

    def __iter__(self):
        return iter(self.sprite_list)

    def pop(self):
        """
        Pop off the last sprite in the list.
        """
        return self.sprite_list.pop()


class Sprite():
    """
    Class that represents a 'sprite' on-screen.

    :Example:

    >>> import arcade
    >>> arcade.open_window("Sprite Example", 800, 600)
    >>> scale = 0.002
    >>> ship_sprite = arcade.Sprite("examples/images/playerShip1_orange.png", \
scale)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> ship_sprite.draw()
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
    """
    def __init__(self, filename=None, scale=0):
        if filename != None:
            self.texture, width, height = load_texture(filename)
            self.textures = [self.texture]
            self.width = width * scale
            self.height = height * scale
        else:
            self.textures = []
            self.width = 0
            self.height = 0

        self.cur_texture_index = 0

        self.center_x = 0
        self.center_y = 0
        self.angle = 0.0

        self.change_x = 0
        self.change_y = 0
        self.change_angle = 0

        self.alpha = 1.0
        self.sprite_lists = []


    def append_texture(self, texture):
        self.textures.append(texture)

    def set_texture(self, texture_no):
        self.texture = self.textures[texture_no]

    def get_points(self):
        """
        Get the corner points for the rect that makes up the sprite.
        """
        x1, y1 = rotate(self.center_x - self.width / 2,
                        self.center_y - self.height / 2,
                        self.center_x,
                        self.center_y,
                        self.angle)
        x2, y2 = rotate(self.center_x + self.width / 2,
                        self.center_y - self.height / 2,
                        self.center_x,
                        self.center_y,
                        self.angle)
        x3, y3 = rotate(self.center_x + self.width / 2,
                        self.center_y + self.height / 2,
                        self.center_x,
                        self.center_y,
                        self.angle)
        x4, y4 = rotate(self.center_x - self.width / 2,
                        self.center_y + self.height / 2,
                        self.center_x,
                        self.center_y,
                        self.angle)

        return ((x1, y1), (x2, y2), (x3, y3), (x4, y4))

    points = property(get_points)

    def _get_bottom(self):
        """ The lowest y coordinate. """
        points = self.get_points()
        return min(points[0][1], points[1][1], points[2][1], points[3][1])

    bottom = property(_get_bottom)

    def _get_top(self):
        """ The highest y coordinate. """
        points = self.get_points()
        return max(points[0][1], points[1][1], points[2][1], points[3][1])

    top = property(_get_top)

    def _get_left(self):
        """ Left-most coordinate. """
        points = self.get_points()
        return min(points[0][0], points[1][0], points[2][0], points[3][0])

    left = property(_get_left)

    def _get_right(self):
        """ Right-most coordinate """
        points = self.get_points()
        return max(points[0][0], points[1][0], points[2][0], points[3][0])

    right = property(_get_right)

    def _register_sprite_list(self, new_list):
        self.sprite_lists.append(new_list)

    def draw(self):
        """ Draw the sprite. """
        draw_texture_rect(self.center_x, self.center_y,
                          self.width, self.height,
                          self.texture, self.angle, self.alpha)

    def update(self):
        """ Update the sprite. """
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.angle += self.change_angle

    def kill(self):
        """ Remove the sprite from all sprite lists. """
        for sprite_list in self.sprite_lists:
            if self in sprite_list:
                sprite_list.remove(self)


class TurningSprite(Sprite):
    """ Sprite that sets its angle to the direction it is traveling in. """
    def update(self):
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x)) \
            - 90
