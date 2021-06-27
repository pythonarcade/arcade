"""
Texture atlas for SpriteList

The long term goal is to rely on pyglet's texture atlas, but
it's still unclear what features we need supported in arcade
so need to prototype something to get started.

We're still building on pyglet's allocator.

Pyglet atlases are located here:
https://github.com/einarf/pyglet/blob/master/pyglet/image/atlas.py

"""
from array import array
from collections import deque
import logging
from typing import Dict, Set, Tuple, Sequence, TYPE_CHECKING

from PIL import Image

import arcade

from pyglet.image.atlas import (
    Allocator,
    AllocatorException,
)

if TYPE_CHECKING:
    from arcade import ArcadeContext, Texture
    from arcade.gl import Texture as GLTexture

# How many texture coordinates to store
TEXCOORD_BUFFER_SIZE = 8192
LOG = logging.getLogger(__name__)


# TODO:
# TextureRegion
# repack()
# Detect texture changes
# Clear atlas texture
# Resize?
# SpriteList.preload_textures
# Warning adding large textures?
# SpriteList.update_texture calls _calculate_sprite_buffer()
# Only loop sprites if we are removing unused ones
# Loops "textures" attributes for animated sprites?


class AtlasRegion:
    """Stores information about an allocated region"""

    __slots__ = (
        'atlas', 'texture', 'x', 'y', 'width', 'height',
        'texture_coordinates', 'texture_coordinates_buffer', 'texture_id',
    )

    def __init__(
        self,
        atlas: "TextureAtlas",
        texture: "Texture",
        x: int,
        y: int, width: int,
        height: int,
    ):
        """Represents a region a texture is located.

        :param str atlas: The atlas this region belongs to
        :param str texture: The arcade texture
        :param int x: The x position of the texture
        :param int y: The y position of the texture
        :param int width: The width of the texture in pixels
        :param int height: The height of the texture in pixels
        """
        self.atlas = atlas
        self.texture = texture
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # start_x, start_y, normalized_width, normalized_height
        self.texture_coordinates = (
            self.x / self.atlas.width,
            (self.atlas.height - self.y - self.height) / self.atlas.height,
            self.width / self.atlas.width,
            self.height / self.atlas.height,
        )


class TextureAtlas:
    """
    A texture atlas is a large texture containing several textures
    so OpenGL can easily batch draw thousands or hundreds of thousands
    of sprites on one draw operation.

    This is a fairly simple atlas that stores horizontal strips were
    the height of the strip is the texture/image with the larges height.
    """

    def __init__(
        self,
        size: Tuple[int, int],
        *,
        border: int = 1,
        textures: Sequence["Texture"] = None,
        mutable: bool = False,
        ctx: "ArcadeContext" = None
    ):
        """
        Creates a texture atlas with a size in a context.

        :param Tuple[int, int] size: The width and height of the atlas in pixels
        :param int border: Border in pixels around every texture in the atlas
        :param Sequence[arcade.Texture] textures: The texture for this atlas
        :param bool mutable: If this atlas can be changed after creation
        :param Context ctx: The context for this atlas (will use window context if left empty)
        """
        self._ctx = ctx or arcade.get_window().ctx
        self._size: Tuple[int, int] = size
        self._border: int = border
        self._mutable = True
        self._allocator = Allocator(*self._size)

        self._texture = self._ctx.texture(size, components=4)
        # Creating an fbo makes us able to clear the texture
        self._fbo = self._ctx.framebuffer(color_attachments=[self._texture])

        # A dictionary of all the allocated regions
        # The key is the cache name for a texture
        self._atlas_regions: Dict[str, AtlasRegion] = dict()
        # A set of textures this atlas contains for fast lookups + set oprations
        self._textures: Set["Texture"] = set()

        # Texture containing texture coordinates
        self._uv_texture = self._ctx.texture((TEXCOORD_BUFFER_SIZE, 1), components=4, dtype="f4")
        self._uv_texture.filter = self._ctx.NEAREST, self._ctx.NEAREST
        self._uv_data = array("f", [0] * TEXCOORD_BUFFER_SIZE * 4)
        # Free slos in the texture coordinate texture
        self._uv_slots_free = deque(i for i in range(0, TEXCOORD_BUFFER_SIZE))
        # Map texture names to slots
        self._uv_slots: Dict[str, int] = dict()
        self._uv_data_changed = True

        # Add all the textures
        for tex in textures or []:
            self.add(tex)

        self._mutable = mutable

    @property
    def width(self) -> int:
        """
        The width of the texture atlas in pixels

        :type: int
        """
        return self._size[0]

    @property
    def height(self) -> int:
        """
        The height of the texture atlas in pixels

        :type: int
        """
        return self._size[1]

    @property
    def size(self) -> Tuple[int, int]:
        """
        The width and height of the texture atlas in pixels

        :type: int
        """
        return self._size

    @property
    def border(self) -> int:
        """
        The texture border in pixels

        :type: int
        """
        return self._border

    @property
    def texture(self) -> "GLTexture":
        """
        The atlas texture

        :type: Texture
        """
        return self._texture

    @property
    def uv_texture(self) -> "GLTexture":
        """
        Texture coordinate texture.

        :type: Texture
        """
        return self._uv_texture

    @property
    def mutable(self) -> bool:
        """
        Is this atlas mutable?

        :type: bool
        """
        return self._mutable

    def add(self, texture: "Texture") -> int:
        """
        Add a texture to the atlas.

        :returns: The texture_id in this atlas
        """
        if self.has_texture(texture):
            return self.get_uv_slot(texture.name)

        LOG.debug("Attempting to add texture: %s", texture.name)

        if not self._mutable:
            raise AllocatorException("The atlas is not mutable")

        if texture.image.mode != "RGBA":
            LOG.warning(f"TextureAtlas: Converting texture '{texture.name}' to RGBA")
            texture.image = texture.image.convert("RGBA")

        # Allocate space for texture
        try:
            x, y = self._allocator.alloc(
                texture.image.width + self.border * 2,
                texture.image.height + self.border * 2,
            )
        except AllocatorException:
            # self.show()
            raise AllocatorException(f"No more space for texture {texture.name} size={texture.image.size}")

        LOG.debug("Allocated new space for texture %s : %s %s", texture.name, x, y)

        # Write into atlas at the allocated location
        viewport = (
            x + self._border,
            y + self._border,
            texture.image.width,
            texture.image.height,
        )

        # Write the image directly to vram in the allocated space
        self._texture.write(texture.image.tobytes(), 0, viewport=viewport)

        # Store a texture region for this allocation
        region = AtlasRegion(
            self,
            texture,
            x + 1,
            y + 1,
            texture.image.width,
            texture.image.height,
        )
        self._atlas_regions[texture.name] = region
        slot = self._uv_slots_free.popleft()
        self._uv_slots[texture.name] = slot
        self._uv_data[slot * 4] = region.texture_coordinates[0]
        self._uv_data[slot * 4 + 1] = region.texture_coordinates[1]
        self._uv_data[slot * 4 + 2] = region.texture_coordinates[2]
        self._uv_data[slot * 4 + 3] = region.texture_coordinates[3]
        self._uv_texture.write(self._uv_data, 0)
        self._uv_data_changed = True
        self._textures.add(texture)
        return slot

    def remove(self, texture: "Texture"):
        """
        Remove a texture from the atlas.

        This doesn't remove the image from the underlying texture.
        To physically remove the data you need to rebuild().
        """
        self._textures.remove(texture)
        del self._atlas_regions[texture.name]
        # Reclaim the uv slot
        slot = self._uv_slots[texture.name]
        self._uv_slots_free.appendleft(slot)

    def update_textures(self, textures: Set["Texture"], keep_old_textures=True):
        """Batch update atlas with new textures.

        This is used internally by ``SpriteList``.

        :param textures: List of Texture objects
        :param bool keep_old_textures: Keep old textures around
        """
        new_textures = textures - self._textures

        if keep_old_textures:
            for tex in new_textures:
                self.add(tex)
        else:
            old_textures = self._textures - textures
            if old_textures:
                self.clear()
            for tex in new_textures:
                self.add(tex)

    def get_region_info(self, name: str) -> AtlasRegion:
        """Get the region info for a texture"""
        return self._atlas_regions[name]

    def get_uv_slot(self, name: str) -> int:
        """Get the uv slot for a texture name"""
        return self._uv_slots[name]

    def has_texture(self, texture: "Texture") -> bool:
        """Check if a texture is already in the atlas"""
        return texture in self._textures

    def clear(self) -> None:
        """Clear and reset the texture atlas"""
        self._fbo.clear()
        self._textures = set()
        self._atlas_regions = dict()
        self._allocator = Allocator(*self._size)
        self._uv_slots_free = deque(i for i in range(TEXCOORD_BUFFER_SIZE))
        self._uv_slots = dict()
        self._uv_data_changed = True

    def rebuild(self) -> None:
        """Rebuild the underlying atlas texture.
        
        This method also tries to organize the textures
        more efficiently.
        """
        # Hold a reference to the old textures
        textures = self._textures
        self.clear()
        # Add textures back sorted by height to potentially make more room
        for texture in sorted(textures, key=lambda x: x.image.size[1]):
            self.add(texture)

    # --- Utility functions ---

    def to_image(self):
        """Convert the atlas to a Pillow image"""
        return Image.frombytes("RGBA", self._texture.size, bytes(self._texture.read()))

    def show(self):
        """Show the texture atlas using Pillow"""
        self.to_image().show()

    def save(self, path: str):
        """Save the texture atlas to a png"""
        self.to_image().save(path, format="png")
