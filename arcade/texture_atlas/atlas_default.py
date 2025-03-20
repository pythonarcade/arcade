from __future__ import annotations

import contextlib
import copy

# import logging
# import time
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Sequence,
)
from weakref import WeakSet, WeakValueDictionary, finalize

import PIL.Image
from PIL import Image, ImageDraw
from PIL.Image import Resampling
from pyglet.image.atlas import (
    Allocator,
    AllocatorException,
)
from pyglet.math import Mat4

from arcade.camera.static import static_from_raw_orthographic
from arcade.texture.transforms import Transform
from arcade.window_commands import get_window

from .base import TextureAtlasBase
from .ref_counters import (
    ImageDataRefCounter,
    UniqueTextureRefCounter,
)
from .region import AtlasRegion
from .uv_data import UVData

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

# LOG = logging.getLogger(__name__)
# LOG.handlers = [logging.StreamHandler()]
# LOG.setLevel(logging.INFO)


class DefaultTextureAtlas(TextureAtlasBase):
    """
    A texture atlas with a size in a context.

    A texture atlas is a large texture containing several textures
    so OpenGL can easily batch draw thousands or hundreds of thousands
    of sprites on one draw operation.

    The atlas is auto-GCed meaning that textures and images are removed
    when the user removes all references to them. This is the only way
    to remove textures and images from the atlas.

    This is a fairly simple atlas that stores horizontal strips were
    the height of the strip is the texture/image with the larges height.
    This is done for performance reasons.

    Adding a texture to this atlas generates a texture id.
    This id is used the sprite list vertex data to reference what
    texture each sprite is using. The actual texture coordinates
    are located in a float32 texture this atlas is responsible for
    keeping up to date.

    The atlas deals with image and textures. The image is the actual
    image data. The texture is the Arcade texture object that contains
    the image and other information about such as transforms.
    Several textures can share the same image with different transforms
    applied. The transforms are simply changing the order of the texture
    coordinates to flip, rotate or mirror the image.

    Args:
        size:
            The width and height of the atlas in pixels
        border:
            The number of edge pixels to repeat around images in the atlas.
            This kind of padding is important to avoid edge artifacts.
            Default is 1 pixel.
        textures:
            Optional sequence of textures to add to the atlas on creation
        auto_resize:
            Automatically resize the atlas when full. Default is ``True``.
        ctx:
            The context for this atlas (will use window context if left empty)
        capacity:
            The number of textures the atlas keeps track of.
            This is multiplied by 4096. Meaning capacity=2 is 8192 textures.
            This value can affect the performance of the atlas.
    """

    def __init__(
        self,
        size: tuple[int, int],
        *,
        border: int = 1,
        textures: Sequence[Texture] | None = None,
        auto_resize: bool = True,
        ctx: ArcadeContext | None = None,
        capacity: int = 2,
    ):
        self._ctx = ctx or get_window().ctx
        self._max_size = self._ctx.info.MAX_VIEWPORT_DIMS
        self._size: tuple[int, int] = size
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
        self._image_regions: dict[str, AtlasRegion] = dict()
        self._texture_regions: dict[str, AtlasRegion] = dict()

        # Ref counter for images and textures. Per atlas we need to keep
        # track of ho many times an image is used in textures to determine
        # when to remove an image from the atlas. We only ever track images
        # using their sha256 hash to avoid writing the same image multiple times.
        self._image_ref_count = ImageDataRefCounter()
        # Tracks how many instances of a unique texture we have in the atlas.
        # This basically means textures with the same image and vertex order (atlas_name)
        self._unique_texture_ref_count = UniqueTextureRefCounter()

        # A list of all the images this atlas contains.
        # Unique by: Internal hash property
        self._images: WeakValueDictionary[str, ImageData] = WeakValueDictionary()

        # All textures added to the atlas
        self._textures: WeakSet[Texture] = WeakSet()
        # atlas_name: Set of textures with matching atlas name
        self._unique_textures: dict[str, WeakSet[Texture]] = dict()

        self._textures_added = 0
        self._textures_removed = 0
        self._finalizers_created = 0

        for tex in textures or []:
            self.add(tex)

    @property
    def max_width(self) -> int:
        """The maximum width of the atlas in pixels."""
        return self._max_size[0]

    @property
    def max_height(self) -> int:
        """The maximum height of the atlas in pixels."""
        return self._max_size[1]

    @property
    def max_size(self) -> tuple[int, int]:
        """The maximum size of the atlas in pixels (x, y)."""
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
        """The texture border in pixels"""
        return self._border

    @property
    def image_uv_texture(self) -> Texture2D:
        """Texture coordinate texture for images."""
        return self._image_uvs.texture

    @property
    def texture_uv_texture(self) -> Texture2D:
        """Texture coordinate texture for textures."""
        return self._texture_uvs.texture

    @property
    def textures(self) -> list[Texture]:
        """
        All textures instance added to the atlas regardless
        of their internal state. See :py:meth:`unique_textures``
        for textures with unique image data and transformation.
        """
        return list(self._textures)

    @property
    def unique_textures(self) -> list[Texture]:
        """
        All unique textures in the atlas.

        These are textures using an image with the same hash
        and the same vertex order. The full list of all textures
        can be found in :py:meth:`textures`.
        """
        # Grab the first texture from each set
        textures: list[Texture] = []
        # NOTE: keys can drop out of the dict during iteration.
        #       Copy they keys and look up each set to avoid this.
        for key in list(self._unique_textures.keys()):
            tex_set = self._unique_textures.get(key, None)
            # Entry was GCed during iteration
            if tex_set is None:
                continue
            # Corrupt data
            if len(tex_set) == 0:
                raise RuntimeError("Empty set in unique textures")

            textures.append(next(iter(tex_set)))

        return textures

    @property
    def images(self) -> list[ImageData]:
        """
        Return a list of all the images in the atlas.

        A new list is constructed from the internal weak set of images.
        """
        return list(self._images.values())

    def add(self, texture: Texture) -> tuple[int, AtlasRegion]:
        """
        Add a texture to the atlas.

        Add a texture to the atlas.

        Args:
            texture: The texture to add
        Returns:
            texture_id, AtlasRegion tuple
        Raises:
            AllocatorException: If there are no room for the texture
        """
        return self._add(texture)

    def _add(self, texture: Texture, create_finalizer=True) -> tuple[int, AtlasRegion]:
        """
        Internal add method with additional control. We we rebuild the atlas
        we don't want to create finalizers for the texture or they will be
        removed multiple times causing errors.

        Args:
            texture:
                The texture to add
            create_finalizer:
                If a finalizer should be created
        """
        # Quickly handle a texture already having a unique texture in the atlas
        if self.has_unique_texture(texture):
            # Add add references to the duplicate texture
            if not self.has_texture(texture):
                self._add_texture_ref(texture, create_finalizer=create_finalizer)
            slot = self._texture_uvs.get_slot_or_raise(texture.atlas_name)
            region = self.get_texture_region_info(texture.atlas_name)
            return slot, region

        # Add the *image* to the atlas if it's not already there
        if not self.has_image(texture.image_data):
            try:
                # Attempt to allocate space for the image
                x, y, slot, region = self._allocate_image(texture.image_data)
                # Write the pixel data to the atlas texture
                self.write_image(texture.image_data.image, x, y)
            except AllocatorException:
                if not self._auto_resize:
                    raise AllocatorException(
                        f"No more space for image {texture.image_data.hash} "
                        f"size={texture.image.size}. "
                        f"Curr size: {self._size}. "
                        f"Max size: {self._max_size}"
                    )

                # If we have lost regions/images we can try to rebuild the atlas
                removed_image_count = self._image_ref_count.get_total_decref()
                if removed_image_count > 0:
                    self.rebuild()
                    return self._add(texture, create_finalizer=create_finalizer)

                # Double the size of the atlas (capped by max size)
                width = min(self.width * 2, self.max_width)
                height = min(self.height * 2, self.max_height)
                # If the size didn't change we have a problem ..
                if self._size == (width, height):
                    raise

                # Resize the atlas making more room for images
                self.resize((width, height))

                # Recursively try to add the texture again
                return self._add(texture, create_finalizer=create_finalizer)

        # Finally we can register the texture
        self._add_texture_ref(texture, create_finalizer=create_finalizer)
        info = self._allocate_texture(texture)
        return info

    def _add_texture_ref(self, texture: Texture, create_finalizer=True) -> None:
        """
        Add references to the texture and image data.
        including finalizer to remove the texture when it's no longer used.

        Args:
            texture:
                The texture
            create_finalizer:
                If a finalizer should be created
        """
        self._textures.add(texture)
        self._unique_texture_ref_count.inc_ref(texture)
        self._image_ref_count.inc_ref(texture.image_data)

        if create_finalizer:
            ref = finalize(
                texture,
                self._remove_texture_by_identifiers,
                texture.atlas_name,
                texture.image_data.hash,
            )
            # Don't bother removing texture on program exit
            ref.atexit = False
            self._finalizers_created += 1

        self._textures_added += 1

    def remove(self, texture: Texture) -> None:
        """
        Remove a texture from the atlas.

        This is only supported by static atlases. Dynamic atlases with
        garbage collection will remove texture using python's garbage
        collector.

        Args:
            texture: The texture to remove
        """
        raise RuntimeError(
            "The default texture atlas does not support manual removal of textures. "
            "To remove textures from the atlas you must remove all references to the texture "
            "and let the python garbage collector handle the removal."
        )

    def _allocate_texture(self, texture: Texture) -> tuple[int, AtlasRegion]:
        """
        Add or update a unique texture in the atlas.
        This is mainly responsible for updating the texture coordinates.

        Args:
            texture: The texture to add
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
        # Collect unique textures
        self._unique_textures.setdefault(texture.atlas_name, WeakSet()).add(texture)

        return slot, texture_region

    def _allocate_image(self, image_data: "ImageData") -> tuple[int, int, int, AtlasRegion]:
        """
        Attempts to allocate space for an image in the atlas or
        update the existing space for the image.

        This doesn't write the texture to the atlas texture itself.
        It only allocates space.

        Returns:
            The x, y texture_id, TextureRegion
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

        # LOG.debug("Allocated new space for image %s : %s %s", image_data.hash, x, y)

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

        self._images[image_data.hash] = image_data
        return x, y, slot, region

    def write_image(self, image: PIL.Image.Image, x: int, y: int) -> None:
        """
        Write a PIL image to the atlas in a specific region.

        Args:
            image:
                The pillow image
            x:
                The x position to write the texture
            y:
                The y position to write the texture
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
                "RGBA",
                size=(image.width + self._border * 2, image.height + self._border * 2),
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
                strip_top = strip_top.resize((image.width, self._border), Resampling.NEAREST)
                strip_bottom = strip_bottom.resize((image.width, self._border), Resampling.NEAREST)
                strip_left = strip_left.resize((self._border, image.height), Resampling.NEAREST)
                strip_right = strip_right.resize((self._border, image.height), Resampling.NEAREST)

            tmp.paste(strip_top, (self._border, 0))
            tmp.paste(strip_bottom, (self._border, tmp.height - self._border))
            tmp.paste(strip_left, (0, self._border))
            tmp.paste(strip_right, (tmp.width - self._border, self._border))
        else:
            tmp = image

        # Write the image directly to graphics memory in the allocated space
        self._texture.write(tmp.tobytes(), 0, viewport=viewport)

    def _remove_texture_by_identifiers(self, atlas_name: str, hash: str):
        """
        Called by the finalizer to remove a texture by its identifiers.
        This should never be called directly.

        Args:
            atlas_name: The name of the texture in the atlas
            hash: The hash of the image data
        """
        # LOG.info("Removing texture: %s", atlas_name)
        # print("Removing texture:", atlas_name)

        # Remove the unique texture if ref counter reaches 0
        if self._unique_texture_ref_count.dec_ref_by_atlas_name(atlas_name) == 0:
            # Remove the unique texture key to signal we don't have any more
            refs = self._unique_textures[atlas_name]
            if len(refs) == 0:
                del self._unique_textures[atlas_name]

            # Reclaim region and uv slot
            del self._texture_regions[atlas_name]
            self._texture_uvs.free_slot_by_name(atlas_name)

        # Remove the image if ref counter reaches 0
        if self._image_ref_count.dec_ref_by_hash(hash) == 0:
            # May have been removed by GC
            try:
                del self._images[hash]
            except KeyError:
                pass

            del self._image_regions[hash]

            # Reclaim the image uv slot
            self._image_uvs.free_slot_by_name(hash)

        self._textures_removed += 1

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

        Args:
            texture: The texture to update
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

        Args:
            hash: The hash of the image
        """
        return self._image_regions[hash]

    def get_texture_region_info(self, atlas_name: str) -> AtlasRegion:
        """
        Get the region info for a texture by atlas name

        Args:
            atlas_name: The name of the texture in the atlas
        """
        return self._texture_regions[atlas_name]

    def get_texture_id(self, texture: "Texture") -> int:
        """
        Get the internal id for a Texture in the atlas

        Args:
            texture: The texture to get.
        """
        return self._texture_uvs.get_slot_or_raise(texture.atlas_name)

    def has_texture(self, texture: "Texture") -> bool:
        """
        Check if a texture is already in the atlas.

        Args:
            texture: The texture to check
        """
        return texture in self._textures

    def has_unique_texture(self, texture: "Texture") -> bool:
        """
        Check if the atlas already have a texture with the
        same image data and vertex order

        Args:
            texture: The texture to check
        """
        return texture.atlas_name in self._unique_textures

    def has_image(self, image_data: ImageData) -> bool:
        """
        Check if an image is already in the atlas

        Args:
            image_data: The image data to check
        """
        return image_data.hash in self._images

    def resize(self, size: tuple[int, int], force=False) -> None:
        """
        Resize the atlas.

        This will re-allocate all the images in the atlas to better fit
        the new size. Pixel data will be copied from the old atlas to the
        new one on the gpu meaning it will also persist anything that
        was rendered to the atlas.

        A failed resize will result in an AllocatorException. Unless the
        atlas is resized again to a working size the atlas will be in an
        undefined state.

        Args:
            size:
                The new size
            force:
                Force a resize even if the size is the same
        """
        # LOG.info("[%s] Resizing atlas from %s to %s", id(self), self._size, size)
        # print("Resizing atlas from", self._size, "to", size)

        # Only resize if the size actually changed
        if size == self._size and not force:
            return

        self._check_size(size)
        # resize_start = time.perf_counter()

        # Keep a reference to the old atlas texture so we can copy it into the new one
        atlas_texture_old = self._texture
        atlas_texture_old.filter = self._ctx.NEAREST, self._ctx.NEAREST
        self._size = size

        # Create new image uv data temporarily keeping the old one
        self._image_uvs.write_to_texture()
        image_uvs_old = self._image_uvs
        self._image_uvs = image_uvs_old.clone_with_slots()

        # Create new atlas texture and framebuffer
        self._texture = self._ctx.texture(size, components=4)
        self._fbo = self._ctx.framebuffer(color_attachments=[self._texture])

        # Store old images and textures before clearing the atlas
        images = list(self._images.values())
        textures = self.unique_textures

        # Clear the regions and allocator.
        self._allocator = Allocator(*self._size)
        # NOTE: We keep the image_regions and texture_regions in case the resize fails

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
            0,
            self.width,
            self.height,
            0,
            -100,
            100,
        )

        # Render the old atlas into the new one. This means we actually move
        # all the textures around from the old to the new position.
        with self._fbo.activate():
            # Ensure no context flags are enabled
            with self._ctx.enabled_only():
                self._ctx.geometry_empty.render(
                    self._ctx.atlas_resize_program,
                    mode=self._ctx.POINTS,
                    vertices=self.max_width,
                )

        # duration = time.perf_counter() - resize_start
        # LOG.info("[%s] Atlas resize took %s seconds", id(self), duration)

    def rebuild(self) -> None:
        """
        Rebuild the underlying atlas texture.

        This method also tries to organize the textures more efficiently ordering them by size.
        The texture ids will persist so the sprite list doesn't need to be rebuilt.
        """
        # LOG.info("Rebuilding atlas")

        # Hold a reference to the old textures
        textures = self.textures

        self._image_ref_count.clear()
        self._unique_texture_ref_count.clear()

        # Clear the atlas but keep the uv slot mapping
        self._fbo.clear()

        self._textures.clear()
        self._unique_textures.clear()
        self._images.clear()

        self._image_regions.clear()
        self._texture_regions.clear()
        self._allocator = Allocator(*self._size)

        # Add textures back sorted by height to potentially make more room
        for texture in sorted(textures, key=lambda x: x.image.size[1]):
            self._add(texture, create_finalizer=False)

    def use_uv_texture(self, unit: int = 0) -> None:
        """
        Bind the texture coordinate texture to a channel.
        In addition this method writes the texture
        coordinate to the texture if the data is stale.
        This is to avoid a full update every time a texture
        is added to the atlas.

        Args:
            unit: The texture unit to bind the uv texture
        """
        # Sync the texture coordinates to the texture if dirty
        self._image_uvs.write_to_texture()
        self._texture_uvs.write_to_texture()

        self._texture_uvs.texture.use(unit)

    @contextlib.contextmanager
    def render_into(
        self,
        texture: "Texture",
        projection: tuple[float, float, float, float] | None = None,
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

        Args:
            texture:
                The texture area to render into
            projection:
                The ortho projection to render with. This parameter can be
                left blank if no projection changes are needed.
                The tuple values are: (left, right, button, top)
        """
        region = self._texture_regions[texture.atlas_name]
        prev_camera = self.ctx.current_camera

        # Use provided projection or default
        projection = projection or (0, region.width, 0, region.height)
        # Flip the top and bottom because we need to render things upside down
        projection = projection[0], projection[1], projection[3], projection[2]

        static_camera = static_from_raw_orthographic(
            projection,
            -1,
            1,  # near, far planes
            1.0,  # zoom
        )

        with self._fbo.activate() as fbo:
            try:
                static_camera.use()
                fbo.viewport = region.x, region.y, region.width, region.height
                yield fbo
            finally:
                fbo.viewport = 0, 0, *self._fbo.size
        prev_camera.use()

    def read_texture_image_from_atlas(self, texture: "Texture") -> Image.Image:
        """
        Read the pixel data for a texture directly from the atlas texture on the GPU.
        The contents of this image can be altered by rendering into the atlas and
        is useful in situations were you need the updated pixel data on the python side.

        Args:
            texture: The texture to get the image for
        Returns:
            A pillow image containing the pixel data in the atlas
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
        Update the Arcade Texture's internal image with the pixel data content
        from the atlas texture on the GPU. This can be useful if you render
        into the atlas and need to update the texture with the new pixel data.

        Args:
            texture: The texture to update
        """
        texture.image_data.image = self.read_texture_image_from_atlas(texture)

    def to_image(
        self,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: tuple[int, int, int] = (255, 0, 0),
    ) -> Image.Image:
        """
        Convert the atlas to a Pillow image.

        Borders can also be drawn into the image to visualize the
        regions of the atlas.

        Args:
            flip:
                Flip the image horizontally
            components:
                Number of components. (3 = RGB, 4 = RGBA)
            draw_borders:
                Draw region borders into image
            border_color:
                RGB color of the borders
        Returns:
            A pillow image containing the atlas texture
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
        border_color: tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        """
        Show the texture atlas using Pillow.

        Borders can also be drawn into the image to visualize the
        regions of the atlas.

        Args:
            flip:
                Flip the image horizontally
            components:
                Number of components. (3 = RGB, 4 = RGBA)
            draw_borders:
                Draw region borders into image
            border_color:
                RGB color of the borders
        """
        self.to_image(
            flip=flip,
            components=components,
            draw_borders=draw_borders,
            border_color=border_color,
        ).show()

    def save(
        self,
        path: str | Path,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        """
        Save the texture atlas to a png.

        Borders can also be drawn into the image to visualize the
        regions of the atlas.

        Args:
            path:
                The path to save the atlas on disk
            flip:
                Flip the image horizontally
            components:
                Number of components. (3 = RGB, 4 = RGBA)
            draw_borders:
                Draw region borders into image
            border_color:
                RGB color of the borders
        """
        self.to_image(
            flip=flip,
            components=components,
            draw_borders=draw_borders,
            border_color=border_color,
        ).save(path, format="png")

    def _check_size(self, size: tuple[int, int]) -> None:
        """Check it the atlas exceeds the hardware limitations"""
        if size[0] > self._max_size[0] or size[1] > self._max_size[1]:
            raise Exception(
                "Attempting to create or resize an atlas to "
                f"{size} past its maximum size of {self._max_size}"
            )
