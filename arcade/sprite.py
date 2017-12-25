"""
This module manages all of the code around Sprites.
"""
# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods

import ctypes
import math
import pyglet.gl as gl

from arcade.draw_commands import load_texture
from arcade.draw_commands import draw_texture_rectangle
from arcade.draw_commands import Texture
from arcade.draw_commands import rotate_point

from typing import Iterable
from typing import TypeVar
from typing import Generic

from typing import List
from typing import Sequence
from typing import Tuple

FACE_RIGHT = 1
FACE_LEFT = 2
FACE_UP = 3
FACE_DOWN = 4


class Sprite:
    """
    Class that represents a 'sprite' on-screen.

    Attributes:
        :scale: Scale the sprite. Default is 1. Setting to 0.5 would halve \
the width and height.
        :center_x: x coordinate of the sprite's center.
        :center_y: y coordinate of the sprite's center.
        :angle: Angle at which the sprite is drawn. 0 is default, 180 is \
upside-down.
        :change_x: Movement vector, in the x direction.
        :change_y: Movement vector, in the y direction.
        :change_angle: Change in rotation.
        :alpha: Transparency. 1 is solid, 0 is fully transparent \
    (invisible).
        :transparent: Set to True if this sprite can be transparent.
        :sprite_lists: List of all the sprite lists this sprite is part of.
        :textures: List of textures associated with this sprite.
        :cur_texture_index: Index of current texture being used.

    :Example:

    >>> import arcade
    >>> arcade.open_window(800,600,"Sprite Example")
    >>> SCALE = 1
    >>> # Test creating an empty sprite
    >>> empty_sprite = arcade.Sprite()
    >>> # Create a sprite with an image
    >>> filename = "arcade/examples/images/playerShip1_orange.png"
    >>> ship_sprite = arcade.Sprite(filename, SCALE)
    >>> # Draw the sprite
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> ship_sprite.draw()
    >>> arcade.finish_render()
    >>> # Move the sprite
    >>> ship_sprite.change_x = 1
    >>> ship_sprite.change_y = 1
    >>> ship_sprite.angle = 45
    >>> ship_sprite.update() # Move/update the ship
    >>> # Remove the sprite
    >>> ship_sprite.kill()
    >>> ship_sprite = arcade.Sprite(filename, SCALE, image_height=-1)
    Traceback (most recent call last):
    ...
    ValueError: Height entered is less than zero. Height must be a positive float.

    >>> ship_sprite = arcade.Sprite(filename, SCALE, image_width=-1)
    Traceback (most recent call last):
    ...
    ValueError: Width of image can't be less than zero.

    >>> ship_sprite = arcade.Sprite(filename, SCALE, image_width=0, image_height=1)
    Traceback (most recent call last):
    ...
    ValueError: Width can't be zero.

    >>> ship_sprite = arcade.Sprite(filename, SCALE, image_height=0, image_width=1)
    Traceback (most recent call last):
    ...
    ValueError: Height can't be zero.

    >>> arcade.quick_run(0.25)
    """

    def __init__(self,
                 filename: str=None,
                 scale: float=1,
                 image_x: float=0, image_y: float=0,
                 image_width: float=0, image_height: float=0,
                 center_x: float=0, center_y: float=0):
        """
        Create a new sprite.

        Args:
            filename (str): Filename of an image that represents the sprite.
            scale (float): Scale the image up or down. Scale of 1.0 is none.
            image_x (float): Scale the image up or down. Scale of 1.0 is none.
            image_y (float): Scale the image up or down. Scale of 1.0 is none.
            image_width (float): Width of the sprite
            image_height (float): Height of the sprite
            center_x (float): Location of the sprite
            center_y (float): Location of the sprite

        """

        if image_width < 0:
            raise ValueError("Width of image can't be less than zero.")

        if image_height < 0:
            raise ValueError("Height entered is less than zero. Height must be a positive float.")

        if image_width == 0 and image_height != 0:
            raise ValueError("Width can't be zero.")

        if image_height == 0 and image_width != 0:
            raise ValueError("Height can't be zero.")

        if filename is not None:
            self.texture = load_texture(filename, image_x, image_y,
                                        image_width, image_height)

            self.textures = [self.texture]
            self.width = self.texture.width * scale
            self.height = self.texture.height * scale
        else:
            self.textures = []
            self._texture = None
            self.width = 0
            self.height = 0

        self.cur_texture_index = 0
        self.scale = scale
        self.position = [center_x, center_y]
        self._angle = 0.0

        self.velocity = [0, 0]
        self.change_angle = 0

        self.boundary_left = None
        self.boundary_right = None
        self.boundary_top = None
        self.boundary_bottom = None

        self.alpha = 1.0
        self.sprite_lists = []
        self.transparent = True
        self._collision_radius = None

        self.can_cache = True
        self._points = None
        self._point_list_cache = None

        self.last_center_x = self.center_x
        self.last_center_y = self.center_y
        self.last_angle = 0

        self.force = [0, 0]

    def append_texture(self, texture: Texture):
        """
        Appends a new texture to the list of textures that can be
        applied to this sprite.

        >>> import arcade
        >>> empty_sprite = arcade.Sprite()
        >>> my_texture = Texture(1, 10, 10)
        >>> empty_sprite.append_texture(my_texture)
        """
        self.textures.append(texture)

    def set_texture(self, texture_no: int):
        """
        Assuming 'texture' is a list of textures, this sets
        which texture index should be displayed. It also resets
        the width and height based on the scale of the texture.

        >>> import arcade
        >>> empty_sprite = arcade.Sprite()
        >>> my_texture = Texture(1, 10, 10)
        >>> empty_sprite.append_texture(my_texture)
        >>> empty_sprite.set_texture(0)
        """
        self.texture = self.textures[texture_no]
        self.cur_texture_index = texture_no
        self.width = self.textures[texture_no].width * self.scale
        self.height = self.textures[texture_no].height * self.scale

    def get_texture(self) -> int:
        """
        This returns the index of which texture is being
        displayed.

        >>> import arcade
        >>> empty_sprite = arcade.Sprite()
        >>> my_texture = Texture(1, 10, 10)
        >>> empty_sprite.append_texture(my_texture)
        >>> empty_sprite.get_texture()
        0
        """
        return self.cur_texture_index

    def set_position(self, center_x: float, center_y: float):
        """
        Set a sprite's position

        >>> import arcade
        >>> empty_sprite = arcade.Sprite()
        >>> empty_sprite.set_position(10, 10)
        """
        self.center_x = center_x
        self.center_y = center_y

    def set_points(self, points: Sequence[Sequence[float]]):
        """
        Set a sprite's position

        >>> import arcade
        >>> empty_sprite = arcade.Sprite()
        >>> my_points = (0,0),(1,1),(0,1),(1,0)
        >>> empty_sprite.set_points(my_points)
        """
        self._points = points

    def get_points(self) -> Tuple[Tuple[float, float]]:
        """
        Get the corner points for the rect that makes up the sprite.

        >>> import arcade
        >>> empty_sprite = arcade.Sprite()
        >>> my_points = (0,0),(1,1),(0,1),(1,0)
        >>> empty_sprite.set_points(my_points)
        >>> empty_sprite.get_points()
        ((0, 0), (1, 1), (0, 1), (1, 0))
        """
        if self._point_list_cache is not None:
            return self._point_list_cache

        if self._points is not None:
            point_list = []
            for point in range(len(self._points)):
                point = (self._points[point][0] + self.center_x,
                         self._points[point][1] + self.center_y)
                point_list.append(point)
            self._point_list_cache = tuple(point_list)
            return self._point_list_cache
        else:
            x1, y1 = rotate_point(self.center_x - self.width / 2,
                                  self.center_y - self.height / 2,
                                  self.center_x,
                                  self.center_y,
                                  self.angle)
            x2, y2 = rotate_point(self.center_x + self.width / 2,
                                  self.center_y - self.height / 2,
                                  self.center_x,
                                  self.center_y,
                                  self.angle)
            x3, y3 = rotate_point(self.center_x + self.width / 2,
                                  self.center_y + self.height / 2,
                                  self.center_x,
                                  self.center_y,
                                  self.angle)
            x4, y4 = rotate_point(self.center_x - self.width / 2,
                                  self.center_y + self.height / 2,
                                  self.center_x,
                                  self.center_y,
                                  self.angle)

            self._point_list_cache = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
            return self._point_list_cache

    points = property(get_points, set_points)

    def _set_collision_radius(self, collision_radius):
        """
        Set the collision radius.
        Note: Final collision checking is done via geometry that was
        set in get_points/set_points. These points are used in the
        check_for_collision function. This collision_radius variable
        is used as a "pre-check." We do a super-fast check with
        collision_radius and see if the sprites are close. If they are,
        then we look at the geometry and figure if they really are colliding.

        >>> import arcade
        >>> empty_sprite = arcade.Sprite()
        >>> empty_sprite.collision_radius = 5
        """
        self._collision_radius = collision_radius

    def _get_collision_radius(self):
        """
        Get the collision radius.
        Note: Final collision checking is done via geometry that was
        set in get_points/set_points. These points are used in the
        check_for_collision function. This collision_radius variable
        is used as a "pre-check." We do a super-fast check with
        collision_radius and see if the sprites are close. If they are,
        then we look at the geometry and figure if they really are colliding.

        >>> import arcade
        >>> empty_sprite = arcade.Sprite()
        >>> empty_sprite.width = 3
        >>> empty_sprite.height = 4
        >>> empty_sprite.collision_radius
        4
        """
        if not self._collision_radius:
            self._collision_radius = max(self.width, self.height)
        return self._collision_radius

    collision_radius = property(_get_collision_radius, _set_collision_radius)

    def __lt__(self, other):
        return self.texture.texture_id.value < other.texture.texture_id.value

    def _get_bottom(self) -> float:
        """
        Return the y coordinate of the bottom of the sprite.

        >>> import arcade
        >>> arcade.open_window(800,600,"Sprite Example")
        >>> scale = 1.0
        >>> ship_sprite = \
arcade.Sprite("arcade/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_y = 0.0
        >>> print(ship_sprite.bottom)
        -37.5
        >>> ship_sprite.bottom = 1.0
        >>> print(ship_sprite.bottom)
        1.0
        >>> arcade.quick_run(0.25)
        """
        points = self.get_points()
        my_min = points[0][1]
        for point in range(1, len(points)):
            my_min = min(my_min, points[point][1])
        return my_min

    def _set_bottom(self, amount: float):
        """
        Set the location of the sprite based on the bottom y coordinate.
        """
        lowest = self._get_bottom()
        diff = lowest - amount
        self.center_y -= diff

    bottom = property(_get_bottom, _set_bottom)

    def _get_top(self) -> float:
        """
        Return the y coordinate of the top of the sprite.

        >>> import arcade
        >>> arcade.open_window(800,600,"Sprite Example")
        >>> scale = 1.0
        >>> ship_sprite = \
arcade.Sprite("arcade/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_y = 0.0
        >>> print(ship_sprite.top)
        37.5
        >>> ship_sprite.top = 1.0
        >>> print(ship_sprite.top)
        1.0
        >>> ship_sprite.angle = 90
        >>> arcade.quick_run(0.25)
        """
        points = self.get_points()
        my_max = points[0][1]
        for i in range(1, len(points)):
            my_max = max(my_max, points[i][1])
        return my_max

    def _set_top(self, amount: float):
        """ The highest y coordinate. """
        highest = self._get_top()
        diff = highest - amount
        self.center_y -= diff

    top = property(_get_top, _set_top)

    def _get_center_x(self) -> float:
        """ Get the center x coordinate of the sprite. """
        return self.position[0]

    def _set_center_x(self, new_value: float):
        """ Set the center x coordinate of the sprite. """
        if new_value != self.position[0]:
            self.position[0] = new_value
            self._point_list_cache = None

    center_x = property(_get_center_x, _set_center_x)

    def _get_center_y(self) -> float:
        """ Get the center y coordinate of the sprite. """
        return self.position[1]

    def _set_center_y(self, new_value: float):
        """ Set the center y coordinate of the sprite. """
        if new_value != self.position[1]:
            self.position[1] = new_value
            self._point_list_cache = None

    center_y = property(_get_center_y, _set_center_y)

    def _get_change_x(self) -> float:
        """ Get the velocity in the x plane of the sprite. """
        return self.velocity[0]

    def _set_change_x(self, new_value: float):
        """ Set the velocity in the x plane of the sprite. """
        self.velocity[0] = new_value

    change_x = property(_get_change_x, _set_change_x)

    def _get_change_y(self) -> float:
        """ Get the velocity in the y plane of the sprite. """
        return self.velocity[1]

    def _set_change_y(self, new_value: float):
        """ Set the velocity in the y plane of the sprite. """
        self.velocity[1] = new_value

    change_y = property(_get_change_y, _set_change_y)

    def _get_angle(self) -> float:
        """ Get the angle of the sprite's rotation. """
        return self._angle

    def _set_angle(self, new_value: float):
        """ Set the angle of the sprite's rotation. """
        if new_value != self._angle:
            self._angle = new_value
            self._point_list_cache = None

    angle = property(_get_angle, _set_angle)

    def _get_left(self) -> float:
        """
        Left-most coordinate.

        :Example:

        >>> import arcade
        >>> arcade.open_window(800,600,"Sprite Example")
        >>> scale = 1.0
        >>> ship_sprite = \
arcade.Sprite("arcade/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_x = 0.0
        >>> print(ship_sprite.left)
        -49.5
        >>> ship_sprite.left = 1.0
        >>> print(ship_sprite.left)
        1.0
        >>> arcade.quick_run(0.25)
        """
        points = self.get_points()
        my_min = points[0][0]
        for i in range(1, len(points)):
            my_min = min(my_min, points[i][0])
        return my_min

    def _set_left(self, amount: float):
        """ The left most x coordinate. """
        leftmost = self._get_left()
        diff = amount - leftmost
        self.center_x += diff

    left = property(_get_left, _set_left)

    def _get_right(self) -> float:
        """
        Return the x coordinate of the right-side of the sprite.

        :Example:

        >>> import arcade
        >>> arcade.open_window(800,600,"Sprite Example")
        >>> scale = 1.0
        >>> ship_sprite = \
arcade.Sprite("arcade/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_x = 0.0
        >>> print(ship_sprite.right)
        49.5
        >>> ship_sprite.right = 1.0
        >>> print(ship_sprite.right)
        1.0
        >>> arcade.quick_run(0.25)
        """

        points = self.get_points()
        my_max = points[0][0]
        for point in range(1, len(points)):
            my_max = max(my_max, points[point][0])
        return my_max

    def _set_right(self, amount: float):
        """ The right most x coordinate. """
        rightmost = self._get_right()
        diff = rightmost - amount
        self.center_x -= diff

    right = property(_get_right, _set_right)

    def _get_texture(self) -> Texture:
        """
        Return the texture that the sprite uses.
        """
        return self._texture

    def _set_texture(self, texture: Texture):
        """
        Set the current sprite texture.
        """
        if isinstance(texture, Texture):
            self._texture = texture
            self.width = texture.width
            self.height = texture.height
        else:
            raise SystemError("Can't set the texture to something that is " +
                              "not an instance of the Texture class.")

    texture = property(_get_texture, _set_texture)

    def register_sprite_list(self, new_list):
        """
        Register this sprite as belonging to a list. We will automatically
        remove ourselves from the the list when kill() is called.
        """
        self.sprite_lists.append(new_list)

    def draw(self):
        """ Draw the sprite. """
        draw_texture_rectangle(self.center_x, self.center_y,
                               self.width, self.height,
                               self.texture, self.angle, self.alpha,
                               self.transparent)

    def update(self):
        """
        Update the sprite.
        """
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.angle += self.change_angle

    def update_animation(self):
        """
        Override this to add code that will change
        what image is shown, so the sprite can be
        animated.
        """
        pass

    def kill(self):
        """
        Remove the sprite from all sprite lists.
        """
        for sprite_list in self.sprite_lists:
            if self in sprite_list:
                sprite_list.remove(self)


T = TypeVar('T', bound=Sprite)


class SpriteList(Generic[T]):
    """
    List of sprites.

    :Unit Test:

    >>> import arcade
    >>> import random
    >>> import os
    >>> arcade.open_window(600,600,"Sprite Example")
    >>> scale = 1
    >>> meteor_list = arcade.SpriteList()
    >>> filename = "arcade/examples/images/meteorGrey_big1.png"
    >>> for i in range(100):
    ...     meteor = arcade.Sprite(filename, scale)
    ...     meteor.center_x = random.random() * 2 - 1
    ...     meteor.center_y = random.random() * 2 - 1
    ...     meteor_list.append(meteor)
    >>> meteor_list.remove(meteor) # Remove last meteor, just to test
    >>> m = meteor_list.pop() # Remove another meteor, just to test
    >>> meteor_list.update() # Call update on all items
    >>> print(len(meteor_list))
    98
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> meteor_list.draw(fast=False)
    >>> if 'APPVEYOR' not in os.environ or os.environ['APPVEYOR'] != 'TRUE':
    ...     meteor_list.draw()
    >>> meteor_list.move(0, -1)
    >>> arcade.finish_render()
    >>> for meteor in meteor_list:
    ...     meteor.kill()
    >>> arcade.quick_run(0.25)
    """
    def __init__(self, is_static=False):
        """
        Initialize the sprite list
        """
        # List of sprites in the sprite list
        self.sprite_list = []
        # List of vertex buffers that go with the sprites
        self.vertex_vbo_id = None
        # List of texture coordinate buffers (map textures to coordinages)
        # that go with this list.
        self.texture_coord_vbo_id = None
        # Set to True if we add/remove items. This way we can regenerate
        # the buffers.
        self.vbo_dirty = True
        self.change_x = 0
        self.change_y = 0
        self.is_static = is_static
        self.sorted_by_x = None
        self.sorted_by_y = None

    def append(self, item: T):
        """
        Add a new sprite to the list.
        """
        self.sprite_list.append(item)
        item.register_sprite_list(self)
        self.vbo_dirty = True

    def remove(self, item: T):
        """
        Remove a specific sprite from the list.
        """
        self.sprite_list.remove(item)
        self.vbo_dirty = True

    def update(self):
        """
        Call the update() method on each sprite in the list.
        """
        for sprite in self.sprite_list:
            sprite.update()

    def update_animation(self):
        """
        Call the update_animation() method on each sprite in the list.
        """
        for sprite in self.sprite_list:
            sprite.update_animation()

    def move(self, change_x: float, change_y: float):
        for sprite in self.sprite_list:
            sprite.center_x += change_x
            sprite.last_center_x += change_x
            sprite.center_y += change_y
            sprite.last_center_y += change_y

    def draw(self, fast: bool=True):
        """
        Call the draw() method on each sprite in the list.
        """
        # Run this if we are running 'fast' with vertex buffers
        # and we haven't yet created vertex buffers.
        if fast and self.vertex_vbo_id is None:
            self.vbo_dirty = True
            self.vertex_vbo_id = _create_vbo()
            self.texture_coord_vbo_id = _create_vbo()
            # print("Setup VBO")

        if not self.is_static:
            # See if any of the sprites moved, and we need to regenerate the VBOs.
            for sprite in self.sprite_list:
                if sprite.center_x != sprite.last_center_x \
                        or sprite.center_y != sprite.last_center_y \
                        or sprite.angle != sprite.last_angle:
                    self.vbo_dirty = True
                    sprite.last_center_x = sprite.center_x
                    sprite.last_center_y = sprite.center_y
                    sprite.last_angle = sprite.angle

        # Run this if we are running 'fast' and we added or
        # removed sprites, and thus need to recreate our buffer
        # objects.
        if fast and self.vbo_dirty:
            self.sprite_list.sort()
            rects = _create_rects(self.sprite_list)
            _set_vbo(self.vertex_vbo_id, rects)
            _set_vbo(self.texture_coord_vbo_id,
                     [0, 0, 1, 0, 1, 1, 0, 1] * len(self.sprite_list))
            self.vbo_dirty = False
            self.change_x = 0
            self.change_y = 0

        # If we run fast, use vertex buffers. Otherwise do it the
        # super slow way.
        if fast:
            _draw_rects(self.sprite_list, self.vertex_vbo_id,
                        self.texture_coord_vbo_id, self.change_x, self.change_y)
        else:
            for sprite in self.sprite_list:
                sprite.draw()

    def __len__(self) -> int:
        """ Return the length of the sprite list. """
        return len(self.sprite_list)

    def __iter__(self) -> Iterable[T]:
        """ Return an iterable object of sprites. """
        return iter(self.sprite_list)

    def __getitem__(self, i):
        return self.sprite_list[i]

    def pop(self) -> Sprite:
        """
        Pop off the last sprite in the list.
        """
        return self.sprite_list.pop()


class AnimatedTimeSprite(Sprite):
    """
    Sprite for platformer games that supports animations.

    >>> import arcade
    >>> my_sprite = arcade.AnimatedTimeSprite()
    >>> my_texture = arcade.Texture(1, 10, 10)
    >>> my_sprite.append_texture(my_texture)
    >>> my_sprite.update_animation()
    """

    def __init__(self, scale: float=1,
                 image_x: float=0, image_y: float=0,
                 center_x: float=0, center_y: float=0):

        super().__init__(scale=scale, image_x=image_x, image_y=image_y,
                         center_x=center_x, center_y=center_y)
        self.state = FACE_RIGHT
        self.cur_texture_index = 0
        self.texture_change_frames = 5
        self.frame = 0
        self.can_cache = False

    def update_animation(self):
        """
        Logic for selecting the proper texture to use.
        """
        if self.frame % self.texture_change_frames == 0:
            self.cur_texture_index += 1
            if self.cur_texture_index >= len(self.textures):
                self.cur_texture_index = 0
            self.set_texture(self.cur_texture_index)
        self.frame += 1


class AnimatedWalkingSprite(Sprite):
    """
    Sprite for platformer games that supports animations.

    >>> my_sprite = AnimatedWalkingSprite()
    >>> my_texture1 = Texture(1, 10, 10)
    >>> my_texture2 = Texture(1, 10, 10)
    >>> my_sprite.stand_right_textures = my_texture1, my_texture2
    >>> my_sprite.update_animation()
    """
    def __init__(self, scale: float=1,
                 image_x: float=0, image_y: float=0,
                 center_x: float=0, center_y: float=0):
        super().__init__(scale=scale, image_x=image_x, image_y=image_y,
                         center_x=center_x, center_y=center_y)
        self.state = FACE_RIGHT
        self.stand_right_textures = None
        self.stand_left_textures = None
        self.walk_left_textures = None
        self.walk_right_textures = None
        self.walk_up_textures = None
        self.walk_down_textures = None
        self.cur_texture_index = 0
        self.texture_change_distance = 20
        self.last_texture_change_center_x = 0
        self.last_texture_change_center_y = 0

    def update_animation(self):
        """
        Logic for selecting the proper texture to use.
        """
        x1 = self.center_x
        x2 = self.last_texture_change_center_x
        y1 = self.center_y
        y2 = self.last_texture_change_center_y
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        texture_list = []

        change_direction = False
        if self.change_x > 0 \
                and self.change_y == 0 \
                and self.state != FACE_RIGHT \
                and self.walk_right_textures \
                and len(self.walk_right_textures) > 0:
            self.state = FACE_RIGHT
            change_direction = True
        elif self.change_x < 0 and self.change_y == 0 and self.state != FACE_LEFT \
                and self.walk_left_textures and len(self.walk_left_textures) > 0:
            self.state = FACE_LEFT
            change_direction = True
        elif self.change_y < 0 and self.change_x == 0 and self.state != FACE_DOWN \
                and self.walk_down_textures and len(self.walk_down_textures) > 0:
            self.state = FACE_DOWN
            change_direction = True
        elif self.change_y > 0 and self.change_x == 0 and self.state != FACE_UP \
                and self.walk_up_textures and len(self.walk_up_textures) > 0:
            self.state = FACE_UP
            change_direction = True

        if self.change_x == 0 and self.change_y == 0:
            if self.state == FACE_LEFT:
                self.texture = self.stand_left_textures[0]
            elif self.state == FACE_RIGHT:
                self.texture = self.stand_right_textures[0]
            elif self.state == FACE_UP:
                self.texture = self.walk_up_textures[0]
            elif self.state == FACE_DOWN:
                self.texture = self.walk_down_textures[0]

        elif change_direction or distance >= self.texture_change_distance:
            self.last_texture_change_center_x = self.center_x
            self.last_texture_change_center_y = self.center_y

            if self.state == FACE_LEFT:
                texture_list = self.walk_left_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError("update_animation was called on a sprite that doesn't have a "
                                       "list of walk left textures.")
            elif self.state == FACE_RIGHT:
                texture_list = self.walk_right_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError("update_animation was called on a sprite that doesn't have a list of "
                                       "walk right textures.")
            elif self.state == FACE_UP:
                texture_list = self.walk_up_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError("update_animation was called on a sprite that doesn't have a list of "
                                       "walk up textures.")
            elif self.state == FACE_DOWN:
                texture_list = self.walk_down_textures
                if texture_list is None or len(texture_list) == 0:
                    raise RuntimeError(
                        "update_animation was called on a sprite that doesn't have a list of walk down textures.")

            self.cur_texture_index += 1
            if self.cur_texture_index >= len(texture_list):
                self.cur_texture_index = 0

            self.texture = texture_list[self.cur_texture_index]

        self.width = self.texture.width * self.scale
        self.height = self.texture.height * self.scale


def _set_vbo(vbo_id: gl.GLuint, points: List[float]):
    """
    Given a vertex buffer id, this sets the vertexes to be
    part of that buffer.
    """

    data2 = (gl.GLfloat * len(points))(*points)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2, gl.GL_STATIC_DRAW)


def _create_vbo() -> gl.GLuint:
    """
    This creates a new vertex buffer id.
    """
    vbo_id = gl.GLuint()

    gl.glGenBuffers(1, ctypes.pointer(vbo_id))

    return vbo_id


def _create_rects(rect_list: Iterable[Sprite]) -> List[float]:
    """
    Create a vertex buffer for a set of rectangles.
    """

    v2f = []
    for shape in rect_list:
        # v2f.extend([-shape.width / 2, -shape.height / 2,
        #            shape.width / 2, -shape.height / 2,
        #            shape.width / 2, shape.height / 2,
        #            -shape.width / 2, shape.height / 2])
        x1 = -shape.width / 2 + shape.center_x
        x2 = shape.width / 2 + shape.center_x
        y1 = -shape.height / 2 + shape.center_y
        y2 = shape.height / 2 + shape.center_y

        p1 = x1, y1
        p2 = x2, y1
        p3 = x2, y2
        p4 = x1, y2

        if shape.angle:
            p1 = rotate_point(p1[0], p1[1], shape.center_x, shape.center_y, shape.angle)
            p2 = rotate_point(p2[0], p2[1], shape.center_x, shape.center_y, shape.angle)
            p3 = rotate_point(p3[0], p3[1], shape.center_x, shape.center_y, shape.angle)
            p4 = rotate_point(p4[0], p4[1], shape.center_x, shape.center_y, shape.angle)

        v2f.extend([p1[0], p1[1],
                   p2[0], p2[1],
                   p3[0], p3[1],
                   p4[0], p4[1]])

    return v2f


def _render_rect_filled(offset: int, texture_id: str,
                        texture_coord_vbo: gl.GLuint, batch_count):
    """
    Render the rectangle at the right spot.
    """
    # Set color
    # gl.glLoadIdentity()
    # gl.glTranslatef(shape.center_x, shape.center_y, 0)

    # if shape.angle != 0:
    #     gl.glRotatef(shape.angle, 0, 0, 1)

    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

    gl.glTexCoordPointer(2, gl.GL_FLOAT, 0, texture_coord_vbo)
    gl.glDrawArrays(gl.GL_QUADS, offset, batch_count)


def _draw_rects(shape_list: List[Sprite], vertex_vbo_id: gl.GLuint,
                texture_coord_vbo_id: gl.GLuint, change_x: float, change_y: float):
    """
    Draw a set of rectangles using vertex buffers. This is more efficient
    than drawing them individually.
    """

    if len(shape_list) == 0:
        return

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_TEXTURE_2D)  # As soon as this happens, can't use drawing commands
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glHint(gl.GL_POLYGON_SMOOTH_HINT, gl.GL_NICEST)
    gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)

    # gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    # gl.glMatrixMode(gl.GL_MODELVIEW)
    # gl.glDisable(gl.GL_BLEND)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_vbo_id)
    gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
    gl.glVertexPointer(2, gl.GL_FLOAT, 0, 0)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, texture_coord_vbo_id)

    last_alpha = shape_list[0].alpha
    gl.glColor4f(1, 1, 1, last_alpha)
    gl.glLoadIdentity()

    # gl.glLoadIdentity()
    gl.glTranslatef(change_x, change_y, 0)

    # Ideally, we want to draw these in "batches."
    # We seek to find groups of squares with the same texture. Then draw
    # them all at once.

    last_texture_id = None
    last_alpha = 1
    batch_count = 0
    offset = 0
    batch_offset = 0
    texture_coord_vbo_id = None

    for shape in shape_list:

        if shape.texture.texture_id != last_texture_id or shape.alpha != last_alpha:
            # Ok, if the 'if' triggered above, we are now looking at a different
            # texture than we looked at with the last loop. So draw the last
            # "batch" of squares. We'll start a new batch with the current
            # square but not draw it yet
            if batch_count > 0:
                gl.glColor4f(1, 1, 1, last_alpha)
                _render_rect_filled(batch_offset,
                                    last_texture_id,
                                    texture_coord_vbo_id,
                                    batch_count)

            batch_count = 0
            batch_offset = offset
            last_texture_id = shape.texture.texture_id
            last_alpha = shape.alpha

        batch_count += 4
        offset += 4

    # Draw the last batch, if it exists
    _render_rect_filled(batch_offset,
                        last_texture_id,
                        texture_coord_vbo_id,
                        batch_count)

    gl.glDisable(gl.GL_TEXTURE_2D)
