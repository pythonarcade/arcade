"""
This module provides functionality to manage Sprites.

"""

from typing import Iterable
from typing import TypeVar
from typing import Generic
from typing import List

import ctypes

import pyglet.gl as gl

import math
import moderngl
import numpy as np

from PIL import Image

from arcade.sprite import Sprite
from arcade.sprite import get_distance_between_sprites

from arcade.draw_commands import rotate_point
from arcade.window_commands import get_opengl_context
from arcade.window_commands import get_projection

VERTEX_SHADER = """
#version 330
uniform mat4 Projection;
in vec2 in_vert;
in vec2 in_texture;
in vec3 in_pos;
in float in_angle;
in vec2 in_scale;
in vec4 in_sub_tex_coords;
out vec2 v_texture;
void main() {
    mat2 rotate = mat2(
                cos(in_angle), sin(in_angle),
                -sin(in_angle), cos(in_angle)
            );
    vec3 pos;
    pos = in_pos + vec3(rotate * (in_vert * in_scale), 0.);
    gl_Position = Projection * vec4(pos, 1.0);

    vec2 tex_offset = in_sub_tex_coords.xy;
    vec2 tex_size = in_sub_tex_coords.zw;

    v_texture = (in_texture * tex_size + tex_offset) * vec2(1, -1);
}
"""

FRAGMENT_SHADER = """
#version 330
uniform sampler2D Texture;
in vec2 v_texture;
out vec4 f_color;
void main() {
    vec4 basecolor = texture(Texture, v_texture);
    if (basecolor.a == 0.0){
        discard;
    }
    f_color = basecolor;
}
"""


class OpenGLBuffer:
    def __init__(self, type, data):
        self.type = type
        self.data = data
        self.id = gl.GLuint()
        gl.glGenBuffers(1, ctypes.pointer(self.id))
        self.data_ptr = (gl.GLfloat * len(data))(*data)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.id)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(self.data_ptr), self.data_ptr, gl.GL_STATIC_DRAW)

    def bind(self):
        pass

    def unbind(self):
        pass


class VertexBuffer(OpenGLBuffer):
    def __init__(self, data):
        super().__init__(gl.GL_VERTEX_ARRAY, data)

    def bind(self):
        gl.glEnableClientState(self.type)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.id)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, 0)


class ColorBuffer(OpenGLBuffer):
    def __init__(self, data):
        super().__init__(gl.GL_COLOR_ARRAY, data)

    def bind(self):
        gl.glEnableClientState(self.type)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.id)
        gl.glColorPointer(4, gl.GL_FLOAT, 0, 0)


class TextureCoordBuffer(OpenGLBuffer):
    def __init__(self, data):
        super().__init__(gl.GL_TEXTURE_COORD_ARRAY, data)

    def bind(self):
        gl.glEnableClientState(self.type)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.id)
        gl.glTexCoordPointer(2, gl.GL_FLOAT, 0, 0)


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


def _draw_rects(shape_list: List[Sprite], vertex_buffer: VertexBuffer,
                texture_coord_buffer: TextureCoordBuffer,
                color_buffer: ColorBuffer,
                change_x: float, change_y: float):
    """
    Draw a set of rectangles using vertex buffers. This is more efficient
    than drawing them individually.
    """

    if len(shape_list) == 0:
        return

    gl.glEnable(gl.GL_BLEND)
    gl.glEnable(gl.GL_TEXTURE_2D)  # As soon as this happens, can't use drawing commands
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glHint(gl.GL_POLYGON_SMOOTH_HINT, gl.GL_NICEST)
    gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)

    vertex_buffer.bind()
    color_buffer.bind()
    texture_coord_buffer.bind()

    gl.glLoadIdentity()
    gl.glTranslatef(change_x, change_y, 0)

    # Ideally, we want to draw these in "batches."
    # We seek to find groups of squares with the same texture. Then draw
    # them all at once.

    last_texture_id = None
    batch_count = 0
    offset = 0
    batch_offset = 0
    texture_coord_vbo_id = None

    for shape in shape_list:

        if shape.texture.texture_id != last_texture_id:
            # Ok, if the 'if' triggered above, we are now looking at a different
            # texture than we looked at with the last loop. So draw the last
            # "batch" of squares. We'll start a new batch with the current
            # square but not draw it yet
            if batch_count > 0:
                _render_rect_filled(batch_offset,
                                    last_texture_id,
                                    texture_coord_vbo_id,
                                    batch_count)

            batch_count = 0
            batch_offset = offset
            last_texture_id = shape.texture.texture_id

        batch_count += 4
        offset += 4

    # Draw the last batch, if it exists
    _render_rect_filled(batch_offset,
                        last_texture_id,
                        texture_coord_vbo_id,
                        batch_count)

    # Must do this, or drawing commands won't work.
    gl.glDisable(gl.GL_TEXTURE_2D)


class SpatialHash:
    """
    Structure for fast collision checking.

    See: https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/
    """

    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.contents = {}

    def _hash(self, point):
        return int(point[0] / self.cell_size), int(point[1] / self.cell_size)

    def insert_object_for_box(self, new_object: Sprite):
        """
        Insert a sprite.
        """
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
        """
        Remove a Sprite.
        """
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

    def get_objects_for_box(self, check_object: Sprite) -> List[Sprite]:
        """
        Returns colliding Sprites.
        """
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
        self.vertex_buffer = None
        self.texture_coord_buffer = None

        # List of texture coordinate buffers (map textures to coordinates)
        # that go with this list.
        # self.texture_coord_vbo_id = None
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
        if self.use_spatial_hash:
            self.spatial_hash.insert_object_for_box(item)

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
        """
        Moves all contained Sprites.
        """
        for sprite in self.sprite_list:
            sprite.center_x += change_x
            sprite.center_y += change_y

    def draw(self, fast: bool = True):
        """
        Call the draw() method on each sprite in the list.
        """
        # Run this if we are running 'fast' with vertex buffers
        # and we haven't yet created vertex buffers.
        if fast and self.vertex_buffer is None:
            self.vbo_dirty = True

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

            # Set up vertices
            rects = _create_rects(self.sprite_list)
            self.vertex_buffer = VertexBuffer(rects)

            # Set up coordinates for how the texture maps to the coordinates
            # (Which is the same for each quad, but whatever.)
            vbo_list = []
            for sprite in self.sprite_list:
                vbo_list.extend([0, 0,
                                 sprite.repeat_count_x, 0,
                                 sprite.repeat_count_x, sprite.repeat_count_y,
                                 0, sprite.repeat_count_y])
            self.texture_coord_buffer = TextureCoordBuffer(vbo_list)

            color_list = []
            # Loop for each sprite
            for sprite in self.sprite_list:
                # There are four corners for each sprite, so they all get a color
                for i in range(4):
                    color_list.extend([1.0, 1.0, 1.0, sprite.alpha])

            self.color_buffer = ColorBuffer(color_list)

            self.vbo_dirty = False
            self.change_x = 0
            self.change_y = 0

        # If we run fast, use vertex buffers. Otherwise do it the
        # super slow way.
        if fast:
            _draw_rects(self.sprite_list, self.vertex_buffer,
                        self.texture_coord_buffer,
                        self.color_buffer,
                        self.change_x, self.change_y)
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


class SpriteList2(Generic[T]):

    next_texture_id = 100

    def __init__(self, use_spatial_hash=True, spatial_hash_cell_size=128, is_static=False):
        """
        Initialize the sprite list
        """
        # List of sprites in the sprite list
        self.sprite_list = []

        # Used in drawing optimization via OpenGL
        self.program = None
        self.pos_angle_scale = None
        self.pos_angle_scale_buf = None
        self.texture_id = None
        self.vao = None

        # Used in collision detection optimization
        self.spatial_hash = SpatialHash(cell_size=spatial_hash_cell_size)
        self.use_spatial_hash = use_spatial_hash

    def append(self, item: T):
        """
        Add a new sprite to the list.
        """
        self.sprite_list.append(item)
        item.register_sprite_list(self)
        self.prog = None
        if self.use_spatial_hash:
            self.spatial_hash.insert_object_for_box(item)

    def recalculate_spatial_hash(self, item: T):
        if self.use_spatial_hash:
            self.spatial_hash.remove_object(item)
            self.spatial_hash.append_object(item)

    def remove(self, item: T):
        """
        Remove a specific sprite from the list.
        """
        self.sprite_list.remove(item)
        self.program = None
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
        """
        Moves all contained Sprites.
        """
        for sprite in self.sprite_list:
            sprite.center_x += change_x
            sprite.center_y += change_y

    def calculate_sprite_buffer(self):

        if len(self.sprite_list) == 0:
            return

        if self.program is None:
            self.program = get_opengl_context().program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

        # Loop through each sprite and grab its position, and the texture it will be using.
        array_of_positions = []
        array_of_texture_names = []
        array_of_images = []
        array_of_sizes = []

        for sprite in self.sprite_list:
            array_of_positions.append([sprite.center_x, sprite.center_y, 0])
            if sprite.texture_name not in array_of_texture_names:
                if sprite.image is not None:
                    array_of_texture_names.append(sprite.texture_name)
                    image = sprite.image
                else:
                    array_of_texture_names.append(sprite.texture_name)
                    image = Image.open(sprite.texture_name)
                array_of_images.append(image)
            size_h = sprite.height / 2
            size_w = sprite.width / 2
            array_of_sizes.append([size_w, size_h])

        # Get their sizes
        widths, heights = zip(*(i.size for i in array_of_images))

        # Figure out what size a composate would be
        total_width = sum(widths)
        max_height = max(heights)

        # Make the composite image
        new_image = Image.new('RGBA', (total_width, max_height))

        x_offset = 0
        for image in array_of_images:
            new_image.paste(image, (x_offset, 0))
            x_offset += image.size[0]

        # Create a texture out the composite image
        self.texture = get_opengl_context().texture((new_image.width, new_image.height), 4, np.asarray(new_image))
        if self.texture_id is None:
            self.texture_id = SpriteList2.next_texture_id
            SpriteList2.next_texture_id += 1

        self.texture.use(self.texture_id)

        # Create a list with the coordinates of all the unique textures
        tex_coords = []
        start_x = 0.0
        for image in array_of_images:
            end_x = start_x + (image.width / total_width)
            normalized_width = image.width / total_width
            normalized_height = image.height / max_height
            tex_coords.append([start_x, 0.0, normalized_width, normalized_height])
            start_x = end_x

        # Go through each sprite and pull from the coordinate list, the proper
        # coordinates for that sprite's image.
        array_of_sub_tex_coords = []
        for sprite in self.sprite_list:
            index = array_of_texture_names.index(sprite.texture_name)
            array_of_sub_tex_coords.append(tex_coords[index])

        # Create numpy array with info on location and such
        np_array_positions = np.array(array_of_positions).astype('f4')

        # np_array_angles = (np.random.rand(INSTANCES, 1) * 2 * np.pi).astype('f4')
        np_array_angles = np.tile(np.array(0, dtype=np.float32), (len(self.sprite_list), 1))
        np_array_sizes = np.array(array_of_sizes).astype('f4')
        np_sub_tex_coords = np.array(array_of_sub_tex_coords).astype('f4')
        self.pos_angle_scale = np.hstack((np_array_positions, np_array_angles, np_array_sizes, np_sub_tex_coords))
        self.pos_angle_scale_buf = get_opengl_context().buffer(self.pos_angle_scale.tobytes())

        vertices = np.array([
            #  x,    y,   u,   v
            -1.0, -1.0, 0.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
        ], dtype=np.float32
        )
        vbo_buf = get_opengl_context().buffer(vertices.tobytes())

        vao_content = [
            (vbo_buf, '2f 2f', 'in_vert', 'in_texture'),
            (self.pos_angle_scale_buf, '3f 1f 2f 4f/i', 'in_pos', 'in_angle', 'in_scale', 'in_sub_tex_coords')
        ]

        self.vao = get_opengl_context().vertex_array(self.program, vao_content)

        self.update_positions()

    def update_positions(self):

        if self.program is None:
            return

        for i, sprite in enumerate(self.sprite_list):
            self.pos_angle_scale[i, 0] = sprite.center_x
            self.pos_angle_scale[i, 1] = sprite.center_y
            self.pos_angle_scale[i, 3] = math.radians(sprite.angle)
            self.pos_angle_scale[i, 4] = sprite.width / 2
            self.pos_angle_scale[i, 5] = sprite.height / 2

    def update_position(self, sprite):

        if self.program is None:
            return

        i = self.sprite_list.index(sprite)

        self.pos_angle_scale[i, 0] = sprite.center_x
        self.pos_angle_scale[i, 1] = sprite.center_y
        self.pos_angle_scale[i, 3] = math.radians(sprite.angle)
        self.pos_angle_scale[i, 4] = sprite.width / 2
        self.pos_angle_scale[i, 5] = sprite.height / 2

    def draw(self):

        if len(self.sprite_list) == 0:
            return

        if self.program is None:
            self.calculate_sprite_buffer()

        self.texture.use(self.texture_id)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        self.program['Texture'].value = self.texture_id
        self.program['Projection'].write(get_projection().tobytes())
        self.pos_angle_scale_buf.write(self.pos_angle_scale.tobytes())
        self.vao.render(moderngl.TRIANGLE_STRIP, instances=len(self.sprite_list))
        self.pos_angle_scale_buf.orphan()

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
        self.program = None
        return self.sprite_list.pop()


SpriteList = SpriteList2

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
