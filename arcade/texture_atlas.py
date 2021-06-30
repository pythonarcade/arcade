"""
Texture atlas for SpriteList

The long term goal is to rely on pyglet's texture atlas, but
it's still unclear what features we need supported in arcade
so need to prototype something to get started.

We're still building on pyglet's allocator.

Pyglet atlases are located here:
https://github.com/einarf/pyglet/blob/master/pyglet/image/atlas.py

"""
from arcade.gl.framebuffer import Framebuffer
from array import array
from collections import deque
import gc
import math
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
# Detect texture changes
# Resize?
# SpriteList.preload_textures
# SpriteList.update_texture calls _calculate_sprite_buffer()


class AtlasRegion:
    """Stores information about an allocated region"""

    __slots__ = (
        "atlas",
        "texture",
        "x",
        "y",
        "width",
        "height",
        "texture_coordinates",
        "texture_coordinates_buffer",
        "texture_id",
    )

    def __init__(
        self,
        atlas: "TextureAtlas",
        texture: "Texture",
        x: int,
        y: int,
        width: int,
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

    def verify_image_size(self):
        """
        Verify the image has the right size.
        The internal image of a texture can be tampered with
        at any point causing an atlas update to fail.
        """
        if self.texture.image.size != (self.width, self.height):
            raise ValueError((
                f"Texture '{self.texture.name}' change their internal image "
                f"size from {self.width}x{self.height} to "
                f"{self.texture.image.size[0]}x{self.texture.image.size[1]}. "
                "It's not possible to fit this into the old allocated area in the atlas. "
            ))

class TextureAtlas:
    """
    A texture atlas is a large texture containing several textures
    so OpenGL can easily batch draw thousands or hundreds of thousands
    of sprites on one draw operation.

    This is a fairly simple atlas that stores horizontal strips were
    the height of the strip is the texture/image with the larges height.

    Adding a texture to this atlas generates a texture id.
    This id is used the sprite list vertex data to reference what
    texture each sprite is using. The actual texture coordinates
    are located in a float32 texture this atlas is responsible for
    keeping up to date.
    """

    def __init__(
        self,
        size: Tuple[int, int],
        *,
        border: int = 1,
        textures: Sequence["Texture"] = None,
        mutable: bool = True,
        ctx: "ArcadeContext" = None,
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
        self._uv_texture = self._ctx.texture(
            (TEXCOORD_BUFFER_SIZE, 1), components=4, dtype="f4"
        )
        self._uv_texture.filter = self._ctx.NEAREST, self._ctx.NEAREST
        self._uv_data = array("f", [0] * TEXCOORD_BUFFER_SIZE * 4)
        # Free slots in the texture coordinate texture
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

        :rtype: int
        """
        return self._size[0]

    @property
    def height(self) -> int:
        """
        The height of the texture atlas in pixels

        :rtype: int
        """
        return self._size[1]

    @property
    def size(self) -> Tuple[int, int]:
        """
        The width and height of the texture atlas in pixels

        :rtype: int
        """
        return self._size

    @property
    def border(self) -> int:
        """
        The texture border in pixels

        :rtype: int
        """
        return self._border

    @property
    def texture(self) -> "GLTexture":
        """
        The atlas texture

        :rtype: Texture
        """
        return self._texture

    @property
    def uv_texture(self) -> "GLTexture":
        """
        Texture coordinate texture.

        :rtype: Texture
        """
        return self._uv_texture

    @property
    def fbo(self) -> Framebuffer:
        """The framebuffer object for this atlas"""
        return self._fbo

    @property
    def mutable(self) -> bool:
        """
        Is this atlas mutable?

        :rtype: bool
        """
        return self._mutable

    def add(self, texture: "Texture") -> int:
        """
        Add a texture to the atlas.

        :param Texture texture: The texture to add
        :return: The texture_id in this atlas
        """
        if self.has_texture(texture):
            return self.get_texture_id(texture.name)

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
            raise AllocatorException(
                f"No more space for texture {texture.name} size={texture.image.size}"
            )

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
            x + self._border,
            y + self._border,
            texture.image.width,
            texture.image.height,
        )
        self._atlas_regions[texture.name] = region
        # Get the existing slot for this texture or grab a new one.
        # Existing slots for textures will only happen when re-bulding
        # the atlas since we want to keep the same slots to avoid
        # re-bulding the sprite list
        existing_slot = self._uv_slots.get(texture.name)
        slot = existing_slot if existing_slot is not None else self._uv_slots_free.popleft()
        self._uv_slots[texture.name] = slot
        self._uv_data[slot * 4] = region.texture_coordinates[0]
        self._uv_data[slot * 4 + 1] = region.texture_coordinates[1]
        self._uv_data[slot * 4 + 2] = region.texture_coordinates[2]
        self._uv_data[slot * 4 + 3] = region.texture_coordinates[3]
        self._uv_data_changed = True
        self._textures.add(texture)
        return slot

    def remove(self, texture: "Texture") -> None:
        """
        Remove a texture from the atlas.

        This doesn't remove the image from the underlying texture.
        To physically remove the data you need to ``rebuild()``.

        :param Texture texture: The texture to remove
        """
        self._textures.remove(texture)
        del self._atlas_regions[texture.name]
        # Reclaim the uv slot
        slot = self._uv_slots[texture.name]
        del self._uv_slots[texture.name]
        self._uv_slots_free.appendleft(slot)

    def update_texture_image(self, texture: "Texture"):
        """
        Updates the internal image of a texture in the atlas texture.
        The new image needs to be the exact same size as the original
        one meaning the texture already need to exist in the atlas.

        This can be used in cases were the image is manipulated in some way
        and we need a quick way to sync these changes to graphics memory.
        This operation is fairly expensive, but still orders of magnitude
        faster than removing the old texture, adding the new one and
        re-building the entire atlas.

        :param Texture texture: The texture to update
        """
        region = self._atlas_regions[texture.name]
        region.verify_image_size()
        viewport = (
            region.x + self._border,
            region.y + self._border,
            region.width,
            region.height,
        )
        self._texture.write(texture.image.tobytes(), 0, viewport=viewport)

    def update_textures(self, textures: Set["Texture"], keep_old_textures=True):
        """Batch update atlas with new textures.

        :param textures: List of Texture objects
        :param bool keep_old_textures: Keep textures not in the texture list
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
        """
        Get the region info for a texture

        :return: The AtlasRegion for the given texture name
        """
        return self._atlas_regions[name]

    def get_texture_id(self, name: str) -> int:
        """
        Get the uv slot for a texture name

        :return: The texture id for the given texture name
        """
        return self._uv_slots[name]

    def has_texture(self, texture: "Texture") -> bool:
        """Check if a texture is already in the atlas"""
        return texture in self._textures

    def resize(self, size: Tuple[int, int]) -> None:
        """
        Resize the texture atlas.
        This will cause a full rebuild.

        :param Tuple[int,int]: The new size
        """
        self._size = size
        self._texture = None
        self._fbo = None
        gc.collect()  # Try to force garbage collection of the gl resource asap
        self._texture = self._ctx.texture(size, components=4)
        self._fbo = self._ctx.framebuffer(color_attachments=[self._texture])
        self.rebuild()

    def clear(self, uv_slots=True) -> None:
        """
        Clear and reset the texture atlas.
        Note that also clearing "uv_slot" makes the atlas
        lose track of the old texture ids. This
        means the sprite list must be rebuild from scratch.

        :param bool uv_slots: Also clear the assigned texture ids
        """
        self._fbo.clear()
        self._textures = set()
        self._atlas_regions = dict()
        self._allocator = Allocator(*self._size)
        if uv_slots:
            self._uv_slots_free = deque(i for i in range(TEXCOORD_BUFFER_SIZE))
            self._uv_slots = dict()

    def rebuild(self) -> None:
        """Rebuild the underlying atlas texture.

        This method also tries to organize the textures
        more efficiently ordering them by size.
        The texture ids will persist so the sprite list
        don't need to be rebuilt.
        """
        # Hold a reference to the old textures
        textures = self._textures
        # Clear the atlas but keep the uv slot mapping
        self.clear(uv_slots=False)
        # Add textures back sorted by height to potentially make more room
        for texture in sorted(textures, key=lambda x: x.image.size[1]):
            self.add(texture)

    def use_uv_texture(self, unit: int = 0) -> None:
        """
        Bind the texture coordinate texture to a channel.
        In addition this method writes the texture
        coordinate to the texture if the data is stale.
        This is to avoid a full update every time a texture
        is added to the atlas.

        :param int unit: The texture unit to bind the uv texture
        """
        if self._uv_data_changed:
            self._uv_texture.write(self._uv_data, 0)
            self._uv_data_changed = False

        self._uv_texture.use(unit)

    # --- Utility functions ---

    @classmethod
    def calculate_minimum_size(self, textures: Sequence["Texture"], border: int = 1):
        """
        Calculate the minimum atlas size needed to store the
        the provided sequence of textures

        :param Sequence[Texture] textures: Sequence of textures
        :return: An estimated minimum size as a (width, height) tuple
        """
        # Ensure all textures are unique
        textures = set(textures)
        # Sort the images by height
        textures = sorted(textures, key=lambda x: x.image.size[1])

        # Try to guess some sane minimum size to reduce the brute force iterations
        total_area = sum(t.image.size[0] * t.image.size[1] for t in textures)
        sqrt_size = int(math.sqrt(total_area))
        start_size = sqrt_size or 64
        if start_size % 64:
            start_size = sqrt_size + (64 - sqrt_size % 64)

        # For now we just brute force a solution by gradually
        # increasing the atlas size using the allocator as a guide.
        for size in range(start_size, 16385, 64):
            allocator = Allocator(size, size)
            try:
                for texture in textures:
                    allocator.alloc(
                        texture.image.width + border * 2,
                        texture.image.height + border * 2,
                    )
            except AllocatorException:
                continue
            break
        else:
            raise ValueError("Too many textures to fit into one atlas")

        return size, size

    def to_image(self):
        """
        Convert the atlas to a Pillow image

        :return: A pillow image containing the atlas texture
        """
        return Image.frombytes("RGBA", self._texture.size, bytes(self._texture.read()))

    def show(self):
        """Show the texture atlas using Pillow"""
        self.to_image().show()

    def save(self, path: str):
        """
        Save the texture atlas to a png.

        :param str path: The path to save the atlas on disk
        """
        self.to_image().save(path, format="png")
