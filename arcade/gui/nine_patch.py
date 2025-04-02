import arcade
import arcade.gl as gl
from arcade.texture_atlas.base import TextureAtlasBase


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

        # pixel texture co-ordinate start and end of central box.
        self._left = left
        self._right = right
        self._bottom = bottom
        self._top = top

        self._check_sizes()

        # Created in _init_deferred
        self._program: gl.program.Program
        self._geometry: gl.Geometry
        self._ctx: arcade.ArcadeContext
        self._atlas: TextureAtlasBase
        try:
            self._init_deferred()
        except Exception:
            pass

    def _init_deferred(self):
        """Deferred initialization when lazy loaded"""
        self._ctx = arcade.get_window().ctx
        # TODO: Cache in context?
        self._program = self._ctx.load_program(
            vertex_shader=":system:shaders/gui/nine_patch_vs.glsl",
            geometry_shader=":system:shaders/gui/nine_patch_gs.glsl",
            fragment_shader=":system:shaders/gui/nine_patch_fs.glsl",
        )
        # Configure texture channels
        self._program.set_uniform_safe("uv_texture", 0)
        self._program["sprite_texture"] = 1

        # TODO: Cache in context?
        self._geometry = self._ctx.geometry()

        # References for the texture
        self._atlas = self._custom_atlas or self._ctx.default_atlas
        self._add_to_atlas(self.texture)

        self._initialized = True

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
    def program(self) -> gl.program.Program:
        """Get or set the shader program.

        Returns the default shader if no other shader is assigned.
        """
        if not self._initialized:
            raise RuntimeError("The NinePatchTexture has not been initialized")

        return self._program

    @program.setter
    def program(self, program: gl.program.Program):
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

        if blend:
            self._ctx.enable_only(self._ctx.BLEND)
        else:
            self._ctx.disable(self._ctx.BLEND)

        self.program.set_uniform_safe("texture_id", self._atlas.get_texture_id(self._texture))
        if pixelated:
            self._atlas.texture.filter = self._ctx.NEAREST, self._ctx.NEAREST
        else:
            self._atlas.texture.filter = self._ctx.LINEAR, self._ctx.LINEAR

        self.program["position"] = rect.bottom_left
        self.program["start"] = self._left, self._bottom
        self.program["end"] = self.width - self._right, self.height - self._top
        self.program["size"] = rect.size
        self.program["t_size"] = self._texture.size

        self._atlas.use_uv_texture(0)
        self._atlas.texture.use(1)
        self._geometry.render(self._program, vertices=1)

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
