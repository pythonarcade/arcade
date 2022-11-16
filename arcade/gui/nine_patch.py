from typing import Optional, Tuple

import arcade
import arcade.gl as gl


class NinePatchTexture:
    """
    A 9-patch texture which take a specific texture and two pixel coordinates.

    Using these coordinates the texture is split into 9 'patches'.
    each patch is then stretched in specific ways to keep the edges a specific width/height.

    :param start: start coordinate of patch slices (lower left)
    :param end: end coordinate of patch slices (upper right)
    :param Texture texture: The texture used for the 9-patch
    :param TextureAtlas atlas: the atlas which the texture belongs to (defaults to arcades default atlas)
    """

    def __init__(
        self,
        *,
        start: Tuple[float, float],
        end: Tuple[float, float],
        texture: arcade.Texture,
        atlas: Optional[arcade.TextureAtlas] = None
    ):
        self._ctx = arcade.get_window().ctx

        # TODO: Cache in context
        self._program = self.ctx.load_program(
            vertex_shader=":resources:shaders/gui/nine_patch_vs.glsl",
            geometry_shader=":resources:shaders/gui/nine_patch_gs.glsl",
            fragment_shader=":resources:shaders/gui/nine_patch_fs.glsl",
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
        self._start = start
        self._end = end

    @property
    def ctx(self) -> arcade.ArcadeContext:
        """
        The OpenGL context for this renderer.
        """
        return self._ctx

    @property
    def texture(self) -> arcade.Texture:
        """
        Get or set the texture.
        """
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
        if not self._atlas.has_texture(texture):
            self._atlas.add(texture)
        self._texture = texture

    @property
    def size(self) -> Tuple[float, float]:
        """
        Get size of texture.
        """
        return self.texture.size

    @property
    def width(self):
        return self.texture.width

    @property
    def height(self):
        return self.texture.height

    def draw_sized(
        self,
        *,
        size: Tuple[float, float],
        **kwargs
    ):
        """
        Draw the 9-patch.
        """
        # TODO support to draw at a given position
        self.program.set_uniform_safe(
            "texture_id", self._atlas.get_texture_id(self._texture.name)
        )

        self.program["start"] = self._start
        self.program["end"] = self._end
        self.program["size"] = size
        self.program["t_size"] = self._texture.size

        self._atlas.use_uv_texture(0)
        self._atlas.texture.use(1)
        self._geometry.render(self._program, vertices=1)

    def reload_shader(self):
        print("reloading shader")
        self._program = self.ctx.load_program(
            vertex_shader=":resources:shaders/gui/nine_patch_vs.glsl",
            geometry_shader=":resources:shaders/gui/nine_patch_gs.glsl",
            fragment_shader=":resources:shaders/gui/nine_patch_fs.glsl",
        )
        # Configure texture channels
        self.program.set_uniform_safe("uv_texture", 0)
        self.program["sprite_texture"] = 1
