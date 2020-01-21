"""
This module provides functionality to manage Sprites in a list.

"""

from typing import Iterable
from typing import Any
from typing import TypeVar
from typing import Generic
from typing import List
from typing import Tuple
from typing import Optional

import pyglet.gl as gl

import math
import array

from PIL import Image

from arcade import Sprite
from arcade import get_distance_between_sprites
from arcade import are_polygons_intersecting
from arcade import is_point_in_polygon

from arcade import rotate_point
from arcade import get_projection
from arcade import shader
from arcade import Point

_VERTEX_SHADER = """
#version 330
uniform mat4 Projection;

// per vertex
in vec2 in_vert;
in vec2 in_texture;

// per instance
in vec2 in_pos;
in float in_angle;
in vec2 in_size;
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
    pos = in_pos + vec2(rotate * (in_vert * (in_size / 2)));
    gl_Position = Projection * vec4(pos, 0.0, 1.0);

    vec2 tex_offset = in_sub_tex_coords.xy;
    vec2 tex_size = in_sub_tex_coords.zw;

    v_texture = (in_texture * tex_size + tex_offset) * vec2(1, -1);
    v_color = in_color;
}
"""

_FRAGMENT_SHADER = """
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

        close_by_sprites: List[Sprite] = []
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

    def get_objects_for_point(self, check_point: Point) -> List[Sprite]:
        """
        Returns Sprites at or close to a point.

        :param Point check_point: Point we are checking to see if there are
            other sprites in the same box(es)

        :return: List of close-by sprites
        :rtype: List


        """

        hash_point = self._hash(check_point)

        close_by_sprites: List[Sprite] = []
        new_items = self.contents.setdefault(hash_point, [])
        close_by_sprites.extend(new_items)

        return close_by_sprites


_SpriteType = TypeVar('_SpriteType', bound=Sprite)


class SpriteList(Generic[_SpriteType]):

    array_of_images: Optional[List[Any]]
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

        self._sprite_pos_data = None
        self._sprite_pos_buf = None
        self._sprite_pos_desc = None
        self._sprite_pos_changed = False

        self._sprite_size_data = None
        self._sprite_size_buf = None
        self._sprite_size_desc = None
        self._sprite_size_changed = False

        self._sprite_angle_data = None
        self._sprite_angle_buf = None
        self._sprite_angle_desc = None
        self._sprite_angle_changed = False

        self._sprite_color_data = None
        self._sprite_color_buf = None
        self._sprite_color_desc = None
        self._sprite_color_changed = False

        self._sprite_sub_tex_data = None
        self._sprite_sub_tex_buf = None
        self._sprite_sub_tex_desc = None
        self._sprite_sub_tex_changed = False

        self.texture_id = None
        self._texture = None
        self._vao1 = None
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

    def append(self, item: _SpriteType):
        """
        Add a new sprite to the list.

        :param Sprite item: Sprite to add to the list.
        """
        idx = len(self.sprite_list)
        self.sprite_list.append(item)
        self.sprite_idx[item] = idx
        item.register_sprite_list(self)
        self._vao1 = None
        if self.use_spatial_hash:
            self.spatial_hash.insert_object_for_box(item)

    def _recalculate_spatial_hash(self, item: _SpriteType):
        """ Recalculate the spatial hash for a particular item. """
        if self.use_spatial_hash:
            self.spatial_hash.remove_object(item)
            self.spatial_hash.insert_object_for_box(item)

    def _recalculate_spatial_hashes(self):
        if self.use_spatial_hash:
            self.spatial_hash.reset()
            for sprite in self.sprite_list:
                self.spatial_hash.insert_object_for_box(sprite)

    def remove(self, item: _SpriteType):
        """
        Remove a specific sprite from the list.
        :param Sprite item: Item to remove from the list
        """
        self.sprite_list.remove(item)

        # Rebuild index list
        self.sprite_idx[item] = dict()
        for idx, sprite in enumerate(self.sprite_list):
            self.sprite_idx[sprite] = idx

        self._vao1 = None
        if self.use_spatial_hash:
            self.spatial_hash.remove_object(item)

    def update(self):
        """
        Call the update() method on each sprite in the list.
        """
        for sprite in self.sprite_list:
            sprite.update()

    def on_update(self, delta_time: float = 1/60):
        """
        Update the sprite. Similar to update, but also takes a delta-time.
        """
        for sprite in self.sprite_list:
            sprite.on_update(delta_time)

    def update_animation(self, delta_time: float = 1/60):
        for sprite in self.sprite_list:
            sprite.update_animation(delta_time)

    def _get_center(self) -> Tuple[float, float]:
        """ Get the mean center coordinates of all sprites in the list. """
        x = sum((sprite.center_x for sprite in self.sprite_list)) / len(self.sprite_list)
        y = sum((sprite.center_y for sprite in self.sprite_list)) / len(self.sprite_list)
        return x, y

    center = property(_get_center)

    def rescale(self, factor: float) -> None:
        """ Rescale all sprites in the list relative to the spritelists center. """
        for sprite in self.sprite_list:
            sprite.rescale_relative_to_point(self.center, factor)

    def move(self, change_x: float, change_y: float):
        """
        Moves all Sprites in the list by the same amount.

        :param float change_x: Amount to change all x values by
        :param float change_y: Amount to change all y values by
        """
        for sprite in self.sprite_list:
            sprite.center_x += change_x
            sprite.center_y += change_y

    def preload_textures(self, texture_names: List):
        """
        Preload a set of textures that will be used for sprites in this
        sprite list.

        :param array texture_names: List of file names to load in as textures.
        """
        self.array_of_texture_names.extend(texture_names)
        self.array_of_images = None

    def _calculate_sprite_buffer(self):

        if self.is_static:
            usage = 'static'
        else:
            usage = 'stream'

        def calculate_pos_buffer():
            self._sprite_pos_data = array.array('f')
            # print("A")
            for sprite in self.sprite_list:
                self._sprite_pos_data.append(sprite.center_x)
                self._sprite_pos_data.append(sprite.center_y)

            self._sprite_pos_buf = shader.buffer(
                self._sprite_pos_data.tobytes(),
                usage=usage
            )
            variables = ['in_pos']
            self._sprite_pos_desc = shader.BufferDescription(
                self._sprite_pos_buf,
                '2f',
                variables,
                instanced=True)
            self._sprite_pos_changed = False

        def calculate_size_buffer():
            self._sprite_size_data = array.array('f')
            for sprite in self.sprite_list:
                self._sprite_size_data.append(sprite.width)
                self._sprite_size_data.append(sprite.height)

            self._sprite_size_buf = shader.buffer(
                self._sprite_size_data.tobytes(),
                usage=usage
            )
            variables = ['in_size']
            self._sprite_size_desc = shader.BufferDescription(
                self._sprite_size_buf,
                '2f',
                variables,
                instanced=True)
            self._sprite_size_changed = False

        def calculate_angle_buffer():
            self._sprite_angle_data = array.array('f')
            for sprite in self.sprite_list:
                self._sprite_angle_data.append(math.radians(sprite.angle))

            self._sprite_angle_buf = shader.buffer(
                self._sprite_angle_data.tobytes(),
                usage=usage
            )
            variables = ['in_angle']
            self._sprite_angle_desc = shader.BufferDescription(
                self._sprite_angle_buf,
                '1f',
                variables,
                instanced=True)
            self._sprite_angle_changed = False

        def calculate_colors():
            self._sprite_color_data = array.array('B')
            for sprite in self.sprite_list:
                self._sprite_color_data.append(int(sprite.color[0]))
                self._sprite_color_data.append(int(sprite.color[1]))
                self._sprite_color_data.append(int(sprite.color[2]))
                self._sprite_color_data.append(int(sprite.alpha))

            self._sprite_color_buf = shader.buffer(
                self._sprite_color_data.tobytes(),
                usage=usage
            )
            variables = ['in_color']
            self._sprite_color_desc = shader.BufferDescription(
                self._sprite_color_buf,
                '4B',
                variables,
                normalized=['in_color'], instanced=True)
            self._sprite_color_changed = False

        def calculate_sub_tex_coords():

            new_array_of_texture_names = []
            new_array_of_images = []
            new_texture = False
            if self.array_of_images is None:
                new_texture = True

            # print()
            # print("New texture start: ", new_texture)

            for sprite in self.sprite_list:

                # noinspection PyProtectedMember
                if sprite.texture is None:
                    raise Exception("Error: Attempt to draw a sprite without a texture set.")

                name_of_texture_to_check = sprite.texture.name
                if name_of_texture_to_check not in self.array_of_texture_names:
                    new_texture = True
                    # print("New because of ", name_of_texture_to_check)

                if name_of_texture_to_check not in new_array_of_texture_names:
                    new_array_of_texture_names.append(name_of_texture_to_check)
                    image = sprite.texture.image
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
                texture_bytes = new_image.tobytes()
                self._texture = shader.texture(
                     (new_image.width, new_image.height),
                     4,
                     texture_bytes
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
            array_of_sub_tex_coords = array.array('f')
            for sprite in self.sprite_list:
                index = self.array_of_texture_names.index(sprite.texture.name)
                for coord in tex_coords[index]:
                    array_of_sub_tex_coords.append(coord)

            self._sprite_sub_tex_buf = shader.buffer(
                array_of_sub_tex_coords.tobytes(),
                usage=usage
            )

            self._sprite_sub_tex_desc = shader.BufferDescription(
                self._sprite_sub_tex_buf,
                '4f',
                ['in_sub_tex_coords'],
                instanced=True)
            self._sprite_sub_tex_changed = False

        if len(self.sprite_list) == 0:
            return

        calculate_pos_buffer()
        calculate_size_buffer()
        calculate_angle_buffer()
        calculate_sub_tex_coords()
        calculate_colors()

        vertices = array.array('f', [
            #  x,    y,   u,   v
            -1.0, -1.0, 0.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
        ]
        )
        self.vbo_buf = shader.buffer(vertices.tobytes())
        vbo_buf_desc = shader.BufferDescription(
            self.vbo_buf,
            '2f 2f',
            ('in_vert', 'in_texture')
        )

        # Can add buffer to index vertices
        vao_content = [vbo_buf_desc,
                       self._sprite_pos_desc,
                       self._sprite_size_desc,
                       self._sprite_angle_desc,
                       self._sprite_sub_tex_desc,
                       self._sprite_color_desc]
        self._vao1 = shader.vertex_array(self.program, vao_content)

    def dump(self):
        buffer = self._sprite_pos_data.tobytes()
        record_size = len(buffer) / len(self.sprite_list)
        for i, char in enumerate(buffer):
            if i % record_size == 0:
                print()
            print(f"{char:02x} ", end="")

    def _update_positions(self):
        """ Called by the Sprite class to update position, angle, size and color
        of all sprites in the list.
        Necessary for batch drawing of items. """

        if self._vao1 is None:
            return

        for i, sprite in enumerate(self.sprite_list):
            self._sprite_pos_data[i * 2] = sprite.position[0]
            self._sprite_pos_data[i * 2 + 1] = sprite.position[1]
            self._sprite_pos_changed = True

            self._sprite_angle_data[i] = math.radians(sprite.angle)
            self._sprite_angle_changed = True

            self._sprite_color_data[i * 4] = sprite.color[0]
            self._sprite_color_data[i * 4 + 1] = sprite.color[1]
            self._sprite_color_data[i * 4 + 2] = sprite.color[2]
            self._sprite_color_data[i * 4 + 3] = sprite.alpha
            self._sprite_color_changed = True

            self._sprite_size_data[i * 2] = sprite.width
            self._sprite_size_data[i * 2 + 1] = sprite.height
            self._sprite_size_changed = True

    def update_texture(self, _sprite):
        """ Make sure we update the texture for this sprite for the next batch
        drawing"""
        if self._vao1 is None:
            return

        self._calculate_sprite_buffer()

    def update_position(self, sprite: Sprite):
        """
        Called by the Sprite class to update position, angle, size and color
        of the specified sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self._vao1 is None:
            return

        i = self.sprite_idx[sprite]

        self._sprite_pos_data[i * 2] = sprite.position[0]
        self._sprite_pos_data[i * 2 + 1] = sprite.position[1]
        self._sprite_pos_changed = True

        self._sprite_angle_data[i] = math.radians(sprite.angle)
        self._sprite_angle_changed = True

        self._sprite_color_data[i * 4] = int(sprite.color[0])
        self._sprite_color_data[i * 4 + 1] = int(sprite.color[1])
        self._sprite_color_data[i * 4 + 2] = int(sprite.color[2])
        self._sprite_color_data[i * 4 + 3] = int(sprite.alpha)
        self._sprite_color_changed = True

    def update_color(self, sprite: Sprite):
        """
        Called by the Sprite class to update position, angle, size and color
        of the specified sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self._vao1 is None:
            return

        i = self.sprite_idx[sprite]

        self._sprite_color_data[i * 4] = int(sprite.color[0])
        self._sprite_color_data[i * 4 + 1] = int(sprite.color[1])
        self._sprite_color_data[i * 4 + 2] = int(sprite.color[2])
        self._sprite_color_data[i * 4 + 3] = int(sprite.alpha)
        self._sprite_color_changed = True

    def update_size(self, sprite: Sprite):
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self._vao1 is None:
            return

        i = self.sprite_idx[sprite]

        self._sprite_size_data[i * 2] = sprite.width
        self._sprite_size_data[i * 2 + 1] = sprite.height
        self._sprite_size_changed = True

    def update_height(self, sprite: Sprite):
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self._vao1 is None:
            return

        i = self.sprite_idx[sprite]

        self._sprite_size_data[i * 2 + 1] = sprite.height
        self._sprite_size_changed = True

    def update_width(self, sprite: Sprite):
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self._vao1 is None:
            return

        i = self.sprite_idx[sprite]

        self._sprite_size_data[i * 2] = sprite.width
        self._sprite_size_changed = True

    def update_location(self, sprite: Sprite):
        """
        Called by the Sprite class to update the location in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self._vao1 is None:
            return

        i = self.sprite_idx[sprite]

        self._sprite_pos_data[i * 2] = sprite.position[0]
        self._sprite_pos_data[i * 2 + 1] = sprite.position[1]
        self._sprite_pos_changed = True

    def update_angle(self, sprite: Sprite):
        """
        Called by the Sprite class to update the angle in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self._vao1 is None:
            return

        i = self.sprite_idx[sprite]
        self._sprite_angle_data[i] = math.radians(sprite.angle)
        self._sprite_angle_changed = True

    def draw(self, **kwargs):
        """
        Draw this list of sprites.

        :param filter: Optional parameter to set OpenGL filter, such as
                       `gl.GL_NEAREST` to avoid smoothing.
        """
        if self.program is None:
            # Used in drawing optimization via OpenGL
            self.program = shader.program(
                vertex_shader=_VERTEX_SHADER,
                fragment_shader=_FRAGMENT_SHADER
            )

        if len(self.sprite_list) == 0:
            return

        if self._vao1 is None:
            self._calculate_sprite_buffer()

        self._texture.use(0)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        if "filter" in kwargs:
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, kwargs["filter"])
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, kwargs["filter"])
        # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        # gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        with self._vao1:
            self.program['Texture'] = self.texture_id
            self.program['Projection'] = get_projection().flatten()

            if not self.is_static:
                if self._sprite_pos_changed:
                    self._sprite_pos_buf.orphan()
                    self._sprite_pos_buf.write(self._sprite_pos_data.tobytes())
                    self._sprite_pos_changed = False

                if self._sprite_size_changed:
                    self._sprite_size_buf.orphan()
                    self._sprite_size_buf.write(self._sprite_size_data.tobytes())
                    self._sprite_size_changed = False

                if self._sprite_angle_changed:
                    self._sprite_angle_buf.orphan()
                    self._sprite_angle_buf.write(self._sprite_angle_data.tobytes())
                    self._sprite_angle_changed = False

                if self._sprite_color_changed:
                    self._sprite_color_buf.orphan()
                    self._sprite_color_buf.write(self._sprite_color_data.tobytes())
                    self._sprite_color_changed = False

                if self._sprite_sub_tex_changed:
                    self._sprite_sub_tex_buf.orphan()
                    self._sprite_sub_tex_buf.write(self._sprite_sub_tex_data.tobytes())
                    self._sprite_sub_tex_changed = False

            self._vao1.render(gl.GL_TRIANGLE_STRIP, instances=len(self.sprite_list))

    def __len__(self) -> int:
        """ Return the length of the sprite list. """
        return len(self.sprite_list)

    def __iter__(self) -> Iterable[_SpriteType]:
        """ Return an iterable object of sprites. """
        return iter(self.sprite_list)

    def __getitem__(self, i):
        return self.sprite_list[i]

    def pop(self) -> Sprite:
        """
        Pop off the last sprite in the list.
        """
        if len(self.sprite_list) == 0:
            raise(ValueError("pop from empty list"))

        sprite = self.sprite_list[-1]
        self.remove(sprite)
        return sprite


def get_closest_sprite(sprite: Sprite, sprite_list: SpriteList) -> Optional[Tuple[Sprite, float]]:
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


def check_for_collision(sprite1: Sprite, sprite2: Sprite) -> bool:
    """
    Check for a collision between two sprites.

    :param sprite1: First sprite
    :param sprite2: Second sprite

    :Returns: True or False depending if the sprites intersect.
    """
    if not isinstance(sprite1, Sprite):
        raise TypeError("Parameter 1 is not an instance of the Sprite class.")
    if isinstance(sprite2, SpriteList):
        raise TypeError("Parameter 2 is a instance of the SpriteList instead of a required Sprite. See if you meant to "
                        "call check_for_collision_with_list instead of check_for_collision.")
    elif not isinstance(sprite2, Sprite):
        raise TypeError("Parameter 2 is not an instance of the Sprite class.")

    return _check_for_collision(sprite1, sprite2)


def _check_for_collision(sprite1: Sprite, sprite2: Sprite) -> bool:
    """
    Check for collision between two sprites.

    :param Sprite sprite1: Sprite 1
    :param Sprite sprite2: Sprite 2

    :returns: Boolean
    """
    collision_radius_sum = sprite1.collision_radius + sprite2.collision_radius

    diff_x = sprite1.position[0] - sprite2.position[0]
    diff_x2 = diff_x * diff_x

    if diff_x2 > collision_radius_sum * collision_radius_sum:
        return False

    diff_y = sprite1.position[1] - sprite2.position[1]
    diff_y2 = diff_y * diff_y
    if diff_y2 > collision_radius_sum * collision_radius_sum:
        return False

    distance = diff_x2 + diff_y2
    if distance > collision_radius_sum * collision_radius_sum:
        return False

    return are_polygons_intersecting(sprite1.get_adjusted_hit_box(), sprite2.get_adjusted_hit_box())


def check_for_collision_with_list(sprite: Sprite,
                                  sprite_list: SpriteList) -> List[Sprite]:
    """
    Check for a collision between a sprite, and a list of sprites.

    :param Sprite sprite: Sprite to check
    :param SpriteList sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    """
    if not isinstance(sprite, Sprite):
        raise TypeError(f"Parameter 1 is not an instance of the Sprite class, it is an instance of {type(sprite)}.")
    if not isinstance(sprite_list, SpriteList):
        raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    if sprite_list.use_spatial_hash:
        sprite_list_to_check = sprite_list.spatial_hash.get_objects_for_box(sprite)
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
    else:
        sprite_list_to_check = sprite_list

    collision_list = [sprite2
                      for sprite2 in sprite_list_to_check
                      if sprite is not sprite2 and _check_for_collision(sprite, sprite2)]

    # collision_list = []
    # for sprite2 in sprite_list_to_check:
    #     if sprite1 is not sprite2 and sprite2 not in collision_list:
    #         if _check_for_collision(sprite1, sprite2):
    #             collision_list.append(sprite2)
    return collision_list


def get_sprites_at_point(point: Point,
                         sprite_list: SpriteList) -> List[Sprite]:
    """
    Get a list of sprites at a particular point

    :param Point point: Point to check
    :param SpriteList sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    """
    if not isinstance(sprite_list, SpriteList):
        raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    if sprite_list.use_spatial_hash:
        sprite_list_to_check = sprite_list.spatial_hash.get_objects_for_point(point)
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
    else:
        sprite_list_to_check = sprite_list

    collision_list = [sprite2
                      for sprite2 in sprite_list_to_check
                      if is_point_in_polygon(point[0], point[1], sprite2.get_adjusted_hit_box())]

    return collision_list
