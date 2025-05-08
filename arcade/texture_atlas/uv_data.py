"""
A helper class to keep track of texture coordinates stored in a texture.
"""

from __future__ import annotations

from array import array
from collections import deque
from typing import TYPE_CHECKING

from .base import (
    UV_TEXTURE_WIDTH,
    TexCoords,
)

if TYPE_CHECKING:
    from arcade import ArcadeContext
    from arcade.gl import Texture2D


class UVData:
    """
    A container for float32 texture coordinates stored in a texture.
    Each texture coordinate has a slot/index in the texture and is
    looked up by a shader to obtain the texture coordinates. The
    shader would look up texture coordinates by the id of the texture.

    The purpose of this system is to:

    - Greatly increase the performance of the texture atlas
    - Greatly simplify the system
    - Allow images to move freely around the atlas without having to update the vertex buffers.
      Meaning we can allow re-building and re-sizing. The resize can even
      be done in the GPU by rendering the old atlas into the new one.
    - Avoid spending lots of time packing texture data into buffers
    - Avoid spending lots of buffer memory

    Args:
        ctx:
            The Arcade context
        capacity:
            The number of textures the atlas keeps track of.
            This is multiplied by 4096. Meaning capacity=2 is 8192 textures.
    """

    def __init__(self, ctx: ArcadeContext, capacity: int):
        self._ctx = ctx
        self._capacity = capacity
        self._num_slots = UV_TEXTURE_WIDTH * capacity
        self._dirty = False

        # The GPU resource
        self._texture = self._ctx.texture(
            (UV_TEXTURE_WIDTH, self._num_slots * 2 // UV_TEXTURE_WIDTH),
            components=4,
            dtype="f4",
        )
        self._texture.filter = self._ctx.NEAREST, self._ctx.NEAREST

        # Python resources: data + tracker for slots
        # 8 floats per texture (4 x vec2 coordinates)
        self._data = array("f", [0] * self._num_slots * 8)
        self._slots: dict[str, int] = dict()
        self._slots_free = deque(i for i in range(0, self._num_slots))

    def clone_with_slots(self) -> UVData:
        """
        Clone the UVData with the current slot data. The UV data itself
        and the opengl texture is not cloned.

        This is useful when we are re-building the atlas since we can't
        lost the slot data since the indices in the uv texture must not
        change. If they change the entire spritelist must be updated.
        """
        clone = UVData(self._ctx, self._capacity)
        clone._slots = self._slots
        clone._slots_free = self._slots_free
        clone._dirty = True
        return clone

    @property
    def num_slots(self) -> int:
        """The amount of texture coordinates (x4) this UVData can hold"""
        return self._num_slots

    @property
    def num_free_slots(self) -> int:
        """The amount of free texture coordinates slots"""
        return len(self._slots_free)

    @property
    def texture(self) -> Texture2D:
        """The opengl texture containing the texture coordinates"""
        return self._texture

    def get_slot_or_raise(self, name: str) -> int:
        """
        Get the slot for a texture by name or raise an exception

        Args:
            name: The name of the texture
        """
        slot = self._slots.get(name)
        if slot is None:
            raise Exception(f"Texture '{name}' not found in UVData")
        return slot

    def get_existing_or_free_slot(self, name: str) -> int:
        """
        Get the slot for a texture by name or a free slot.
        Getting existing slots is useful when the resize or re-build
        the atlas.

        Args:
            name: The name of the texture
        """
        slot = self._slots.get(name)
        if slot is not None:
            return slot

        try:
            slot = self._slots_free.popleft()
            self._slots[name] = slot
            return slot
        except IndexError:
            raise Exception(
                "No more free slots in the UV texture."
                f"Max number of textures: {self._num_slots}."
                "Consider creating a texture atlas with a larger capacity."
            )

    def free_slot_by_name(self, name: str) -> None:
        """
        Free a slot for a texture by name.
        If the slot is not found no action is taken

        Args:
            name: The name of the texture
        """
        try:
            slot = self._slots.pop(name)
            self._slots_free.appendleft(slot)
        except KeyError:
            return

    def set_slot_data(self, slot: int, data: TexCoords) -> None:
        """
        Update the texture coordinates for a slot.

        Args:
            slot: The slot to update
            data: The texture coordinates
        """
        self._data[slot * 8 : slot * 8 + 8] = array("f", data)
        self._dirty = True

    def write_to_texture(self) -> None:
        """Write the texture coordinates to the opengl texture if dirty"""
        if self._dirty:
            self._texture.write(self._data, 0)
            self._dirty = False

    def __len__(self) -> int:
        return len(self._slots)
