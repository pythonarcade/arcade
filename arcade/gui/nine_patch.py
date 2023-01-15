from typing import Optional, Tuple

import arcade
import arcade.gl as gl


class NinePatchTexture:
    """
    A 9-patch texture is a texture that can be stretched in specific ways to keep
    the edges a specific width/height. This is useful for GUI elements that need
    to be stretched but have a specific border that should not be stretched.
    The center content of the texture will be stretched.

    Patch structure::

              left              right 
        +------+-----------------+------+
        | (1)  | (2)             | (3)  |
        |      |                 |      |
        +------+-----------------+------+ top
        | (4)  | (5)             | (6)  |
        |      |                 |      |
        |      |                 |      |
        |      |                 |      |
        |      |                 |      |
        |      |                 |      |
        +------+-----------------+------+ bottom
        | (7)  | (8)             | (9)  |
        |      |                 |      |
        +------+-----------------+------+

    To summarize, the texture will be stretched in the following ways:
    * Areas (1), (3), (7) and (9) will not be stretched.
    * Area (5) will be stretched horizontally and vertically.
    * Areas (2) and (8) will be stretched horizontally.
    * Areas (4) and (6) will be stretched vertically.

    :param int left: The left border of the 9-patch (in pixels)
    :param int right: The right border of the 9-patch (in pixels)
    :param int bottom: The bottom border of the 9-patch (in pixels)
    :param int top: The top border of the 9-patch (in pixels)
    :param Texture texture: The texture used for the 9-patch
    :param TextureAtlas atlas: the atlas which the texture belongs to (defaults to arcades default atlas)
    """

    def __init__(
        self,
        *,
        left: int,
        right: int,
        bottom: int,
        top: int,
        texture: arcade.Texture,
        atlas: Optional[arcade.TextureAtlas] = None
    ):
        self._ctx = arcade.get_window().ctx

        # TODO: Cache in context?
        self._program = self.ctx.load_program(
            vertex_shader=":resources:shaders/gui/nine_patch_vs.glsl",
            geometry_shader=":resources:shaders/gui/nine_patch_gs.glsl",
            fragment_shader=":resources:shaders/gui/nine_patch_fs.glsl",
            common=(":resources:shaders/lib/sprite.glsl",),
        )
        # Configure texture channels
        self.program.set_uniform_safe("uv_texture", 0)
        self.program["sprite_texture"] = 1

        # TODO: Cache in context
        self._geometry = self.ctx.geometry()

        # References for the texture
        self._atlas = atlas or self.ctx.default_atlas
        self._texture = texture
        self._set_texture(texture)

        # pixel texture co-ordinate start and end of central box.
        self._left = left
        self._right = right
        self._bottom = bottom
        self._top = top

        self._check_sizes()

    @property
    def ctx(self) -> arcade.ArcadeContext:
        """The OpenGL context."""
        return self._ctx

    @property
    def texture(self) -> arcade.Texture:
        """Get or set the texture."""
        return self._texture

    @texture.setter
    def texture(self, texture: arcade.Texture):
        self._set_texture(texture)

    @property
    def program(self) -> gl.program.Program:
        """
        Get or set the shader program.
        Returns the default shader if no shader is assigned.
        """
        return self._program

    @program.setter
    def program(self, program: gl.program.Program):
        self._program = program

    def _set_texture(self, texture: arcade.Texture):
        """
        Internal method for setting the texture.
        It simply ensures the texture is added to the global atlas
        """
        if not self._atlas.has_texture(texture):
            self._atlas.add(texture)
        self._texture = texture

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
    def size(self) -> Tuple[int, int]:
        """
        Get size of texture.
        """
        return self.texture.size

    @property
    def width(self) -> int:
        """The width of the texture in pixels."""
        return self.texture.width

    @property
    def height(self) -> int:
        """The height of the texture in pixels."""
        return self.texture.height

    def draw_sized(
        self,
        *,
        position: Tuple[float, float] = (0, 0),
        size: Tuple[float, float],
        **kwargs
    ):
        """
        Draw the 9-patch.

        :param size: size of the 9-patch
        """
        # TODO support to draw at a given position
        self.program.set_uniform_safe(
            "texture_id", self._atlas.get_texture_id(self._texture.name)
        )

        self.program["position"] = position
        self.program["start"] = self._left, self._bottom
        self.program["end"] = self.width - self._right, self.height - self._top
        self.program["size"] = size
        self.program["t_size"] = self._texture.size

        self._atlas.use_uv_texture(0)
        self._atlas.texture.use(1)
        self._geometry.render(self._program, vertices=1)

    def _check_sizes(self):
        """
        Check if borders are valid
        """
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
