from array import array

import arcade
from arcade.gl import Buffer, BufferDescription, Geometry, Program
from arcade.math import Vec2
from arcade.texture_atlas.base import TextureAtlasBase
from arcade.types import Rect


class NinePatchTexture:
    """Keeps borders & corners at constant widths while stretching the middle.

    It can be used with new or existing :py:class:`~arcade.gui.UIWidget`
    subclasses wherever an ordinary :py:class:`arcade.Texture` is
    supported. This is useful for GUI elements which must grow or shrink
    while keeping their border decorations constant, such as dialog boxes
    or text boxes.

    The diagram below explains the stretching behavior of this class:

    * Numbered regions with arrows (``<--->``) stretch along the
      direction(s) of any arrows present
    * Bars (``|---|``) mark the distances specified by the border
      parameters (``left``, etc)

    .. code-block::
        :caption: Stretch Axes & Border Parameters

            left                        right
            |------|                 |------|
                                               top
            +------+-----------------+------+  ---
            | (1)  | (2)             | (3)  |   |
            |      | <-------------> |      |   |
            +------+-----------------+------+  ---
            | (4)  | (5)    ^        | (6)  |
            |  ^   |        |        |   ^  |
            |  |   |        |        |   |  |
            |  |   | <------+------> |   |  |
            |  |   |        |        |   |  |
            |  |   |        |        |   |  |
            |  v   |        v        |   v  |
            +------+-----------------+------+  ---
            | (7)  | (8)             | (9)  |   |
            |      | <-------------> |      |   |
            +------+-----------------+------+  ---
                                              bottom

    As the texture is stretched, the numbered slices of the texture behave
    as follows:

    * Areas ``(1)``, ``(3)``, ``(7)`` and ``(9)`` never stretch.
    * Area ``(5)`` stretches both horizontally and vertically.
    * Areas ``(2)`` and ``(8)`` only stretch horizontally.
    * Areas ``(4)`` and ``(6)`` only stretch vertically.

    Args:
        left: The width of the left border of the 9-patch (in pixels)
        right: The width of the right border of the 9-patch (in pixels)
        bottom: The height of the bottom border of the 9-patch (in
            pixels)
        top: The height of the top border of the 9-patch (in pixels)
        texture: The raw texture to use for the 9-patch
        atlas: Specify an atlas other than Arcade's default texture
            atlas
    """

    def __init__(
        self,
        left: int,
        right: int,
        bottom: int,
        top: int,
        texture: arcade.Texture,
        *,
        atlas: TextureAtlasBase | None = None,
    ):
        self._initialized = False
        self._texture = texture
        self._custom_atlas = atlas
        self._geometry_cache: tuple[int, int, int, int, int, Rect] | None = None

        # pixel texture co-ordinate start and end of central box.
        self._left = left
        self._right = right
        self._bottom = bottom
        self._top = top

        self._check_sizes()

        # Created in _init_deferred
        self._buffer: Buffer
        self._program: Program
        self._geometry: Geometry
        self._ctx: arcade.ArcadeContext
        self._atlas: TextureAtlasBase
        try:
            self._init_deferred()
        except Exception:
            pass

    def initialize(self) -> None:
        """
        Manually initialize the NinePatchTexture if it was lazy loaded.
        This has no effect if the NinePatchTexture was already initialized.
        """
        if not self._initialized:
            self._init_deferred()

    @property
    def ctx(self) -> arcade.ArcadeContext:
        """The OpenGL context."""
        if not self._initialized:
            raise RuntimeError("The NinePatchTexture has not been initialized")
        return self._ctx

    @property
    def texture(self) -> arcade.Texture:
        """Get or set the texture."""
        return self._texture

    @texture.setter
    def texture(self, texture: arcade.Texture):
        self._texture = texture
        self._add_to_atlas(texture)

    @property
    def program(self) -> Program:
        """Get or set the shader program.

        Returns the default shader if no other shader is assigned.
        """
        if not self._initialized:
            raise RuntimeError("The NinePatchTexture has not been initialized")

        return self._program

    @program.setter
    def program(self, program: Program):
        if not self._initialized:
            raise RuntimeError("The NinePatchTexture has not been initialized")

        self._program = program

    def _add_to_atlas(self, texture: arcade.Texture):
        """Internal method for setting the texture.

        It ensures the texture is added to the global atlas.
        """
        if not self._atlas.has_texture(texture):
            self._atlas.add(texture)

    @property
    def left(self) -> int:
        """Get or set the left border of the 9-patch."""
        return self._left

    @left.setter
    def left(self, left: int):
        self._left = left

    @property
    def right(self) -> int:
        """Get or set the right border of the 9-patch."""
        return self._right

    @right.setter
    def right(self, right: int):
        self._right = right

    @property
    def bottom(self) -> int:
        """Get or set the bottom border of the 9-patch."""
        return self._bottom

    @bottom.setter
    def bottom(self, bottom: int):
        self._bottom = bottom

    @property
    def top(self) -> int:
        """Get or set the top border of the 9-patch."""
        return self._top

    @top.setter
    def top(self, top: int):
        self._top = top

    @property
    def size(self) -> tuple[int, int]:
        """The size of texture as a width, height tuple in pixels."""
        return self.texture.size

    @property
    def width(self) -> int:
        """The width of the texture in pixels."""
        return self.texture.width

    @property
    def height(self) -> int:
        """The height of the texture in pixels."""
        return self.texture.height

    def draw_rect(
        self,
        *,
        rect: arcade.types.Rect,
        pixelated: bool = True,
        blend: bool = True,
        **kwargs,
    ):
        """Draw the 9-patch texture with a specific size.

        Warning:
            This method assumes the passed dimensions are proper!

            Unexpected behavior may occur if you specify a size
            smaller than the total size of the border areas.

        Args:
            rect: Rectangle to draw the 9-patch texture in
            pixelated: Whether to draw with nearest neighbor
                interpolation
        """
        if not self._initialized:
            self._init_deferred()

        self._create_geometry(rect)

        if blend:
            self._ctx.enable_only(self._ctx.BLEND)
        else:
            self._ctx.disable(self._ctx.BLEND)

        if pixelated:
            self._atlas.texture.filter = self._ctx.NEAREST, self._ctx.NEAREST
        else:
            self._atlas.texture.filter = self._ctx.LINEAR, self._ctx.LINEAR

        self._atlas.use_uv_texture(0)
        self._atlas.texture.use(1)

        self._geometry.render(self._program)

        if blend:
            self._ctx.disable(self._ctx.BLEND)

    def _check_sizes(self):
        """Raise a ValueError if any dimension is invalid."""
        # Sanity check values
        if self._left < 0:
            raise ValueError("Left border must be a positive integer")
        if self._right < 0:
            raise ValueError("Right border must be a positive integer")
        if self._bottom < 0:
            raise ValueError("Bottom border must be a positive integer")
        if self._top < 0:
            raise ValueError("Top border must be a positive integer")

        # Sanity check texture size
        if self._left + self._right > self._texture.width:
            raise ValueError("Left and right border must be smaller than texture width")
        if self._bottom + self._top > self._texture.height:
            raise ValueError("Bottom and top border must be smaller than texture height")

    def _init_deferred(self):
        """Deferred initialization when lazy loaded"""
        self._ctx = arcade.get_window().ctx
        # TODO: Cache in context?
        self._program = self._ctx.load_program(
            vertex_shader=":system:shaders/gui/nine_patch_vs.glsl",
            fragment_shader=":system:shaders/gui/nine_patch_fs.glsl",
        )
        # Configure texture channels
        self._program.set_uniform_safe("uv_texture", 0)
        self._program["sprite_texture"] = 1

        # 4 byte floats * 4 floats * 4 vertices * 9 patches
        self._buffer = self._ctx.buffer(reserve=576)
        # fmt: off
        self._ibo = self._ctx.buffer(
            data=array("i",
                [
                    # Triangulate the patches
                    # First rot
                    0, 1, 2,
                    3, 1, 2,

                    4, 5, 6,
                    7, 5, 6,

                    8, 9, 10,
                    11, 9, 10,

                    # Middle row
                    12, 13, 14,
                    15, 13, 14,

                    16, 17, 18,
                    19, 17, 18,

                    20, 21, 22,
                    23, 21, 22,

                    # Bottom row
                    24, 25, 26,
                    27, 25, 26,

                    28, 29, 30,
                    31, 29, 30,

                    32, 33, 34,
                    35, 33, 34,
                ]
            ),
        )
        # fmt: on
        self._geometry = self._ctx.geometry(
            content=[BufferDescription(self._buffer, "2f 2f", ["in_position", "in_uv"])],
            index_buffer=self._ibo,
            mode=self._ctx.TRIANGLES,
            index_element_size=4,
        )

        # References for the texture
        self._atlas = self._custom_atlas or self._ctx.default_atlas
        self._add_to_atlas(self.texture)
        self._initialized = True

    def _create_geometry(self, rect: Rect):
        """Create vertices for the 9-patch texture."""
        # NOTE: This was ported from glsl geometry shader to python
        # Simulate old uniforms
        cache_key = (
            self._atlas.version,
            self._left,
            self._right,
            self._bottom,
            self._top,
            rect,
        )
        if cache_key == self._geometry_cache:
            return
        self._geometry_cache = cache_key

        position = rect.bottom_left
        start = Vec2(self._left, self._bottom)
        end = Vec2(self.width - self._right, self.height - self._top)
        size = rect.size
        t_size = Vec2(*self._texture.size)
        atlas_size = Vec2(*self._atlas.size)

        # Patch points starting from upper left row by row
        p1 = position + Vec2(0.0, size.y)
        p2 = position + Vec2(start.x, size.y)
        p3 = position + Vec2(size.x - (t_size.x - end.x), size.y)
        p4 = position + Vec2(size.x, size.y)

        y = size.y - (t_size.y - end.y)
        p5 = position + Vec2(0.0, y)
        p6 = position + Vec2(start.x, y)
        p7 = position + Vec2(size.x - (t_size.x - end.x), y)
        p8 = position + Vec2(size.x, y)

        p9 = position + Vec2(0.0, start.y)
        p10 = position + Vec2(start.x, start.y)
        p11 = position + Vec2(size.x - (t_size.x - end.x), start.y)
        p12 = position + Vec2(size.x, start.y)

        p13 = position + Vec2(0.0, 0.0)
        p14 = position + Vec2(start.x, 0.0)
        p15 = position + Vec2(size.x - (t_size.x - end.x), 0.0)
        p16 = position + Vec2(size.x, 0.0)

        # <AtlasRegion
        #     x=1 y=1
        #     width=100 height=100
        #     uvs=(
        #         0.001953125, 0.001953125,
        #         0.197265625, 0.001953125,
        #         0.001953125, 0.197265625,
        #         0.197265625, 0.197265625,
        #     )
        # Get texture coordinates
        # vec2 uv0, uv1, uv2, uv3
        region = self._atlas.get_texture_region_info(self._texture.atlas_name)
        tex_coords = region.texture_coordinates
        uv0 = Vec2(tex_coords[0], tex_coords[1])
        uv1 = Vec2(tex_coords[2], tex_coords[3])
        uv2 = Vec2(tex_coords[4], tex_coords[5])
        uv3 = Vec2(tex_coords[6], tex_coords[7])

        # Local corner offsets in pixels
        left = start.x
        right = t_size.x - end.x
        top = t_size.y - end.y
        bottom = start.y

        # UV offsets to the inner rectangle in the patch
        # This is the global texture coordinate offset in the entire atlas
        c1 = Vec2(left, top) / atlas_size  # Upper left corner
        c2 = Vec2(right, top) / atlas_size  # Upper right corner
        c3 = Vec2(left, bottom) / atlas_size  # Lower left corner
        c4 = Vec2(right, bottom) / atlas_size  # Lower right corner

        # Texture coordinates for all the points in the patch
        t1 = uv0
        t2 = uv0 + Vec2(c1.x, 0.0)
        t3 = uv1 - Vec2(c2.x, 0.0)
        t4 = uv1

        t5 = uv0 + Vec2(0.0, c1.y)
        t6 = uv0 + c1
        t7 = uv1 + Vec2(-c2.x, c2.y)
        t8 = uv1 + Vec2(0.0, c2.y)

        t9 = uv2 - Vec2(0.0, c3.y)
        t10 = uv2 + Vec2(c3.x, -c3.y)
        t11 = uv3 - c4
        t12 = uv3 - Vec2(0.0, c4.y)

        t13 = uv2
        t14 = uv2 + Vec2(c3.x, 0.0)
        t15 = uv3 - Vec2(c4.x, 0.0)
        t16 = uv3

        # fmt: off
        primitives = [
            # First row - two fixed corners + stretchy middle
            # Upper left corner. Fixed size.
            p1, t1,
            p5, t5,
            p2, t2,
            p6, t6,
            # Upper middle part stretches on x axis
            p2, t2,
            p6, t6,
            p3, t3,
            p7, t7,
            # Upper right corner. Fixed size
            p3, t3,
            p7, t7,
            p4, t4,
            p8, t8,

            #  Middle row: Two stretchy sides + stretchy middle
            # left border sketching on y axis
            p5, t5,
            p9, t9,
            p6, t6,
            p10, t10,
            # Center stretchy area
            p6, t6,
            p10, t10,
            p7, t7,
            p11, t11,
            # Right border. Stenches on y axis
            p7, t7,
            p11, t11,
            p8, t8,
            p12, t12,

            # Bottom row: two fixed corners + stretchy middle
            # Lower left corner. Fixed size.
            p9, t9,
            p13, t13,
            p10, t10,
            p14, t14,
            # Lower middle part stretches on x axis
            p10, t10,
            p14, t14,
            p11, t11,
            p15, t15,
            # Lower right corner. Fixed size
            p11, t11,
            p15, t15,
            p12, t12,
            p16, t16,
        ]
        # fmt: on

        data = array("f", [coord for point in primitives for coord in point])
        self._buffer.write(data.tobytes())
