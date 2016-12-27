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

from numbers import Number
from typing import Iterable, List, Sequence

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
    >>> arcade.open_window("Sprite Example", 800, 600)
    >>> SCALE = 1
    >>> # Test creating an empty sprite
    >>> empty_sprite = arcade.Sprite()
    >>> # Create a sprite with an image
    >>> filename = "examples/images/playerShip1_orange.png"
    >>> ship_sprite = arcade.Sprite(filename, SCALE)
    >>> # Draw the sprite
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> ship_sprite.draw()
    >>> arcade.finish_render()
    >>> # Move the sprite
    >>> ship_sprite.change_x = 1
    >>> ship_sprite.change_y = 1
    >>> ship_sprite.update() # Move/update the ship
    >>> # Remove the sprite
    >>> ship_sprite.kill()
    >>> ship_sprite = arcade.Sprite(filename, SCALE, image_height=-1)
    Traceback (most recent call last):
    ...
    ValueError: Height entered is less than zero. Height must be a positive float.

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

        self.can_cache = True
        self._points = None
        self._point_list_cache = None

        self.force = [0, 0]

    def append_texture(self, texture: Texture):
        """
        Appends a new texture to the list of textures that can be
        applied to this sprite.
        """
        self.textures.append(texture)

    def set_texture(self, texture_no: int):
        """
        Assuming 'texture' is a list of textures, this sets
        which texture index should be displayed. It also resets
        the width and height based on the scale of the texture.
        """
        self.texture = self.textures[texture_no]
        self.cur_texture_index = texture_no
        self.width = self.textures[texture_no].width * self.scale
        self.height = self.textures[texture_no].height * self.scale

    def get_texture(self) -> int:
        """
        This returns the index of which texture is being
        displayed.
        """
        return self.cur_texture_index

    def set_position(self, center_x: float, center_y: float):
        """
        Set a sprite's position
        """
        self.center_x = center_x
        self.center_y = center_y

    def set_points(self, points: Sequence[Sequence[float]]):
        self._points = points

    def get_points(self) -> List[List[float]]:
        """
        Get the corner points for the rect that makes up the sprite.
        """
        if self._point_list_cache is not None:
            return self._point_list_cache

        if self._points is not None:
            point_list = []
            for point in range(len(self._points)):
                point = (self._points[point][0] + self.center_x,
                         self._points[point][1] + self.center_y)
                point_list.append(point)
            self._point_list_cache = point_list
            return point_list
        else:
            x1, y1 = _rotate(self.center_x - self.width / 2,
                             self.center_y - self.height / 2,
                             self.center_x,
                             self.center_y,
                             self.angle)
            x2, y2 = _rotate(self.center_x + self.width / 2,
                             self.center_y - self.height / 2,
                             self.center_x,
                             self.center_y,
                             self.angle)
            x3, y3 = _rotate(self.center_x + self.width / 2,
                             self.center_y + self.height / 2,
                             self.center_x,
                             self.center_y,
                             self.angle)
            x4, y4 = _rotate(self.center_x - self.width / 2,
                             self.center_y + self.height / 2,
                             self.center_x,
                             self.center_y,
                             self.angle)

        self._point_list_cache = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
        return self._point_list_cache

    points = property(get_points, set_points)

    def _get_bottom(self) -> float:
        """
        Return the y coordinate of the bottom of the sprite.

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1.0
        >>> ship_sprite = \
arcade.Sprite("examples/images/playerShip1_orange.png", scale)
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
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1.0
        >>> ship_sprite = \
arcade.Sprite("examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_y = 0.0
        >>> print(ship_sprite.top)
        37.5
        >>> ship_sprite.top = 1.0
        >>> print(ship_sprite.top)
        1.0
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

    def _get_left(self) -> Number:
        """
        Left-most coordinate.

        :Example:

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1.0
        >>> ship_sprite = \
arcade.Sprite("examples/images/playerShip1_orange.png", scale)
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
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1.0
        >>> ship_sprite = \
arcade.Sprite("examples/images/playerShip1_orange.png", scale)
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

    def _register_sprite_list(self, new_list):
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


class SpriteList:
    """
    List of sprites.

    :Unit Test:

    >>> import arcade
    >>> import random
    >>> arcade.open_window("Sprite Example", 600, 600)
    >>> scale = 1
    >>> meteor_list = arcade.SpriteList()
    >>> filename = "examples/images/meteorGrey_big1.png"
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
    >>> arcade.finish_render()
    >>> for meteor in meteor_list:
    ...     meteor.kill()
    >>> arcade.quick_run(0.25)
    """
    def __init__(self):
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

    def append(self, item: Sprite):
        """
        Add a new sprite to the list.
        """
        self.sprite_list.append(item)
        item._register_sprite_list(self)
        self.vbo_dirty = True

    def remove(self, item: Sprite):
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

        # Run this if we are running 'fast' and we added or
        # removed sprites, and thus need to recreate our buffer
        # objects.
        if fast and self.vbo_dirty:
            rects = _create_rects(self.sprite_list)
            _set_vbo(self.vertex_vbo_id, rects)
            _set_vbo(self.texture_coord_vbo_id,
                     [0, 0, 1, 0, 1, 1, 0, 1] * len(self.sprite_list))
            self.vbo_dirty = False
            # print("Upload new vbo data")

        # If we run fast, use vertex buffers. Otherwise do it the
        # super slow way.
        if fast:
            _draw_rects(self.sprite_list, self.vertex_vbo_id,
                        self.texture_coord_vbo_id)
        else:
            for sprite in self.sprite_list:
                sprite.draw()

    def __len__(self) -> int:
        """ Return the length of the sprite list. """
        return len(self.sprite_list)

    def __iter__(self) -> Iterable[Sprite]:
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
    """

    def __init__(self, scale: float=1,
                 image_x: float=0, image_y: float=0,
                 center_x: float=0, center_y: float=0):

        super().__init__(scale=scale, image_x=image_x, image_y=image_y,
                         center_x=center_x, center_y=center_y)
        self.last_center_x = self.center_x
        self.last_center_y = self.center_y
        self.state = FACE_RIGHT
        self.textures = None
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
    """
    def __init__(self, scale: float=1,
                 image_x: float=0, image_y: float=0,
                 center_x: float=0, center_y: float=0):
        super().__init__(scale=scale, image_x=image_x, image_y=image_y,
                         center_x=center_x, center_y=center_y)
        self.last_center_x = self.center_x
        self.last_center_y = self.center_y
        self.state = FACE_RIGHT
        self.stand_right_textures = None
        self.stand_left_textures = None
        self.walk_left_textures = None
        self.walk_right_textures = None
        self.walk_up_textures = None
        self.walk_down_textures = None
        self.cur_texture_index = 0
        self.texture_change_distance = 20
        self.can_cache = False

    def update_animation(self):
        """
        Logic for selecting the proper texture to use.
        """
        x1 = self.center_x
        x2 = self.last_center_x
        y1 = self.center_y
        y2 = self.last_center_y
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        texture_list = []

        change_direction = False
        if self.change_x > 0 and self.change_y == 0 and self.state != FACE_RIGHT:
            self.state = FACE_RIGHT
            change_direction = True
        elif self.change_x < 0 and self.change_y == 0 and self.state != FACE_LEFT:
            self.state = FACE_LEFT
            change_direction = True
        elif self.change_y < 0 and self.change_x == 0 and self.state != FACE_DOWN:
            self.state = FACE_DOWN
            change_direction = True
        elif self.change_y > 0 and self.change_x == 0 and self.state != FACE_UP:
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
            self.last_center_x = self.center_x
            self.last_center_y = self.center_y

            if self.state == FACE_LEFT:
                texture_list = self.walk_left_textures
            elif self.state == FACE_RIGHT:
                texture_list = self.walk_right_textures
            elif self.state == FACE_UP:
                texture_list = self.walk_up_textures
            elif self.state == FACE_DOWN:
                texture_list = self.walk_down_textures

            self.cur_texture_index += 1
            if self.cur_texture_index >= len(texture_list):
                self.cur_texture_index = 0

            self.texture = texture_list[self.cur_texture_index]

        self.width = self.texture.width * self.scale
        self.height = self.texture.height * self.scale


def _rotate(x: float, y: float, cx: float, cy: float,
            angle: float) -> Iterable[Number]:
    """
    Rotate a point around a center.

    >>> x, y = _rotate(1, 1, 0, 0, 90)
    >>> print("x = {:.1f}, y = {:.1f}".format(x, y))
    x = -1.0, y = 1.0
    """
    temp_x = x - cx
    temp_y = y - cy

    # now apply rotation
    rotated_x = temp_x * math.cos(math.radians(angle)) - \
        temp_y * math.sin(math.radians(angle))
    rotated_y = temp_x * math.sin(math.radians(angle)) + \
        temp_y * math.cos(math.radians(angle))

    # translate back
    x = rotated_x + cx
    y = rotated_y + cy

    return x, y


def _set_vbo(vbo_id: gl.GLuint, points: List[float]):
    """
    Given a vertex buffer id, this sets the vertexes to be
    part of that buffer.
    """

    # todo what does it do?
    data2 = (gl.GLfloat*len(points))(*points)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    gl.GL_STATIC_DRAW)


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
        v2f.extend([-shape.width / 2, -shape.height / 2,
                   shape.width / 2, -shape.height / 2,
                   shape.width / 2, shape.height / 2,
                   -shape.width / 2, shape.height / 2])

    return v2f


def _render_rect_filled(shape: Sprite, offset: int, texture_id: str,
                        texture_coord_vbo: gl.GLuint):
    """
    Render the rectangle at the right spot.
    """
    # Set color
    gl.glLoadIdentity()
    gl.glTranslatef(shape.center_x, shape.center_y, 0)

    if shape.angle != 0:
        gl.glRotatef(shape.angle, 0, 0, 1)

    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

    gl.glTexCoordPointer(2, gl.GL_FLOAT, 0, texture_coord_vbo)
    gl.glDrawArrays(gl.GL_QUADS, offset, 4)


def _draw_rects(shape_list: Iterable[Sprite], vertex_vbo_id: gl.GLuint,
                texture_coord_vbo_id: gl.GLuint):
    """
    Draw a set of rectangles using vertex buffers. This is more efficient
    than drawing them individually.
    """
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_TEXTURE_2D) # As soon as this happens, can't use drawing commands
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

    offset = 0
    for shape in shape_list:
        if shape.can_cache:
            texture_coord_vbo_id = None

            gl.glColor4f(1, 1, 1, shape.alpha)

            _render_rect_filled(shape, offset,
                                shape.texture.texture_id, texture_coord_vbo_id)

            offset += 4
        else:
            shape.draw()
    gl.glDisable(gl.GL_TEXTURE_2D)
