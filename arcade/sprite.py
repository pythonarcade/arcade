"""
This module manages all of the code around Sprites.

For information on Spatial Hash Maps, see:
https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/
"""


import math


from arcade.draw_commands import load_texture
from arcade.draw_commands import draw_texture_rectangle
from arcade.draw_commands import Texture
from arcade.draw_commands import rotate_point
from arcade.arcade_types import RGB

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
        :alpha: Transparency of sprite. 0 is invisible, 255 is opaque.
        :angle: Rotation angle in degrees.
        :radians: Rotation angle in radians.
        :bottom: Set/query the sprite location by using the bottom coordinate. \
        This will be the 'y' of the bottom of the sprite.
        :boundary_left: Used in movement. Left boundary of moving sprite.
        :boundary_right: Used in movement. Right boundary of moving sprite.
        :boundary_top: Used in movement. Top boundary of moving sprite.
        :boundary_bottom: Used in movement. Bottom boundary of moving sprite.
        :center_x: X location of the center of the sprite
        :center_y: Y location of the center of the sprite
        :change_x: Movement vector, in the x direction.
        :change_y: Movement vector, in the y direction.
        :change_angle: Change in rotation.
        :color: Color tint the sprite
        :collision_radius: Used as a fast-check to see if this item is close \
        enough to another item. If this check works, we do a slower more accurate check.
        :cur_texture_index: Index of current texture being used.
        :guid: Unique identifier for the sprite. Useful when debugging.
        :height: Height of the sprite.
        :force: Force being applied to the sprite. Useful when used with Pymunk \
        for physics.
        :left: Set/query the sprite location by using the left coordinate. This \
        will be the 'x' of the left of the sprite.
        :points: Points, in relation to the center of the sprite, that are used \
        for collision detection. Arcade defaults to creating points for a rectangle \
        that encompass the image. If you are creating a ramp or making better \
        hit-boxes, you can custom-set these.
        :position: A list with the (x, y) of where the sprite is.
        :repeat_count_x: Unused
        :repeat_count_y: Unused
        :right: Set/query the sprite location by using the right coordinate. \
        This will be the 'y=x' of the right of the sprite.
        :sprite_lists: List of all the sprite lists this sprite is part of.
        :texture: `Texture` class with the current texture.
        :textures: List of textures associated with this sprite.
        :top: Set/query the sprite location by using the top coordinate. This \
        will be the 'y' of the top of the sprite.
        :scale: Scale the image up or down. Scale of 1.0 is original size, 0.5 \
        is 1/2 height and width.
        :velocity: Change in x, y expressed as a list. (0, 0) would be not moving.
        :width: Width of the sprite

    It is common to over-ride the `update` method and provide mechanics on
    movement or other sprite updates.

    """

    def __init__(self,
                 filename: str=None,
                 scale: float=1,
                 image_x: float=0, image_y: float=0,
                 image_width: float=0, image_height: float=0,
                 center_x: float=0, center_y: float=0,
                 repeat_count_x=1, repeat_count_y=1):
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

        self.sprite_lists = []

        if filename is not None:
            self._texture = load_texture(filename, image_x, image_y,
                                         image_width, image_height)

            self.textures = [self._texture]
            self._width = self._texture.width * scale
            self._height = self._texture.height * scale
            self._texture.scale = scale
        else:
            self.textures = []
            self._texture = None
            self._width = 0
            self._height = 0

        self.cur_texture_index = 0

        self._scale = scale
        self._position = [center_x, center_y]
        self._angle = 0.0

        self.velocity = [0, 0]
        self.change_angle = 0

        self.boundary_left = None
        self.boundary_right = None
        self.boundary_top = None
        self.boundary_bottom = None

        self._alpha = 255
        self._collision_radius = None
        self._color = (255, 255, 255)

        self._points = None
        self._point_list_cache = None

        self.force = [0, 0]
        self.guid = None

        self.repeat_count_x = repeat_count_x
        self.repeat_count_y = repeat_count_y

    def append_texture(self, texture: Texture):
        """
        Appends a new texture to the list of textures that can be
        applied to this sprite.

        :param Texture texture: Texture to add ot the list of available textures

        """
        self.textures.append(texture)

    def _get_position(self) -> (float, float):
        """
        Get the center x coordinate of the sprite.

        Returns:
            (width, height)
        """
        return self._position

    def _set_position(self, new_value: (float, float)):
        """
        Set the center x coordinate of the sprite.

        Args:
            new_value:

        Returns:

        """
        if new_value[0] != self._position[0] or new_value[1] != self._position[1]:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._position[0], self._position[1] = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_location(self)

    position = property(_get_position, _set_position)

    def set_position(self, center_x: float, center_y: float):
        """
        Set a sprite's position

        :param float center_x: New x position of sprite
        :param float center_y: New y position of sprite
        """
        self._set_position((center_x, center_y))

    def set_points(self, points: Sequence[Sequence[float]]):
        """
        Set a sprite's position
        """
        self._points = points

    def forward(self, speed: float=1.0):
        """
        Set a Sprite's position to speed by its angle
        :param speed: speed factor
        """
        self.change_x += math.cos(self.radians) * speed
        self.change_y += math.sin(self.radians) * speed

    def reverse(self, speed: float=1.0):
        self.forward(-speed)

    def strafe(self, speed: float=1.0):
        """
        Set a sprites position perpendicular to its angle by speed
        :param speed: speed factor
        """
        self.change_x += -math.sin(self.radians) * speed
        self.change_y += math.cos(self.radians) * speed

    def turn_right(self, theta: float=90):
        self.angle -= theta

    def turn_left(self, theta: float=90):
        self.angle += theta

    def stop(self):
        """
        Stop the Sprite's motion
        """
        self.change_x = 0
        self.change_y = 0
        self.change_angle = 0

    def get_points(self) -> Tuple[Tuple[float, float]]:
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
            self._point_list_cache = tuple(point_list)
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

    def _set_collision_radius(self, collision_radius: float):
        """
        Set the collision radius.

        .. note:: Final collision checking is done via geometry that was
            set in get_points/set_points. These points are used in the
            check_for_collision function. This collision_radius variable
            is used as a "pre-check." We do a super-fast check with
            collision_radius and see if the sprites are close. If they are,
            then we look at the geometry and figure if they really are colliding.

        :param float collision_radius: Collision radius
        """
        self._collision_radius = collision_radius

    def _get_collision_radius(self):
        """
        Get the collision radius.

        .. note:: Final collision checking is done via geometry that was
            set in get_points/set_points. These points are used in the
            check_for_collision function. This collision_radius variable
            is used as a "pre-check." We do a super-fast check with
            collision_radius and see if the sprites are close. If they are,
            then we look at the geometry and figure if they really are colliding.

        """
        if not self._collision_radius:
            self._collision_radius = max(self.width, self.height)
        return self._collision_radius

    collision_radius = property(_get_collision_radius, _set_collision_radius)

    def __lt__(self, other):
        return self._texture.texture_id.value < other.texture.texture_id.value

    def clear_spatial_hashes(self):
        """
        Search the sprite lists this sprite is a part of, and remove it
        from any spatial hashes it is a part of.

        """
        for sprite_list in self.sprite_lists:
            if sprite_list.use_spatial_hash and sprite_list.spatial_hash is not None:
                try:
                    sprite_list.spatial_hash.remove_object(self)
                except ValueError:
                    print("Warning, attempt to remove item from spatial hash that doesn't exist in the hash.")

    def add_spatial_hashes(self):
        for sprite_list in self.sprite_lists:
            if sprite_list.use_spatial_hash:
                sprite_list.spatial_hash.insert_object_for_box(self)

    def _get_bottom(self) -> float:
        """
        Return the y coordinate of the bottom of the sprite.
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

    def _get_width(self) -> float:
        """ Get the width of the sprite. """
        return self._width

    def _set_width(self, new_value: float):
        """ Set the width in pixels of the sprite. """
        if new_value != self._width:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._width = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_position(self)

    width = property(_get_width, _set_width)

    def _get_height(self) -> float:
        """ Get the height in pixels of the sprite. """
        return self._height

    def _set_height(self, new_value: float):
        """ Set the center x coordinate of the sprite. """
        if new_value != self._height:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._height = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_position(self)

    height = property(_get_height, _set_height)

    def _get_scale(self) -> float:
        """ Get the scale of the sprite. """
        return self._scale

    def _set_scale(self, new_value: float):
        """ Set the center x coordinate of the sprite. """
        if new_value != self._height:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._scale = new_value
            if self._texture:
                self._width = self._texture.width * self._scale
                self._height = self._texture.height * self._scale
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_position(self)

    scale = property(_get_scale, _set_scale)

    def _get_center_x(self) -> float:
        """ Get the center x coordinate of the sprite. """
        return self._position[0]

    def _set_center_x(self, new_value: float):
        """ Set the center x coordinate of the sprite. """
        if new_value != self._position[0]:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._position[0] = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_location(self)

    center_x = property(_get_center_x, _set_center_x)

    def _get_center_y(self) -> float:
        """ Get the center y coordinate of the sprite. """
        return self._position[1]

    def _set_center_y(self, new_value: float):
        """ Set the center y coordinate of the sprite. """
        if new_value != self._position[1]:
            self.clear_spatial_hashes()
            self._point_list_cache = None
            self._position[1] = new_value
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_location(self)

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
            self.clear_spatial_hashes()
            self._angle = new_value
            self._point_list_cache = None
            self.add_spatial_hashes()

            for sprite_list in self.sprite_lists:
                sprite_list.update_angle(self)

    angle = property(_get_angle, _set_angle)

    def _to_radians(self) -> float:
        """
        Converts the degrees representation of self.angle into radians.
        :return: float
        """
        return self.angle / 180.0 * math.pi

    def _from_radians(self, new_value: float):
        """
        Converts a radian value into degrees and stores it into angle.
        """
        self.angle = new_value * 180.0 / math.pi

    radians = property(_to_radians, _from_radians)

    def _get_left(self) -> float:
        """
        Left-most coordinate.
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

    def set_texture(self, texture_no: int):
        """ Sets texture by texture id. Should be renamed but keeping
        this for backwards compatibility. """
        if self.textures[texture_no] == self._texture:
            return

        texture = self.textures[texture_no]
        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._texture = texture
        self._width = texture.width * texture.scale
        self._height = texture.height * texture.scale
        self.add_spatial_hashes()
        for sprite_list in self.sprite_lists:
            sprite_list.update_texture(self)

    def _set_texture2(self, texture: Texture):
        """ Sets texture by texture id. Should be renamed but keeping
        this for backwards compatibility. """
        if texture == self._texture:
            return

        self.clear_spatial_hashes()
        self._point_list_cache = None
        self._texture = texture
        self._width = texture.width * texture.scale
        self._height = texture.height * texture.scale
        self.add_spatial_hashes()
        for sprite_list in self.sprite_lists:
            sprite_list.update_texture(self)

    def _get_texture(self):
        return self._texture

    texture = property(_get_texture, _set_texture2)

    def _get_color(self) -> RGB:
        """
        Return the RGB color associated with the sprite.
        """
        return self._color

    def _set_color(self, color: RGB):
        """
        Set the current sprite color as a RGB value
        """
        self._color = color
        for sprite_list in self.sprite_lists:
            sprite_list.update_position(self)

    color = property(_get_color, _set_color)

    def _get_alpha(self) -> RGB:
        """
        Return the alpha associated with the sprite.
        """
        return self._alpha

    def _set_alpha(self, alpha: RGB):
        """
        Set the current sprite color as a value
        """
        self._alpha = alpha
        for sprite_list in self.sprite_lists:
            sprite_list.update_position(self)

    alpha = property(_get_alpha, _set_alpha)

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
                               self._texture, self.angle, self.alpha,  # TODO: review this function
                               repeat_count_x=self.repeat_count_x,
                               repeat_count_y=self.repeat_count_y)

    def update(self):
        """
        Update the sprite.
        """
        self.position = [self._position[0] + self.change_x, self._position[1] + self.change_y]
        self.angle += self.change_angle

    def update_animation(self):
        """
        Override this to add code that will change
        what image is shown, so the sprite can be
        animated.
        """
        pass

    def remove_from_sprite_lists(self):
        """
        Remove the sprite from all sprite lists.
        """
        for sprite_list in self.sprite_lists:
            if self in sprite_list:
                sprite_list.remove(self)
        self.sprite_lists.clear()

    def kill(self):
        """
        Alias of `remove_from_sprite_lists`
        """
        self.remove_from_sprite_lists()


class AnimatedTimeSprite(Sprite):
    """
    Sprite for platformer games that supports animations.
    """

    def __init__(self, scale: float = 1,
                 image_x: float = 0, image_y: float = 0,
                 center_x: float = 0, center_y: float = 0):

        super().__init__(scale=scale, image_x=image_x, image_y=image_y,
                         center_x=center_x, center_y=center_y)
        self.state = FACE_RIGHT
        self.cur_texture_index = 0
        self.texture_change_frames = 5
        self.frame = 0

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
    def __init__(self, scale: float = 1,
                 image_x: float = 0, image_y: float = 0,
                 center_x: float = 0, center_y: float = 0):
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

        if self._texture is None:
            print("Error, no texture set")
        else:
            self.width = self._texture.width * self.scale
            self.height = self._texture.height * self.scale


def get_distance_between_sprites(sprite1: Sprite, sprite2: Sprite) -> float:
    """
    Returns the distance between the center of two given sprites
    :param Sprite sprite1: Sprite one
    :param Sprite sprite2: Sprite two
    :return: Distance
    :rtype: float
    """
    distance = math.sqrt((sprite1.center_x - sprite2.center_x) ** 2 + (sprite1.center_y - sprite2.center_y) ** 2)
    return distance
