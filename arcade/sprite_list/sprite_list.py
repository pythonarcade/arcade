"""
This module provides functionality to manage Sprites in a list
and efficiently batch drawing them. Drawing sprites using
SpriteList is orders of magnitude faster then drawing
individual sprites.
"""

from __future__ import annotations

# import logging
import random
from array import array
from collections import deque
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Deque,
    Generic,
    Iterable,
    Iterator,
    Sized,
    cast,
)

from arcade import (
    Sprite,
    SpriteType,
    get_window,
    gl,
)
from arcade.gl import Program, Texture2D
from arcade.gl.buffer import Buffer
from arcade.gl.types import BlendFunction, OpenGlFilter, PyGLenum
from arcade.gl.vertex_array import Geometry
from arcade.types import RGBA255, Color, RGBANormalized, RGBOrANormalized
from arcade.utils import copy_dunders_unimplemented

if TYPE_CHECKING:
    from arcade import DefaultTextureAtlas, Texture
    from arcade.texture_atlas import TextureAtlasBase

# LOG = logging.getLogger(__name__)

# The slot index that makes a sprite invisible.
# 2^31-1 is usually reserved for primitive restart
# NOTE: Possibly we want to use slot 0 for this?
_SPRITE_SLOT_INVISIBLE = 2000000000

# The default capacity from spritelists
_DEFAULT_CAPACITY = 100


@copy_dunders_unimplemented  # Temp fixes https://github.com/pythonarcade/arcade/issues/2074
class SpriteList(Generic[SpriteType]):
    """
    The purpose of the spriteList is to batch draw a list of sprites.
    Drawing single sprites will not get you anywhere performance wise
    as the number of sprites in your project increases. The spritelist
    contains many low level optimizations taking advantage of your
    graphics processor. To put things into perspective, a spritelist
    can contain tens of thousands of sprites without any issues.
    Sprites outside the viewport/window will not be rendered.

    If the spritelist are going to be used for collision it's a good
    idea to enable spatial hashing. Especially if no sprites are moving.
    This will make collision checking **a lot** faster.
    In technical terms collision checking is ``O(1)`` with spatial hashing
    enabled and ``O(N)`` without. However, if you have a
    list of moving sprites the cost of updating the spatial hash
    when they are moved can be greater than what you save with
    spatial collision checks. This needs to be profiled on a
    case by case basis.

    For the advanced options check the advanced section in the
    Arcade documentation.

    Args:
        use_spatial_hash:
            If set to True, this will make creating a sprite, and moving a sprite
            in the SpriteList slower, but it will speed up collision detection
            with items in the SpriteList. Great for doing collision detection
            with static walls/platforms in large maps.
        spatial_hash_cell_size:
            The cell size of the spatial hash (default: 128)
        atlas:
            (Advanced) The texture atlas for this sprite list. If no
            atlas is supplied the global/default one will be used.
        capacity:
            (Advanced) The initial capacity of the internal buffer.
            It's a suggestion for the maximum amount of sprites this list
            can hold. Can normally be left with default value.
        lazy:
            (Advanced) ``True`` delays creating OpenGL resources
            for the sprite list until either its :py:meth:`~SpriteList.draw`
            or :py:meth:`~SpriteList.initialize` method is called. See
            :ref:`pg_spritelist_advanced_lazy_spritelists` to learn more.
        visible:
            Setting this to False will cause the SpriteList to not
            be drawn. When draw is called, the method will just return without drawing.
    """

    #: The default texture filter used when no other filter is specified.
    #: This can be used to change the global default for all spritelists
    #:
    #: Example::
    #:
    #:     from arcade import gl
    #:     # Set global default to nearest filtering (pixelated)
    #:     arcade.SpriteList.DEFAULT_TEXTURE_FILTER = gl.NEAREST, gl.NEAREST
    #:     # Set global default to linear filtering (smooth). This is the default.
    #:     arcade.SpriteList.DEFAULT_TEXTURE_FILTER = gl.NEAREST, gl.NEAREST
    DEFAULT_TEXTURE_FILTER: ClassVar[tuple[int, int]] = gl.LINEAR, gl.LINEAR

    def __init__(
        self,
        use_spatial_hash: bool = False,
        spatial_hash_cell_size: int = 128,
        atlas: TextureAtlasBase | None = None,
        capacity: int = 100,
        lazy: bool = False,
        visible: bool = True,
    ) -> None:
        self.program: Program | None = None
        self._atlas: TextureAtlasBase | None = atlas
        self._initialized = False
        self._lazy = lazy
        self._visible = visible
        self._blend = True
        self._color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)

        # The initial capacity of the spritelist buffers (internal)
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
        self.sprite_list: list[SpriteType] = []
        # Buffer slots for the sprites (excluding index buffer)
        # This has nothing to do with the index in the spritelist itself
        self.sprite_slot: dict[SpriteType, int] = dict()

        # Python representation of buffer data
        self._sprite_pos_data = array("f", [0] * self._buf_capacity * 3)
        self._sprite_size_data = array("f", [0] * self._buf_capacity * 2)
        self._sprite_angle_data = array("f", [0] * self._buf_capacity)
        self._sprite_color_data = array("B", [0] * self._buf_capacity * 4)
        self._sprite_texture_data = array("f", [0] * self._buf_capacity)
        # Index buffer
        self._sprite_index_data = array("i", [0] * self._idx_capacity)

        # Define and annotate storage space for buffers
        self._sprite_pos_buf: Buffer | None = None
        self._sprite_size_buf: Buffer | None = None
        self._sprite_angle_buf: Buffer | None = None
        self._sprite_color_buf: Buffer | None = None
        self._sprite_texture_buf: Buffer | None = None

        # Index buffer
        self._sprite_index_buf: Buffer | None = None

        self._geometry: Geometry | None = None

        # Flags for signaling if a buffer needs to be written to the OpenGL buffer
        self._sprite_pos_changed: bool = False
        self._sprite_size_changed: bool = False
        self._sprite_angle_changed: bool = False
        self._sprite_color_changed: bool = False
        self._sprite_texture_changed: bool = False
        self._sprite_index_changed: bool = False

        # Used in collision detection optimization
        from .spatial_hash import SpatialHash

        self._spatial_hash_cell_size = spatial_hash_cell_size
        self.spatial_hash: SpatialHash[SpriteType] | None = None
        if use_spatial_hash:
            self.spatial_hash = SpatialHash(cell_size=self._spatial_hash_cell_size)

        self.properties: dict[str, Any] | None = None

        # LOG.debug(
        #     "[%s] Creating SpriteList use_spatial_hash=%s capacity=%s",
        #     id(self),
        #     use_spatial_hash,
        #     self._buf_capacity,
        # )

        # Check if the window/context is available
        try:
            get_window()
            if not self._lazy:
                self._init_deferred()
        except RuntimeError:
            pass

    def _init_deferred(self) -> None:
        """
        Since spritelist can be created before the window we need to defer initialization.

        It also makes us able to support lazy loading.
        """
        if self._initialized:
            return

        self.ctx = get_window().ctx
        self.program = self.ctx.sprite_list_program_cull
        if not self._atlas:
            self._atlas = self.ctx.default_atlas

        # Buffers for each sprite attribute (read by shader) with initial capacity
        self._sprite_pos_buf = self.ctx.buffer(reserve=self._buf_capacity * 12)  # 3 x 32 bit floats
        self._sprite_size_buf = self.ctx.buffer(reserve=self._buf_capacity * 8)  # 2 x 32 bit floats
        self._sprite_angle_buf = self.ctx.buffer(reserve=self._buf_capacity * 4)  # 32 bit float
        self._sprite_color_buf = self.ctx.buffer(reserve=self._buf_capacity * 4)  # 4 x bytes colors
        self._sprite_texture_buf = self.ctx.buffer(reserve=self._buf_capacity * 4)  # 32 bit int
        # Index buffer
        self._sprite_index_buf = self.ctx.buffer(
            reserve=self._idx_capacity * 4
        )  # 32 bit unsigned integers

        contents = [
            gl.BufferDescription(self._sprite_pos_buf, "3f", ["in_pos"]),
            gl.BufferDescription(self._sprite_size_buf, "2f", ["in_size"]),
            gl.BufferDescription(self._sprite_angle_buf, "1f", ["in_angle"]),
            gl.BufferDescription(self._sprite_texture_buf, "1f", ["in_texture"]),
            gl.BufferDescription(
                self._sprite_color_buf,
                "4f1",
                ["in_color"],
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
            if sprite._texture is None:
                raise ValueError("Attempting to use a sprite without a texture")
            self._update_texture(sprite)
            if hasattr(sprite, "textures"):
                if TYPE_CHECKING:
                    assert isinstance(sprite, Sprite)
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

    def __getitem__(self, i: int) -> SpriteType:
        return self.sprite_list[i]

    def __setitem__(self, index: int, sprite: SpriteType) -> None:
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
        Get or set the visible flag for this spritelist.

        If visible is ``False`` the ``draw()`` has no effect.
        """
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value

    @property
    def blend(self) -> bool:
        """Enable or disable alpha blending for the spritelist."""
        return self._blend

    @blend.setter
    def blend(self, value: bool) -> None:
        self._blend = value

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
        """
        return Color.from_normalized(self._color)

    @color.setter
    def color(self, color: RGBA255) -> None:
        self._color = Color.from_iterable(color).normalized

    @property
    def color_normalized(self) -> RGBANormalized:
        """
        Get or set the spritelist color in normalized form (0.0 -> 1.0 floats).

        This property works the same as :py:attr:`~arcade.SpriteList.color`.
        """
        return self._color

    @color_normalized.setter
    def color_normalized(self, value: RGBOrANormalized) -> None:
        try:
            r, g, b, *_a = value
            assert len(_a) <= 1
        except (ValueError, AssertionError) as e:
            raise ValueError("color_normalized must unpack as 3 or 4 float values") from e

        self._color = r, g, b, _a[0] if _a else 1.0

    @property
    def alpha(self) -> int:
        """
        Get or set the alpha/transparency of the entire spritelist.

        This is a byte value from 0 to 255 were 0 is completely
        transparent/invisible and 255 is opaque.
        """
        return int(self._color[3] * 255)

    @alpha.setter
    def alpha(self, value: int) -> None:
        # value = clamp(value, 0, 255)
        self._color = self._color[0], self._color[1], self._color[2], value / 255

    @property
    def alpha_normalized(self) -> float:
        """
        Get or set the alpha/transparency of all the sprites in the list.

        This is a floating point number from 0.0 to 1.0 were 0.0 is completely
        transparent/invisible and 1.0 is opaque.

        This is a shortcut for setting the alpha value in the spritelist color.
        """
        return self._color[3]

    @alpha_normalized.setter
    def alpha_normalized(self, value: float) -> None:
        # value = clamp(value, 0.0, 1.0)
        self._color = self._color[0], self._color[1], self._color[2], value

    @property
    def atlas(self) -> TextureAtlasBase | None:
        """Get the texture atlas for this sprite list"""
        return self._atlas

    @property
    def geometry(self) -> Geometry:
        """
        Returns the internal OpenGL geometry for this spritelist.
        This can be used to execute custom shaders with the
        spritelist data.

        One or multiple of the following inputs must be defined in your vertex shader::

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
        Get the internal OpenGL position buffer for this spritelist.

        The buffer contains 32 bit float values with
        x, y and z positions. These are the center positions
        for each sprite.

        This buffer is attached to the :py:attr:`~arcade.SpriteList.geometry`
        instance with name ``in_pos``.
        """
        if self._sprite_pos_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_pos_buf

    @property
    def buffer_sizes(self) -> Buffer:
        """
        Get the internal OpenGL size buffer for this spritelist.

        The buffer contains 32 bit float width and height values.

        This buffer is attached to the :py:attr:`~arcade.SpriteList.geometry`
        instance with name ``in_size``.
        """
        if self._sprite_size_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_size_buf

    @property
    def buffer_angles(self) -> Buffer:
        """
        Get the internal OpenGL angle buffer for the spritelist.

        This buffer contains a series of 32 bit floats
        representing the rotation angle for each sprite in degrees.

        This buffer is attached to the :py:attr:`~arcade.SpriteList.geometry`
        instance with name ``in_angle``.
        """
        if self._sprite_angle_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_angle_buf

    @property
    def buffer_colors(self) -> Buffer:
        """
        Get the internal OpenGL color buffer for this spritelist.

        This buffer contains a series of 32 bit floats representing
        the RGBA color for each sprite. 4 x floats = RGBA.


        This buffer is attached to the :py:attr:`~arcade.SpriteList.geometry`
        instance with name ``in_color``.
        """
        if self._sprite_color_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_color_buf

    @property
    def buffer_textures(self) -> Buffer:
        """
        Get the internal openGL texture id buffer for the spritelist.

        This buffer contains a series of single 32 bit floats referencing
        a texture ID. This ID references a texture in the texture
        atlas assigned to this spritelist. The ID is used to look up
        texture coordinates in a 32bit floating point texture the
        texture atlas provides. This system makes sure we can resize
        and rebuild a texture atlas without having to rebuild every
        single spritelist.

        This buffer is attached to the :py:attr:`~arcade.SpriteList.geometry`
        instance with name ``in_texture``.

        Note that it should ideally an unsigned integer, but due to
        compatibility we store them as 32 bit floats. We cast them
        to integers in the shader.
        """
        if self._sprite_texture_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_texture_buf

    @property
    def buffer_indices(self) -> Buffer:
        """
        Get the internal index buffer for this spritelist.

        The data in the other buffers are not in the correct order
        matching ``spritelist[i]``. The index buffer has to be
        used used to resolve the right order. It simply contains
        a series of integers referencing locations in the other buffers.

        Also note that the length of this buffer might be bigger than
        the number of sprites. Rely on ``len(spritelist)`` for the
        correct length.

        This index buffer is attached to the :py:attr:`~arcade.SpriteList.geometry`
        instance and will be automatically be applied the the input buffers
        when rendering or transforming.
        """
        if self._sprite_index_buf is None:
            raise ValueError("SpriteList is not initialized")
        return self._sprite_index_buf

    def _next_slot(self) -> int:
        """
        Get the next available slot in sprite buffers

        :return: index slot, buffer_slot
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
        Return the index of a sprite in the spritelist

        Args:
            sprite: Sprite to find and return the index of
        """
        return self.sprite_list.index(sprite)

    def clear(self, *, capacity: int | None = None, deep: bool = True) -> None:
        """
        Remove all the sprites resetting the spritelist
        to it's initial state.

        The complexity of this method is ``O(N)`` with a deep clear (default).

        If ALL the sprites in the list gets garbage collected with the list itself
        you can do an ``O(1)``` clear using ``deep=False``. **Make sure you know
        exactly what you are doing before using this option.** Any lingering sprite
        reference will cause a massive memory leak. The ``deep`` option will
        iterate all the sprites and remove their references to this spritelist.
        Sprite and SpriteList have a circular reference for performance reasons.

        Args:
            deep: Whether to do a deep clear or not. Default is ``True``.
            capacity: The size of the internal buffers used to store the sprites.
                      Defaults to preserving the current capacity.
        """
        from .spatial_hash import SpatialHash

        # Manually remove the spritelist from all sprites
        if deep:
            for sprite in self.sprite_list:
                sprite.sprite_lists.remove(self)

        self.sprite_list = []
        self.sprite_slot = dict()

        # Reset SpatialHash
        if self.spatial_hash is not None:
            self.spatial_hash = SpatialHash(cell_size=self._spatial_hash_cell_size)

        # Clear the slot_idx and slot info and other states
        capacity = abs(capacity or self._buf_capacity)

        self._buf_capacity = capacity
        self._idx_capacity = capacity
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
        """Attempt to pop a sprite from the list.

        This works like :external:ref:`popping from <tut-morelists>` a
        standard Python :py:class:`list`:

        #. If the list is empty, raise an :py:class:`IndexError`
        #. If no ``index`` is passed, try to pop the last
           :py:class:`Sprite` in the list

        Args:
            index:
                Index of sprite to remove (defaults to ``-1`` for the last item)
        """
        if len(self.sprite_list) == 0:
            raise IndexError("pop from empty list")

        sprite = self.sprite_list[index]
        self.remove(sprite)
        return sprite

    def append(self, sprite: SpriteType) -> None:
        """
        Add a new sprite to the list.

        Args:
            sprite: Sprite to add to the list.
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
            self._atlas.add(sprite.texture)  # type: ignore

    def swap(self, index_1: int, index_2: int) -> None:
        """
        Swap two sprites by index.

        Args:
            index_1: Item index to swap
            index_2: Item index to swap
        """
        # Swap order in python spritelist
        sprite_1 = self.sprite_list[index_1]
        sprite_2 = self.sprite_list[index_2]
        self.sprite_list[index_1] = sprite_2
        self.sprite_list[index_2] = sprite_1

        # Swap order in index buffer to change rendering order
        slot_1 = self.sprite_slot[sprite_1]
        slot_2 = self.sprite_slot[sprite_2]
        i1 = self._sprite_index_data.index(slot_1)
        i2 = self._sprite_index_data.index(slot_2)
        self._sprite_index_data[i1] = slot_2
        self._sprite_index_data[i2] = slot_1

        self._sprite_index_changed = True

    def remove(self, sprite: SpriteType) -> None:
        """
        Remove a specific sprite from the list.

        Args:
            sprite: Item to remove from the list
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

    def extend(self, sprites: Iterable[SpriteType] | SpriteList[SpriteType]) -> None:
        """
        Extends the current list with the given iterable

        Args:
            sprites: Iterable of Sprites to add to the list
        """
        for sprite in sprites:
            self.append(sprite)

    def insert(self, index: int, sprite: SpriteType) -> None:
        """
        Inserts a sprite at a given index.

        Args:
            index: The index at which to insert
            sprite: The sprite to insert
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

    def reverse(self) -> None:
        """Reverses the current list in-place"""
        # Ensure the index buffer is normalized
        self._normalize_index_buffer()

        # Reverse the sprites and index buffer
        self.sprite_list.reverse()
        # This seems to be the reasonable way to reverse a subset of an array
        reverse_data = self._sprite_index_data[0 : len(self.sprite_list)]
        reverse_data.reverse()
        self._sprite_index_data[0 : len(self.sprite_list)] = reverse_data

        self._sprite_index_changed = True

    def shuffle(self) -> None:
        """Shuffles the current list in-place"""
        # The only thing we need to do when shuffling is
        # to shuffle the sprite_list and index buffer in
        # in the same operation. We don't change the sprite buffers

        # Make sure the index buffer is the same length as the sprite list
        self._normalize_index_buffer()

        # zip index and sprite into pairs and shuffle
        pairs = list(zip(self.sprite_list, self._sprite_index_data))
        random.shuffle(pairs)

        # Reconstruct the lists again from pairs
        sprites, indices = cast(tuple[list[SpriteType], list[int]], zip(*pairs))
        self.sprite_list = list(sprites)
        self._sprite_index_data = array("I", indices)

        # Resize the index buffer to the original capacity
        if len(self._sprite_index_data) < self._idx_capacity:
            extend_by = self._idx_capacity - len(self._sprite_index_data)
            self._sprite_index_data.extend([0] * extend_by)

        self._sprite_index_changed = True

    def sort(self, *, key: Callable, reverse: bool = False) -> None:
        """
        Sort the spritelist in place using ``<`` comparison between sprites.
        This function is similar to python's :py:meth:`list.sort`.

        Example sorting sprites based on y-axis position using a lambda::

            # Normal order
            spritelist.sort(key=lambda x: x.position[1])
            # Reversed order
            spritelist.sort(key=lambda x: x.position[1], reverse=True)

        Example sorting sprites using a function::

            # More complex sorting logic can be applied, but let's just stick to y position
            def create_y_pos_comparison(sprite):
                return sprite.position[1]

            spritelist.sort(key=create_y_pos_comparison)

        Args:
            key:
                A function taking a sprite as an argument returning a comparison key
            reverse:
                If set to ``True`` the sprites will be sorted in reverse
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
        """Deletes the internal spatial hash object."""
        self.spatial_hash = None

    def enable_spatial_hashing(self, spatial_hash_cell_size: int = 128) -> None:
        """
        Turn on spatial hashing unless it is already enabled with the same cell size.

        Args:
            spatial_hash_cell_size: The size of the cell in the spatial hash.
        """
        if self.spatial_hash is None or self.spatial_hash.cell_size != spatial_hash_cell_size:
            # LOG.debug("Enabled spatial hashing with cell size %s", spatial_hash_cell_size)
            from .spatial_hash import SpatialHash

            self.spatial_hash = SpatialHash(cell_size=spatial_hash_cell_size)
            self._recalculate_spatial_hashes()
        # else:
        #     LOG.debug("Spatial hashing is already enabled with size %s", spatial_hash_cell_size)

    def _recalculate_spatial_hashes(self) -> None:
        if self.spatial_hash is None:
            from .spatial_hash import SpatialHash

            self.spatial_hash = SpatialHash(cell_size=self._spatial_hash_cell_size)

        self.spatial_hash.reset()
        for sprite in self.sprite_list:
            self.spatial_hash.add(sprite)

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        """
        Call the update() method on each sprite in the list.

        Args:
            delta_time: Time since last update in seconds
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        for sprite in self.sprite_list:
            sprite.update(delta_time, *args, **kwargs)

    def update_animation(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        """
        Call the update_animation in every sprite in the sprite list.

        Args:
            delta_time: Time since last update in seconds
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        # NOTE: Can we limit this to animated sprites?
        for sprite in self.sprite_list:
            sprite.update_animation(delta_time, *args, **kwargs)

    def _get_center(self) -> tuple[float, float]:
        """Get the mean center coordinates of all sprites in the list."""
        x = sum((sprite.center_x for sprite in self.sprite_list)) / len(self.sprite_list)
        y = sum((sprite.center_y for sprite in self.sprite_list)) / len(self.sprite_list)
        return x, y

    center = property(_get_center)

    def rescale(self, factor: float) -> None:
        """Rescale all sprites in the list relative to the spritelists center."""
        for sprite in self.sprite_list:
            sprite.rescale_relative_to_point(self.center, factor)

    def move(self, change_x: float, change_y: float) -> None:
        """
        Moves all Sprites in the list by the same amount.
        This can be a very expensive operation depending on the
        size of the sprite list.

        Args:
            change_x: Amount to change all x values by
            change_y: Amount to change all y values by
        """
        for sprite in self.sprite_list:
            sprite.center_x += change_x
            sprite.center_y += change_y

    def preload_textures(self, texture_list: Iterable["Texture"]) -> None:
        """
        Preload a set of textures that will be used for sprites in this
        sprite list.

        Args:
            texture_list: List of textures.
        """
        if not self.ctx:
            raise ValueError("Cannot preload textures before the window is created")

        for texture in texture_list:
            # Ugly spacing is a fast workaround for None type checking issues
            self._atlas.add(texture)  # type: ignore

    def write_sprite_buffers_to_gpu(self) -> None:
        """
        Ensure buffers are resized and fresh sprite data is written into the internal
        sprite buffers.

        This is automatically called in :py:meth:`SpriteList.draw`, but there are
        instances when using custom shaders we need to force this to happen since
        we might have not called :py:meth:`SpriteList.draw` since the spritelist
        was modified.

        If you have added, removed, moved or changed ANY sprite property this method
        will synchronize the data on the gpu side (buffer resizing and writing in
        new data).
        """
        self._write_sprite_buffers_to_gpu()

    def _write_sprite_buffers_to_gpu(self) -> None:
        # LOG.debug(
        #     (
        #         "[%s] SpriteList._write_sprite_buffers_to_gpu: "
        #         "pos=%s, size=%s, angle=%s, color=%s tex=%s idx=%s"
        #     ),
        #     id(self),
        #     self._sprite_pos_changed,
        #     self._sprite_size_changed,
        #     self._sprite_angle_changed,
        #     self._sprite_color_changed,
        #     self._sprite_texture_changed,
        #     self._sprite_index_changed,
        # )

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

    def initialize(self) -> None:
        """
        Request immediate creation of OpenGL resources for this list.

        Calling this method is optional. It only has an effect for lists
        created with ``lazy=True``. If this method is not called,
        uninitialized sprite lists will automatically initialize OpenGL
        resources on their first :py:meth:`~SpriteList.draw` call instead.

        This method is useful for performance optimization, advanced
        techniques, and writing tests. Do not call it across thread
        boundaries. See :ref:`pg_spritelist_advanced_lazy_spritelists`
        to learn more.
        """
        self._init_deferred()

    def draw(
        self,
        *,
        filter: PyGLenum | OpenGlFilter | None = None,
        pixelated: bool | None = None,
        blend_function: BlendFunction | None = None,
    ) -> None:
        """
        Draw this list of sprites.

        Uninitialized sprite lists will first create OpenGL resources
        before drawing. This may cause a performance stutter when the
        following are true:

        1. You created the sprite list with ``lazy=True``
        2. You did not call :py:meth:`~SpriteList.initialize` before drawing
        3. You are initializing many sprites and/or lists at once

        See :ref:`pg_spritelist_advanced_lazy_spritelists` to learn more.

        Args:
            filter:
                Optional parameter to set OpenGL filter, such as
                `gl.GL_NEAREST` to avoid smoothing.
            pixelated:
                ``True`` for pixelated and ``False`` for smooth interpolation.
                Shortcut for setting filter to GL_NEAREST for a pixelated look.
                The filter parameter have precedence over this.
            blend_function:
                Optional parameter to set the OpenGL blend function used for drawing
                the sprite list, such as 'arcade.Window.ctx.BLEND_ADDITIVE' or
                'arcade.Window.ctx.BLEND_DEFAULT'
        """
        if len(self.sprite_list) == 0 or not self._visible or self.alpha_normalized == 0.0:
            return

        self._init_deferred()
        if not self.program:
            raise ValueError("Attempting to render without shader program.")
        self._write_sprite_buffers_to_gpu()

        prev_blend_func = self.ctx.blend_func
        if self._blend:
            self.ctx.enable(self.ctx.BLEND)
            # Set custom blend function or revert to default
            if blend_function is not None:
                self.ctx.blend_func = blend_function
            else:
                self.ctx.blend_func = self.ctx.BLEND_DEFAULT
        else:
            self.ctx.disable(self.ctx.BLEND)

        # Workarounds for Optional[TextureAtlas] + slow . lookup speed
        atlas: DefaultTextureAtlas = self.atlas  # type: ignore
        atlas_texture: Texture2D = atlas.texture

        # Set custom filter or reset to default
        if filter:
            if hasattr(
                filter,
                "__len__",
            ):  # assume it's a collection
                if len(cast(Sized, filter)) != 2:
                    raise ValueError("Can't use sequence of length != 2")
                atlas_texture.filter = tuple(filter)  # type: ignore
            else:  # assume it's an int
                atlas_texture.filter = cast(OpenGlFilter, (filter, filter))
        else:
            # Handle the pixelated shortcut if filter is not set
            if pixelated:
                atlas_texture.filter = self.ctx.NEAREST, self.ctx.NEAREST
            else:
                atlas_texture.filter = self.DEFAULT_TEXTURE_FILTER

        self.program["spritelist_color"] = self._color

        # Control center pixel interpolation:
        # 0.0 = raw interpolation using texture corners
        # 1.0 = center pixel interpolation
        if self.ctx.NEAREST in atlas_texture.filter:
            self.program.set_uniform_safe("uv_offset_bias", 0.0)
        else:
            self.program.set_uniform_safe("uv_offset_bias", 1.0)

        atlas_texture.use(0)
        atlas.use_uv_texture(1)
        if not self._geometry:
            raise ValueError("Attempting to render without '_geometry' field being set.")
        self._geometry.render(
            self.program,
            mode=self.ctx.POINTS,
            vertices=self._sprite_index_slots,
        )

        # Leave global states to default
        if self._blend:
            self.ctx.disable(self.ctx.BLEND)
            if blend_function is not None:
                self.ctx.blend_func = prev_blend_func

    def draw_hit_boxes(self, color: RGBA255 = (0, 0, 0, 255), line_thickness: float = 1.0) -> None:
        """
        Draw all the hit boxes in this list.

        .. warning:: This method is slow and should only be used for debugging.

        Args:
            color: The color of the hit boxes
            line_thickness: The thickness of the lines
        """
        # NOTE: Find a way to efficiently draw this
        for sprite in self.sprite_list:
            sprite.draw_hit_box(color, line_thickness)

    def _normalize_index_buffer(self) -> None:
        """
        Removes unused slots in the index buffer.
        The other buffers don't need this because they re-use slots.
        New sprites on the other hand always needs to be added
        to the end of the index buffer to preserve order
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

    def _grow_sprite_buffers(self) -> None:
        """Double the internal buffer sizes"""
        # Resize sprite buffers if needed
        if self._sprite_buffer_slots <= self._buf_capacity:
            return

        # Double the capacity
        extend_by = self._buf_capacity
        self._buf_capacity = self._buf_capacity * 2

        # LOG.debug(
        #     "(%s) Increasing buffer capacity from %s to %s",
        #     self._sprite_buffer_slots,
        #     extend_by,
        #     self._buf_capacity,
        # )

        # Extend the buffers so we don't lose the old data
        self._sprite_pos_data.extend([0] * extend_by * 3)
        self._sprite_size_data.extend([0] * extend_by * 2)
        self._sprite_angle_data.extend([0] * extend_by)
        self._sprite_color_data.extend([0] * extend_by * 4)
        self._sprite_texture_data.extend([0] * extend_by)

        if self._initialized:
            # Proper initialization implies these buffers are allocated
            self._sprite_pos_buf.orphan(double=True)  # type: ignore
            self._sprite_size_buf.orphan(double=True)  # type: ignore
            self._sprite_angle_buf.orphan(double=True)  # type: ignore
            self._sprite_color_buf.orphan(double=True)  # type: ignore
            self._sprite_texture_buf.orphan(double=True)  # type: ignore

        self._sprite_pos_changed = True
        self._sprite_size_changed = True
        self._sprite_angle_changed = True
        self._sprite_color_changed = True
        self._sprite_texture_changed = True

    def _grow_index_buffer(self) -> None:
        # Extend the index buffer capacity if needed
        if self._sprite_index_slots <= self._idx_capacity:
            return

        extend_by = self._idx_capacity
        self._idx_capacity = self._idx_capacity * 2

        # LOG.debug(
        #     "Buffers: index_slots=%s sprite_slots=%s over-allocation-ratio=%s",
        #     self._sprite_index_slots,
        #     self._sprite_buffer_slots,
        #     self._sprite_index_slots / self._sprite_buffer_slots,
        # )

        # LOG.debug(
        #     "(%s) Increasing index capacity from %s to %s",
        #     self._sprite_index_slots,
        #     extend_by,
        #     self._idx_capacity,
        # )

        self._sprite_index_data.extend([0] * extend_by)
        if self._initialized and self._sprite_index_buf:
            self._sprite_index_buf.orphan(size=self._idx_capacity * 4)

        self._sprite_index_changed = True

    def _update_all(self, sprite: SpriteType) -> None:
        """
        Update all sprite data. This is faster when adding and moving sprites.
        This duplicate code, but reduces call overhead, dict lookups etc.

        Args:
            sprite: Sprite to update.
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
        self._sprite_color_data[slot * 4 + 3] = sprite._color[3] * sprite._visible
        self._sprite_color_changed = True

        # Don't deal with textures if spritelist is not initialized.
        # This can often mean we don't have a context/window yet.
        if not self._initialized:
            return

        if not sprite._texture:
            return

        # Ugly syntax makes type checking pass without perf hit from cast
        tex_slot: int = self._atlas.add(sprite._texture)[0]  # type: ignore
        slot = self.sprite_slot[sprite]

        self._sprite_texture_data[slot] = tex_slot
        self._sprite_texture_changed = True

    def _update_texture(self, sprite: SpriteType) -> None:
        """
        Make sure we update the texture for this sprite for the next batch drawing.

        Args:
            sprite: Sprite to update.
        """
        # We cannot interact with texture atlases unless the context
        # is created. We defer all texture initialization for later
        if not self._initialized:
            return

        if not sprite._texture:
            return
        atlas = self._atlas
        # Ugly spacing makes type checking work with specificity
        tex_slot: int = atlas.add(sprite._texture)[0]  # type: ignore
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

        Args:
            sprite: Sprite to update.
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

        Args:
            sprite: Sprite to update.
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

        Args:
            sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_pos_data[slot * 3 + 1] = sprite._position[1]
        self._sprite_pos_changed = True

    def _update_depth(self, sprite: SpriteType) -> None:
        """
        Called by the Sprite class to update the depth of the specified sprite.
        Necessary for batch drawing of items.

        Args:
            sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_pos_data[slot * 3 + 2] = sprite._depth
        self._sprite_pos_changed = True

    def _update_color(self, sprite: SpriteType) -> None:
        """
        Called by the Sprite class to update position, angle, size and color
        of the specified sprite.
        Necessary for batch drawing of items.

        Args:
            sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_color_data[slot * 4] = int(sprite._color[0])
        self._sprite_color_data[slot * 4 + 1] = int(sprite._color[1])
        self._sprite_color_data[slot * 4 + 2] = int(sprite._color[2])
        self._sprite_color_data[slot * 4 + 3] = int(sprite._color[3] * sprite._visible)
        self._sprite_color_changed = True

    def _update_size(self, sprite: SpriteType) -> None:
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        Args:
            sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_size_data[slot * 2] = sprite._width
        self._sprite_size_data[slot * 2 + 1] = sprite._height
        self._sprite_size_changed = True

    def _update_width(self, sprite: SpriteType) -> None:
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        Args:
            sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_size_data[slot * 2] = sprite._width
        self._sprite_size_changed = True

    def _update_height(self, sprite: SpriteType) -> None:
        """
        Called by the Sprite class to update the size/scale in this sprite.
        Necessary for batch drawing of items.

        Args:
            sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_size_data[slot * 2 + 1] = sprite._height
        self._sprite_size_changed = True

    def _update_angle(self, sprite: SpriteType) -> None:
        """
        Called by the Sprite class to update the angle in this sprite.
        Necessary for batch drawing of items.

        Args:
            sprite: Sprite to update.
        """
        slot = self.sprite_slot[sprite]
        self._sprite_angle_data[slot] = sprite._angle
        self._sprite_angle_changed = True
