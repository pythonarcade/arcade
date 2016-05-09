from .draw_commands import *
from .geometry import *

FACE_RIGHT = 1
FACE_LEFT = 2
FACE_UP = 3
FACE_DOWN = 4


def _set_vbo(vbo_id, points):
    data2 = (GL.GLfloat*len(points))(*points)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo_id)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    GL.GL_STATIC_DRAW)


def _create_vbo():
    vbo_id = GL.GLuint()

    GL.glGenBuffers(1, ctypes.pointer(vbo_id))

    return vbo_id


def _create_rects(rect_list):
    """ Create a vertex buffer for a set of rectangles. """

    v2f = []
    for shape in rect_list:
        v2f.extend([-shape.width / 2, -shape.height / 2,
                   shape.width / 2, -shape.height / 2,
                   shape.width / 2, shape.height / 2,
                   -shape.width / 2, shape.height / 2])

    return v2f


def _render_rect_filled(shape, offset, texture_id, texture_coord_vbo):
    """ Render the shape at the right spot. """
    # Set color
    GL.glLoadIdentity()
    GL.glTranslatef(shape.center_x, shape.center_y, 0)

    if shape.angle != 0:
        GL.glRotatef(shape.angle, 0, 0, 1)

    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)

    GL.glTexCoordPointer(2, GL.GL_FLOAT, 0, texture_coord_vbo)
    GL.glDrawArrays(GL.GL_QUADS, offset, 4)


def _draw_rects(shape_list, vertex_vbo_id, texture_coord_vbo_id):
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_PERSPECTIVE_CORRECTION_HINT, GL.GL_NICEST)
    GL.glColor4f(1, 1, 1, 1)
    # GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    # GL.glMatrixMode(GL.GL_MODELVIEW)
    # GL.glDisable(GL.GL_BLEND)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertex_vbo_id)
    GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY)
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glVertexPointer(2, GL.GL_FLOAT, 0, 0)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, texture_coord_vbo_id)

    offset = 0
    for shape in shape_list:
        if shape.can_cache:
            texture_coord_vbo_id = None
            _render_rect_filled(shape, offset,
                                shape.texture.id, texture_coord_vbo_id)

            offset += 4
        else:
            shape.draw()


class SpriteList():
    """
    List of sprites.

    :Unit Test:

    >>> import arcade
    >>> import random
    >>> arcade.open_window("Sprite Example", 600, 600)
    >>> scale = 1
    >>> meteor_list = arcade.SpriteList()
    >>> filename = "doc/source/examples/images/meteorGrey_big1.png"
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
        self.sprite_list = []
        self.vertex_vbo_id = None
        self.texture_coord_vbo_id = None
        self.vbo_dirty = True

    def append(self, item):
        """
        Add a new sprite to the list.
        """
        self.sprite_list.append(item)
        item._register_sprite_list(self)
        self.vbo_dirty = True

    def remove(self, item):
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

    def draw(self, fast=True):
        """
        Call the draw() method on each sprite in the list.
        """
        if fast and self.vertex_vbo_id is None:
            self.vbo_dirty = True
            self.vertex_vbo_id = _create_vbo()
            self.texture_coord_vbo_id = _create_vbo()
            # print("Setup VBO")

        if fast and self.vbo_dirty:
            rects = _create_rects(self.sprite_list)
            _set_vbo(self.vertex_vbo_id, rects)
            _set_vbo(self.texture_coord_vbo_id,
                     [0, 0, 1, 0, 1, 1, 0, 1] * len(self.sprite_list))
            self.vbo_dirty = False
            # print("Upload new vbo data")

        if fast:
            _draw_rects(self.sprite_list, self.vertex_vbo_id,
                        self.texture_coord_vbo_id)
        else:
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
    >>> filename = "doc/source/examples/images/playerShip1_orange.png"
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
    >>> arcade.quick_run(0.25)
    """
    def __init__(self, filename=None, scale=1, x=0, y=0, width=0, height=0):
        """
        Create a new sprite.

        Args:
            filename (str): Filename of an image that represents the sprite.
            scale (float): Scale the image up or down. Scale of 1.0 is none.
            width (float): Width of the sprite
            height (float): Height of the sprite

        """

        if width < 0:
            raise SystemError("Width of image can't be less than zero.")

        if height < 0:
            raise SystemError("Height of image can't be less than zero.")

        if width == 0 and height != 0:
            raise SystemError("Width can't be zero.")

        if height == 0 and width != 0:
            raise SystemError("Height can't be zero.")

        if filename is not None:
            self.texture = load_texture(filename, x, y,
                                        width, height)

            self.textures = [self.texture]
            self.width = self.texture.width * scale
            self.height = self.texture.height * scale
        else:
            self.textures = []
            self.width = 0
            self.height = 0

        self.cur_texture_index = 0
        self.scale = scale
        self._center_x = 0
        self._center_y = 0
        self._angle = 0.0

        self.change_x = 0
        self.change_y = 0
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

    def append_texture(self, texture):
        self.textures.append(texture)

    def set_texture(self, texture_no):
        self.texture = self.textures[texture_no]
        self.cur_texture_index = texture_no
        self.width = self.textures[texture_no].width * self.scale
        self.height = self.textures[texture_no].height * self.scale

    def get_texture(self):
        return self.cur_texture_index

    def set_position(self, center_x, center_y):
        """
        Set a sprite's position
        """
        self.center_x = center_x
        self.center_y = center_y

    def set_points(self, points):
        self._points = points

    def get_points(self):
        """
        Get the corner points for the rect that makes up the sprite.
        """
        if self._point_list_cache is not None:
            return self._point_list_cache

        if self._points is not None:
            point_list = []
            for i in range(len(self._points)):
                point = (self._points[i][0] + self.center_x,
                         self._points[i][1] + self.center_y)
                point_list.append(point)
            self._point_list_cache = point_list
            return point_list
        else:
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

        self._point_list_cache = ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
        return self._point_list_cache

    points = property(get_points, set_points)

    def _get_bottom(self):
        """
        Return the y coordinate of the bottom of the sprite.

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1
        >>> ship_sprite = \
arcade.Sprite("doc/source/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_y = 0
        >>> print(ship_sprite.bottom)
        -37.5
        >>> ship_sprite.bottom = 1
        >>> print(ship_sprite.bottom)
        1.0
        >>> arcade.quick_run(0.25)
        """
        points = self.get_points()
        my_min = points[0][1]
        for i in range(1, len(points)):
            my_min = min(my_min, points[i][1])
        return my_min

    def _set_bottom(self, amount):
        """
        Set the location of the sprite based on the bottom y coordinate.
        """
        lowest = self._get_bottom()
        diff = lowest - amount
        self.center_y -= diff

    bottom = property(_get_bottom, _set_bottom)

    def _get_top(self):
        """
        Return the y coordinate of the top of the sprite.

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1
        >>> ship_sprite = \
arcade.Sprite("doc/source/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_y = 0
        >>> print(ship_sprite.top)
        37.5
        >>> ship_sprite.top = 1
        >>> print(ship_sprite.top)
        1.0
        >>> arcade.quick_run(0.25)
        """
        points = self.get_points()
        points = self.get_points()
        my_max = points[0][1]
        for i in range(1, len(points)):
            my_max = max(my_max, points[i][1])
        return my_max

    def _set_top(self, amount):
        """ The highest y coordinate. """
        highest = self._get_top()
        diff = highest - amount
        self.center_y -= diff

    top = property(_get_top, _set_top)

    def _get_center_x(self):
        return self._center_x

    def _set_center_x(self, new_value):
        if new_value != self._center_x:
            self._center_x = new_value
            self._point_list_cache = None

    center_x = property(_get_center_x, _set_center_x)

    def _get_center_y(self):
        return self._center_y

    def _set_center_y(self, new_value):
        if new_value != self._center_y:
            self._center_y = new_value
            self._point_list_cache = None

    center_y = property(_get_center_y, _set_center_y)

    def _get_angle(self):
        return self._angle

    def _set_angle(self, new_value):
        if new_value != self._angle:
            self._angle = new_value
            self._point_list_cache = None

    angle = property(_get_angle, _set_angle)

    def _get_left(self):
        """
        Left-most coordinate.

        :Example:

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1
        >>> ship_sprite = \
arcade.Sprite("doc/source/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_x = 0
        >>> print(ship_sprite.left)
        -49.5
        >>> ship_sprite.left = 1
        >>> print(ship_sprite.left)
        1.0
        >>> arcade.quick_run(0.25)
        """
        points = self.get_points()
        points = self.get_points()
        my_min = points[0][0]
        for i in range(1, len(points)):
            my_min = min(my_min, points[i][0])
        return my_min

    def _set_left(self, amount):
        """ The left most x coordinate. """
        leftmost = self._get_left()
        diff = amount - leftmost
        self.center_x += diff

    left = property(_get_left, _set_left)

    def _get_right(self):
        """
        Return the x coordinate of the right-side of the sprite.

        :Example:

        >>> import arcade
        >>> arcade.open_window("Sprite Example", 800, 600)
        >>> scale = 1
        >>> ship_sprite = \
arcade.Sprite("doc/source/examples/images/playerShip1_orange.png", scale)
        >>> ship_sprite.center_x = 0
        >>> print(ship_sprite.right)
        49.5
        >>> ship_sprite.right = 1
        >>> print(ship_sprite.right)
        1.0
        >>> arcade.quick_run(0.25)
        """

        points = self.get_points()
        my_max = points[0][0]
        for i in range(1, len(points)):
            my_max = max(my_max, points[i][0])
        return my_max

    def _set_right(self, amount):
        """ The right most x coordinate. """
        rightmost = self._get_right()
        diff = rightmost - amount
        self.center_x -= diff

    right = property(_get_right, _set_right)

    def _get_texture(self):
        """
        Return the texture that the sprite uses.
        """
        return self._texture

    def _set_texture(self, texture):
        """
        Set the current sprite texture.
        """
        if type(texture) is Texture:
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


class AnimatedSprite(Sprite):
    """
    Sprite for platformer games that supports animations.

    >>> import arcade
    >>> arcade.open_window("Sprite Example", 800, 600)
    >>> player = arcade.AnimatedSprite()
    >>> top_trim = 100
    >>> ltrim = 2
    >>> rtrim = 2
    >>> image_location_list = [
    ... [520 + ltrim, 516 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [520 + ltrim, 258 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [520 + ltrim, 0 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 1548 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 1290 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 516 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 258 + top_trim, 128 - ltrim - rtrim, 256 - top_trim]]
    >>> filename = "doc/source/examples/images/spritesheet_complete.png"
    >>> texture_info_list = arcade.load_textures(filename, image_location_list)
    >>> for texture_info in texture_info_list:
    ...     texture = texture_info
    ...     player.append_texture(texture)
    >>> texture_info_list = arcade.load_textures(\
filename, image_location_list, True)
    >>> for texture_info in texture_info_list:
    ...     texture = texture_info
    ...     player.append_texture(texture)
    >>> player.set_left_walk_textures([12, 13])
    >>> player.set_right_walk_textures([5, 6])
    >>> player.set_left_jump_textures([10])
    >>> player.set_right_jump_textures([3])
    >>> player.set_left_stand_textures([11])
    >>> player.set_right_stand_textures([4])
    >>> player.texture_change_distance = 5
    >>> player.speed = 10
    >>> player.set_position(5, 5)
    >>> player.jump()
    >>> player.change_x = 10 # Jump
    >>> player.change_y = 1
    >>> player.update()
    >>> player.go_left()
    >>> player.update()
    >>> player.update()
    >>> player.update()
    >>> player.stop_left()
    >>> player.update()
    >>> player.face_left()
    >>> player.update()
    >>> player.change_x = -10 #Left
    >>> player.change_y = 0.0
    >>> player.update()
    >>> player.go_left()
    >>> player.update()
    >>> player.stop_left()
    >>> player.update()
    >>> player.face_right()
    >>> player.change_x = 10 # Right
    >>> player.change_y = 0.0
    >>> player.update()
    >>> player.go_right()
    >>> player.update()
    >>> player.update()
    >>> player.stop_right()
    >>> player.update()
    >>> player.stop_right()
    >>> player.change_x = 0 # Stop
    >>> player.change_y = 0.0
    >>> player.update()
    >>> player.kill()
    >>> arcade.quick_run(0.25)
    """
    def __init__(self):
        super().__init__()
        self.last_change_x = self.center_x
        self.facing = "right"
        self.left_walk_textures = []
        self.right_walk_textures = []
        self.up_walk_textures = []
        self.down_walk_textures = []
        self.jump_textures = []
        self.left_stand_textures = []
        self.right_stand_textures = []
        self.up_stand_textures = []
        self.down_stand_textures = []
        self.jump_speed = 10
        self.cur_texture_index = 0
        self.texture_change_distance = 0
        self.speed = 5
        self.can_cache = False

    def update(self):
        """
        Logic for selecting the proper texture to use.
        """
        super().update()

        if self.change_y == 0.0:
            if self.change_x < 0:
                if abs(self.last_change_x - self.center_x) > \
                        self.texture_change_distance:
                    if self.cur_texture_index in self.left_textures:
                        pos = self.left_textures.index(self.cur_texture_index)\
                            + 1
                    else:
                        pos = 0
                    if pos >= len(self.left_textures):
                        pos = 0
                    self.set_texture(self.left_textures[pos])
                    self.last_change_x = self.center_x

            elif self.change_x > 0:
                if abs(self.last_change_x - self.center_x) \
                        > self.texture_change_distance:
                    if self.cur_texture_index in self.right_textures:
                        i = self.cur_texture_index
                        pos = self.right_textures.index(i) + 1
                    else:
                        pos = 0
                    if pos >= len(self.right_textures):
                        pos = 0
                    self.set_texture(self.right_textures[pos])
                    self.last_change_x = self.center_x
            else:
                if self.facing == "right":
                    self.set_texture(self.right_stand_textures[0])
                if self.facing == "left":
                    self.set_texture(self.left_stand_textures[0])

        else:
            if self.facing == "right":
                self.set_texture(self.jump_right_textures[0])
            if self.facing == "left":
                self.set_texture(self.jump_left_textures[0])

    def set_left_walk_textures(self, texture_index_list):
        self.left_textures = texture_index_list

    def set_right_walk_textures(self, texture_index_list):
        self.right_textures = texture_index_list

    def set_left_jump_textures(self, texture_index_list):
        self.jump_left_textures = texture_index_list

    def set_right_jump_textures(self, texture_index_list):
        self.jump_right_textures = texture_index_list

    def set_left_stand_textures(self, texture_index_list):
        self.left_stand_textures = texture_index_list

    def set_right_stand_textures(self, texture_index_list):
        self.right_stand_textures = texture_index_list

    def go_left(self):
        self.change_x = -self.speed

    def stop_left(self):
        if self.change_x < 0:
            self.change_x = 0

    def go_right(self):
        self.change_x = self.speed

    def stop_right(self):
        if self.change_x > 0:
            self.change_x = 0

    def face_left(self):
        if self.facing != "left":
            self.facing = "left"

    def face_right(self):
        if self.facing != "right":
            self.facing = "right"

    def jump(self):
        self.change_y = self.jump_speed


class AnimatedTimeSprite(Sprite):
    """
    Sprite for platformer games that supports animations.
    """
    def __init__(self, scale=1, x=0, y=0):
        super().__init__(scale=scale, x=x, y=y)
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
            self.texture = self.textures[self.cur_texture_index]
        self.frame += 1


class AnimatedWalkingSprite(Sprite):
    """
    Sprite for platformer games that supports animations.
    """
    def __init__(self, scale=1, x=0, y=0):
        super().__init__(scale=scale, x=x, y=y)
        self.last_center_x = self.center_x
        self.last_center_y = self.center_y
        self.state = FACE_RIGHT
        self.stand_right_textures = None
        self.stand_left_textures = None
        self.walk_left_textures = None
        self.walk_right_textures = None
        self.walk_up_walk_textures = None
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

        change_direction = False
        if self.change_x > 0 and self.state == FACE_LEFT:
            self.state = FACE_RIGHT
            change_direction = True

        elif self.change_x < 0 and self.state == FACE_RIGHT:
            self.state = FACE_LEFT
            change_direction = True

        if self.change_x == 0 and self.change_y == 0:
            if self.state == FACE_LEFT:
                self.texture = self.stand_left_textures[0]
            else:
                self.texture = self.stand_right_textures[0]

        elif change_direction or distance >= self.texture_change_distance:
            self.last_center_x = self.center_x
            self.last_center_y = self.center_y

            if self.state == FACE_LEFT:
                texture_list = self.walk_left_textures
            else:
                texture_list = self.walk_right_textures

            self.cur_texture_index += 1
            if self.cur_texture_index >= len(texture_list):
                self.cur_texture_index = 0

            self.texture = texture_list[self.cur_texture_index]
