"""
This module provides a SpriteList class which abstracts batch drawing.

Drawing sprites using SpriteList is orders of magnitude faster than
drawing individual sprites.
"""

import logging
import random
from array import array
from collections import deque
from typing import (
    TYPE_CHECKING,
    Any,
    Deque,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
    Generic,
    Callable,
)

from arcade import (
    Sprite,
    SpriteType,
    get_window,
    gl,
)
from arcade.types import Color, RGBA255
from arcade.color import BLACK
from arcade.gl.buffer import Buffer
from arcade.gl.vertex_array import Geometry

if TYPE_CHECKING:
    from arcade import Texture, TextureAtlas

LOG = logging.getLogger(__name__)

# The slot index that makes a sprite invisible.
# 2^31-1 is usually reserved for primitive restart
# NOTE: Possibly we want to use slot 0 for this?
_SPRITE_SLOT_INVISIBLE = 2000000000

# The default capacity from spritelists
_DEFAULT_CAPACITY = 100


class SpriteList(Generic[SpriteType]):
    """
    SpriteList supports batch operations on sprites, especially drawing

    You should use :py:meth:`.SpriteList.draw` to draw sprites in
    batches because it is much faster than trying to draw them
    individually.

    See the :ref:`Programming Guide's page on SpriteLists <pg_spritelists>`
    for more information on why, as well as an overview of SpriteList's
    advanced features.

    :param bool use_spatial_hash: Set this to ``True`` for
           :ref:`faster collision checking & slower changes <pg_spritelists_spatial_hashing>`
    :param int spatial_hash_cell_size: The cell size of the spatial hash
           in pixels, if enabled (default: 128).
    :param TextureAtlas atlas: :ref:`Override the default/global atlas <pg_spritelist_lazy_spritelists>`
           for this SpriteList.
    :param int capacity: The initial capacity of the internal
           buffer. The default of 100 is usually ok, but you can change
           it when you know a list will be much larger or smaller.
    :param bool lazy: Set this to True to delay creating OpenGL
           resources until the 1st draw or :py:meth:`~.SpriteList.initialize`
           is called. See the :ref:`Programming Guide <pg_spritelist_lazy_spritelists>`
           for more information on when & how to use this.
    :param bool visible: When this is False, calling draw on this list
           will do nothing.
    """

    def __init__(
        self,
        use_spatial_hash: Optional[bool] = None,
        spatial_hash_cell_size: int = 128,
        atlas: Optional["TextureAtlas"] = None,
        capacity: int = 100,
        lazy: bool = False,
        visible: bool = True,
    ):
        self.program = None
        if atlas:
            self._atlas: TextureAtlas = atlas
        self._initialized = False
        self._lazy = lazy
        self._visible = visible
        self._color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)

        # The initial capacity of the SpriteList buffers (internal)
        self._buf_capacity = abs(capacity) or _DEFAULT_CAPACITY
        # The initial capacity of the index buffer (internal)
        self._idx_capacity = abs(capacity) or _DEFAULT_CAPACITY
        # The number of slots used in the sprite buffer
        self._sprite_buffer_slots = 0
        # Number of slots used in the index buffer
        self._sprite_index_slots = 0
        # List of free slots in the sprite buffers. These are filled when sprites are removed.
        self._sprite_buffer_free_slots: Deque[int] = deque()

        # List of sprites in the sprite list
        self.sprite_list: List[SpriteType] = []
        # Buffer slots for the sprites (excluding index buffer)
        # This has nothing to do with the index in the spritelist itself
        self.sprite_slot: Dict[SpriteType, int] = dict()

        # Python representation of buffer data
        self._sprite_pos_data = array("f", [0] * self._buf_capacity * 3)
        self._sprite_size_data = array("f", [0] * self._buf_capacity * 2)
        self._sprite_angle_data = array("f", [0] * self._buf_capacity)
        self._sprite_color_data = array("B", [0] * self._buf_capacity * 4)
        self._sprite_texture_data = array("f", [0] * self._buf_capacity)

        # Index buffer
        self._sprite_index_data = array("i", [0] * self._idx_capacity)

        self._sprite_pos_buf = None
        self._sprite_size_buf = None
        self._sprite_angle_buf = None
        self._sprite_color_buf = None
        self._sprite_texture_buf = None
        # Index buffer
        self._sprite_index_buf = None

        self._geometry = None
        # Flags for signaling if a buffer needs to be written to the opengl buffer
        self._sprite_pos_changed = False
        self._sprite_size_changed = False
        self._sprite_angle_changed = False
        self._sprite_color_changed = False
        self._sprite_texture_changed = False
        self._sprite_index_changed = False

        # Used in collision detection optimization
        from .spatial_hash import SpatialHash

        self._spatial_hash_cell_size = spatial_hash_cell_size
        self.spatial_hash: Optional[SpatialHash] = None
        if use_spatial_hash is True:
            self.spatial_hash = SpatialHash(cell_size=self._spatial_hash_cell_size)

        self.properties: Optional[Dict[str, Any]] = None

        LOG.debug(
            "[%s] Creating SpriteList use_spatial_hash=%s capacity=%s",
            id(self),
            use_spatial_hash,
            self._buf_capacity,
        )

        # Check if the window/context is available
        try:
            get_window()
            if not self._lazy:
                self._init_deferred()
        except RuntimeError:
            pass

    def _init_deferred(self):
        """
        Re-usable abstraction for deferred loading.

        Since SpriteList can be created before the window we need to
        defer initialization. It also allows support for lazy loading.
        """
        if self._initialized:
            return

        self.ctx = get_window().ctx
        self.program = self.ctx.sprite_list_program_cull
        self._atlas: TextureAtlas = (
            getattr(self, "_atlas", None) or self.ctx.default_atlas
        )

        # Buffers for each sprite attribute (read by shader) with initial capacity
        self._sprite_pos_buf = self.ctx.buffer(reserve=self._buf_capacity * 12)  # 3 x 32 bit floats
        self._sprite_size_buf = self.ctx.buffer(reserve=self._buf_capacity * 8)  # 2 x 32 bit floats
        self._sprite_angle_buf = self.ctx.buffer(reserve=self._buf_capacity * 4)  # 32 bit float
        self._sprite_color_buf = self.ctx.buffer(reserve=self._buf_capacity * 4)  # 4 x bytes colors
        self._sprite_texture_buf = self.ctx.buffer(reserve=self._buf_capacity * 4)  # 32 bit int
        # Index buffer
        self._sprite_index_buf = self.ctx.buffer(reserve=self._idx_capacity * 4)  # 32 bit unsigned integers

        contents = [
            gl.BufferDescription(self._sprite_pos_buf, "3f", ["in_pos"]),
            gl.BufferDescription(self._sprite_size_buf, "2f", ["in_size"]),
            gl.BufferDescription(self._sprite_angle_buf, "1f", ["in_angle"]),
            gl.BufferDescription(self._sprite_texture_buf, "1f", ["in_texture"]),
            gl.BufferDescription(
                self._sprite_color_buf, "4f1", ["in_color"], normalized=["in_color"]
            ),
        ]
        self._geometry = self.ctx.geometry(
            contents,
            index_buffer=self._sprite_index_buf,
            index_element_size=4,  # 32 bit integers
        )

        self._initialized = True

        # Load all the textures and write texture coordinates into buffers.
        for sprite in self.sprite_list:
            # noinspection PyProtectedMember
            if sprite._texture is None:
                raise ValueError("Attempting to use a sprite without a texture")
            self._update_texture(sprite)
            if hasattr(sprite, "textures"):
                for texture in sprite.textures or []:
                    self._atlas.add(texture)

        self._sprite_pos_changed = True
        self._sprite_size_changed = True
        self._sprite_angle_changed = True
        self._sprite_color_changed = True
        self._sprite_texture_changed = True
        self._sprite_index_changed = True

    def __len__(self) -> int:
        """Return the length of the sprite list."""
        return len(self.sprite_list)

    def __contains__(self, sprite: Sprite) -> bool:
        """Return if the sprite list contains the given sprite"""
        return sprite in self.sprite_slot

    def __iter__(self) -> Iterator[SpriteType]:
        """Return an iterable object of sprites."""
        return iter(self.sprite_list)

    def __getitem__(self, i):
        return self.sprite_list[i]

    def __setitem__(self, index: int, sprite: SpriteType):
        """Replace a sprite at a specific index"""
        # print(f"{id(self)} : {id(sprite)} __setitem__({index})")

        try:
            existing_index = self.sprite_list.index(sprite)  # raise ValueError
            if existing_index == index:
                return
            raise Exception(f"Sprite is already in the list (index {existing_index})")
        except ValueError:
            pass

        sprite_to_be_removed = self.sprite_list[index]
        sprite_to_be_removed.sprite_lists.remove(self)
        self.sprite_list[index] = sprite  # Replace sprite
        sprite.register_sprite_list(self)

        if self.spatial_hash is not None:
            self.spatial_hash.remove(sprite_to_be_removed)
            self.spatial_hash.add(sprite)

        # Steal the slot from the old sprite
        slot = self.sprite_slot[sprite_to_be_removed]
        del self.sprite_slot[sprite_to_be_removed]
        self.sprite_slot[sprite] = slot

        # Update the internal sprite buffer data
        self._update_all(sprite)

    @property
    def visible(self) -> bool:
        """
        Get or set the visible flag for this SpriteList.

        If visible is ``False``, calling
        :py:meth:`~arcade.SpriteList.draw` has no effect.

        :rtype: bool
        """
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value

    @property
    def color(self) -> Color:
        """
        Get or set the multiply color for all sprites in the list RGBA integers

        This will affect all sprites in the list, and each value must be
        between 0 and 255.

        The color may be specified as any of the following:

        * an RGBA :py:class:`tuple` with each channel value between 0 and 255
        * an instance of :py:class:`~arcade.types.Color`
        * an RGB :py:class:`tuple`, in which case the color will be treated as opaque

        Each individual sprite can also be assigned a color via its
        :py:attr:`~arcade.BasicSprite.color` property.

        When :py:meth:`.SpriteList.draw` is called, each pixel will default
        to a value equivalent to the following:

        1. Convert the sampled texture, sprite, and list colors into normalized floats (0.0 to 1.0)
        2. Multiply the color channels together: ``texture_color * sprite_color * spritelist_color``
        3. Multiply the floating point values by 255 and round the result

        :rtype: Color
        """
        return Color.from_normalized(self._color)

    @color.setter
    def color(self, color: RGBA255):
        self._color = Color.from_iterable(color).normalized

    @property
    def color_normalized(self) -> Tuple[float, float, float, float]:
        """
        Get or set the SpriteList color in normalized form (0.0 -> 1.0 floats).

        Aside from being normalized, this property works the same way as
        :py:attr:`~arcade.SpriteList.color`.
        """
        return self._color

    @color_normalized.setter
    def color_normalized(self, value):
        self._color = value

    @property
    def alpha(self) -> int:
        """
        Get/set the SpriteList's alpha/transparency as a byte value.

        0 is completely transparent/invisible while 255 is opaque. This value
        is taken from the alpha channel of SpriteList's color

        :rtype: int
        """
        return int(self._color[3] * 255)

    @alpha.setter
    def alpha(self, value: int):
        # value = clamp(value, 0, 255)
        self._color = self._color[0], self._color[1], self._color[2], value / 255

    @property
    def alpha_normalized(self) -> float:
        """
        Get/set the SpriteList's alpha/transparency as a normalized float.

        This float is in the range from 0.0 to 1.0, where 0.0 is completely
        transparent/invisible and 1.0 is opaque. This returns the alpha
        channel of SpriteList's color_normalized.

        :rtype: float
        """
        return self._color[3]

    @alpha_normalized.setter
    def alpha_normalized(self, value: float):
        # value = clamp(value, 0.0, 1.0)
        self._color = self._color[0], self._color[1], self._color[2], value

    @property
    def atlas(self) -> "TextureAtlas":
        """Get the texture atlas for this sprite list"""
        return self._atlas

    @property
    def geometry(self) -> Geometry:
        """
        Return the internal OpenGL geometry for this SpriteList.

        This can be used to execute custom shaders with the
        SpriteList data.

        At least one of the following inputs must be defined in your
        vertex shader::

            in vec2 in_pos;
            in float in_angle;
            in vec2 in_size;
            in float in_texture;
            in vec4 in_color;
        """
        if not self._geometry:
            raise ValueError("SpriteList is not initialized.")

        return self._geometry

    @property
    def buffer_positions(self) -> Buffer:
        """
        Get the internal OpenGL position buffer for this SpriteList.

        The buffer contains 32-bit float values with x, y and z
        coordinates for the center positions of each sprite.

        This buffer is attached to the list's :py:attr:`~arcade.SpriteList.geometry`
        instance under the name ``in_pos``.
        """
        if self._sprite_pos_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_pos_buf

    @property
    def buffer_sizes(self) -> Buffer:
        """
        Get the internal OpenGL size buffer for this SpriteList.

        The buffer contains pairs of 32-bit floats recording width and
        height values.

        This buffer is attached to the list's :py:attr:`~arcade.SpriteList.geometry`
        instance under the name ``in_size``.
        """
        if self._sprite_size_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_size_buf

    @property
    def buffer_angles(self) -> Buffer:
        """
        Get the internal OpenGL angle buffer for the SpriteList.

        This buffer contains a series of 32-bit floats
        representing the rotation angle for each sprite in degrees.

        This buffer is attached to the list's :py:attr:`~arcade.SpriteList.geometry`
        instance under the name ``in_angle``.
        """
        if self._sprite_angle_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_angle_buf

    @property
    def buffer_colors(self) -> Buffer:
        """
        Get the internal OpenGL color buffer for this SpriteList.

        This buffer contains a series of 32-bit floats. The RGBA
        multiply color for each individual sprite is stored as 4
        floats, with 1 float per channel.

        This buffer is attached to list's :py:attr:`~arcade.SpriteList.geometry`
        instance under the name ``in_color``.
        """
        if self._sprite_color_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_color_buf

    @property
    def buffer_textures(self) -> Buffer:
        """
        Get the internal OpenGL texture ID buffer of the SpriteList.

        This buffer contains a series of individual 33-bit floats, each
        referencing a texture ID. The ID references a texture in the
        :py:class:`~arcade.TextureAtlas` assigned to
        this SpriteList. The ID is used to look up texture coordinates
        in a 32-bit floating point texture the atlas provides.

        This system allows resizing & rebuilding a TextureAtlas
        without having to rebuild every single SpriteList using it.

        The underlying buffer is attached to the list's
        :py:attr:`~arcade.SpriteList.geometry` instance under the name
        ``in_texture``.

        Although the ID should ideally be an unsigned integer, we store
        them as 32-bit floats for compatibility. We cast them to
        integers in the shader.
        """
        if self._sprite_texture_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_texture_buf

    @property
    def buffer_indices(self) -> Buffer:
        """
        Get the internal index buffer for this SpriteList.

        This index buffer contains integers used as lookup indices
        for data in other buffers. The data in the other buffers is not
        stored in the same order as indexed access via ``spritelist[i]``.

        .. warning:: Use ``len(spritelist)`` to get the number of sprites!

                     The length of internal buffers may be larger than the
                     current number of sprites!

        This index buffer is attached to the :py:attr:`~arcade.SpriteList.geometry`
        instance and will be automatically be applied the input buffers when
        rendering or transforming.
        """
        if self._sprite_index_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_index_buf

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

    def index(self, sprite: SpriteType) -> int:
        """
        Attempt to get the index of the passed :py:class:`~arcade.Sprite`

        If the sprite is not in the list, a :py:class:`ValueError` will
        be raised.

        :param Sprite sprite: A Sprite to attempt to return the index of

        :rtype: int
        """
        return self.sprite_list.index(sprite)

    def clear(self, deep: bool = True):
        """
        Remove all sprites & reset to the initial state.

        This method is ``O(N)`` when ``deep=True`` (default). In this
        mode, this function iterates over all sprites and removes their
        internal references to this SpriteList. Under normal conditions,
        there is a circular reference between :py:class:`~arcade.Sprite`
        instances and any SpriteList holdoing them.

        .. warning:: Using ``deep=False`` is very dangerous!

                     Turning off reference deletion can cause a massive memory
                     if it leaves any references behind! You probably shouldn't
                     change this option! Most people never need it!

        Setting ``deep=False`` will skip removing references to this
        SpriteList from each sprite before removing them. Only use this
        option when you know that the ALL sprites in the list will get
        garbage collected with the list itself. In this case, you can
        safely make clear ``O(1)`` with ``deep=False``.

        :param bool deep: Remove references to this SpriteList from sprites
                          before clearing the list.
        """
        from .spatial_hash import SpatialHash

        # Manually remove the SpriteList from all sprites
        if deep:
            for sprite in self.sprite_list:
                sprite.sprite_lists.remove(self)

        self.sprite_list = []
        self.sprite_slot = dict()

        # Reset SpatialHash
        if self.spatial_hash is not None:
            self.spatial_hash = SpatialHash(cell_size=self._spatial_hash_cell_size)

        # Clear the slot_idx and slot info and other states
        self._buf_capacity = _DEFAULT_CAPACITY
        self._idx_capacity = _DEFAULT_CAPACITY
        self._sprite_buffer_slots = 0
        self._sprite_index_slots = 0
        self._sprite_buffer_free_slots = deque()

        # Reset buffers
        # Python representation of buffer data
        self._sprite_pos_data = array("f", [0] * self._buf_capacity * 3)
        self._sprite_size_data = array("f", [0] * self._buf_capacity * 2)
        self._sprite_angle_data = array("f", [0] * self._buf_capacity)
        self._sprite_color_data = array("B", [0] * self._buf_capacity * 4)
        self._sprite_texture_data = array("f", [0] * self._buf_capacity)
        # Index buffer
        self._sprite_index_data = array("I", [0] * self._idx_capacity)

        if self._initialized:
            self._initialized = False
            self._init_deferred()

    def pop(self, index: int = -1) -> SpriteType:
        """
        Pop off the last sprite, or the given index, from the list.

        This works the same way as :py:meth:`list.pop`, aside from
        running more slowly for SpriteLists with
        :ref:`spatial hashing <pg_spritelists_spatial_hashing>` enabled.

        :param int index: Index of sprite to remove, defaulting to
                          -1 for the last item.
        """
        if len(self.sprite_list) == 0:
            raise (ValueError("pop from empty list"))

        sprite = self.sprite_list[index]
        self.remove(sprite)
        return sprite

    def append(self, sprite: SpriteType):
        """
        Add a new sprite to the end of the list.

        This works the same way as :py:meth:`list.append`, aside from
        running more slowly for SpriteLists with
        :ref:`spatial hashing <pg_spritelists_spatial_hashing>` enabled.

        :param Sprite sprite: A :py:class:`~arcade.Sprite` to add to the
            end of the list.
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

        if self.spatial_hash is not None:
            self.spatial_hash.add(sprite)

        # Load additional textures attached to the sprite
        # if hasattr(sprite, "textures") and self._initialized:
        #     for texture in sprite.textures or []:
        #         self._atlas.add(texture)
        if self._initialized:
            if sprite.texture is None:
                raise ValueError("Sprite must have a texture when added to a SpriteList")
            self._atlas.add(sprite.texture)

    def swap(self, index_1: int, index_2: int):
        """
        Swap the sprites at the passed indices.

        Does not interact with the
        :ref:`spatial hash <pg_spritelists_spatial_hashing>`
        if it is enabled.

        :param int index_1: Item index to swap
        :param int index_2: Item index to swap
        """
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

    def remove(self, sprite: SpriteType):
        """
        Attempt to remove a specific sprite from the list.

        If `sprite` is not in this list, a :py:class:`ValueError` will be
        raised.

        This works the same way as :py:meth:`list.remove`,
        aside from running more slowly for SpriteLists with
        :ref:`spatial hashing <pg_spritelists_spatial_hashing>`
        enabled.

        :param Sprite sprite: Sprite to attempt to remove from the list
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

        if self.spatial_hash is not None:
            self.spatial_hash.remove(sprite)

    def extend(self, sprites: Union[Iterable[SpriteType], "SpriteList"]):
        """
        Extend the current SpriteList from the given iterable.

        This works the same way as :py:meth:`list.extend`, aside from
        running more slowly for SpriteLists with
        :ref:`spatial hashing <pg_spritelists_spatial_hashing>`
        enabled.

        :param list sprites: An Iterable of Sprites to add to the list
        """
        for sprite in sprites:
            self.append(sprite)

    def insert(self, index: int, sprite: SpriteType):
        """
        Inserts a sprite at a given index.

        This works the same way as :py:meth:`list.insert`, aside from
        running more slowly for SpriteLists with
        :ref:`spatial hashing <pg_spritelists_spatial_hashing>`
        enabled.

        :param int index: The index at which to insert the Sprite
        :param Sprite sprite: The :py:class:`~arcade.Sprite` to insert
        """
        if sprite in self.sprite_list:
            raise ValueError("Sprite is already in list")

        index = max(min(len(self.sprite_list), index), 0)

        self.sprite_list.insert(index, sprite)
        sprite.register_sprite_list(self)

        # Allocate a new slot and write the data
        slot = self._next_slot()
        self.sprite_slot[sprite] = slot
        self._update_all(sprite)

        # Allocate room in the index buffer
        self._normalize_index_buffer()
        # idx_slot = self._sprite_index_slots
        self._sprite_index_slots += 1
        self._grow_index_buffer()
        self._sprite_index_data.insert(index, slot)
        self._sprite_index_data.pop()

        if self.spatial_hash is not None:
            self.spatial_hash.add(sprite)

    def reverse(self):
        """
        Reverse the current SpriteList in-place.

        .. tip:: Don't call this after using :py:meth:`.SpriteList.sort`!

                 It is more efficient to pass `reverse=True` to
                 :py:meth:`.SpriteList.sort` instead of calling ``reverse``
                 afterward.

        This works the same way as :py:meth:`list.reverse`. It
        does not interact with the
        :ref:`spatial hash <pg_spritelists_spatial_hashing>`
        if it is enabled.
        """
        # Ensure the index buffer is normalized
        self._normalize_index_buffer()

        # Reverse the sprites and index buffer
        self.sprite_list.reverse()
        # This seems to be the reasonable way to reverse a subset of an array
        reverse_data = self._sprite_index_data[0:len(self.sprite_list)]
        reverse_data.reverse()
        self._sprite_index_data[0:len(self.sprite_list)] = reverse_data

        self._sprite_index_changed = True

    def shuffle(self):
        """
        Shuffles the current list in-place.

        This uses :py:func:`random.shuffle` internally and will behave
        the same way. It does not interact with the
        :ref:`spatial hashing <pg_spritelists_spatial_hashing>`
        if it is enabled.
        """
        # The only thing we need to do when shuffling is to
        # shuffle the sprite_list and index buffer in the same
        # operation. We don't change the sprite buffers.

        # Make sure the index buffer is the same length as the sprite list
        self._normalize_index_buffer()

        # zip index and sprite into pairs and shuffle
        pairs = list(zip(self.sprite_list, self._sprite_index_data))
        random.shuffle(pairs)

        # Reconstruct the lists again from pairs
        sprites, indices = zip(*pairs)
        self.sprite_list = list(sprites)
        self._sprite_index_data = array("I", indices)

        # Resize the index buffer to the original capacity
        if len(self._sprite_index_data) < self._idx_capacity:
            extend_by = self._idx_capacity - len(self._sprite_index_data)
            self._sprite_index_data.extend([0] * extend_by)

        self._sprite_index_changed = True

    def sort(self, *, key: Callable, reverse: bool = False):
        """
        Attempt to sort the SpriteList's contents in place.

        This method works the same way as :py:meth:`list.sort`. It does
        not interact with the
        :ref:`spatial hash <pg_spritelists_spatial_hashing>`
        if it is enabled.

        .. tip:: You should pass a `callable <https://docs.python.org/3/library/functions.html#callable>`_ via ``key``!

                 ``sprite_a < sprite_b`` doesn't mean anything by default,
                 so you have to specify how to sort.

                 See the :ref:`sorting section of the SpriteLists article <pg_spritelists_draw_order_and_sorting>`
                 for more information.

        :param key: A `callable <https://docs.python.org/3/glossary.html#term-callable>`_
                such as a
                `lambda <https://docs.python.org/3/howto/functional.html#small-functions-and-the-lambda-expression>`_
                or function which returns a comparison key.
        :param reverse: If set to ``True``, the sprites will be sorted in reverse
        """
        # Ensure the index buffer is normalized
        self._normalize_index_buffer()

        # In-place sort the spritelist
        self.sprite_list.sort(key=key, reverse=reverse)
        # Loop over the sorted sprites and assign new values in index buffer
        for i, sprite in enumerate(self.sprite_list):
            self._sprite_index_data[i] = self.sprite_slot[sprite]

        self._sprite_index_changed = True

    def disable_spatial_hashing(self) -> None:
        """
        Delete the internal spatial hash object
        """
        self.spatial_hash = None

    def enable_spatial_hashing(self, spatial_hash_cell_size: int = 128):
        """
        Turn on spatial hashing for this SpriteList.

        A new :py:class:`~arcade.SpatialHash` will be created and filled
        from the sprites in the list.

        :param spatial_hash_cell_size: The size of the hash cell size in pixels.
        """
        if self.spatial_hash is None or self.spatial_hash.cell_size != spatial_hash_cell_size:
            LOG.debug("Enabled spatial hashing with cell size %s", spatial_hash_cell_size)
            from .spatial_hash import SpatialHash
            self.spatial_hash = SpatialHash(cell_size=spatial_hash_cell_size)
            self._recalculate_spatial_hashes()
        else:
            LOG.debug("Spatial hashing is already enabled with size %s", spatial_hash_cell_size)

    def _recalculate_spatial_hashes(self):
        if self.spatial_hash is None:
            from .spatial_hash import SpatialHash
            self.spatial_hash = SpatialHash(cell_size=self._spatial_hash_cell_size)

        self.spatial_hash.reset()
        for sprite in self.sprite_list:
            self.spatial_hash.add(sprite)

    def update(self) -> None:
        """
        Call the update() method on each sprite in the list.

        If any sprites move or otherwise change their hitboxes,
        the :ref:`spatial hash <pg_spritelists_spatial_hashing>` will
        be updated if it is enabled.
        """
        for sprite in self.sprite_list:
            sprite.update()

    def on_update(self, delta_time: float = 1 / 60):
        """
        Update the sprite using the passed time step.

        Similar to :py:meth:`.SpriteList.update`, except it calls
        :py:meth:`arcade.Sprite.on_update` with the same ``delta_time``
        value on each Sprite instead.

        If any sprites move or otherwise change their hitboxes,
        the :ref:`spatial hash <pg_spritelists_spatial_hashing>` will
        be updated if it is enabled.

        :param delta_time: The time step to pass to each :py:class:~arcade.Sprite`
        """
        for sprite in self.sprite_list:
            sprite.on_update(delta_time)

    def update_animation(self, delta_time: float = 1 / 60):
        """
        Call :py:meth:`arcade.Sprite.update_animation` on every Sprite in the SpriteList

        If this changes the texture, this may trigger an update of the
        :ref:`spatial hash <pg_spritelists_spatial_hashing>`
        if it is enabled.

        :param delta_time: The time step to update the animation by.
        """
        # NOTE: Can we limit this to animated sprites?
        for sprite in self.sprite_list:
            sprite.update_animation(delta_time)

    def _get_center(self) -> Tuple[float, float]:
        """Get the mean center coordinates of all sprites in the list."""
        x = sum((sprite.center_x for sprite in self.sprite_list)) / len(
            self.sprite_list
        )
        y = sum((sprite.center_y for sprite in self.sprite_list)) / len(
            self.sprite_list
        )
        return x, y

    center = property(_get_center)

    def rescale(self, factor: float) -> None:
        """
        Rescale all Sprites in this list relative to this SpriteList's center.

        This can be a very expensive operation if this SpriteList
        contains many :py:class:`~arcade.Sprite` instances, especially
        if :ref:`spatial hashing <pg_spritelists_spatial_hashing>` is
        enabled.

        :param float factor: the factor to scale by.
        """
        for sprite in self.sprite_list:
            sprite.rescale_relative_to_point(self.center, factor)

    def move(self, change_x: float, change_y: float) -> None:
        """
        Move all Sprites in this list by the same amount.

        This can be a very expensive operation if this SpriteList
        contains many :py:class:`~arcade.Sprite` instances, especially
        if :ref:`spatial hashing <pg_spritelists_spatial_hashing>` is
        enabled.

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

    def write_sprite_buffers_to_gpu(self) -> None:
        """
        Resize & synchronize data, writing it to the GPU.

        If you have added, removed, moved or changed ANY sprite property,
        this method will synchronize the data from RAM to the GPU's memory.
        This includes buffer resizing and writing the new data to VRAM.

        It is automatically called in :py:meth:`SpriteList.draw`, but
        there are cases when using custom shaders will mean you must force
        synchronization because :py:meth:`SpriteList.draw` may not have been
        called since the SpriteList was modified.
        """
        self._write_sprite_buffers_to_gpu()

    def _write_sprite_buffers_to_gpu(self):
        LOG.debug(
            "[%s] SpriteList._write_sprite_buffers_to_gpu: pos=%s, size=%s, angle=%s, color=%s tex=%s idx=%s",
            id(self),
            self._sprite_pos_changed,
            self._sprite_size_changed,
            self._sprite_angle_changed,
            self._sprite_color_changed,
            self._sprite_texture_changed,
            self._sprite_index_changed,
        )

        if self._sprite_pos_changed and self._sprite_pos_buf:
            self._sprite_pos_buf.orphan()
            self._sprite_pos_buf.write(self._sprite_pos_data)
            self._sprite_pos_changed = False

        if self._sprite_size_changed and self._sprite_size_buf:
            self._sprite_size_buf.orphan()
            self._sprite_size_buf.write(self._sprite_size_data)
            self._sprite_size_changed = False

        if self._sprite_angle_changed and self._sprite_angle_buf:
            self._sprite_angle_buf.orphan()
            self._sprite_angle_buf.write(self._sprite_angle_data)
            self._sprite_angle_changed = False

        if self._sprite_color_changed and self._sprite_color_buf:
            self._sprite_color_buf.orphan()
            self._sprite_color_buf.write(self._sprite_color_data)
            self._sprite_color_changed = False

        if self._sprite_texture_changed and self._sprite_texture_buf:
            self._sprite_texture_buf.orphan()
            self._sprite_texture_buf.write(self._sprite_texture_data)
            self._sprite_texture_changed = False

        if self._sprite_index_changed and self._sprite_index_buf:
            self._sprite_index_buf.orphan()
            self._sprite_index_buf.write(self._sprite_index_data)
            self._sprite_index_changed = False

    def initialize(self):
        """
        Allocate internal OpenGL abstractions & their underlying GPU resources

        .. warning:: Only the main thread is allowed to access OpenGL!

                     Calling this method outside the main thread will
                     raise an OpenGL error.

        If the SpriteList is already fully initialized, this method will
        return without having any effect.

        Otherwise, this method is useful for
        :ref:`controlling lazy SpriteLists <pg_spritelist_lazy_spritelists>`
        as part of performance optimization or unit tests.
        """
        self._init_deferred()

    def draw(self, *, filter: Optional[int] = None, pixelated: bool = False, blend_function: Optional[int] = None):
        """
        Draw this SpriteList into the current OpenGL context.

        By default, SpriteLists draw starting from their lowest index
        toward their highest.

        For the best results when using pixel art, use
        ``pixelated=True`` and follow the advice of the
        :ref:`Programming Guide's article on edge artifacts <edge_artifacts>`.

        :param filter: Set a custom OpenGL filter, such as ``gl.GL_NEAREST``
            to avoid smoothing.
        :param pixelated: Set this to ``True`` as a memorable shorthand for setting
            ``filter=GL_NEAREST``.
        :param blend_function: Use a custom OpenGL blend function for drawing this
            SpriteList, such as ``arcade.Window.ctx.BLEND_ADDITIVE`` or
            ``arcade.Window.ctx.BLEND_DEFAULT``
        """
        if len(self.sprite_list) == 0 or not self._visible or self.alpha_normalized == 0.0:
            return

        self._init_deferred()
        self._write_sprite_buffers_to_gpu()

        self.ctx.enable(self.ctx.BLEND)
        # Set custom blend function or revert to default
        if blend_function is not None:
            self.ctx.blend_func = blend_function
        else:
            self.ctx.blend_func = self.ctx.BLEND_DEFAULT

        # Set custom filter or reset to default
        if filter:
            self.atlas.texture.filter = filter, filter
        else:
            self.atlas.texture.filter = self.ctx.LINEAR, self.ctx.LINEAR

        # Handle the pixelated shortcut
        if pixelated:
            self.atlas.texture.filter = self.ctx.NEAREST, self.ctx.NEAREST
        else:
            self.atlas.texture.filter = self.ctx.LINEAR, self.ctx.LINEAR

        if not self.program:
            raise ValueError("Attempting to render without 'program' field being set.")

        self.program["spritelist_color"] = self._color

        self._atlas.texture.use(0)
        self._atlas.use_uv_texture(1)
        if not self._geometry:
            raise ValueError("Attempting to render without '_geometry' field being set.")
        self._geometry.render(
            self.program,
            mode=self.ctx.POINTS,
            vertices=self._sprite_index_slots,
        )

    def draw_hit_boxes(self, color: RGBA255 = BLACK, line_thickness: float = 1):
        """
        Draw the hit boxes of sprites as lines of the passed color & thickness

        :param color: The color to draw the hit boxes with.
        :param line_thickness: How many pixels wide the lines should be.
        """
        # NOTE: Find a way to efficiently draw this
        for sprite in self.sprite_list:
            sprite.draw_hit_box(color, line_thickness)

    def _normalize_index_buffer(self):
        """
        Removes unused slots in the index buffer.

        The other buffers don't need this because they re-use slots. New
        sprites, on the other hand, always need to be added to the end
        of the index buffer to preserve order.
        """
        # NOTE: Currently we keep the index buffer normalized
        #       but we can increase the performance in the future
        #       delaying normalization.
        # Need counter for how many slots are used in index buffer.
        # 1) Sort the deleted indices (descending) and pop() them in a loop
        # 2) Create a new array.array and manually copy every
        #    item in the list except the deleted index slots
        # 3) Use a transform (gpu) to trim the index buffer and
        #    read this buffer back into a new array using array.from_bytes
        # NOTE: Right now the index buffer is always normalized
        pass

    def _grow_sprite_buffers(self):
        """Double the internal buffer sizes"""
        # Resize sprite buffers if needed
        if self._sprite_buffer_slots <= self._buf_capacity:
            return

        # Double the capacity
        extend_by = self._buf_capacity
        self._buf_capacity = self._buf_capacity * 2

        LOG.debug(
            "(%s) Increasing buffer capacity from %s to %s",
            self._sprite_buffer_slots,
            extend_by,
            self._buf_capacity,
        )

        # Extend the buffers so we don't lose the old data
        self._sprite_pos_data.extend([0] * extend_by * 3)
        self._sprite_size_data.extend([0] * extend_by * 2)
        self._sprite_angle_data.extend([0] * extend_by)
        self._sprite_color_data.extend([0] * extend_by * 4)
        self._sprite_texture_data.extend([0] * extend_by)

        if self._initialized:
            self._sprite_pos_buf.orphan(double=True)
            self._sprite_size_buf.orphan(double=True)
            self._sprite_angle_buf.orphan(double=True)
            self._sprite_color_buf.orphan(double=True)
            self._sprite_texture_buf.orphan(double=True)

        self._sprite_pos_changed = True
        self._sprite_size_changed = True
        self._sprite_angle_changed = True
        self._sprite_color_changed = True
        self._sprite_texture_changed = True

    def _grow_index_buffer(self):
        # Extend the index buffer capacity if needed
        if self._sprite_index_slots <= self._idx_capacity:
            return

        extend_by = self._idx_capacity
        self._idx_capacity = self._idx_capacity * 2

        LOG.debug(
            "Buffers: index_slots=%s sprite_slots=%s over-allocation-ratio=%s",
            self._sprite_index_slots,
            self._sprite_buffer_slots,
            self._sprite_index_slots / self._sprite_buffer_slots,
        )

        LOG.debug(
            "(%s) Increasing index capacity from %s to %s",
            self._sprite_index_slots,
            extend_by,
            self._idx_capacity,
        )

        self._sprite_index_data.extend([0] * extend_by)
        if self._initialized and self._sprite_index_buf:
            self._sprite_index_buf.orphan(size=self._idx_capacity * 4)

        self._sprite_index_changed = True

    def _update_all(self, sprite: SpriteType):
        """
        Update all sprite data. This is faster when adding and moving sprites.
        This duplicate code, but reduces call overhead, dict lookups etc.
        """
        slot = self.sprite_slot[sprite]
        # position
        self._sprite_pos_data[slot * 3] = sprite._position[0]
        self._sprite_pos_data[slot * 3 + 1] = sprite._position[1]
        self._sprite_pos_data[slot * 3 + 2] = sprite._depth
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
        self._sprite_color_data[slot * 4 + 3] = sprite._color[3]
        self._sprite_color_changed = True

        # Don't deal with textures if spritelist is not initialized.
        # This can often mean we don't have a context/window yet.
        if not self._initialized:
            return

        if not sprite._texture:
            return

        tex_slot, _ = self._atlas.add(sprite._texture)
        slot = self.sprite_slot[sprite]

        self._sprite_texture_data[slot] = tex_slot
        self._sprite_texture_changed = True

    def _update_texture(self, sprite) -> None:
        """Make sure we update the texture for this sprite for the next batch
        drawing"""
        # We cannot interact with texture atlases unless the context
        # is created. We defer all texture initialization for later
        if not self._initialized:
            return

        if not sprite._texture:
            return

        tex_slot, _ = self._atlas.add(sprite._texture)
        slot = self.sprite_slot[sprite]

        self._sprite_texture_data[slot] = tex_slot
        self._sprite_texture_changed = True

        # Update size in cas the sprite was initialized without size
        # NOTE: There should be a better way to do this
        self._sprite_size_data[slot * 2] = sprite._width
        self._sprite_size_data[slot * 2 + 1] = sprite._height
        self._sprite_size_changed = True

    def _update_position(self, sprite: SpriteType) -> None:
        """
        Called when setting initial position of a sprite when
        added or inserted into the SpriteList.

        ``update_location`` should be called to move them
        once the sprites are in the list.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_pos_data[slot * 3] = sprite._position[0]
        self._sprite_pos_data[slot * 3 + 1] = sprite._position[1]
        self._sprite_pos_changed = True

    def _update_position_x(self, sprite: SpriteType) -> None:
        """
        Called when setting initial position of a sprite when
        added or inserted into the SpriteList.

        ``update_location`` should be called to move them
        once the sprites are in the list.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_pos_data[slot * 3] = sprite._position[0]
        self._sprite_pos_changed = True

    def _update_position_y(self, sprite: SpriteType) -> None:
        """
        Called when setting initial position of a sprite when
        added or inserted into the SpriteList.

        ``update_location`` should be called to move them
        once the sprites are in the list.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_pos_data[slot * 3 + 1] = sprite._position[1]
        self._sprite_pos_changed = True

    def _update_depth(self, sprite: SpriteType) -> None:
        """
        Called by the Sprite class to update the depth of the specified sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_pos_data[slot * 3 + 2] = sprite._depth
        self._sprite_pos_changed = True

    def _update_color(self, sprite: SpriteType) -> None:
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
        self._sprite_color_data[slot * 4 + 3] = int(sprite._color[3])
        self._sprite_color_changed = True

    def _update_size(self, sprite: SpriteType) -> None:
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_size_data[slot * 2] = sprite._width
        self._sprite_size_data[slot * 2 + 1] = sprite._height
        self._sprite_size_changed = True

    def _update_width(self, sprite: SpriteType):
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_size_data[slot * 2] = sprite._width
        self._sprite_size_changed = True

    def _update_height(self, sprite: SpriteType):
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_size_data[slot * 2 + 1] = sprite._height
        self._sprite_size_changed = True

    def _update_angle(self, sprite: SpriteType):
        """
        Called by the Sprite class to update the angle in this sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_angle_data[slot] = sprite._angle
        self._sprite_angle_changed = True
