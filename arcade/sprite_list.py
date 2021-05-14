"""
This module provides functionality to manage Sprites in a list.
"""
import logging
from array import array
from collections import deque
from random import shuffle

from typing import (
    Dict,
    Deque,
    Iterable,
    Iterator,
    Sequence,
    TYPE_CHECKING,
    TypeVar,
    List,
    Tuple,
    Optional,
    Union,
    Set,
)

from arcade.context import ArcadeContext
from arcade import (
    Color,
    Matrix3x3,
    Sprite,
    get_distance_between_sprites,
    are_polygons_intersecting,
    is_point_in_polygon,
    rotate_point,
    get_window,
    Point,
    gl,
)

if TYPE_CHECKING:
    from arcade import TextureAtlas
    from arcade import Texture

LOG = logging.getLogger(__name__)

# The slot index that makes a sprite invisible.
# 2^32-1 is usually reserved for primitive restart
# NOTE: Possibly we want to use slot 0 for this?
_SPRITE_SLOT_INVISIBLE = 2**32-2


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
    _keep_textures = True
    __slots__ = (
        'ctx',
        'program',
        '_atlas',
        '_deferred_sprites',
        '_initialized',
        'sprite_list',
        'sprite_slot',
        'is_static',
        '_buf_capacity',
        '_idx_capacity',
        '_sprite_buffer_slots',
        '_sprite_index_slots',
        '_sprite_buffer_free_slots',
        '_sprite_pos_data',
        '_sprite_size_data',
        '_sprite_angle_data',
        '_sprite_color_data',
        '_sprite_sub_tex_data',
        '_sprite_sub_tex_data',
        '_sprite_index_data',
        '_sprite_pos_buf',
        '_sprite_size_buf',
        '_sprite_angle_buf',
        '_sprite_color_buf',
        '_sprite_sub_tex_buf',
        '_sprite_index_buf',
        '_sprite_pos_changed',
        '_sprite_size_changed',
        '_sprite_angle_changed',
        '_sprite_color_changed',
        '_sprite_sub_tex_changed',
        '_sprite_index_changed',
        '_geometry',
        '_sprites_moved',
        '_percent_sprites_moved',
        '_use_spatial_hash',
        'spatial_hash',
        'extra',
        '__weakref__',
    )

    def __init__(self,
                 use_spatial_hash=None,
                 spatial_hash_cell_size=128,
                 is_static=False,
                 atlas: "TextureAtlas" = None,
                 capacity: int = 100):
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
        :param TextureAtlas atlas: The texture alas for this sprite list. If no
               atlas is supplied the global/default one will be used.
        :param int capacity: The initial capacity of the internal buffer.
               It's a suggestion for the maximum amount of sprites this list
               can hold. Can normally be left with default value.
        """
        self.ctx = None
        self.program = None
        if atlas:
            self._atlas: TextureAtlas = atlas
        self._initialized = False
        self.extra = None

        # The initial capacity of the spritelist buffers (internal)
        self._buf_capacity = abs(capacity) or 100
        # The initial capacity of the index buffer (internal)
        self._idx_capacity = abs(capacity) or 100
        # The number of slots used in the sprite buffer
        self._sprite_buffer_slots = 0
        # Number of slots used in the index buffer
        self._sprite_index_slots = 0
        # List of free slots in the sprite buffers. These are filled when sprites are removed.
        self._sprite_buffer_free_slots: Deque[int] = deque()

        # Sprites added before the window/context is created
        self._deferred_sprites: Set[Sprite] = set()

        # List of sprites in the sprite list
        self.sprite_list: List[Sprite] = []
        # Buffer slots for the sprites (exclusing index buffer)
        # This has nothing to do with the index in the spritelist itself
        self.sprite_slot: Dict[Sprite, int] = dict()
        # TODO: Figure out what to do with this. Might be obsolete.
        self.is_static = is_static

        # Python representation of buffer data
        self._sprite_pos_data = array('f', [0] * self._buf_capacity * 2)
        self._sprite_size_data = array('f', [0] * self._buf_capacity * 2)
        self._sprite_angle_data = array('f', [0] * self._buf_capacity)
        self._sprite_color_data = array('B', [0] * self._buf_capacity * 4)
        self._sprite_sub_tex_data = array('f', [0] * self._buf_capacity * 4)
        # Index buffer
        self._sprite_index_data = array('I', [0] * self._idx_capacity)

        # Flags for signaling if a buffer needs to be written to the opengl buffer
        self._sprite_pos_changed = False
        self._sprite_size_changed = False
        self._sprite_angle_changed = False
        self._sprite_color_changed = False
        self._sprite_sub_tex_changed = False
        self._sprite_index_changed = False

        # Info for spatial hash
        self._sprites_moved = 0
        self._percent_sprites_moved = 0

        # Used in collision detection optimization
        self.spatial_hash: Optional[_SpatialHash] = None
        self._use_spatial_hash = use_spatial_hash
        if use_spatial_hash is True:
            self.spatial_hash = _SpatialHash(cell_size=spatial_hash_cell_size)

        LOG.debug("[%s] Creating SpriteList use_spatial_hash=%s is_static=%s",
                  id(self), use_spatial_hash, is_static)

        # Check if the window/context is available
        try:
            get_window()
            self._init_deferred()
        except Exception as ex:
            print(ex)

    def _init_deferred(self):
        """Since spritelist can be created before the window we need to defer initialization"""
        self.ctx: ArcadeContext = get_window().ctx
        self.program = self.ctx.sprite_list_program_cull
        self._atlas: TextureAtlas = getattr(self, '_atlas', None) or self.ctx.default_atlas

        # Buffers for each sprite attribute (read by shader) with initial capacity
        self._sprite_pos_buf = self.ctx.buffer(reserve=self._buf_capacity * 4 * 2)
        self._sprite_size_buf = self.ctx.buffer(reserve=self._buf_capacity * 4 * 2)
        self._sprite_angle_buf = self.ctx.buffer(reserve=self._buf_capacity * 4)
        self._sprite_color_buf = self.ctx.buffer(reserve=self._buf_capacity * 4 * 4)
        self._sprite_sub_tex_buf = self.ctx.buffer(reserve=self._buf_capacity * 4 * 4)
        # Index buffer
        self._sprite_index_buf = self.ctx.buffer(reserve=self._idx_capacity * 4)

        contents = [
            gl.BufferDescription(self._sprite_pos_buf, "2f", ['in_pos']),
            gl.BufferDescription(self._sprite_size_buf, "2f", ['in_size']),
            gl.BufferDescription(self._sprite_angle_buf, "1f", ['in_angle']),
            gl.BufferDescription(self._sprite_sub_tex_buf, "4f", ['in_sub_tex_coords']),
            gl.BufferDescription(self._sprite_color_buf, "4f1", ["in_color"], normalized=["in_color"]),
        ]
        self._geometry = self.ctx.geometry(
            contents,
            index_buffer=self._sprite_index_buf,
            index_element_size=4,  # 32 bit integers
        )

        self._initialized = True

        # Load all the textures and write texture coordinates into buffers
        for sprite in self._deferred_sprites:
            if sprite._texture is None:
                raise ValueError("Attempting to use a sprite without a texture")
            self.update_texture(sprite)
            if hasattr(sprite, "textures"):
                for texture in sprite.textures or []:
                    self._atlas.add(texture)

        self._deferred_sprites = None

        self._sprite_pos_changed = True
        self._sprite_size_changed = True
        self._sprite_angle_changed = True
        self._sprite_color_changed = True
        self._sprite_sub_tex_changed = True
        self._sprite_index_changed = True

    def __len__(self) -> int:
        """ Return the length of the sprite list. """
        return len(self.sprite_list)

    def __iter__(self) -> Iterator[Sprite]:
        """ Return an iterable object of sprites. """
        return iter(self.sprite_list)

    def __getitem__(self, i):
        return self.sprite_list[i]

    def __setitem__(self, index: int, sprite: Sprite):
        """Replace a sprite at a specific index"""
        # print(f"{id(self)} : {id(sprite)} __setitem__({index})")

        try:
            existing_index = self.sprite_list.index(sprite)  # raise ValueError
            if existing_index == index:
                return
            raise Exception(f"Sprite is already in the list (index {existing_index})")
        except ValueError as ex:
            pass

        sprite_to_be_removed = self.sprite_list[index]
        sprite_to_be_removed.sprite_lists.remove(self)
        self.sprite_list[index] = sprite  # Replace sprite
        sprite.register_sprite_list(self)

        if self.spatial_hash:
            self.spatial_hash.remove_object(sprite_to_be_removed)
            self.spatial_hash.insert_object_for_box(sprite)

        # Steal the slot from the old sprite
        slot = self.sprite_slot[sprite_to_be_removed]
        del self.sprite_slot[sprite_to_be_removed]
        self.sprite_slot[sprite] = slot

        # Update the internal sprite buffer data
        self._update_all(sprite)

    @property
    def atlas(self) -> "TextureAtlas":
        """Get the texture atlas for this sprite list"""
        return self._atlas

    def _next_slot(self) -> int:
        """
        Get the next available slot in sprite buffers

        :return: index slot, buffer_slot
        :rtype: int
        """
        # Reuse old slots from deleted sprites
        if self._sprite_buffer_free_slots:
            return self._sprite_buffer_free_slots.popleft()

        # Add a new slot
        buff_slot = self._sprite_buffer_slots
        self._sprite_buffer_slots += 1
        self._grow_sprite_buffers()  # We might need to increase our buffers
        return buff_slot

    def index(self, sprite: Sprite) -> int:
        """
        Return the index of a sprite in the spritelist

        :type: int
        """
        return self.sprite_list.index(sprite)

    def pop(self, index: int = -1) -> Sprite:
        """
        Pop off the last sprite, or the given index, from the list
        """
        if len(self.sprite_list) == 0:
            raise(ValueError("pop from empty list"))

        sprite = self.sprite_list[index]
        self.remove(sprite)
        return sprite

    def append(self, sprite: _SpriteType):
        """
        Add a new sprite to the list.

        :param Sprite item: Sprite to add to the list.
        """
        # print(f"{id(self)} : {id(sprite)} append")
        if sprite in self.sprite_slot:
            raise ValueError("Sprite already in SpriteList")

        slot = self._next_slot()
        self.sprite_slot[sprite] = slot
        self.sprite_list.append(sprite)
        sprite.register_sprite_list(self)

        self._update_all(sprite)

        # Add sprite to the end of the index buffer
        idx_slot = self._sprite_index_slots
        self._sprite_index_slots += 1
        self._grow_index_buffer()
        self._sprite_index_data[idx_slot] = slot
        self._sprite_index_changed = True

        if self.spatial_hash:
            self.spatial_hash.insert_object_for_box(sprite)

        # Load additional textures attached to the sprite
        if hasattr(sprite, "textures") and self._initialized:
            for texture in sprite.textures or []:
                self._atlas.add(texture)

    def swap(self, index_1: int, index_2: int):
        """Swap two sprites by index"""
        # Swap order in spritelist
        sprite_1 = self.sprite_list[index_1]
        sprite_2 = self.sprite_list[index_2]
        self.sprite_list[index_1] = sprite_2
        self.sprite_list[index_2] = sprite_1

        # Swap order in index buffer
        slot_1 = self.sprite_slot[sprite_1]
        slot_2 = self.sprite_slot[sprite_2]
        i1 = self._sprite_index_data.index(slot_1)
        i2 = self._sprite_index_data.index(slot_2)
        self._sprite_index_data[i1] = slot_2
        self._sprite_index_data[i2] = slot_1

    def remove(self, sprite: _SpriteType):
        """
        Remove a specific sprite from the list.
        :param Sprite item: Item to remove from the list
        """
        # print(f"{id(self)} : {id(sprite)} remove")
        try:
            slot = self.sprite_slot[sprite]
        except KeyError:
            raise ValueError("Sprite is not in the SpriteList")

        self.sprite_list.remove(sprite)
        sprite.sprite_lists.remove(self)
        del self.sprite_slot[sprite]

        self._sprite_buffer_free_slots.append(slot)

        # NOTE: Optimize this by deferring removal?
        #       Defer removal
        # Set the sprite as invisible in the index buffer
        # idx_slot = self._sprite_index_data.index(slot)
        # self._sprite_index_data[idx_slot] = _SPRITE_SLOT_INVISIBLE

        # Brutal resize for now. Optimize later
        self._sprite_index_data.remove(slot)
        self._sprite_index_data.append(0)
        self._sprite_index_slots -= 1
        self._sprite_index_changed = True

        if self.spatial_hash:
            self.spatial_hash.remove_object(sprite)

    def extend(self, sprites: Union[list, 'SpriteList']):
        """
        Extends the current list with the given list

        :param list items: list of Sprites to add to the list
        """
        for sprite in sprites:
            self.append(sprite)

    def insert(self, index: int, sprite: _SpriteType):
        """
        Inserts a sprite at a given index.

        :param int index: The index at which to insert
        :param Sprite item: The sprite to insert
        """
        if sprite in self.sprite_list:
            raise ValueError("Sprite is already in list")

        self.sprite_list.insert(index, sprite)
        sprite.register_sprite_list(self)

        # Allocate a new slot and write the data
        slot = self._next_slot()
        self.sprite_slot[sprite] = slot
        self._update_all(sprite)

        # Allocate room in the index buffer
        self._normalize_index_buffer()
        idx_slot = self._sprite_index_slots
        self._sprite_index_slots += 1
        self._grow_index_buffer()
        self._sprite_index_data.insert(index, slot)
        self._sprite_index_data.pop()

        if self.spatial_hash:
            self.spatial_hash.insert_object_for_box(sprite)

    def reverse(self):
        """
        Reverses the current list in-place
        """
        self.sprite_list.reverse()
        # Reverse the index buffer
        # Only revers the part of the array we use
        self._sprite_index_data = self._sprite_index_data[:self._sprite_index_slots]
        self._sprite_index_data.reverse()
        # Resize the index buffer to the original capacity
        if len(self._sprite_index_data) < self._idx_capacity:
            extend_by = self._idx_capacity - len(self._sprite_index_data)
            self._sprite_index_data.extend([0] * extend_by)

        self._sprite_index_changed = True

    def shuffle(self):
        """
        Shuffles the current list in-place
        """
        # Make sure the index buffer is the same length as the sprite list
        self._normalize_index_buffer()
        # zip index and sprite into pairs and shuffle
        pairs = list(zip(self.sprite_list, self._sprite_index_data))
        # Reconstruct the lists again from pairs
        sprites, indices = zip(*pairs)
        self.sprite_list = list(sprites)
        self._sprite_index_data = array('I', indices)
        # Resize the index buffer to the original capacity
        if len(self._sprite_index_data) < self._idx_capacity:
            extend_by = self._idx_capacity - len(self._sprite_index_data)
            self._sprite_index_data.extend([0] * extend_by)

    @property
    def percent_sprites_moved(self):
        """ What percent of the sprites moved? """
        return self._percent_sprites_moved

    @property
    def use_spatial_hash(self) -> bool:
        """ Are we using a spatial hash? """
        return self._use_spatial_hash

    def disable_spatial_hashing(self) -> None:
        """ Turn off spatial hashing. """
        self._use_spatial_hash = False
        self.spatial_hash = None

    def enable_spatial_hashing(self, spatial_hash_cell_size=128):
        """ Turn on spatial hashing. """
        LOG.debug("Enable spatial hashing with cell size %s", spatial_hash_cell_size)
        self.spatial_hash = _SpatialHash(spatial_hash_cell_size)
        self._use_spatial_hash = True
        self._recalculate_spatial_hashes()

    def _recalculate_spatial_hash(self, item: _SpriteType):
        """ Recalculate the spatial hash for a particular item. """
        if self.spatial_hash:
            self.spatial_hash.remove_object(item)
            self.spatial_hash.insert_object_for_box(item)

    def _recalculate_spatial_hashes(self):
        if self._use_spatial_hash:
            self.spatial_hash.reset()
            for sprite in self.sprite_list:
                self.spatial_hash.insert_object_for_box(sprite)

    def update(self) -> None:
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
        # NOTE: Can we limit this to animated sprites?
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

    def move(self, change_x: float, change_y: float) -> None:
        """
        Moves all Sprites in the list by the same amount.
        This can be a very expensive operation depending on the
        size of the sprite list.

        :param float change_x: Amount to change all x values by
        :param float change_y: Amount to change all y values by
        """
        for sprite in self.sprite_list:
            sprite.center_x += change_x
            sprite.center_y += change_y

    def preload_textures(self, texture_list: List["Texture"]) -> None:
        """
        Preload a set of textures that will be used for sprites in this
        sprite list.

        :param array texture_list: List of textures.
        """
        if not self.ctx:
            raise ValueError("Cannot preload textures before the window is created")

        for texture in texture_list:
            self._atlas.add(texture)

    def _update_all(self, sprite: Sprite):
        """
        Update all sprite data. This is faster when adding and moving sprites.
        This duplicate code, but reduces call overhead, dict lookups etc.
        """
        slot = self.sprite_slot[sprite]
        # position
        self._sprite_pos_data[slot * 2] = sprite._position[0]
        self._sprite_pos_data[slot * 2 + 1] = sprite._position[1]
        self._sprite_pos_changed = True
        # size
        self._sprite_size_data[slot * 2] = sprite._width
        self._sprite_size_data[slot * 2 + 1] = sprite._height
        self._sprite_size_changed = True
        # angle
        self._sprite_angle_data[slot] = sprite._angle
        self._sprite_angle_changed = True
        # color
        self._sprite_color_data[slot * 4] = sprite._color[0]
        self._sprite_color_data[slot * 4 + 1] = sprite._color[1]
        self._sprite_color_data[slot * 4 + 2] = sprite._color[2]
        self._sprite_color_data[slot * 4 + 3] = sprite._alpha
        self._sprite_color_changed = True

        # texture
        if not self._initialized:
            self._deferred_sprites.add(sprite)
            return

        if not sprite._texture:
            return

        region = self._atlas.add(sprite._texture)

        slot = self.sprite_slot[sprite]
        new_coords = region.texture_coordinates

        self._sprite_sub_tex_data[slot * 4] = new_coords[0]
        self._sprite_sub_tex_data[slot * 4 + 1] = new_coords[1]
        self._sprite_sub_tex_data[slot * 4 + 2] = new_coords[2]
        self._sprite_sub_tex_data[slot * 4 + 3] = new_coords[3]
        self._sprite_sub_tex_changed = True

    def update_texture(self, sprite) -> None:
        """Make sure we update the texture for this sprite for the next batch
        drawing"""
        # We cannot interact with texture atlases unless the context
        # is created. We defer all texture initialization for later
        if not self._initialized:
            self._deferred_sprites.add(sprite)
            return

        if not sprite._texture:
            return

        region = self._atlas.add(sprite._texture)

        slot = self.sprite_slot[sprite]
        new_coords = region.texture_coordinates

        self._sprite_sub_tex_data[slot * 4] = new_coords[0]
        self._sprite_sub_tex_data[slot * 4 + 1] = new_coords[1]
        self._sprite_sub_tex_data[slot * 4 + 2] = new_coords[2]
        self._sprite_sub_tex_data[slot * 4 + 3] = new_coords[3]
        self._sprite_sub_tex_changed = True

        # Update size in cas the sprite was initialized without size
        # NOTE: There should be a better way to do this
        self._sprite_size_data[slot * 2] = sprite._width
        self._sprite_size_data[slot * 2 + 1] = sprite._height
        self._sprite_size_changed = True

    def update_position(self, sprite: Sprite) -> None:
        """
        Called when setting initial position of a sprite when
        added or inserted into the SpriteList.

        ``update_location`` should be called to move them
        once the sprites are in the list.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_pos_data[slot * 2] = sprite._position[0]
        self._sprite_pos_data[slot * 2 + 1] = sprite._position[1]
        self._sprite_pos_changed = True

    def update_color(self, sprite: Sprite) -> None:
        """
        Called by the Sprite class to update position, angle, size and color
        of the specified sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_color_data[slot * 4] = int(sprite._color[0])
        self._sprite_color_data[slot * 4 + 1] = int(sprite._color[1])
        self._sprite_color_data[slot * 4 + 2] = int(sprite._color[2])
        self._sprite_color_data[slot * 4 + 3] = int(sprite._alpha)
        self._sprite_color_changed = True

    def update_size(self, sprite: Sprite) -> None:
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_size_data[slot * 2] = sprite._width
        self._sprite_size_data[slot * 2 + 1] = sprite._height
        self._sprite_size_changed = True

    def update_height(self, sprite: Sprite):
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_size_data[slot * 2 + 1] = sprite._height
        self._sprite_size_changed = True

    def update_width(self, sprite: Sprite):
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_size_data[slot * 2] = sprite._width
        self._sprite_size_changed = True

    def update_location(self, sprite: Sprite):
        """
        Called by the Sprite class to update the location in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        # print(f"{id(self)} : {id(sprite)} update_location")
        try:
            slot = self.sprite_slot[sprite]
        except KeyError:
            raise ValueError(id(sprite))
        self._sprite_pos_data[slot * 2] = sprite._position[0]
        self._sprite_pos_data[slot * 2 + 1] = sprite._position[1]
        self._sprite_pos_changed = True
        self._sprites_moved += 1

    def update_angle(self, sprite: Sprite):
        """
        Called by the Sprite class to update the angle in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_angle_data[slot] = sprite._angle
        self._sprite_angle_changed = True

    def _write_sprite_buffers_to_gpu(self):
        """Create or resize buffers"""
        LOG.debug(
            "[%s] SpriteList._write_sprite_buffers_to_gpu: pos=%s, size=%s, angle=%s, color=%s tex=%s idx=%s",
            id(self),
            self._sprite_pos_changed,
            self._sprite_size_changed,
            self._sprite_angle_changed,
            self._sprite_color_changed,
            self._sprite_sub_tex_changed,
            self._sprite_index_changed,
        )

        if self._sprite_pos_changed:
            self._sprite_pos_buf.write(self._sprite_pos_data)
            self._sprite_pos_changed = False

        if self._sprite_size_changed:
            self._sprite_size_buf.write(self._sprite_size_data)
            self._sprite_size_changed = False

        if self._sprite_angle_changed:
            self._sprite_angle_buf.write(self._sprite_angle_data)
            self._sprite_angle_changed = False

        if self._sprite_color_changed:
            self._sprite_color_buf.write(self._sprite_color_data)
            self._sprite_color_changed = False

        if self._sprite_sub_tex_changed:
            if not self._keep_textures:
                # Gather all unique textures in a set (Texture hash() is the name)
                textures = set(sprite._texture for sprite in self.sprite_list)
                self._atlas.update_textures(textures, keep_old_textures=self._keep_textures)

            self._sprite_sub_tex_buf.write(self._sprite_sub_tex_data)
            self._sprite_sub_tex_changed = False

        if self._sprite_index_changed:
            self._sprite_index_buf.write(self._sprite_index_data)
            self._sprite_index_changed = False

    def draw(self, **kwargs):
        """
        Draw this list of sprites.

        :param filter: Optional parameter to set OpenGL filter, such as
                       `gl.GL_NEAREST` to avoid smoothing.

        :param blend_function: Optional parameter to set the OpenGL blend function used for drawing the sprite list, such as
                        'arcade.Window.ctx.BLEND_ADDITIVE' or 'arcade.Window.ctx.BLEND_DEFAULT'
        """
        if not self._initialized:
            LOG.warn(
                "SpriteList was created before the window. "
                "Initialization will happen on the first draw() "
                "possibly creating some initial stalls."
            )
            self._init_deferred()

        if len(self.sprite_list) == 0:
            return

        # What percent of this sprite list moved? Used in guessing spatial hashing
        self._percent_sprites_moved = self._sprites_moved / len(self.sprite_list) * 100
        self._sprites_moved = 0

        if any((
            self._sprite_pos_changed,
            self._sprite_size_changed,
            self._sprite_angle_changed,
            self._sprite_color_changed,
            self._sprite_sub_tex_changed,
            self._sprite_index_changed,
            )):
            self._write_sprite_buffers_to_gpu()

        self.ctx.enable(self.ctx.BLEND)
        if "blend_function" in kwargs:
            self.ctx.blend_func = kwargs["blend_function"]
        else:
            self.ctx.blend_func = self.ctx.BLEND_DEFAULT

        if "filter" in kwargs:
            self.atlas.texture.filter = self.ctx.NEAREST, self.ctx.NEAREST

        # TODO: Find a way to re-enable texture transforms
        # texture_transform = None
        # if len(self.sprite_list) > 0:
        #     # always wrap texture transformations with translations
        #     # so that rotate and resize operations act on the texture
        #     # center by default
        #     texture_transform = Matrix3x3().translate(-0.5, -0.5).multiply(self.sprite_list[0].texture_transform.v).multiply(Matrix3x3().translate(0.5, 0.5).v)
        # else:
        #     texture_transform = Matrix3x3()
        # self.program['TextureTransform'] = texture_transform.v

        self.program['TextureTransform'] = Matrix3x3().v

        self._atlas.texture.use(0)
        self._geometry.render(
            self.program,
            mode=self.ctx.POINTS,
            vertices=self._sprite_index_slots,
        )

    def draw_hit_boxes(self, color: Color = (0, 0, 0, 255), line_thickness: float = 1):
        """ Draw all the hit boxes in this list """
        # NOTE: Find a way to efficiently draw this
        for sprite in self.sprite_list:
            sprite.draw_hit_box(color, line_thickness)

    def _normalize_index_buffer(self):
        """
        Removes unused slots in the index buffer.
        The other buffers don't need this because they re-use slots.
        New sprites on the other hand always needs to be added
        to the end of the index buffer to preserve order
        """
        # Need counter for how many slots are used in index buffer.
        # 1) Sort the deleted indices (decending) and pop() them in a loop
        # 2) Create a new array.array and manually copy every
        #    item in the list except the deleted index slots
        # 3) Use a tranform (gpu) to trim the index buffer and
        #    read this buffer back into a new array using array.from_bytes
        # NOTE: Right now the index buffer is always normalized
        pass

    def _grow_sprite_buffers(self):
        """Double the internal buffer sizes"""
        # Resize sprite buffers if needed
        if self._sprite_buffer_slots < self._buf_capacity:
            return

        # double the capacity
        extend_by = self._buf_capacity
        self._buf_capacity = self._buf_capacity * 2

        LOG.debug(
            f"(%s) Increasing buffer capacity from %s to %s",
            self._sprite_buffer_slots,
            extend_by,
            self._buf_capacity,
        )

        # Extend the buffers so we don't lose the old data
        self._sprite_pos_data.extend([0] * extend_by * 2)
        self._sprite_size_data.extend([0] * extend_by * 2)
        self._sprite_angle_data.extend([0] * extend_by)
        self._sprite_color_data.extend([0] * extend_by * 4)
        self._sprite_sub_tex_data.extend([0] * extend_by * 4)

        if self._initialized:
            self._sprite_pos_buf.orphan(size=self._buf_capacity * 4 * 2)
            self._sprite_size_buf.orphan(size=self._buf_capacity * 4 * 2)
            self._sprite_angle_buf.orphan(size=self._buf_capacity * 4)
            self._sprite_color_buf.orphan(size=self._buf_capacity * 4 * 4)
            self._sprite_sub_tex_buf.orphan(size=self._buf_capacity * 4 * 4)

        self._sprite_pos_changed = True
        self._sprite_size_changed = True
        self._sprite_angle_changed = True
        self._sprite_color_changed = True
        self._sprite_sub_tex_changed = True

    def _grow_index_buffer(self):
        # Extend the index buffer capacity if needed
        if self._sprite_index_slots < self._idx_capacity:
            return

        extend_by = self._idx_capacity
        self._idx_capacity = self._idx_capacity * 2

        LOG.debug(
            "Buffers: index_slots=%s sprite_slots=%s over-allocation-ratio=%s",
            self._sprite_index_slots,
            self._sprite_buffer_slots,
            self._sprite_index_slots / self._sprite_buffer_slots
        )

        LOG.debug(
            f"(%s) Increasing index capacity from %s to %s",
            self._sprite_index_slots,
            extend_by,
            self._idx_capacity,
        )

        self._sprite_index_data.extend([0] * extend_by)
        if self._initialized:
            self._sprite_index_buf.orphan(size=self._idx_capacity * 4)

        self._sprite_index_changed = True

    def _dump(self, buffer):
        """
        Debugging method used to dump raw byte data in the OpenGL buffer.
        """
        record_size = len(buffer) / len(self.sprite_list)
        for i, char in enumerate(buffer):
            if i % record_size == 0:
                print()
            print(f"{char:02x} ", end="")


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
    :rtype: bool
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

    :returns: True if sprites overlap.
    :rtype: bool
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
    :rtype: list
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

    if sprite_list.spatial_hash:
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
    :rtype: list
    """
    if not isinstance(sprite_list, SpriteList):
        raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    if sprite_list.spatial_hash:
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
    :rtype: list
    """
    if not isinstance(sprite_list, SpriteList):
        raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    if sprite_list.spatial_hash:
        sprite_list_to_check = sprite_list.spatial_hash.get_objects_for_point(point)
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
        # print("Checks saved: ", checks_saved)
    else:
        sprite_list_to_check = sprite_list

    return [s for s in sprite_list_to_check if s.position == point]
