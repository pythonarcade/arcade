"""
Texture Atlas for SpriteList

The long term goal is to rely on pyglet's texture atlas, but
it's still unclear what features we need supported in arcade
so need to prototype something to get started.

We're still building on pyglet's allocator.

Pyglet atlases are located here:
https://github.com/einarf/pyglet/blob/master/pyglet/image/atlas.py

"""
from __future__ import annotations

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
from weakref import WeakSet

import PIL
import PIL.Image
from PIL import Image, ImageDraw
from pyglet.image.atlas import (
    Allocator,
    AllocatorException,
)
from pyglet.math import Mat4

import arcade
from arcade.gl.framebuffer import Framebuffer
from arcade.texture.transforms import Transform

if TYPE_CHECKING:
    from arcade import ArcadeContext, Texture
    from arcade.gl import Texture2D
    from arcade.texture import ImageData

# The amount of pixels we increase the atlas when scanning for a reasonable size.
# It must divide. Must be a power of two number like 64, 256, 512 etx
RESIZE_STEP = 128
UV_TEXTURE_WIDTH = 4096
LOG = logging.getLogger(__name__)


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

    :param str atlas: The atlas this region belongs to
    :param str texture: The arcade texture
    :param int x: The x position of the texture
    :param int y: The y position of the texture
    :param int width: The width of the texture in pixels
    :param int height: The height of the texture in pixels
    :param tuple texture_coordinates: The texture coordinates (optional)
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
        texture_coordinates: Optional[Tuple[float, float, float, float, float, float, float, float]] = None,
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


class ImageDataRefCounter:
    """
    Helper class to keep track of how many times an image is used
    by a texture in the atlas to determine when it's safe to remove it.
    """
    def __init__(self) -> None:
        self._data: Dict[str, int] = {}

    def inc_ref(self, image_data: "ImageData") -> None:
        self._data[image_data.hash] = self._data.get(image_data.hash, 0) + 1

    def dec_ref(self, image_data: "ImageData") -> None:
        # TODO: Should we raise an error if the ref count is 0?
        if image_data.hash not in self._data:
            return
        self._data[image_data.hash] -= 1
        if self._data[image_data.hash] == 0:
            del self._data[image_data.hash]

    def get_refs(self, image_data: "ImageData") -> int:
        return self._data.get(image_data.hash, 0)

    def count_refs(self) -> int:
        """Helper function to count the total number of references."""
        return sum(self._data.values())

    def __len__(self) -> int:
        return len(self._data)


class TextureAtlas:
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
    :param int border: Currently no effect; Should always be 1 to avoid textures bleeding
    :param Sequence[Texture] textures: The texture for this atlas
    :param bool auto_resize: Automatically resize the atlas when full
    :param Context ctx: The context for this atlas (will use window context if left empty)
    :param int capacity: The number of textures the atlas keeps track of.
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
        self._ctx = ctx or arcade.get_window().ctx
        self._max_size = self._ctx.info.MAX_VIEWPORT_DIMS
        self._size: Tuple[int, int] = size
        self._allocator = Allocator(*self._size)
        self._auto_resize = auto_resize
        self._border: int = border
        if self._border < 0:
            raise ValueError("Border must be 0 or a positive integer")

        # Decides the number of texture and images the atlas can hold.
        # Must be a multiple of UV_TEXTURE_WIDTH due texture coordinates being
        # stored in a float32 texture.
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("Capacity must be a positive integer")
        self._num_image_slots = UV_TEXTURE_WIDTH * capacity  # 16k
        self._num_texture_slots = UV_TEXTURE_WIDTH * capacity  # 16k
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

        # A dictionary of all the allocated regions for images in the atlas
        # The key is the cache name for a texture
        self._image_regions: Dict[str, AtlasRegion] = dict()
        self._texture_regions: Dict[str, AtlasRegion] = dict()
        # Ref counter for images and textures. Per atlas we need to keep
        # track of ho many times an image is used in textures to determine
        # when to remove an image from the atlas.
        self._image_ref_count = ImageDataRefCounter()

        # A list of all the images this atlas contains
        self._images: WeakSet[ImageData] = WeakSet()
        # A set of textures this atlas contains for fast lookups + set operations
        self._textures: WeakSet["Texture"] = WeakSet()

        # Texture containing texture coordinates for images and textures
        # The 4096 width is a safe constant for all GL implementations
        self._image_uv_texture = self._ctx.texture(
            (UV_TEXTURE_WIDTH, self._num_texture_slots * 2 // UV_TEXTURE_WIDTH),
            components=4,
            dtype="f4",
        )
        self._texture_uv_texture = self._ctx.texture(
            (UV_TEXTURE_WIDTH, self._num_image_slots * 2 // UV_TEXTURE_WIDTH),
            components=4,
            dtype="f4",
        )
        self._image_uv_texture.filter = self._ctx.NEAREST, self._ctx.NEAREST
        self._texture_uv_texture.filter = self._ctx.NEAREST, self._ctx.NEAREST
        self._image_uv_data = array("f", [0] * self._num_image_slots * 8)
        self._texture_uv_data = array("f", [0] * self._num_texture_slots * 8)

        # Free slots in the texture coordinate texture for images and textures
        self._image_uv_slots_free = deque(i for i in range(0, self._num_image_slots))
        self._texture_uv_slots_free = deque(i for i in range(0, self._num_texture_slots))

        # Keep track of which slot each texture or image is in
        self._image_uv_slots: Dict[str, int] = dict()  # hash: slot
        self._texture_uv_slots: Dict[str, int] = dict()  # cache_name: slot

        # Dirty flags for when texture coordinates are changed for each type
        self._image_uv_data_changed = True
        self._texture_uv_data_changed = True

        # Add all the textures
        for tex in textures or []:
            self.add(tex)

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

        :rtype: Tuple[int,int]
        """
        return self._size

    @property
    def max_width(self) -> int:
        """
        The maximum width of the atlas in pixels

        :rtype: int
        """
        return self._max_size[0]

    @property
    def max_height(self) -> int:
        """
        The maximum height of the atlas in pixels

        :rtype: int
        """
        return self._max_size[1]

    @property
    def max_size(self) -> Tuple[int, int]:
        """
        The maximum size of the atlas in pixels (x, y)

        :rtype: Tuple[int,int]
        """
        return self._max_size

    @property
    def auto_resize(self) -> bool:
        """
        Get or set the auto resize flag for the atlas.
        If enabled the atlas will resize itself when full.

        :rtype: bool
        """
        return self._auto_resize

    @auto_resize.setter
    def auto_resize(self, value: bool):
        self._auto_resize = value

    @property
    def border(self) -> int:
        """
        The texture border in pixels

        :rtype: int
        """
        return self._border

    @property
    def texture(self) -> "Texture2D":
        """
        The atlas texture.

        :rtype: Texture
        """
        return self._texture

    @property
    def image_uv_texture(self) -> "Texture2D":
        """
        Texture coordinate texture for images.

        :rtype: Texture
        """
        return self._image_uv_texture

    @property
    def texture_uv_texture(self) -> "Texture2D":
        """
        Texture coordinate texture for textures.

        :rtype: Texture
        """
        return self._texture_uv_texture

    @property
    def fbo(self) -> Framebuffer:
        """The framebuffer object for this atlas"""
        return self._fbo

    @property
    def textures(self) -> List["Texture"]:
        """
        Return a list of all the textures in the atlas.

        A new list is constructed from the internal weak set of textures.

        :rtype: Set[Texture]
        """
        return list(self._textures)

    @property
    def images(self) -> List["ImageData"]:
        """
        Return a list of all the images in the atlas.

        A new list is constructed from the internal weak set of images.

        :rtype: List[ImageData]
        """
        return list(self._images)

    def add(self, texture: "Texture") -> Tuple[int, AtlasRegion]:
        """
        Add a texture to the atlas.

        :param Texture texture: The texture to add
        :return: texture_id, AtlasRegion tuple
        """
        # If the texture is already in the atlas we also have the image
        # and can return early with the texture id and region
        if self.has_texture(texture):
            slot = self.get_texture_id(texture.atlas_name)
            region = self.get_texture_region_info(texture.atlas_name)
            return slot, region

        LOG.info("Attempting to add texture: %s | %s", texture.atlas_name)

        # Add the image if we don't already have it.
        # If the atlas is full we will try to resize it.
        if not self.has_image(texture.image_data):
            try:
                x, y, slot, region = self.allocate(texture.image_data)
            except AllocatorException:
                LOG.info("[%s] No room for %s size %s", id(self), texture.atlas_name, texture.image.size)
                if self._auto_resize:
                    width = min(self.width * 2, self.max_width)
                    height = min(self.height * 2, self.max_height)
                    if self._size == (width, height):
                        raise
                    self.resize((width, height))
                    return self.add(texture)
                else:
                    raise

            self.write_image(texture.image_data.image, x, y)

        self._image_ref_count.inc_ref(texture.image_data)
        texture.add_atlas_ref(self)
        return self._allocate_texture(texture)

    def _allocate_texture(self, texture: "Texture") -> Tuple[int, AtlasRegion]:
        """
        Add the texture to the atlas.

        This reserves a slot in the texture coordinate texture
        and returns the slot and region. The region is a copy of
        the image region with the texture coordinates transformed
        using the texture's vertex order.
        """
        if len(self._texture_uv_slots_free) == 0:
            raise AllocatorException((
                "No more free texture slots in the atlas. "
                f"Max number of slots: {self._num_texture_slots}"
            ))

        # Add the texture to the atlas
        existing_slot = self._texture_uv_slots.get(texture.atlas_name)
        slot = existing_slot if existing_slot is not None else self._texture_uv_slots_free.popleft()
        self._texture_uv_slots[texture.atlas_name] = slot
        image_region = self.get_image_region_info(texture.image_data.hash)
        texture_region = copy.deepcopy(image_region)
        # Since we copy the original image region we can always apply the
        # transform without worrying about multiple transforms.
        texture_region.texture_coordinates = Transform.transform_texture_coordinates_order(
            texture_region.texture_coordinates, texture._vertex_order
        )
        self._texture_regions[texture.atlas_name] = texture_region

        # Put texture coordinates into uv buffer
        offset = slot * 8
        for i in range(8):
            self._texture_uv_data[offset + i] = texture_region.texture_coordinates[i]

        self._texture_uv_data_changed = True
        self._textures.add(texture)

        return slot, texture_region

    def allocate(self, image_data: "ImageData") -> Tuple[int, int, int, AtlasRegion]:
        """
        Attempts to allocate space for an image in the atlas.

        This doesn't write the texture to the atlas texture itself.
        It only allocates space.

        :return: The x, y texture_id, TextureRegion
        """
        image = image_data.image

        if len(self._image_uv_slots_free) == 0:
            raise AllocatorException((
                "No more free image slots in the atlas. "
                f"Max number of slots: {self._num_image_slots}"
            ))

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
        existing_slot = self._image_uv_slots.get(image_data.hash)
        slot = existing_slot if existing_slot is not None else self._image_uv_slots_free.popleft()
        self._image_uv_slots[image_data.hash] = slot

        # Put texture coordinates into uv buffer
        offset = slot * 8
        for i in range(8):
            self._image_uv_data[offset + i] = region.texture_coordinates[i]

        self._image_uv_data_changed = True
        self._images.add(image_data)
        return x, y, slot, region

    # def write_texture(self, texture: "Texture", x: int, y: int):
    #     """
    #     Writes an arcade texture to a subsection of the texture atlas
    #     """
    #     self.write_image(texture.image, x, y)

    def write_image(self, image: PIL.Image.Image, x: int, y: int) -> None:
        """
        Write a PIL image to the atlas in a specific region.

        :param PIL.Image.Image image: The pillow image
        :param int x: The x position to write the texture
        :param int y: The y position to write the texture
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
        itself, but leaves the area unclaimed.

        :param Texture texture: The texture to remove
        """
        self._textures.remove(texture)
        # Reclaim the texture uv slot
        del self._texture_regions[texture.atlas_name]
        slot = self._texture_uv_slots[texture.atlas_name]
        del self._texture_uv_slots[texture.atlas_name]
        self._texture_uv_slots_free.appendleft(slot)

        # Decrement the reference count for the image
        self._image_ref_count.dec_ref(texture.image_data)
        # print("Dec ref", texture.image_data.hash, self._image_ref_count.get_refs(texture.image_data))

        # Reclaim the image in the atlas if it's not used by any other texture
        if self._image_ref_count.get_refs(texture.image_data) == 0:
            self._images.remove(texture.image_data)
            del self._image_regions[texture.image_data.hash]
            slot = self._image_uv_slots[texture.image_data.hash]
            del self._image_uv_slots[texture.image_data.hash]
            self._image_uv_slots_free.appendleft(slot)
            # print("Reclaimed image", texture.image_data.hash)

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

        :param str hash: The hash of the image
        :return: The AtlasRegion for the given texture name
        """
        return self._image_regions[hash]

    def get_texture_region_info(self, atlas_name: str) -> AtlasRegion:
        """
        Get the region info for a texture by atlas name

        :return: The AtlasRegion for the given texture name
        """
        return self._texture_regions[atlas_name]

    def get_texture_id(self, atlas_name: str) -> int:
        """
        Get the uv slot for a texture by atlas name

        :param str atlas_name: The name of the texture in the atlas
        :return: The texture id for the given texture name
        """
        return self._texture_uv_slots[atlas_name]

    def get_image_id(self, hash: str) -> int:
        """
        Get the uv slot for a image by hash

        :param str hash: The hash of the image
        :return: The texture id for the given texture name
        """
        return self._image_uv_slots[hash]

    def has_texture(self, texture: "Texture") -> bool:
        """Check if a texture is already in the atlas"""
        return texture in self._textures

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

        :param Tuple[int,int] size: The new size
        """
        LOG.info("[%s] Resizing atlas from %s to %s", id(self), self._size, size)

        # Only resize if the size actually changed
        if size == self._size:
            return

        resize_start = time.perf_counter()

        self._check_size(size)
        self._size = size
        # Keep the old atlas texture and uv texture
        self._image_uv_texture.write(self._image_uv_data, 0)
        image_uv_texture_old = self._image_uv_texture
        # Keep a reference to the old atlas texture so we can copy it into the new one
        atlas_texture_old = self._texture

        # Create new image uv texture as input for the copy shader
        self._image_uv_texture = self._ctx.texture(
            (UV_TEXTURE_WIDTH, self._num_image_slots * 2 // UV_TEXTURE_WIDTH),
            components=4,
            dtype="f4",
        )
        # Create new atlas texture and framebuffer
        self._texture = self._ctx.texture(size, components=4)
        self._fbo = self._ctx.framebuffer(color_attachments=[self._texture])

        # Store old images and textures before clearing the atlas
        images = list(self._images)
        textures = list(self._textures)
        # Clear the atlas without wiping the image and texture ids
        self.clear(clear_texture_ids=False, clear_image_ids=False, texture=False)
        for image in sorted(images, key=lambda x: x.height):
            self.allocate(image)

        # Write the new image uv data
        self._image_uv_texture.write(self._image_uv_data, 0)
        self._image_uv_data_changed = False

        # Update the texture regions. We need to copy the image regions
        # and re-apply the transforms on each texture
        for texture in textures:
            self._allocate_texture(texture)

        self.texture_uv_texture.write(self._texture_uv_data)
        self._texture_uv_data_changed = False

        # Bind textures for atlas copy shader
        atlas_texture_old.use(0)
        self._texture.use(1)
        image_uv_texture_old.use(2)
        self._image_uv_texture.use(3)
        self._ctx.atlas_resize_program["border"] = float(self._border)
        self._ctx.atlas_resize_program["projection"] = Mat4.orthogonal_projection(
            0, self.width, self.height, 0, -100, 100,
        )

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
        # print(duration)

    def rebuild(self) -> None:
        """Rebuild the underlying atlas texture.

        This method also tries to organize the textures more efficiently ordering them by size.
        The texture ids will persist so the sprite list don't need to be rebuilt.
        """
        # Hold a reference to the old textures
        textures = list(self._textures)
        # Clear the atlas but keep the uv slot mapping
        self.clear(clear_image_ids=False, clear_texture_ids=False)
        # Add textures back sorted by height to potentially make more room
        for texture in sorted(textures, key=lambda x: x.image.size[1]):
            self.add(texture)

    def clear(
        self,
        *,
        clear_image_ids: bool = True,
        clear_texture_ids: bool = True,
        texture: bool = True,
    ) -> None:
        """
        Clear and reset the texture atlas.
        Note that also clearing "texture_ids" makes the atlas
        lose track of the old texture ids. This
        means the sprite list must be rebuild from scratch.

        :param bool texture_ids: Clear the assigned texture ids
        :param bool texture: Clear the contents of the atlas texture itself
        """
        if texture:
            self._fbo.clear()
        self._textures = WeakSet()
        self._images = WeakSet()
        self._image_ref_count = ImageDataRefCounter()
        self._image_regions = dict()
        self._texture_regions = dict()
        self._allocator = Allocator(*self._size)
        if clear_image_ids:
            self._image_uv_slots_free = deque(i for i in range(self._num_image_slots))
            self._image_uv_slots = dict()
        if clear_texture_ids:
            self._texture_uv_slots_free = deque(i for i in range(self._num_texture_slots))
            self._texture_uv_slots = dict()

    def use_uv_texture(self, unit: int = 0) -> None:
        """
        Bind the texture coordinate texture to a channel.
        In addition this method writes the texture
        coordinate to the texture if the data is stale.
        This is to avoid a full update every time a texture
        is added to the atlas.

        :param int unit: The texture unit to bind the uv texture
        """
        if self._image_uv_data_changed:
            self._image_uv_texture.write(self._image_uv_data, 0)
            self._image_uv_data_changed = False

        if self._texture_uv_data_changed:
            self._texture_uv_texture.write(self._texture_uv_data, 0)
            self._texture_uv_data_changed = False

        self._texture_uv_texture.use(unit)

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

        :param Texture texture: The texture area to render into
        :param Tuple[float,float,float,float] projection: The ortho projection to render with.
            This parameter can be left blank if no projection changes are needed.
            The tuple values are: (left, right, button, top)
        """
        region = self._texture_regions[texture.atlas_name]
        proj_prev = self._ctx.projection_2d
        # Use provided projection or default
        projection = projection or (0, region.width, 0, region.height)
        # Flip the top and bottom because we need to render things upside down
        projection = projection[0], projection[1], projection[3], projection[2]
        self._ctx.projection_2d = projection

        with self._fbo.activate() as fbo:
            fbo.viewport = region.x, region.y, region.width, region.height
            try:
                yield fbo
            finally:
                fbo.viewport = 0, 0, *self._fbo.size

        self._ctx.projection_2d = proj_prev

    @classmethod
    def create_from_texture_sequence(cls, textures: Sequence["Texture"], border: int = 1) -> "TextureAtlas":
        """
        Create a texture atlas of a reasonable size from a sequence of textures.

        :param Sequence[Texture] textures: A sequence of textures (list, set, tuple, generator etc.)
        :param int border: The border for the atlas in pixels (space between each texture)
        """
        textures = sorted(set(textures), key=lambda x: x.image.size[1])
        size = TextureAtlas.calculate_minimum_size(textures)
        return TextureAtlas(size, textures=textures, border=border)

    @classmethod
    def calculate_minimum_size(cls, textures: Sequence["Texture"], border: int = 1):
        """
        Calculate the minimum atlas size needed to store the
        the provided sequence of textures

        :param Sequence[Texture] textures: Sequence of textures
        :param border: The border around each texture in pixels
        :return: An estimated minimum size as a (width, height) tuple
        """
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

    def get_texture_image(self, texture: "Texture") -> Image.Image:
        """
        Get a Pillow image of a texture's region in the atlas.
        This can be used to inspect the contents of the atlas
        or to save the texture to disk.

        :param Texture texture: The texture to get the image for
        :return: A pillow image containing the pixel data in the atlas
        """
        region = self.get_image_region_info(texture.image_data.hash)
        viewport = (
            region.x + self._border,
            region.y + self._border,
            region.width,
            region.height,
        )
        data = self.fbo.read(viewport=viewport, components=4)
        return Image.frombytes("RGBA", (region.width, region.height), data)

    def sync_texture_image(self, texture: "Texture") -> None:
        """
        Updates a texture's image with the contents in the
        texture atlas. This is usually not needed, but if
        you have altered a texture in the atlas directly
        this can be used to copy the image data back into
        the texture.

        Updating the image will not change the texture's
        hash or the texture's hit box points.

        .. warning::

            This method is somewhat expensive and should be used sparingly.
            Altering the internal image of a texture is not recommended
            unless you know exactly what you're doing. Textures are
            supposed to be immutable.

        :param Texture texture: The texture to update
        """
        texture.image_data.image = self.get_texture_image(texture)

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

        :param bool flip: Flip the image horizontally
        :param int components: Number of components. (3 = RGB, 4 = RGBA)
        :param bool draw_borders: Draw region borders into image
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

        :param bool flip: Flip the image horizontally
        :param int components: Number of components. (3 = RGB, 4 = RGBA)
        :param bool draw_borders: Draw region borders into image
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

        :param str path: The path to save the atlas on disk
        :param bool flip: Flip the image horizontally
        :param int components: Number of components. (3 = RGB, 4 = RGBA)
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
            raise ValueError(
                "Attempting to create or resize an atlas to "
                f"{size} past its maximum size of {self._max_size}"
            )

    def print_contents(self):
        """Debug method to print the contents of the atlas"""
        print("Textures:")
        for texture in self._textures:
            print("->", texture)
        print("Images:")
        for image in self._images:
            print("->", image)
