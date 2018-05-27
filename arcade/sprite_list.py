from typing import Iterable
from typing import TypeVar
from typing import Generic
from typing import List

import ctypes

import pyglet.gl as gl

from arcade.sprite import Sprite
from arcade.sprite import get_distance_between_sprites
from arcade.draw_commands import rotate_point


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
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
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


class SpatialHash:
    """
    See: https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/
    """

    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.contents = {}

    def _hash(self, point):
        return int(point[0] / self.cell_size), int(point[1] / self.cell_size)

    def insert_object_for_box(self, new_object: Sprite):
        # Get the corners
        min_x = new_object.left
        max_x = new_object.right
        min_y = new_object.bottom
        max_y = new_object.top

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        # print("Add: ", min_point, max_point)

        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # append to each intersecting cell
                self.contents.setdefault((i, j), []).append(new_object)

    def remove_object(self, new_object: Sprite):
        # Get the corners
        min_x = new_object.left
        max_x = new_object.right
        min_y = new_object.bottom
        max_y = new_object.top

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)
        # print("Remove: ", min_point, max_point)

        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = self.contents.setdefault((i, j), [])
                try:
                    bucket.remove(new_object)
                except:
                    print("Warning, tried to remove item from spatial hash that wasn't there.")

    def get_objects_for_box(self, check_object: Sprite):
        # Get the corners
        min_x = check_object.left
        max_x = check_object.right
        min_y = check_object.bottom
        max_y = check_object.top

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        close_by_sprites = []
        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # append to each intersecting cell
                close_by_sprites.extend(self.contents.setdefault((i, j), []))

        return close_by_sprites


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

    def __init__(self, is_static=False, use_spatial_hash=True, spatial_hash_cell_size=128):
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
        self.spatial_hash = SpatialHash(cell_size=spatial_hash_cell_size)
        self.use_spatial_hash = use_spatial_hash

    def append(self, item: T):
        """
        Add a new sprite to the list.
        """
        self.sprite_list.append(item)
        item.register_sprite_list(self)
        self.vbo_dirty = True

    def recalculate_spatial_hash(self, item: T):
        if self.use_spatial_hash:
            self.spatial_hash.remove_object(item)
            self.spatial_hash.append_object(item)

    def remove(self, item: T):
        """
        Remove a specific sprite from the list.
        """
        self.sprite_list.remove(item)
        self.vbo_dirty = True
        if self.use_spatial_hash:
            self.spatial_hash.remove_object(item)

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
            sprite.center_y += change_y

    def draw(self, fast: bool = True):
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
            # self.sprite_list.sort()
            rects = _create_rects(self.sprite_list)
            _set_vbo(self.vertex_vbo_id, rects)
            vbo_list = []
            for sprite in self.sprite_list:
                vbo_list.extend([0, 0,
                                 sprite.repeat_count_x, 0,
                                 sprite.repeat_count_x, sprite.repeat_count_y,
                                 0, sprite.repeat_count_y])
            _set_vbo(self.texture_coord_vbo_id, vbo_list)
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


def get_closest_sprite(sprite1: Sprite, sprite_list: SpriteList) -> (Sprite, float):
    """
    Given a Sprite and SpriteList, returns the closest sprite, and its distance.
    """
    if len(sprite_list) == 0:
        return None

    min_pos = 0
    min_distance = get_distance_between_sprites(sprite1, sprite_list[min_pos])
    for i in range(1, len(sprite_list)):
        distance = get_distance_between_sprites(sprite1, sprite_list[i])
        if distance < min_distance:
            min_pos = i
            min_distance = distance
    return sprite_list[min_pos], min_distance
