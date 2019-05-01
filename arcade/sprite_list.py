"""
This module provides functionality to manage Sprites in a list.

"""

from typing import Iterable
from typing import TypeVar
from typing import Generic
from typing import List

import pyglet.gl as gl

import math
import numpy as np

from PIL import Image

from arcade.sprite import Sprite
from arcade.sprite import get_distance_between_sprites

from arcade.draw_commands import rotate_point
from arcade.window_commands import get_projection
from arcade import shader

VERTEX_SHADER = """
#version 330
uniform mat4 Projection;

// per vertex
in vec2 in_vert;
in vec2 in_texture;

// per instance
in vec2 in_pos;
in float in_angle;
in vec2 in_scale;
in vec4 in_sub_tex_coords;
in vec4 in_color;

out vec2 v_texture;
out vec4 v_color;

void main() {
    mat2 rotate = mat2(
                cos(in_angle), sin(in_angle),
                -sin(in_angle), cos(in_angle)
            );
    vec2 pos;
    pos = in_pos + vec2(rotate * (in_vert * in_scale));
    gl_Position = Projection * vec4(pos, 0.0, 1.0);

    vec2 tex_offset = in_sub_tex_coords.xy;
    vec2 tex_size = in_sub_tex_coords.zw;

    v_texture = (in_texture * tex_size + tex_offset) * vec2(1, -1);
    v_color = in_color;
}
"""

FRAGMENT_SHADER = """
#version 330
uniform sampler2D Texture;

in vec2 v_texture;
in vec4 v_color;

out vec4 f_color;

void main() {
    vec4 basecolor = texture(Texture, v_texture);
    basecolor = basecolor * v_color;
    if (basecolor.a == 0.0){
        discard;
    }
    f_color = basecolor;
}
"""


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


class _SpatialHash:
    """
    Structure for fast collision checking.

    See: https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/
    """

    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.contents = {}

    def _hash(self, point):
        return int(point[0] / self.cell_size), int(point[1] / self.cell_size)

    def reset(self):
        self.contents = {}

    def insert_object_for_box(self, new_object: Sprite):
        """
        Insert a sprite.
        """
        # Get the corners
        min_x = new_object.left
        max_x = new_object.right
        min_y = new_object.bottom
        max_y = new_object.top

        # print(f"New - Center: ({new_object.center_x}, {new_object.center_y}), Angle: {new_object.angle}, "
        #       f"Left: {new_object.left}, Right {new_object.right}")

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # print(f"Add 1: {min_point} {max_point}")

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        # print(f"Add 2: {min_point} {max_point}")
        # print("Add: ", min_point, max_point)

        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # append to each intersecting cell
                bucket = self.contents.setdefault((i, j), [])
                if new_object in bucket:
                    # print(f"Error, {new_object.guid} already in ({i}, {j}) bucket. ")
                    pass
                else:
                    bucket.append(new_object)
                    # print(f"Adding {new_object.guid} to ({i}, {j}) bucket. "
                    #       f"{new_object._position} {min_point} {max_point}")

    def remove_object(self, sprite_to_delete: Sprite):
        """
        Remove a Sprite.

        :param Sprite sprite_to_delete: Pointer to sprite to be removed.
        """
        # Get the corners
        min_x = sprite_to_delete.left
        max_x = sprite_to_delete.right
        min_y = sprite_to_delete.bottom
        max_y = sprite_to_delete.top

        # print(f"Del - Center: ({sprite_to_delete.center_x}, {sprite_to_delete.center_y}), "
        #       f"Angle: {sprite_to_delete.angle}, Left: {sprite_to_delete.left}, Right {sprite_to_delete.right}")

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # print(f"Remove 1: {min_point} {max_point}")

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        # print(f"Remove 2: {min_point} {max_point}")
        # print("Remove: ", min_point, max_point)

        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = self.contents.setdefault((i, j), [])
                try:
                    bucket.remove(sprite_to_delete)
                    # print(f"Removing {sprite_to_delete.guid} from ({i}, {j}) bucket. {sprite_to_delete._position} "
                    #       f"{min_point} {max_point}")

                except ValueError:
                    print(f"Warning, tried to remove item {sprite_to_delete.guid} from spatial hash {i} {j} when "
                          f"it wasn't there. {min_point} {max_point}")

    def get_objects_for_box(self, check_object: Sprite) -> List[Sprite]:
        """
        Returns colliding Sprites.

        :param Sprite check_object: Sprite we are checking to see if there are
            other sprites in the same box(es)

        :return: List of close-by sprites
        :rtype: List


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
                # print(f"Checking {i}, {j}")
                # append to each intersecting cell
                new_items = self.contents.setdefault((i, j), [])
                # for item in new_items:
                #     print(f"Found {item.guid} in {i}, {j}")
                close_by_sprites.extend(new_items)

        return close_by_sprites


T = TypeVar('T', bound=Sprite)


class SpriteList(Generic[T]):

    next_texture_id = 0

    def __init__(self, use_spatial_hash=False, spatial_hash_cell_size=128, is_static=False):
        """
        Initialize the sprite list

        :param bool use_spatial_hash: If set to True, this will make moving a sprite
               in the SpriteList slower, but it will speed up collision detection
               with items in the SpriteList. Great for doing collision detection
               with walls/platforms.
        :param int spatial_hash_cell_size:
        :param bool is_static: Speeds drawing if this list won't change.
        """
        # List of sprites in the sprite list
        self.sprite_list = []
        self.sprite_idx = dict()

        # Used in drawing optimization via OpenGL
        self.program = None

        self.sprite_data = None
        self.sprite_data_buf = None
        self.texture_id = None
        self._texture = None
        self.vao = None
        self.vbo_buf = None

        self.array_of_texture_names = []
        self.array_of_images = []

        # Used in collision detection optimization
        self.is_static = is_static
        self.use_spatial_hash = use_spatial_hash
        if use_spatial_hash:
            self.spatial_hash = _SpatialHash(cell_size=spatial_hash_cell_size)
        else:
            self.spatial_hash = None

    def append(self, item: T):
        """
        Add a new sprite to the list.

        :param Sprite item: Sprite to add to the list.
        """
        idx = len(self.sprite_list)
        self.sprite_list.append(item)
        self.sprite_idx[item] = idx
        item.register_sprite_list(self)
        self.vao = None
        if self.use_spatial_hash:
            self.spatial_hash.insert_object_for_box(item)

    def _recalculate_spatial_hash(self, item: T):
        """ Recalculate the spatial hash for a particular item. """
        if self.use_spatial_hash:
            self.spatial_hash.remove_object(item)
            self.spatial_hash.insert_object_for_box(item)

    def _recalculate_spatial_hashes(self):
        if self.use_spatial_hash:
            self.spatial_hash.reset()
            for sprite in self.sprite_list:
                self.spatial_hash.insert_object_for_box(sprite)

    def remove(self, item: T):
        """
        Remove a specific sprite from the list.
        :param Sprite item: Item to remove from the list
        """
        self.sprite_list.remove(item)

        # Rebuild index list
        self.sprite_idx[item] = dict()
        for idx, sprite in enumerate(self.sprite_list):
            self.sprite_idx[sprite] = idx

        self.vao = None
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
        Moves all Sprites in the list by the same amount.

        :param float change_x: Amount to change all x values by
        :param float change_y: Amount to change all y values by
        """
        for sprite in self.sprite_list:
            sprite.center_x += change_x
            sprite.center_y += change_y

    def preload_textures(self, texture_names):
        """
        Preload a set of textures that will be used for sprites in this
        sprite list.

        :param array texture_names: List of file names to load in as textures.
        """
        self.array_of_texture_names.extend(texture_names)
        self.array_of_images = None

    def _calculate_sprite_buffer(self):

        if len(self.sprite_list) == 0:
            return

        # Loop through each sprite and grab its position, and the texture it will be using.
        array_of_positions = []
        array_of_sizes = []
        array_of_colors = []
        array_of_angles = []

        for sprite in self.sprite_list:
            array_of_positions.append([sprite.center_x, sprite.center_y])
            array_of_angles.append(math.radians(sprite.angle))
            size_h = sprite.height / 2
            size_w = sprite.width / 2
            array_of_sizes.append([size_w, size_h])
            array_of_colors.append(sprite.color + (sprite.alpha, ))

        new_array_of_texture_names = []
        new_array_of_images = []
        new_texture = False
        if self.array_of_images is None:
            new_texture = True

        # print()
        # print("New texture start: ", new_texture)

        for sprite in self.sprite_list:

            if sprite._texture is None:
                raise Exception("Error: Attempt to draw a sprite without a texture set.")

            name_of_texture_to_check = sprite._texture.name
            if name_of_texture_to_check not in self.array_of_texture_names:
                new_texture = True
                # print("New because of ", name_of_texture_to_check)

            if name_of_texture_to_check not in new_array_of_texture_names:
                new_array_of_texture_names.append(name_of_texture_to_check)
                image = sprite._texture.image
                new_array_of_images.append(image)

        # print("New texture end: ", new_texture)
        # print(new_array_of_texture_names)
        # print(self.array_of_texture_names)
        # print()

        if new_texture:
            # Add back in any old textures. Chances are we'll need them.
            for index, old_texture_name in enumerate(self.array_of_texture_names):
                if old_texture_name not in new_array_of_texture_names and self.array_of_images is not None:
                    new_array_of_texture_names.append(old_texture_name)
                    image = self.array_of_images[index]
                    new_array_of_images.append(image)

            self.array_of_texture_names = new_array_of_texture_names

            self.array_of_images = new_array_of_images
            # print(f"New Texture Atlas with names {self.array_of_texture_names}")

        # Get their sizes
        widths, heights = zip(*(i.size for i in self.array_of_images))

        # Figure out what size a composite would be
        total_width = sum(widths)
        max_height = max(heights)

        if new_texture:

            # TODO: This code isn't valid, but I think some releasing might be in order.
            # if self.texture is not None:
            #     shader.Texture.release(self.texture_id)

            # Make the composite image
            new_image = Image.new('RGBA', (total_width, max_height))

            x_offset = 0
            for image in self.array_of_images:
                new_image.paste(image, (x_offset, 0))
                x_offset += image.size[0]

            # Create a texture out the composite image
            self._texture = shader.texture(
                 (new_image.width, new_image.height),
                 4,
                 np.asarray(new_image)
            )

            if self.texture_id is None:
                self.texture_id = SpriteList.next_texture_id

        # Create a list with the coordinates of all the unique textures
        tex_coords = []
        start_x = 0.0
        for image in self.array_of_images:
            end_x = start_x + (image.width / total_width)
            normalized_width = image.width / total_width
            start_height = 1 - (image.height / max_height)
            normalized_height = image.height / max_height
            tex_coords.append([start_x, start_height, normalized_width, normalized_height])
            start_x = end_x

        # Go through each sprite and pull from the coordinate list, the proper
        # coordinates for that sprite's image.
        array_of_sub_tex_coords = []
        for sprite in self.sprite_list:
            index = self.array_of_texture_names.index(sprite._texture.name)
            array_of_sub_tex_coords.append(tex_coords[index])

        # Create numpy array with info on location and such
        buffer_type = np.dtype([('position', '2f4'), ('angle', 'f4'), ('size', '2f4'),
                                ('sub_tex_coords', '4f4'), ('color', '4B')])
        self.sprite_data = np.zeros(len(self.sprite_list), dtype=buffer_type)
        self.sprite_data['position'] = array_of_positions
        self.sprite_data['angle'] = array_of_angles
        self.sprite_data['size'] = array_of_sizes
        self.sprite_data['sub_tex_coords'] = array_of_sub_tex_coords
        self.sprite_data['color'] = array_of_colors

        if self.is_static:
            usage = 'static'
        else:
            usage = 'stream'

        self.sprite_data_buf = shader.buffer(
            self.sprite_data.tobytes(),
            usage=usage
        )

        vertices = np.array([
            #  x,    y,   u,   v
            -1.0, -1.0, 0.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
        ], dtype=np.float32
        )
        self.vbo_buf = shader.buffer(vertices.tobytes())
        vbo_buf_desc = shader.BufferDescription(
            self.vbo_buf,
            '2f 2f',
            ('in_vert', 'in_texture')
        )
        pos_angle_scale_buf_desc = shader.BufferDescription(
            self.sprite_data_buf,
            '2f 1f 2f 4f 4B',
            ('in_pos', 'in_angle', 'in_scale', 'in_sub_tex_coords', 'in_color'),
            normalized=['in_color'], instanced=True)

        vao_content = [vbo_buf_desc, pos_angle_scale_buf_desc]

        # Can add buffer to index vertices
        self.vao = shader.vertex_array(self.program, vao_content)

    def _update_positions(self):
        """ Called by the Sprite class to update position, angle, size and color
        of all sprites in the list.
        Necessary for batch drawing of items. """

        if self.vao is None:
            return

        for i, sprite in enumerate(self.sprite_list):
            self.sprite_data[i]['position'] = [sprite.center_x, sprite.center_y]
            self.sprite_data[i]['angle'] = math.radians(sprite.angle)
            self.sprite_data[i]['size'] = [sprite.width / 2, sprite.height / 2]
            self.sprite_data[i]['color'] = sprite.color + (sprite.alpha, )

    def update_texture(self, sprite):
        """ Make sure we update the texture for this sprite for the next batch
        drawing"""
        if self.vao is None:
            return

        self._calculate_sprite_buffer()

    def update_position(self, sprite: Sprite):
        """
        Called by the Sprite class to update position, angle, size and color
        of the specified sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self.vao is None:
            return

        i = self.sprite_idx[sprite]

        self.sprite_data[i]['position'] = [sprite.center_x, sprite.center_y]
        self.sprite_data[i]['angle'] = math.radians(sprite.angle)
        self.sprite_data[i]['size'] = [sprite.width / 2, sprite.height / 2]
        self.sprite_data[i]['color'] = sprite.color + (sprite.alpha, )

    def update_location(self, sprite: Sprite):
        """
        Called by the Sprite class to update the location in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self.vao is None:
            return

        i = self.sprite_idx[sprite]

        self.sprite_data[i]['position'] = sprite.position

    def update_angle(self, sprite: Sprite):
        """
        Called by the Sprite class to update the angle in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self.vao is None:
            return

        i = self.sprite_idx[sprite]
        self.sprite_data[i]['angle'] = math.radians(sprite.angle)

    def draw(self):
        """ Draw this list of sprites. """
        if self.program is None:
            # Used in drawing optimization via OpenGL
            self.program = shader.program(
                vertex_shader=VERTEX_SHADER,
                fragment_shader=FRAGMENT_SHADER
            )

        if len(self.sprite_list) == 0:
            return

        if self.vao is None:
            self._calculate_sprite_buffer()

        self._texture.use(0)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        with self.vao:
            self.program['Texture'] = self.texture_id
            self.program['Projection'] = get_projection().flatten()

            if not self.is_static:
                self.sprite_data_buf.write(self.sprite_data.tobytes())

            self.vao.render(gl.GL_TRIANGLE_STRIP, instances=len(self.sprite_list))

            if not self.is_static:
                self.sprite_data_buf.orphan()

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


def get_closest_sprite(sprite: Sprite, sprite_list: SpriteList) -> (Sprite, float):
    """
    Given a Sprite and SpriteList, returns the closest sprite, and its distance.

    :param Sprite sprite: Target sprite
    :param SpriteList sprite_list: List to search for closest sprite.

    :return: Closest sprite.
    :rtype: Sprite
    """
    if len(sprite_list) == 0:
        return None

    min_pos = 0
    min_distance = get_distance_between_sprites(sprite, sprite_list[min_pos])
    for i in range(1, len(sprite_list)):
        distance = get_distance_between_sprites(sprite, sprite_list[i])
        if distance < min_distance:
            min_pos = i
            min_distance = distance
    return sprite_list[min_pos], min_distance
