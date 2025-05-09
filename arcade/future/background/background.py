import arcade.gl as gl
from arcade.future.background import BackgroundTexture
from arcade.window_commands import get_window


class Background:
    """
    Backgrounds are large geometries to which a Background texture is rendered.
    By default, the position defines the bottom left corner.
    If the size is larger than the given BackgroundTexture the texture will repeat.
    A shift value can be given when calling draw.
    This can be used to move the background without actually adjusting the position
    You may supply your own shader and geometries.
    The default shader implements 4 uniforms.
    vec2 pos, vec2 size, vec3 color, mat3 pixelTransform, and float blend.
    """

    def __init__(
        self,
        texture: BackgroundTexture,
        pos: tuple[float, float],
        size: tuple[int, int],
        color: tuple[float, float, float] | tuple[int, int, int],
        shader: gl.Program | None = None,
        geometry: gl.Geometry | None = None,
    ):
        self._ctx = get_window().ctx
        if shader is None:
            shader = self._ctx.load_program(
                vertex_shader=":system:/shaders/background_vs.glsl",
                fragment_shader=":system:/shaders/background_fs.glsl",
            )
        self.shader = shader

        if geometry is None:
            geometry = gl.geometry.quad_2d(pos=(0.5, 0.5))
        self.geometry = geometry

        self.texture = texture

        self._pos = pos
        try:
            self.shader["pos"] = pos
        except KeyError:
            print(
                "Attempting to set uniform 'pos' when the shader does not "
                "have a uniform with that name."
            )

        self._size = size
        try:
            self.shader["size"] = size
        except KeyError:
            print(
                "Attempting to set uniform 'size' when the shader does not "
                "have a uniform with that name."
            )

        self._blend = 1.0
        try:
            self.shader["blend"] = 1.0
        except KeyError:
            print(
                "Attempting to set uniform 'blend' when the shader does not "
                "have a uniform with that name."
            )

        self._color = (
            color if sum(color) <= 3.0 else (color[0] / 255, color[1] / 255, color[2] / 255)
        )
        try:
            self.shader["color"] = self._color
        except KeyError:
            print(
                "Attempting to set uniform 'color' when the shader does not "
                "have a uniform with that name."
            )

    @staticmethod
    def from_file(
        tex_src: str,
        pos: tuple[float, float] = (0.0, 0.0),
        size: tuple[int, int] | None = None,
        offset: tuple[float, float] = (0.0, 0.0),
        scale: float = 1.0,
        angle: float = 0.0,
        *,
        filters=(gl.NEAREST, gl.NEAREST),
        color: tuple[int, int, int] | None = None,
        color_norm: tuple[float, float, float] | None = None,
        shader: gl.Program | None = None,
        geometry: gl.Geometry | None = None,
    ):
        """
        This will generate a Background from an input image source.
        The generated texture is not stored in the texture cache or any texture atlas.

        Args:
            tex_src: The image source.
            pos: The position of the Background (Bottom Left Corner by default).
            size: The width and height of the Background.
            offset: The BackgroundTexture offset.
            scale: The BackgroundTexture Scale.
            angle: The BackgroundTexture angle.
            filters: The OpenGl Texture filters (gl.Nearest by default).
            color: This is a color defined from 0-255. Priorities color_norm
            color_norm: This is a color defined from 0.0-1.0. Priorities color_norm
                            assumed to be in the range 0.0-1.0.
            shader: The shader used for rendering.
            geometry: The geometry used for rendering (a rectangle equal to the size by default).
        """
        background_texture = BackgroundTexture.from_file(tex_src, offset, scale, angle, filters)
        if size is None:
            size = background_texture.texture.size

        if color_norm:
            _color = color_norm
        elif color:
            _color = color[0] / 255, color[1] / 255, color[2] / 255
        else:
            _color = (1.0, 1.0, 1.0)

        return Background(background_texture, pos, size, _color, shader, geometry)

    @property
    def pos(self) -> tuple[float, float]:
        return self._pos

    @pos.setter
    def pos(self, value: tuple[float, float]):
        self._pos = value

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @size.setter
    def size(self, value: tuple[int, int]):
        self._size = value
        try:
            self.shader["size"] = value
        except KeyError:
            print(
                "Attempting to set uniform 'size' when the shader does not "
                "have a uniform with that name."
            )

    @property
    def blend(self) -> float:
        return self._blend

    @blend.setter
    def blend(self, value):
        self._blend = value
        try:
            self.shader["blend"] = value
        except KeyError:
            print(
                "Attempting to set uniform 'blend' when the shader does not "
                "have a uniform with that name."
            )

    @property
    def color(self) -> tuple[int, int, int]:
        """
        Color in the range of 0-255.
        """
        return (
            int(self._color[0] * 255),
            int(self._color[1] * 255),
            int(self._color[2] * 255),
        )

    @color.setter
    def color(self, value: tuple[int, int, int]):
        """
        Color in the range of 0-255.
        """
        self._color = (value[0] / 255, value[1] / 255, value[2] / 255)
        try:
            self.shader["color"] = self._color
        except KeyError:
            print(
                "Attempting to set uniform 'color' when shader does not "
                "have uniform with that name."
            )

    @property
    def color_norm(self) -> tuple[float, float, float]:
        return self._color

    @color_norm.setter
    def color_norm(self, value: tuple[float, float, float]):
        self._color = value
        try:
            self.shader["color"] = self._color
        except KeyError:
            print(
                "Attempting to set uniform 'color' when shader does not "
                "have uniform with that name."
            )

    def draw(self, shift: tuple[float, float] = (0.0, 0.0)):
        try:
            self.shader["pixelTransform"] = self.texture.pixel_transform
        except KeyError:
            print(
                "Attempting to set uniform 'pixelTransform' when the shader does "
                "not have a uniform with that name."
            )

        try:
            self.shader["pos"] = self.pos[0] + shift[0], self.pos[1] + shift[1]
        except KeyError:
            print(
                "Attempting to set uniform 'pos' when the shader does not have a "
                "uniform with that name."
            )

        self.texture.use(0)
        with self._ctx.enabled(self._ctx.BLEND):
            self.geometry.render(self.shader)

    def blend_layer(self, other, percent: float):
        self.blend = 1 - percent
        other.blend = percent
