import copy
import math
import time
import logging
from pathlib import Path
from typing import (
    Dict,
    Optional,
    Tuple,
    Sequence,
    Union,
    TYPE_CHECKING,
    List,
)
from array import array
from collections import deque
from contextlib import contextmanager
from weakref import WeakSet, WeakValueDictionary

import PIL
import PIL.Image
from PIL import Image, ImageDraw
from pyglet.image.atlas import (
    Allocator,
    AllocatorException,
)
from pyglet.math import Mat4

from arcade.gl.framebuffer import Framebuffer
from arcade.texture.transforms import Transform

from .base import (
    TextureAtlasBase,
    ImageDataRefCounter,
)

if TYPE_CHECKING:
    from arcade import ArcadeContext, Texture
    from arcade.gl import Texture2D
    from arcade.texture import ImageData

# The amount of pixels we increase the atlas when scanning for a reasonable size.
# It must divide. Must be a power of two number like 64, 256, 512 etx
RESIZE_STEP = 128
# This is the maximum size of the float32 UV texture. 4096 is a safe value for
# OpenGL ES 3.1/2. It's not recommended to go higher than this. This is a 2D
# texture anyway, so more rows can be added.
UV_TEXTURE_WIDTH = 4096

LOG = logging.getLogger(__name__)

# Texture coordinates for a texture (4 x vec2)
TexCoords = Tuple[float, float, float, float, float, float, float, float]


class AtlasRegion:
    """
    Stores information about where a texture is located.

    The texture coordinates are stored as a tuple of 8 floats
    (4 points, 2 floats each) in the following order:
    upper_left, upper_right, lower_left, lower_right.

    Layout::

        (0, 1)                                 (1, 1)
        +--------------------------------------+
        |          Atlas Texture               |
        |                                      |
        | (2)               (3)                |
        +-----------------+                    |
        |   Image         |                    |
        |                 |                    |
        |                 |                    |
        |                 |                    |
        |                 |                    |
        | (0)             | (1)                |
        +-----------------+--------------------+
        (0, 0)                                 (1, 0)

    :param atlas: The atlas this region belongs to
    :param texture: The arcade texture
    :param x: The x position of the texture
    :param y: The y position of the texture
    :param width: The width of the texture in pixels
    :param height: The height of the texture in pixels
    :param texture_coordinates: The texture coordinates (optional)
    """

    __slots__ = (
        "x",
        "y",
        "width",
        "height",
        "texture_coordinates",
    )

    def __init__(
        self,
        atlas: "TextureAtlas",
        x: int,
        y: int,
        width: int,
        height: int,
        texture_coordinates: Optional[TexCoords] = None,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Calculate texture coordinates if not provided
        if texture_coordinates:
            self.texture_coordinates = texture_coordinates
        else:
            # start_x, start_y, width, height
            # Width and height
            _width = self.width / atlas.width
            _height = self.height / atlas.height
            # upper_left, upper_right, lower_left, lower_right
            self.texture_coordinates = (
                # upper_left
                self.x / atlas.width,
                self.y / atlas.height,
                # upper_right
                (self.x / atlas.width) + _width,
                (self.y / atlas.height),
                # lower_left
                (self.x / atlas.width),
                (self.y / atlas.height) + _height,
                # lower_right
                (self.x / atlas.width) + _width,
                (self.y / atlas.height) + _height,
            )

    def verify_image_size(self, image_data: "ImageData"):
        """
        Verify the image has the right size.
        The internal image of a texture can be tampered with
        at any point causing an atlas update to fail.
        """
        if image_data.size != (self.width, self.height):
            raise ValueError((
                f"ImageData '{image_data.hash}' change their internal image "
                f"size from {self.width}x{self.height} to "
                f"{image_data.width}x{image_data.height}. "
                "It's not possible to fit this into the old allocated area in the atlas. "
            ))

    def __repr__(self) -> str:
        return (
            f"<AtlasRegion x={self.x} y={self.y} width={self.width} "
            f"height={self.height} uvs={self.texture_coordinates}>"
        )


class UVData:
    """
    A container for float32 texture coordinates stored in a texture.
    Each texture coordinate has a slot/index in the texture and is
    looked up by a shader to obtain the texture coordinates.

    The purpose of this system is to:
    * Greatly increase the performance of the texture atlas
    * Greatly simplify the system
    * Allow images to move freely around the atlas without having to update the vertex buffers.
      Meaning we can allow re-building and re-sizing. The resize can even
      be done in the GPU by rendering the old atlas into the new one.
    * Avoid spending lots of time packing texture data into buffers
    * Avoid spending lots of buffer memory

    :param ctx: The arcade context
    :param capacity: The number of textures the atlas keeps track of.
                     This is multiplied by 4096. Meaning capacity=2 is 8192 textures.
    """
    def __init__(self, ctx: "ArcadeContext", capacity: int):
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
        self._slots: Dict[str, int] = dict()
        self._slots_free = deque(i for i in range(0, self._num_slots))

    def clone_with_slots(self) -> "UVData":
        """
        Clone the UVData with the same texture and slots only.
        We can't lose the global slots when re-building or resizing the atlas.
        """
        clone = UVData(self._ctx, self._capacity)
        clone._slots = self._slots
        clone._slots_free = self._slots_free
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
    def texture(self) -> "Texture2D":
        """The texture containing the texture coordinates"""
        return self._texture

    def get_slot_or_raise(self, name: str) -> int:
        """
        Get the slot for a texture by name or raise an exception

        :param name: The name of the texture
        :return: The slot
        :raises Exception: If the texture is not found
        """
        slot = self._slots.get(name)
        if slot is None:
            raise Exception(f"Texture '{name}' not found in UVData")
        return slot

    def get_existing_or_free_slot(self, name: str) -> int:
        """
        Get the slot for a texture by name or a free slot-

        :param name: The name of the texture
        :return: The slot or a free slot
        """
        slot = self._slots.get(name)
        if slot is not None:
            return slot

        try:
            slot = self._slots_free.popleft()
            self._slots[name] = slot
            return slot
        except IndexError:
            raise Exception((
                "No more free slots in the UV texture. "
                f"Max number of slots: {self._num_slots}"
            ))

    def free_slot_by_name(self, name: str) -> None:
        """
        Free a slot for a texture by name.

        :param name: The name of the texture
        """
        slot = self._slots.pop(name)
        if slot is None:
            raise Exception(f"Texture '{name}' not found in UVData")

        self._slots_free.appendleft(slot)

    def set_slot_data(self, slot: int, data: TexCoords) -> None:
        """
        Update the texture coordinates for a slot.

        :param slot: The slot to update
        :param data: The texture coordinates
        """
        self._data[slot * 8:slot * 8 + 8] = array("f", data)
        self._dirty = True

    def write_to_texture(self) -> None:
        """Write the texture coordinates to the texture if dirty"""
        if self._dirty:
            self._texture.write(self._data, 0)
            self._dirty = False


class TextureAtlas(TextureAtlasBase):
    """
    A texture atlas with a size in a context.

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

    The atlas deals with image and textures. The image is the actual
    image data. The texture is the arcade texture object that contains
    the image and other information about such as transforms.
    Several textures can share the same image with different transforms
    applied. The transforms are simply changing the order of the texture
    coordinates to flip, rotate or mirror the image.

    :param Tuple[int, int] size: The width and height of the atlas in pixels
    :param border: Currently no effect; Should always be 1 to avoid textures bleeding
    :param textures: The texture for this atlas
    :param auto_resize: Automatically resize the atlas when full
    :param ctx: The context for this atlas (will use window context if left empty)
    :param capacity: The number of textures the atlas keeps track of.
                     This is multiplied by 4096. Meaning capacity=2 is 8192 textures.
                     This value can affect the performance of the atlas.
    """
    def __init__(
        self,
        size: Tuple[int, int],
        *,
        border: int = 1,
        textures: Optional[Sequence["Texture"]] = None,
        auto_resize: bool = True,
        ctx: Optional["ArcadeContext"] = None,
        capacity: int = 2,
    ):
        super().__init__(ctx)
        self._max_size = self._ctx.info.MAX_VIEWPORT_DIMS
        self._size: Tuple[int, int] = size
        self._allocator = Allocator(*self._size)
        self._auto_resize = auto_resize
        self._capacity = capacity
        self._border: int = border
        if self._border < 0:
            raise ValueError("Border must be 0 or a positive integer")

        # Decides the number of texture and images the atlas can hold.
        # Must be a multiple of UV_TEXTURE_WIDTH due texture coordinates being
        # stored in a float32 texture.
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("Capacity must be a positive integer")

        self._check_size(self._size)

        # The atlas texture
        self._texture = self._ctx.texture(
            size,
            components=4,
            wrap_x=self._ctx.CLAMP_TO_EDGE,
            wrap_y=self._ctx.CLAMP_TO_EDGE,
        )
        # Creating an fbo makes us able to clear the texture or parts
        # of the texture including rendering to a part of the texture.
        # This also means we can resize the atlas in the gpu
        # by rendering the old atlas into the new one.
        self._fbo = self._ctx.framebuffer(color_attachments=[self._texture])

        # Texture coordinate data for images and textures.
        # * The image UVs are used when rebuilding the atlas
        # * The texture UVs are passed into sprite shaders as a source for texture coordinates
        self._image_uvs = UVData(self._ctx, capacity)
        self._texture_uvs = UVData(self._ctx, capacity)

        # A dictionary of all the allocated regions for images/textures in the atlas.
        # The texture regions are clones of the image regions with transforms applied
        # in order to map the same image using different orders or texture coordinates.
        # The key is the cache name for a texture
        self._image_regions: Dict[str, AtlasRegion] = dict()
        self._texture_regions: Dict[str, AtlasRegion] = dict()

        # Ref counter for images and textures. Per atlas we need to keep
        # track of ho many times an image is used in textures to determine
        # when to remove an image from the atlas. We only ever track images
        # using their sha256 hash to avoid writing the same image multiple times.
        self._image_ref_count = ImageDataRefCounter()

        # A list of all the images this atlas contains.
        # Unique by: Internal hash property
        self._images: WeakSet[ImageData] = WeakSet()
        # All textures added to the atlas
        self._textures: WeakSet[Texture] = WeakSet()
        # atlas_name: Texture
        self._unique_textures: WeakValueDictionary[str, "Texture"] = WeakValueDictionary()

        # Add all the textures
        for tex in textures or []:
            self.add(tex)

    @property
    def width(self) -> int:
        """
        The width of the texture atlas in pixels
        """
        return self._size[0]

    @property
    def height(self) -> int:
        """
        The height of the texture atlas in pixels
        """
        return self._size[1]

    @property
    def size(self) -> Tuple[int, int]:
        """
        The width and height of the texture atlas in pixels
        """
        return self._size

    @property
    def max_width(self) -> int:
        """
        The maximum width of the atlas in pixels
        """
        return self._max_size[0]

    @property
    def max_height(self) -> int:
        """
        The maximum height of the atlas in pixels
        """
        return self._max_size[1]

    @property
    def max_size(self) -> Tuple[int, int]:
        """
        The maximum size of the atlas in pixels (x, y)
        """
        return self._max_size

    @property
    def auto_resize(self) -> bool:
        """
        Get or set the auto resize flag for the atlas.
        If enabled the atlas will resize itself when full.
        """
        return self._auto_resize

    @auto_resize.setter
    def auto_resize(self, value: bool):
        self._auto_resize = value

    @property
    def border(self) -> int:
        """
        The texture border in pixels
        """
        return self._border

    @property
    def texture(self) -> "Texture2D":
        """
        The atlas texture.
        """
        return self._texture

    @property
    def image_uv_texture(self) -> "Texture2D":
        """
        Texture coordinate texture for images.
        """
        return self._image_uvs.texture

    @property
    def texture_uv_texture(self) -> "Texture2D":
        """
        Texture coordinate texture for textures.
        """
        return self._texture_uvs.texture

    @property
    def fbo(self) -> Framebuffer:
        """The framebuffer object for this atlas"""
        return self._fbo

    @property
    def textures(self) -> List["Texture"]:
        """
        All textures instance added to the atlas regardless
        of their internal state. See :py:meth:`unique_textures``
        for textures with unique image data and transformation.
        """
        return list(self._textures)

    @property
    def unique_textures(self) -> List["Texture"]:
        """
        All unique textures in the atlas.

        These are textures using an image with the same hash
        and the same vertex order. The full list of all textures
        can be found in :py:meth:`textures`.
        """
        return list(self._unique_textures.values())

    @property
    def images(self) -> List["ImageData"]:
        """
        Return a list of all the images in the atlas.

        A new list is constructed from the internal weak set of images.
        """
        return list(self._images)

    def add(self, texture: "Texture") -> Tuple[int, AtlasRegion]:
        """
        Add a texture to the atlas.

        :param texture: The texture to add
        :return: texture_id, AtlasRegion tuple
        :raises AllocatorException: If there are no room for the texture
        """
        # Store a reference to the texture instance if we don't already have it
        # These are any texture instances regardless of content
        if not self.has_texture(texture):
            self._textures.add(texture)
            texture.add_atlas_ref(self)
            self._image_ref_count.inc_ref(texture.image_data)

        # Return existing texture if we already have a texture with the same image hash and vertex order
        if self.has_unique_texture(texture):
            slot = self._texture_uvs.get_slot_or_raise(texture.atlas_name)
            region = self.get_texture_region_info(texture.atlas_name)
            return slot, region

        LOG.info("Attempting to add texture: %s", texture.atlas_name)

        # Add the *image* to the atlas if it's not already there
        if not self.has_image(texture.image_data):
            try:
                # Attempt to allocate space for the image
                x, y, slot, region = self._allocate_image(texture.image_data)
                # Write the pixel data to the atlas texture
                self.write_image(texture.image_data.image, x, y)
            except AllocatorException:
                LOG.info("[%s] No room for %s size %s", id(self), texture.atlas_name, texture.image.size)
                if not self._auto_resize:
                    raise

                # If we have lost regions/images we can try to rebuild the atlas
                removed_image_count = self._image_ref_count.get_total_decref()
                if removed_image_count > 0:
                    LOG.info("[%s] Rebuilding atlas due to %s lost images", id(self), removed_image_count)
                    self.rebuild()
                    return self.add(texture)

                # Double the size of the atlas (capped my max size)
                width = min(self.width * 2, self.max_width)
                height = min(self.height * 2, self.max_height)
                # If the size didn't change we have a problem ..
                if self._size == (width, height):
                    raise

                # Resize the atlas making more room for images
                self.resize((width, height))

                # Recursively try to add the texture again
                return self.add(texture)

        # Finally we can register the texture
        info = self._allocate_texture(texture)
        return info

    def _allocate_texture(self, texture: "Texture") -> Tuple[int, AtlasRegion]:
        """
        Add or update a unique texture in the atlas.
        This is mainly responsible for updating the texture coordinates
        """
        # NOTE: This is also called when re-building the atlas meaning we
        #       need to support updating the texture coordinates for existing textures
        slot = self._texture_uvs.get_existing_or_free_slot(texture.atlas_name)

        # Copy the region for the image and apply the texture transform
        image_region = self.get_image_region_info(texture.image_data.hash)
        texture_region = copy.deepcopy(image_region)
        texture_region.texture_coordinates = Transform.transform_texture_coordinates_order(
            texture_region.texture_coordinates, texture._vertex_order
        )
        self._texture_regions[texture.atlas_name] = texture_region  # add or update region

        # Put texture coordinates into uv buffer
        self._texture_uvs.set_slot_data(slot, texture_region.texture_coordinates)
        self._unique_textures[texture.atlas_name] = texture  # add or update texture

        return slot, texture_region

    def _allocate_image(self, image_data: "ImageData") -> Tuple[int, int, int, AtlasRegion]:
        """
        Attempts to allocate space for an image in the atlas or
        update the existing space for the image.

        This doesn't write the texture to the atlas texture itself.
        It only allocates space.

        :return: The x, y texture_id, TextureRegion
        """
        image = image_data.image

        # Allocate space for texture
        try:
            x, y = self._allocator.alloc(
                image.width + self._border * 2,
                image.height + self._border * 2,
            )
        except AllocatorException:
            raise AllocatorException(
                f"No more space for image {image_data.hash} size={image.size}. "
                f"Curr size: {self._size}. "
                f"Max size: {self._max_size}"
            )

        LOG.debug("Allocated new space for image %s : %s %s", image_data.hash, x, y)

        # Store a texture region for this allocation
        # The xy position must be offset by the border size
        # while the image size must stay as its true size
        region = AtlasRegion(
            self,
            x + self._border,
            y + self._border,
            image.width,
            image.height,
        )
        self._image_regions[image_data.hash] = region

        # Get the existing slot for this texture or grab a new one.
        # Existing slots for textures will only happen when re-building
        # the atlas since we want to keep the same slots to avoid
        # re-building the sprite list
        slot = self._image_uvs.get_existing_or_free_slot(image_data.hash)
        # Put texture coordinates into uv buffer
        self._image_uvs.set_slot_data(slot, region.texture_coordinates)

        self._images.add(image_data)
        return x, y, slot, region

    # def write_texture(self, texture: "Texture", x: int, y: int):
    #     """
    #     Writes an arcade texture to a subsection of the texture atlas.

    #     :param texture: The arcade texture
    #     :param x: The x position to write the texture
    #     :param y: The y position to write the texture
    #     """
    #     self.write_image(texture.image, x, y)

    def write_image(self, image: PIL.Image.Image, x: int, y: int) -> None:
        """
        Write a PIL image to the atlas in a specific region.

        :param image: The pillow image
        :param x: The x position to write the texture
        :param y: The y position to write the texture
        """
        # Write into atlas at the allocated location + border
        viewport = (
            x,
            y,
            image.width + self._border * 2,
            image.height + self._border * 2,
        )

        # Only do extrusion if we have a border
        if self._border > 0:
            # Make new image with room for borders
            tmp = Image.new(
                'RGBA',
                size=(
                    image.width + self._border * 2,
                    image.height + self._border * 2
                ),
                color=(0, 0, 0, 0),
            )
            # Paste the image into the center of the new image
            tmp.paste(image, (self._border, self._border))

            # Copy 1 pixel strips from each side of the image to the border
            # so we can repeat this pixel data in the border region
            # left, top, right, bottom
            strip_top = image.crop((0, 0, image.width, 1))
            strip_bottom = image.crop((0, image.height - 1, image.width, image.height))
            strip_left = image.crop((0, 0, 1, image.height))
            strip_right = image.crop((image.width - 1, 0, image.width, image.height))

            # Resize the strips to the border size if larger than 1
            if self._border > 1:
                strip_top = strip_top.resize((image.width, self._border), Image.NEAREST)
                strip_bottom = strip_bottom.resize((image.width, self._border), Image.NEAREST)
                strip_left = strip_left.resize((self._border, image.height), Image.NEAREST)
                strip_right = strip_right.resize((self._border, image.height), Image.NEAREST)

            tmp.paste(strip_top, (self._border, 0))
            tmp.paste(strip_bottom, (self._border, tmp.height - self._border))
            tmp.paste(strip_left, (0, self._border))
            tmp.paste(strip_right, (tmp.width - self._border, self._border))
        else:
            tmp = image

        # Write the image directly to graphics memory in the allocated space
        self._texture.write(tmp.tobytes(), 0, viewport=viewport)

    def remove(self, texture: "Texture") -> None:
        """
        Remove a texture from the atlas.

        This doesn't erase the pixel data from the atlas texture
        itself, but leaves the area unclaimed. The area will be
        reclaimed when the atlas is rebuilt.

        :param texture: The texture to remove
        """
        # print("Removing texture", texture.atlas_name)
        # The texture is not there if GCed but we still
        # need to remove if it it's a manual action
        try:
            self._textures.remove(texture)
        except KeyError:
            pass

        # Remove the unique texture if it's there
        if self.has_unique_texture(texture):
            del self._unique_textures[texture.atlas_name]
            # Reclaim the texture uv slot
            del self._texture_regions[texture.atlas_name]
            self._texture_uvs.free_slot_by_name(texture.atlas_name)

        # Reclaim the image in the atlas if it's not used by any other texture
        if self._image_ref_count.dec_ref(texture.image_data) == 0:
            # Image might be GCed already
            try:
                self._images.remove(texture.image_data)
            except KeyError:
                pass
            del self._image_regions[texture.image_data.hash]
            self._image_uvs.free_slot_by_name(texture.image_data.hash)

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

        :param texture: The texture to update
        """
        region = self._image_regions[texture.image_data.hash]
        region.verify_image_size(texture.image_data)
        viewport = (
            region.x,
            region.y,
            region.width,
            region.height,
        )
        self._texture.write(texture.image.tobytes(), 0, viewport=viewport)

    def get_image_region_info(self, hash: str) -> AtlasRegion:
        """
        Get the region info for and image by has

        :param hash: The hash of the image
        :return: The AtlasRegion for the given texture name
        """
        return self._image_regions[hash]

    def get_texture_region_info(self, atlas_name: str) -> AtlasRegion:
        """
        Get the region info for a texture by atlas name

        :return: The AtlasRegion for the given texture name
        """
        return self._texture_regions[atlas_name]

    def get_texture_id(self, texture: "Texture") -> int:
        """
        Get the internal id for a Texture in the atlas

        :param atlas_name: The name of the texture in the atlas
        :return: The texture id for the given texture name
        :raises Exception: If the texture is not in the atlas
        """
        return self._texture_uvs.get_slot_or_raise(texture.atlas_name)

    def has_texture(self, texture: "Texture") -> bool:
        """Check if a texture is already in the atlas"""
        return texture in self._textures

    def has_unique_texture(self, texture: "Texture") -> bool:
        """
        Check if the atlas already have a texture with the
        same image data and vertex order
        """
        return texture.atlas_name in self._unique_textures

    def has_image(self, image_data: "ImageData") -> bool:
        """Check if a image is already in the atlas"""
        return image_data in self._images

    def resize(self, size: Tuple[int, int]) -> None:
        """
        Resize the atlas on the gpu.

        This will copy the pixel data from the old to the
        new atlas retaining the exact same data.
        This is useful if the atlas was rendered into directly
        and we don't have to transfer each texture individually
        from system memory to graphics memory.

        :param size: The new size
        """
        LOG.info("[%s] Resizing atlas from %s to %s", id(self), self._size, size)
        # print("Resizing atlas from", self._size, "to", size)

        # Only resize if the size actually changed
        if size == self._size:
            return

        self._check_size(size)
        resize_start = time.perf_counter()

        # Keep a reference to the old atlas texture so we can copy it into the new one
        atlas_texture_old = self._texture
        self._size = size

        # Create new image uv data temporarily keeping the old one
        self._image_uvs.write_to_texture()
        image_uvs_old = self._image_uvs
        self._image_uvs = image_uvs_old.clone_with_slots()

        # Create new atlas texture and framebuffer
        self._texture = self._ctx.texture(size, components=4)
        self._fbo = self._ctx.framebuffer(color_attachments=[self._texture])

        # Store old images and textures before clearing the atlas
        images = list(self._images)
        textures = self.unique_textures

        # Clear the regions and allocator
        self._image_regions = dict()
        self._texture_regions = dict()
        self._allocator = Allocator(*self._size)

        # Re-allocate the images
        for image in sorted(images, key=lambda x: x.height):
            self._allocate_image(image)
        self._image_uvs.write_to_texture()

        # Update the texture regions. We need to copy the image regions
        # and re-apply the transforms on each texture
        for texture in textures:
            self._allocate_texture(texture)
        self._texture_uvs.write_to_texture()

        # Bind textures for atlas copy shader
        atlas_texture_old.use(0)
        self._texture.use(1)
        image_uvs_old.texture.use(2)
        self._image_uvs.texture.use(3)
        self._ctx.atlas_resize_program["border"] = float(self._border)
        self._ctx.atlas_resize_program["projection"] = Mat4.orthogonal_projection(
            0, self.width, self.height, 0, -100, 100,
        )

        # Render the old atlas into the new one. This means we actually move
        # all the textures around from the old to the new position.
        with self._fbo.activate():
            # Ensure no context flags are enabled
            with self._ctx.enabled_only():
                self._ctx.atlas_geometry.render(
                    self._ctx.atlas_resize_program,
                    mode=self._ctx.POINTS,
                    vertices=self.max_width,
                )

        duration = time.perf_counter() - resize_start
        LOG.info("[%s] Atlas resize took %s seconds", id(self), duration)

    def rebuild(self) -> None:
        """
        Rebuild the underlying atlas texture.

        This method also tries to organize the textures more efficiently ordering them by size.
        The texture ids will persist so the sprite list don't need to be rebuilt.
        """
        # print("Rebuilding atlas")

        # Hold a reference to the old textures
        textures = self.textures
        self._image_ref_count.clear()

        # Clear the atlas but keep the uv slot mapping
        self._fbo.clear()

        self._textures = WeakSet()
        self._unique_textures = WeakValueDictionary()
        self._images = WeakSet()

        self._image_regions = dict()
        self._texture_regions = dict()
        self._allocator = Allocator(*self._size)

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

        :param unit: The texture unit to bind the uv texture
        """
        # Sync the texture coordinates to the texture if dirty
        self._image_uvs.write_to_texture()
        self._texture_uvs.write_to_texture()

        self._texture_uvs.texture.use(unit)

    @contextmanager
    def render_into(
        self, texture: "Texture",
        projection: Optional[Tuple[float, float, float, float]] = None,
    ):
        """
        Render directly into a sub-section of the atlas.
        The sub-section is defined by the already allocated space
        of the texture supplied in this method.

        By default the projection will be set to match the texture area size
        were `0, 0` is the lower left corner and `width, height` (of texture)
        is the upper right corner.

        This method should should be used with the ``with`` statement::

            with atlas.render_into(texture):
                # Draw commands here

            # Specify projection
            with atlas.render_into(texture, projection=(0, 100, 0, 100))
                # Draw geometry

        :param texture: The texture area to render into
        :param projection: The ortho projection to render with.
            This parameter can be left blank if no projection changes are needed.
            The tuple values are: (left, right, button, top)
        """
        region = self._texture_regions[texture.atlas_name]
        proj_prev = self._ctx.projection_matrix
        # Use provided projection or default
        projection = projection or (0, region.width, 0, region.height)
        # Flip the top and bottom because we need to render things upside down
        projection = projection[0], projection[1], projection[3], projection[2]
        self._ctx.projection_matrix = Mat4.orthogonal_projection(
            left=projection[0],
            right=projection[1],
            bottom=projection[2],
            top=projection[3],
            z_near=-1,
            z_far=1,
        )

        with self._fbo.activate() as fbo:
            fbo.viewport = region.x, region.y, region.width, region.height
            try:
                yield fbo
            finally:
                fbo.viewport = 0, 0, *self._fbo.size

        self._ctx.projection_matrix = proj_prev

    @classmethod
    def create_from_texture_sequence(cls, textures: Sequence["Texture"], border: int = 1) -> "TextureAtlas":
        """
        Create a texture atlas of a reasonable size from a sequence of textures.

        :param textures: A sequence of textures (list, set, tuple, generator etc.)
        :param border: The border for the atlas in pixels (space between each texture)
        """
        textures = sorted(set(textures), key=lambda x: x.image.size[1])
        size = TextureAtlas.calculate_minimum_size(textures)
        return TextureAtlas(size, textures=textures, border=border)

    @classmethod
    def calculate_minimum_size(cls, textures: Sequence["Texture"], border: int = 1):
        """
        Calculate the minimum atlas size needed to store the
        the provided sequence of textures

        :param textures: Sequence of textures
        :param border: The border around each texture in pixels
        :return: An estimated minimum size as a (width, height) tuple
        """
        # TODO: This method is not very efficient.

        # Try to guess some sane minimum size to reduce the brute force iterations
        total_area = sum(t.image.size[0] * t.image.size[1] for t in textures)
        sqrt_size = int(math.sqrt(total_area))
        start_size = sqrt_size or RESIZE_STEP
        if start_size % RESIZE_STEP:
            start_size = sqrt_size + (64 - sqrt_size % RESIZE_STEP)

        # For now we just brute force a solution by gradually
        # increasing the atlas size using the allocator as a guide.
        for size in range(start_size, 16385, RESIZE_STEP):
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

    def read_texture_image_from_atlas(self, texture: "Texture") -> Image.Image:
        """
        Read the pixel data for a texture directly from the atlas texture on the GPU.
        The contents of this image can be altered by rendering into the atlas and
        is useful in situations were you need the updated pixel data on the python side.

        :param texture: The texture to get the image for
        :return: A pillow image containing the pixel data in the atlas
        """
        region = self.get_image_region_info(texture.image_data.hash)
        viewport = (
            region.x,
            region.y,
            region.width,
            region.height,
        )
        data = self.fbo.read(viewport=viewport, components=4)
        return Image.frombytes("RGBA", (region.width, region.height), data)

    def update_texture_image_from_atlas(self, texture: "Texture") -> None:
        """
        Update the arcade Texture's internal image with the pixel data content
        from the atlas texture on the GPU. This can be useful if you render
        into the atlas and need to update the texture with the new pixel data.

        :param texture: The texture to update
        """
        texture.image_data.image = self.read_texture_image_from_atlas(texture)

    def to_image(
        self,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: Tuple[int, int, int] = (255, 0, 0),
    ) -> Image.Image:
        """
        Convert the atlas to a Pillow image.

        Borders can also be drawn into the image to visualize the
        regions of the atlas.

        :param flip: Flip the image horizontally
        :param components: Number of components. (3 = RGB, 4 = RGBA)
        :param draw_borders: Draw region borders into image
        :param color: RGB color of the borders
        :return: A pillow image containing the atlas texture
        """
        if components not in (3, 4):
            raise ValueError(f"Components must be 3 or 4, not {components}")

        mode = "RGBA"[:components]

        image = Image.frombytes(
            mode,
            self._texture.size,
            bytes(self._fbo.read(components=components)),
        )

        if draw_borders:
            draw = ImageDraw.Draw(image)
            for rg in self._image_regions.values():
                p1 = rg.x, rg.y
                p2 = rg.x + rg.width - 1, rg.y + rg.height - 1
                draw.rectangle((p1, p2), outline=border_color, width=1)

        if flip:
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        return image

    def show(
        self,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: Tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        """
        Show the texture atlas using Pillow.

        Borders can also be drawn into the image to visualize the
        regions of the atlas.

        :param flip: Flip the image horizontally
        :param components: Number of components. (3 = RGB, 4 = RGBA)
        :param draw_borders: Draw region borders into image
        :param color: RGB color of the borders
        """
        self.to_image(
            flip=flip,
            components=components,
            draw_borders=draw_borders,
            border_color=border_color,
        ).show()

    def save(
        self,
        path: Union[str, Path],
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: Tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        """
        Save the texture atlas to a png.

        Borders can also be drawn into the image to visualize the
        regions of the atlas.

        :param path: The path to save the atlas on disk
        :param flip: Flip the image horizontally
        :param components: Number of components. (3 = RGB, 4 = RGBA)
        :param color: RGB color of the borders
        :return: A pillow image containing the atlas texture
        """
        self.to_image(
            flip=flip,
            components=components,
            draw_borders=draw_borders,
            border_color=border_color,
        ).save(path, format="png")

    def _check_size(self, size: Tuple[int, int]) -> None:
        """Check it the atlas exceeds the hardware limitations"""
        if size[0] > self._max_size[0] or size[1] > self._max_size[1]:
            raise Exception(
                "Attempting to create or resize an atlas to "
                f"{size} past its maximum size of {self._max_size}"
            )
