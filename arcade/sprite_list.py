"""
This module provides functionality to manage Sprites in a list.

"""

from typing import Iterable, Iterator
from typing import Any
from typing import TypeVar
from typing import List
from typing import Tuple
from typing import Optional
from typing import Union
from typing import Set

import logging
import math
import array
import time

from PIL import Image

from arcade import Color
from arcade import Matrix3x3
from arcade import Sprite
from arcade import get_distance_between_sprites
from arcade import are_polygons_intersecting
from arcade import is_point_in_polygon

from arcade import rotate_point
from arcade import get_window
from arcade import Point
from arcade import gl

LOG = logging.getLogger(__name__)


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

        p1 = [x1, y1]
        p2 = [x2, y1]
        p3 = [x2, y2]
        p4 = [x1, y2]

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
        """
        Clear the spatial hash
        """
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

    def get_objects_for_box(self, check_object: Sprite) -> Set[Sprite]:
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

        return set(close_by_sprites)

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


class SpriteList:
    """
    Keep a list of sprites. Contains many optimizations around batch-drawing sprites
    and doing collision detection. For optimization reasons, use_spatial_hash and
    is_static are very important.
    """
    array_of_images: Optional[List[Any]]
    next_texture_id = 0

    def __init__(self,
                 use_spatial_hash=None,
                 spatial_hash_cell_size=128,
                 is_static=False):
        """
        Initialize the sprite list

        :param bool use_spatial_hash: If set to True, this will make moving a sprite
               in the SpriteList slower, but it will speed up collision detection
               with items in the SpriteList. Great for doing collision detection
               with static walls/platforms.
        :param int spatial_hash_cell_size:
        :param bool is_static: Speeds drawing if the sprites in the list do not
               move. Will result in buggy behavior if the sprites move when this
               is set to True.
        """
        # The context this sprite list belongs to
        self.ctx = None
        self.program = None

        # List of sprites in the sprite list
        self.sprite_list = []

        self.sprite_idx = dict()

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

        self._tex_coords = None

        self.texture_id = None
        self._texture = None
        self._vao1 = None
        self.vbo_buf = None

        self._force_new_atlas_generation = False

        self.array_of_texture_names = []
        self.array_of_images = []

        self._sprites_moved = 0
        self._percent_sprites_moved = 0

        # Used in collision detection optimization
        self.is_static = is_static
        self._use_spatial_hash = use_spatial_hash
        if use_spatial_hash is True:
            self.spatial_hash = _SpatialHash(cell_size=spatial_hash_cell_size)
        else:
            self.spatial_hash = None

        LOG.debug("[%s] Creating SpriteList use_spatial_hash=%s is_static=%s",
                  id(self), use_spatial_hash, is_static)

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
        if self._use_spatial_hash:
            self.spatial_hash.insert_object_for_box(item)

    def extend(self, items: Union[list, 'SpriteList']):
        """
        Extends the current list with the given list

        :param list items: list of Sprites to add to the list
        """
        for item in items:
            self.append(item)

    def insert(self, index: int, item: _SpriteType):
        """
        Inserts a sprite at a given index

        :param int index: The index at which to insert
        :param Sprite item: The sprite to insert
        """
        self.sprite_list.insert(index, item)
        item.register_sprite_list(self)
        for idx, sprite in enumerate(self.sprite_list[index:], start=index):
            self.sprite_idx[sprite] = idx

        self._vao1 = None
        if self._use_spatial_hash:
            self.spatial_hash.insert_object_for_box(item)

    def reverse(self):
        """
        Reverses the current list inplace
        """
        self.sprite_list.reverse()
        for idx, sprite in enumerate(self.sprite_list):
            self.sprite_idx[sprite] = idx

        self._vao1 = None

    @property
    def percent_sprites_moved(self):
        """ What percent of the sprites moved? """
        return self._percent_sprites_moved

    @property
    def use_spatial_hash(self):
        """ Are we using a spatial hash? """
        return self._use_spatial_hash

    def disable_spatial_hashing(self):
        """ Turn off spatial hashing. """
        self._use_spatial_hash = False
        self.spatial_hash = None

    def enable_spatial_hashing(self, spatial_hash_cell_size=128):
        """ Turn on spatial hashing. """
        LOG.debug("Setting use_spatial_hash={new_use_spatial_hash}")
        self.spatial_hash = _SpatialHash(spatial_hash_cell_size)
        self._use_spatial_hash = True
        self._recalculate_spatial_hashes()

    def _recalculate_spatial_hash(self, item: _SpriteType):
        """ Recalculate the spatial hash for a particular item. """
        if self._use_spatial_hash:
            self.spatial_hash.remove_object(item)
            self.spatial_hash.insert_object_for_box(item)

    def _recalculate_spatial_hashes(self):
        if self._use_spatial_hash:
            self.spatial_hash.reset()
            for sprite in self.sprite_list:
                self.spatial_hash.insert_object_for_box(sprite)

    def remove(self, item: _SpriteType):
        """
        Remove a specific sprite from the list.
        :param Sprite item: Item to remove from the list
        """
        self.sprite_list.remove(item)
        item.sprite_lists.remove(self)

        # Rebuild index list
        self.sprite_idx[item] = dict()
        for idx, sprite in enumerate(self.sprite_list):
            self.sprite_idx[sprite] = idx

        self._vao1 = None
        if self._use_spatial_hash:
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
        """
        Call the update_animation in every sprite in the sprite list.
        """
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

    def preload_textures(self, texture_list: List):
        """
        Preload a set of textures that will be used for sprites in this
        sprite list.

        :param array texture_list: List of textures.
        """
        if self.array_of_texture_names is None:
            self.array_of_texture_names = []

        if self.array_of_images is None:
            self.array_of_images = []

        for texture in texture_list:
            if texture.name not in self.array_of_texture_names:
                self.array_of_texture_names.append(texture.name)
                self.array_of_images.append(texture.image)

        self._force_new_atlas_generation = True

    def _calculate_sprite_buffer(self):

        if self.is_static:
            usage = 'static'
        else:
            usage = 'stream'

        def _calculate_pos_buffer():
            self._sprite_pos_data = array.array('f')
            # print("A")
            for sprite in self.sprite_list:
                self._sprite_pos_data.append(sprite.center_x)
                self._sprite_pos_data.append(sprite.center_y)

            self._sprite_pos_buf = self.ctx.buffer(
                data=self._sprite_pos_data,
                usage=usage
            )
            variables = ['in_pos']
            self._sprite_pos_desc = gl.BufferDescription(
                self._sprite_pos_buf,
                '2f',
                variables,
            )
            self._sprite_pos_changed = False

        def _calculate_size_buffer():
            self._sprite_size_data = array.array('f')
            for sprite in self.sprite_list:
                self._sprite_size_data.append(sprite.width)
                self._sprite_size_data.append(sprite.height)

            self._sprite_size_buf = self.ctx.buffer(
                data=self._sprite_size_data,
                usage=usage
            )
            variables = ['in_size']
            self._sprite_size_desc = gl.BufferDescription(
                self._sprite_size_buf,
                '2f',
                variables)
            self._sprite_size_changed = False

        def _calculate_angle_buffer():
            self._sprite_angle_data = array.array('f')
            for sprite in self.sprite_list:
                self._sprite_angle_data.append(sprite.angle)

            self._sprite_angle_buf = self.ctx.buffer(
                data=self._sprite_angle_data,
                usage=usage
            )
            variables = ['in_angle']
            self._sprite_angle_desc = gl.BufferDescription(
                self._sprite_angle_buf,
                '1f',
                variables,
            )
            self._sprite_angle_changed = False

        def _calculate_colors():
            self._sprite_color_data = array.array('B')

            for sprite in self.sprite_list:
                self._sprite_color_data.extend(sprite.color[:3])
                self._sprite_color_data.append(int(sprite.alpha))

            self._sprite_color_buf = self.ctx.buffer(
                data=self._sprite_color_data,
                usage=usage
            )
            variables = ['in_color']
            self._sprite_color_desc = gl.BufferDescription(
                self._sprite_color_buf,
                '4f1',
                variables,
                normalized=['in_color']
            )
            self._sprite_color_changed = False

        def _calculate_sub_tex_coords():
            """
            Create a sprite sheet, and set up subtexture coordinates to point
            to images in that sheet.
            """
            new_array_of_texture_names = []
            new_array_of_images = []
            new_texture = False
            if self.array_of_images is None or self._force_new_atlas_generation:
                new_texture = True
                self._force_new_atlas_generation = False

            # print()
            # print("New texture start: ", new_texture)

            for sprite in self.sprite_list:

                # noinspection PyProtectedMember
                if sprite.texture is None:
                    raise Exception("Error: Attempt to draw a sprite without a texture set.")

                name_of_texture_to_check = sprite.texture.name

                # Do we already have this in our old texture atlas?
                if name_of_texture_to_check not in self.array_of_texture_names:
                    # No, so flag that we'll have to create a new one.
                    new_texture = True
                    # print("New because of ", name_of_texture_to_check)

                # Do we already have this created because of a prior loop?
                if name_of_texture_to_check not in new_array_of_texture_names:
                    # No, so make as a new image
                    new_array_of_texture_names.append(name_of_texture_to_check)
                    if sprite.texture is None:
                        raise ValueError(f"Sprite has no texture.")
                    if sprite.texture.image is None:
                        raise ValueError(f"Sprite texture {sprite.texture.name} has no image.")
                    image = sprite.texture.image

                    # Create a new image with a transparent border around it to help prevent artifacts
                    tmp = Image.new('RGBA', (image.width+2, image.height+2))
                    tmp.paste(image, (1, 1))
                    tmp.paste(tmp.crop((1          , 1           , image.width+1, 2             )), (1            , 0             ))
                    tmp.paste(tmp.crop((1          , image.height, image.width+1, image.height+1)), (1            , image.height+1))
                    tmp.paste(tmp.crop((1          , 0           ,             2, image.height+2)), (0            , 0             ))
                    tmp.paste(tmp.crop((image.width, 0           , image.width+1, image.height+2)), (image.width+1, 0             ))

                    # Put in our array of new images
                    new_array_of_images.append(tmp)

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

            grid_item_width, grid_item_height = max(widths), max(heights)
            image_count = len(self.array_of_images)
            root = math.sqrt(image_count)
            grid_width = int(math.sqrt(image_count))
            # print(f"\nimage_count={image_count}, root={root}")
            if root == grid_width:
                # Perfect square
                grid_height = grid_width
                # print("\nA")
            else:
                grid_height = grid_width
                grid_width += 1
                if grid_width * grid_height < image_count:
                    grid_height += 1
                # print("\nB")

            # Figure out sprite sheet size
            margin = 0

            sprite_sheet_width = (grid_item_width + margin) * grid_width
            sprite_sheet_height = (grid_item_height + margin) * grid_height

            if new_texture:

                # TODO: This code isn't valid, but I think some releasing might be in order.
                # if self.texture is not None:
                #     .Texture.release(self.texture_id)

                # Make the composite image
                new_image2 = Image.new('RGBA', (sprite_sheet_width, sprite_sheet_height))

                x_offset = 0
                for index, image in enumerate(self.array_of_images):

                    x = (index % grid_width) * (grid_item_width + margin)
                    y = (index // grid_width) * (grid_item_height + margin)

                    # print(f"Pasting {new_array_of_texture_names[index]} at {x, y}")

                    new_image2.paste(image, (x, y))
                    x_offset += image.size[0]

                # Create a texture out the composite image
                texture_bytes2 = new_image2.tobytes()
                self._texture = self.ctx.texture(
                    (new_image2.width, new_image2.height),
                    components=4,
                    data=texture_bytes2,
                )

                if self.texture_id is None:
                    self.texture_id = SpriteList.next_texture_id

                # new_image2.save("sprites.png")

            # Create a list with the coordinates of all the unique textures
            self._tex_coords = []
            offset = 1

            for index, image in enumerate(self.array_of_images):
                column = index % grid_width
                row = index // grid_width

                # Texture coordinates are reversed in y axis
                row = grid_height - row - 1

                x = column * (grid_item_width + margin) + offset
                y = row * (grid_item_height + margin) + offset

                # Because, coordinates are reversed
                y += (grid_item_height - (image.height - margin))

                normalized_x = x / sprite_sheet_width
                normalized_y = y / sprite_sheet_height

                start_x = normalized_x
                start_y = normalized_y

                normalized_width = (image.width-2*offset) / sprite_sheet_width
                normalized_height = (image.height-2*offset) / sprite_sheet_height

                # print(f"Fetching {new_array_of_texture_names[index]} at {row}, {column} => {x}, {y} normalized to {start_x:.2}, {start_y:.2} size {normalized_width}, {normalized_height}")

                self._tex_coords.append([start_x, start_y, normalized_width, normalized_height])

            # Go through each sprite and pull from the coordinate list, the proper
            # coordinates for that sprite's image.
            self._sprite_sub_tex_data = array.array('f')
            for sprite in self.sprite_list:
                index = self.array_of_texture_names.index(sprite.texture.name)
                for coord in self._tex_coords[index]:
                    self._sprite_sub_tex_data.append(coord)

            self._sprite_sub_tex_buf = self.ctx.buffer(
                data=self._sprite_sub_tex_data,
                usage=usage
            )

            self._sprite_sub_tex_desc = gl.BufferDescription(
                self._sprite_sub_tex_buf,
                '4f',
                ['in_sub_tex_coords'],
            )
            self._sprite_sub_tex_changed = False

        if len(self.sprite_list) == 0:
            return

        perf_time = time.perf_counter()

        _calculate_pos_buffer()
        _calculate_size_buffer()
        _calculate_angle_buffer()
        _calculate_sub_tex_coords()
        _calculate_colors()

        # vertices = array.array('f', [
        #     #  x,    y,   u,   v
        #     -1.0, -1.0, 0.0, 0.0,
        #     -1.0, 1.0, 0.0, 1.0,
        #     1.0, -1.0, 1.0, 0.0,
        #     1.0, 1.0, 1.0, 1.0,
        # ])
        # self.vbo_buf = self.ctx.buffer(data=vertices)
        # vbo_buf_desc = gl.BufferDescription(
        #     self.vbo_buf,
        #     '2f 2f',
        #     ('in_vert', 'in_texture')
        # )

        # Can add buffer to index vertices
        # vao_content = [vbo_buf_desc,
        #                self._sprite_pos_desc,
        #                self._sprite_size_desc,
        #                self._sprite_angle_desc,
        #                self._sprite_sub_tex_desc,
        #                self._sprite_color_desc]
        vao_content = [self._sprite_pos_desc,
                       self._sprite_size_desc,
                       self._sprite_angle_desc,
                       self._sprite_sub_tex_desc,
                       self._sprite_color_desc]

        self._vao1 = self.ctx.geometry(vao_content)
        LOG.debug('[%s] _calculate_sprite_buffer: %s sec', id(self), time.perf_counter() - perf_time)

    def _dump(self, buffer):
        """
        Debugging method used to dump raw byte data in the OpenGL buffer.
        """
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

            self._sprite_angle_data[i] = sprite.angle
            self._sprite_angle_changed = True

            self._sprite_color_data[i * 4] = sprite.color[0]
            self._sprite_color_data[i * 4 + 1] = sprite.color[1]
            self._sprite_color_data[i * 4 + 2] = sprite.color[2]
            self._sprite_color_data[i * 4 + 3] = sprite.alpha
            self._sprite_color_changed = True

            self._sprite_size_data[i * 2] = sprite.width
            self._sprite_size_data[i * 2 + 1] = sprite.height
            self._sprite_size_changed = True

    def update_texture(self, sprite):
        """ Make sure we update the texture for this sprite for the next batch
        drawing"""
        if self._vao1 is None:
            return

        if sprite.texture is None:
            return

        name_of_texture_to_check = sprite.texture.name
        if name_of_texture_to_check not in self.array_of_texture_names:
            self._calculate_sprite_buffer()

        self._sprite_sub_tex_changed = True

        index = self.array_of_texture_names.index(sprite.texture.name)
        new_coords = self._tex_coords[index]

        i = self.sprite_idx[sprite]

        self._sprite_sub_tex_data[i * 4] = new_coords[0]
        self._sprite_sub_tex_data[i * 4 + 1] = new_coords[1]
        self._sprite_sub_tex_data[i * 4 + 2] = new_coords[2]
        self._sprite_sub_tex_data[i * 4 + 3] = new_coords[3]

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

        self._sprite_angle_data[i] = sprite.angle
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

        self._sprites_moved += 1

    def update_angle(self, sprite: Sprite):
        """
        Called by the Sprite class to update the angle in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self._vao1 is None:
            return

        i = self.sprite_idx[sprite]
        self._sprite_angle_data[i] = sprite.angle
        self._sprite_angle_changed = True

    def draw(self, **kwargs):
        """
        Draw this list of sprites.

        :param filter: Optional parameter to set OpenGL filter, such as
                       `gl.GL_NEAREST` to avoid smoothing.

        :param blend_function: Optional parameter to set the OpenGL blend function used for drawing the sprite list, such as
                        'arcade.Window.ctx.BLEND_ADDITIVE' or 'arcade.Window.ctx.BLEND_DEFAULT'
        """
        if len(self.sprite_list) == 0:
            return

        # What percent of this sprite list moved? Used in guessing spatial hashing
        self._percent_sprites_moved = self._sprites_moved / len(self.sprite_list) * 100
        self._sprites_moved = 0

        # Make sure window context exists
        if self.ctx is None:
            self.ctx = get_window().ctx
            # Used in drawing optimization via OpenGL
            self.program = self.ctx.sprite_list_program_cull

        if self._vao1 is None:
            self._calculate_sprite_buffer()

        self.ctx.enable(self.ctx.BLEND)
        if "blend_function" in kwargs:
            self.ctx.blend_func = kwargs["blend_function"]
        else:
            self.ctx.blend_func = self.ctx.BLEND_DEFAULT

        self._texture.use(0)

        if "filter" in kwargs:
            self._texture.filter = self.ctx.NEAREST, self.ctx.NEAREST

        self.program['Texture'] = self.texture_id

        texture_transform = None
        if len(self.sprite_list) > 0:
            # always wrap texture transformations with translations
            # so that rotate and resize operations act on the texture
            # center by default
            texture_transform = Matrix3x3().translate(-0.5, -0.5).multiply(self.sprite_list[0].texture_transform.v).multiply(Matrix3x3().translate(0.5, 0.5).v)
        else:
            texture_transform = Matrix3x3()
        self.program['TextureTransform'] = texture_transform.v

        if not self.is_static:
            if self._sprite_pos_changed:
                self._sprite_pos_buf.orphan()
                self._sprite_pos_buf.write(self._sprite_pos_data)
                self._sprite_pos_changed = False

            if self._sprite_size_changed:
                self._sprite_size_buf.orphan()
                self._sprite_size_buf.write(self._sprite_size_data)
                self._sprite_size_changed = False

            if self._sprite_angle_changed:
                self._sprite_angle_buf.orphan()
                self._sprite_angle_buf.write(self._sprite_angle_data)
                self._sprite_angle_changed = False

            if self._sprite_color_changed:
                self._sprite_color_buf.orphan()
                self._sprite_color_buf.write(self._sprite_color_data)
                self._sprite_color_changed = False

            if self._sprite_sub_tex_changed:
                self._sprite_sub_tex_buf.orphan()
                self._sprite_sub_tex_buf.write(self._sprite_sub_tex_data)
                self._sprite_sub_tex_changed = False

        self._vao1.render(self.program, mode=self.ctx.POINTS, vertices=len(self.sprite_list))

    def draw_hit_boxes(self, color: Color = (0, 0, 0, 255), line_thickness: float = 1):
        """ Draw all the hit boxes in this list """
        for sprite in self.sprite_list:
            sprite.draw_hit_box(color, line_thickness)

    def __len__(self) -> int:
        """ Return the length of the sprite list. """
        return len(self.sprite_list)

    def __iter__(self) -> Iterator[Sprite]:
        """ Return an iterable object of sprites. """
        return iter(self.sprite_list)

    def __getitem__(self, i):
        return self.sprite_list[i]

    def __setitem__(self, key: int, value: Sprite):
        self._vao1 = None
        self.sprite_list[key] = value
        self.sprite_idx[value] = key

    def index(self, key):
        """ Return the index of this sprite """
        return self.sprite_list.index(key)

    def pop(self, index: int = -1) -> Sprite:
        """
        Pop off the last sprite, or the given index, from the list
        """
        if len(self.sprite_list) == 0:
            raise(ValueError("pop from empty list"))

        sprite = self.sprite_list[index]
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

    if sprite_list.use_spatial_hash is None and len(sprite_list) > 30 and sprite_list.percent_sprites_moved < 10:
        LOG.debug(f"Enabling spatial hash - Spatial hash is none, sprite list "
                  f"is {len(sprite_list)} elements. Percent moved "
                  f"{sprite_list._percent_sprites_moved * 100}.")
        sprite_list.enable_spatial_hashing()

    if sprite_list.use_spatial_hash:
        sprite_list_to_check = sprite_list.spatial_hash.get_objects_for_box(sprite)
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
    else:
        sprite_list_to_check = sprite_list

    # print(len(sprite_list_to_check.sprite_list))
    return [sprite2
                      for sprite2 in sprite_list_to_check
                      if sprite is not sprite2 and _check_for_collision(sprite, sprite2)]

    # collision_list = []
    # for sprite2 in sprite_list_to_check:
    #     if sprite1 is not sprite2 and sprite2 not in collision_list:
    #         if _check_for_collision(sprite1, sprite2):
    #             collision_list.append(sprite2)


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
        # print("Checks saved: ", checks_saved)
    else:
        sprite_list_to_check = sprite_list

    return [s for s in sprite_list_to_check if
                      is_point_in_polygon(point[0], point[1], s.get_adjusted_hit_box())]


def get_sprites_at_exact_point(point: Point,
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
        # print("Checks saved: ", checks_saved)
    else:
        sprite_list_to_check = sprite_list

    return [s for s in sprite_list_to_check if s.position == point]
