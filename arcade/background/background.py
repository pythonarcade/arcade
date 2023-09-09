from __future__ import annotations

from typing import Optional, Union, Tuple

from arcade.window_commands import get_window
import arcade.gl as gl

from arcade.background import BackgroundTexture


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
        pos: Tuple[float, float],
        size: Tuple[int, int],
        color: Union[Tuple[float, float, float], Tuple[int, int, int]],
        shader: Optional[gl.Program] = None,
        geometry: Optional[gl.Geometry] = None,
    ):

        if shader is None:
            shader = get_window().ctx.load_program(
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
                "Attempting to set uniform 'pos' when the shader does not have a uniform with that name."
            )

        self._size = size
        try:
            self.shader["size"] = size
        except KeyError:
            print(
                "Attempting to set uniform 'size' when the shader does not have a uniform with that name."
            )

        self._blend = 1.0
        try:
            self.shader["blend"] = 1.0
        except KeyError:
            print(
                "Attempting to set uniform 'blend' when the shader does not have a uniform with that name."
            )

        self._color = (
            color
            if sum(color) <= 3.0
            else (color[0] / 255, color[1] / 255, color[2] / 255)
        )
        try:
            self.shader["color"] = self._color
        except KeyError:
            print(
                "Attempting to set uniform 'color' when the shader does not have a uniform with that name."
            )

    @staticmethod
    def from_file(
        tex_src: str,
        pos: Tuple[float, float] = (0.0, 0.0),
        size: Optional[Tuple[int, int]] = None,
        offset: Tuple[float, float] = (0.0, 0.0),
        scale: float = 1.0,
        angle: float = 0.0,
        *,
        filters=(gl.NEAREST, gl.NEAREST),
        color: Optional[Tuple[int, int, int]] = None,
        color_norm: Optional[Tuple[float, float, float]] = None,
        shader: Optional[gl.Program] = None,
        geometry: Optional[gl.Geometry] = None
    ):
        """
        This will generate a Background from an input image source. The generated texture is not stored in the
        texture cache or any texture atlas.
        :param tex_src: The image source.
        :param pos: The position of the Background (Bottom Left Corner by default).
        :param size: The width and height of the Background.
        :param offset: The BackgroundTexture offset.
        :param scale: The BackgroundTexture Scale.
        :param angle: The BackgroundTexture angle.
        :param filters: The OpenGl Texture filters (gl.Nearest by default).
        :param color: This is a color defined from 0-255. Prioritises color_norm
        :param color_norm: This is a color defined from 0.0-1.0. Prioritises color_norm
        assumed to be in the range 0.0-1.0.
        :param shader: The shader used for rendering.
        :param geometry: The geometry used for rendering (a rectangle equal to the size by default).
        :return: The generated Background.
        """
        background_texture = BackgroundTexture.from_file(
            tex_src, offset, scale, angle, filters
        )
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
    def pos(self) -> Tuple[float, float]:
        return self._pos

    @pos.setter
    def pos(self, value: Tuple[float, float]):
        self._pos = value

    @property
    def size(self) -> Tuple[int, int]:
        return self._size

    @size.setter
    def size(self, value: Tuple[int, int]):
        self._size = value
        try:
            self.shader["size"] = value
        except KeyError:
            print(
                "Attempting to set uniform 'size' when the shader does not have a uniform with that name."
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
                "Attempting to set uniform 'blend' when the shader does not have a uniform with that name."
            )

    @property
    def color(self) -> Tuple[int, int, int]:
        """
        Color in the range of 0-255.
        """
        return (
            int(self._color[0] * 255),
            int(self._color[1] * 255),
            int(self._color[2] * 255),
        )

    @color.setter
    def color(self, value: Tuple[int, int, int]):
        """
        Color in the range of 0-255.
        """
        self._color = (value[0] / 255, value[1] / 255, value[2] / 255)
        try:
            self.shader["color"] = self._color
        except KeyError:
            print(
                "Attempting to set uniform 'color' when shader does not have uniform with that name."
            )

    @property
    def color_norm(self) -> Tuple[float, float, float]:
        return self._color

    @color_norm.setter
    def color_norm(self, value: Tuple[float, float, float]):
        self._color = value
        try:
            self.shader["color"] = self._color
        except KeyError:
            print(
                "Attempting to set uniform 'color' when shader does not have uniform with that name."
            )

    def draw(self, shift: Tuple[float, float] = (0.0, 0.0)):
        try:
            self.shader["pixelTransform"] = self.texture.pixel_transform
        except KeyError:
            print(
                "Attempting to set uniform 'pixelTransform' when the shader does not have a uniform with that name."
            )

        try:
            self.shader["pos"] = self.pos[0] + shift[0], self.pos[1] + shift[1]
        except KeyError:
            print(
                "Attempting to set uniform 'pos' when the shader does not have a uniform with that name."
            )

        self.texture.use(0)

        self.geometry.render(self.shader)

    def blend_layer(self, other, percent: float):
        self.blend = 1 - percent
        other.blend = percent
