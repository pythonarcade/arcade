"""
Texture atlas for SpriteList

The long term goal is to rely on pyglet's texture atlas, but
it's still unclear what features we need supported in arcade
so need to prototype something to get started.

We're still building on pyglet's allocator.

Pyglet atlases are located here:
https://github.com/einarf/pyglet/blob/master/pyglet/image/atlas.py

"""
import math
import time
import logging
from typing import Dict, List, Tuple, Sequence, TYPE_CHECKING
from array import array

import PIL
from PIL import Image, ImageDraw
from arcade.gl.framebuffer import Framebuffer
from collections import deque
from contextlib import contextmanager


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
# The amount of pixels we increase the atlas when scanning for a reasonable size.
# It must divide. Must be a power of two number like 64, 256, 512 etx
RESIZE_STEP = 128
LOG = logging.getLogger(__name__)


class AtlasRegion:
    """
    Stores information about where a texture is located

    :param str atlas: The atlas this region belongs to
    :param str texture: The arcade texture
    :param int x: The x position of the texture
    :param int y: The y position of the texture
    :param int width: The width of the texture in pixels
    :param int height: The height of the texture in pixels
    """

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

    :param Tuple[int, int] size: The width and height of the atlas in pixels
    :param int border: Currently no effect; Should always be 1 to avoid textures bleeding
    :param Sequence[arcade.Texture] textures: The texture for this atlas
    :param bool auto_resize: Automatically resize the atlas when full
    :param Context ctx: The context for this atlas (will use window context if left empty)
    """

    def __init__(
        self,
        size: Tuple[int, int],
        *,
        border: int = 1,
        textures: Sequence["Texture"] = None,
        auto_resize: bool = True,
        ctx: "ArcadeContext" = None,
    ):

        self._ctx = ctx or arcade.get_window().ctx
        self._max_size = self._ctx.info.MAX_VIEWPORT_DIMS
        self._size: Tuple[int, int] = size
        self._border: int = 1
        self._allocator = Allocator(*self._size)
        self._auto_resize = auto_resize
        self._check_size(self._size)

        self._texture = self._ctx.texture(size, components=4)
        # Creating an fbo makes us able to clear the texture
        self._fbo = self._ctx.framebuffer(color_attachments=[self._texture])

        # A dictionary of all the allocated regions
        # The key is the cache name for a texture
        self._atlas_regions: Dict[str, AtlasRegion] = dict()

        # A set of textures this atlas contains for fast lookups + set operations
        self._textures: List["Texture"] = []

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

    def add(self, texture: "Texture") -> Tuple[int, AtlasRegion]:
        """
        Add a texture to the atlas.

        :param Texture texture: The texture to add
        :return: texture_id, AtlasRegion tuple
        """
        if self.has_texture(texture):
            slot = self.get_texture_id(texture.name)
            region = self.get_region_info(texture.name)
            return slot, region

        LOG.info("Attempting to add texture: %s", texture.name)

        try:
            x, y, slot, region = self.allocate(texture)
        except AllocatorException:
            LOG.info("[%s] No room for %s size %s", id(self), texture.name, texture.image.size)
            if self._auto_resize:
                width = min(self.width * 2, self.max_width)
                height = min(self.height * 2, self.max_height)
                if self._size == (width, height):
                    raise
                self.resize((width, height))
                return self.add(texture)
            else:
                raise

        self.write_texture(texture, x, y)
        return slot, region

    def allocate(self, texture: "Texture") -> Tuple[int, int, int, AtlasRegion]:
        """
        Attempts to allocate space for a texture in the atlas.
        This doesn't write the texture to the atlas texture itself.
        It only allocates space.

        :return: The x, y texture_id, TextureRegion
        """
        # Allocate space for texture
        try:
            x, y = self._allocator.alloc(
                texture.image.width + self.border * 2,
                texture.image.height + self.border * 2,
            )
        except AllocatorException:
            raise AllocatorException(
                f"No more space for texture {texture.name} size={texture.image.size}"
            )

        LOG.debug("Allocated new space for texture %s : %s %s", texture.name, x, y)

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
        # Existing slots for textures will only happen when re-building
        # the atlas since we want to keep the same slots to avoid
        # re-building the sprite list
        existing_slot = self._uv_slots.get(texture.name)
        slot = existing_slot if existing_slot is not None else self._uv_slots_free.popleft()
        self._uv_slots[texture.name] = slot
        self._uv_data[slot * 4] = region.texture_coordinates[0]
        self._uv_data[slot * 4 + 1] = region.texture_coordinates[1]
        self._uv_data[slot * 4 + 2] = region.texture_coordinates[2]
        self._uv_data[slot * 4 + 3] = region.texture_coordinates[3]
        self._uv_data_changed = True
        self._textures.append(texture)
        return x, y, slot, region

    def write_texture(self, texture: "Texture", x: int, y: int):
        """
        Writes an arcade texture to a subsection of the texture atlas
        """
        # NOTE: We convert to RGBA when padding the image data
        # if texture.image.mode != "RGBA":
        #     LOG.warning(f"TextureAtlas: Converting texture '{texture.name}' to RGBA")
        #     texture.image = texture.image.convert("RGBA")

        self.write_image(texture.image, x, y)

    def write_image(self, image: PIL.Image.Image, x: int, y: int) -> None:
        """
        Write a PIL image to the atlas in a specific region.

        :param PIL.Image.Image image: The pillow image
        :param int x: The x position to write the texture
        :param int y: The y position to write the texture
        """
        # NOTE: We assume border is at least 1 here
        # Write into atlas at the allocated location + a 1 pixel border
        viewport = (
            x + self._border - 1,
            y + self._border - 1,
            image.width + 2,
            image.height + 2,
        )
        # print(image.size, viewport,"|", x, y, self._border)

        # Pad the 1-pixel border with repeating data
        tmp = Image.new('RGBA', (image.width + 2, image.height + 2))
        tmp.paste(image, (1, 1))
        tmp.paste(tmp.crop((1          , 1           , image.width+1, 2             )), (1            , 0             ))  # noqa
        tmp.paste(tmp.crop((1          , image.height, image.width+1, image.height+1)), (1            , image.height+1))  # noqa
        tmp.paste(tmp.crop((1          , 0           ,             2, image.height+2)), (0            , 0             ))  # noqa
        tmp.paste(tmp.crop((image.width, 0           , image.width+1, image.height+2)), (image.width+1, 0             ))  # noqa

        # Write the image directly to graphics memory in the allocated space
        self._texture.write(tmp.tobytes(), 0, viewport=viewport)

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
            region.x,
            region.y,
            region.width,
            region.height,
        )
        self._texture.write(texture.image.tobytes(), 0, viewport=viewport)

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
        return texture.name in self._atlas_regions

    # TODO: Possibly let user decide the resize function
    # def resize(self, size: Tuple[int, int]) -> None:
    #     """
    #     Resize the texture atlas.
    #     This will cause a full rebuild.

    #     :param Tuple[int,int]: The new size
    #     """
    #     # if size == self._size:
    #     #     return

    #     self._check_size(size)
    #     self._size = size
    #     self._texture = None
    #     self._fbo = None
    #     gc.collect()  # Try to force garbage collection of the gl resource asap
    #     self._texture = self._ctx.texture(size, components=4)
    #     self._fbo = self._ctx.framebuffer(color_attachments=[self._texture])
    #     self.rebuild()

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

        if size == self._size:
            return

        resize_start = time.perf_counter()

        self._check_size(size)
        self._size = size
        # Keep the old atlas texture and uv texture
        uv_texture_old = self._uv_texture
        texture_old = self._texture
        self._uv_texture.write(self._uv_data, 0)

        # Create new atlas texture and uv texture + fbo
        self._uv_texture = self._ctx.texture(
            (TEXCOORD_BUFFER_SIZE, 1), components=4, dtype="f4"
        )
        self._texture = self._ctx.texture(size, components=4)
        self._fbo = self._ctx.framebuffer(color_attachments=[self._texture])

        textures = self._textures
        self.clear(texture_ids=False, texture=False)
        for texture in sorted(textures, key=lambda x: x.image.size[1]):
            self.allocate(texture)

        # Write the new UV data
        self._uv_texture.write(self._uv_data, 0)
        self._uv_data_changed = False

        # Bind textures for atlas copy shader
        texture_old.use(0)
        self._texture.use(1)
        uv_texture_old.use(2)
        self._uv_texture.use(3)
        self._ctx.atlas_resize_program["projection"] = arcade.create_orthogonal_projection(
            0, self.width, self.height, 0,
        )

        with self._fbo.activate():
            self._ctx.disable(self._ctx.BLEND)
            self._ctx.atlas_geometry.render(
                self._ctx.atlas_resize_program,
                mode=self._ctx.POINTS,
                vertices=TEXCOORD_BUFFER_SIZE,
            )
        LOG.info("[%s] Atlas resize took %s seconds", id(self), time.perf_counter() - resize_start)

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
        self.clear(texture_ids=False)
        # Add textures back sorted by height to potentially make more room
        for texture in sorted(textures, key=lambda x: x.image.size[1]):
            self.add(texture)

    def clear(self, texture_ids: bool = True, texture: bool = True) -> None:
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
        self._textures = []
        self._atlas_regions = dict()
        self._allocator = Allocator(*self._size)
        if texture_ids:
            self._uv_slots_free = deque(i for i in range(TEXCOORD_BUFFER_SIZE))
            self._uv_slots = dict()

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

    @contextmanager
    def render_into(
        self, texture: "Texture",
        projection: Tuple[float, float, float, float] = None,
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
        region = self._atlas_regions[texture.name]
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
        :param border:
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

    def to_image(
        self,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: Tuple[int, int, int] = (255, 0, 0),
    ) -> Image.Image:
        """
        Convert the atlas to a Pillow image

        :param bool flip: Flip the image horizontally
        :param int components: Number of components. (3 = RGB, 4 = RGBA)
        :param bool draw_borders: Draw region borders into image
        :param color: RGB color of the borders
        :return: A pillow image containing the atlas texture
        """
        if components == 4:
            mode = "RGBA"
        elif components == 3:
            mode = "RGB"
        else:
            raise ValueError(f"Components must be 3 or 4, not {components}")
        image = Image.frombytes(
            mode,
            self._texture.size,
            bytes(self._fbo.read(components=components)),
        )

        if self.border == 1 and draw_borders:
            draw = ImageDraw.Draw(image)
            for rg in self._atlas_regions.values():
                p1 = rg.x - 1, rg.y - 1
                p2 = rg.x + rg.width, rg.y + rg.height
                draw.rectangle([p1, p2], outline=border_color, width=1)

        if flip:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

        return image

    def show(
        self,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: Tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        """
        Show the texture atlas using Pillow

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
        path: str,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: Tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        """
        Save the texture atlas to a png.

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
