from PIL import Image

from arcade.context import ArcadeContext
from arcade.window_commands import get_window
from arcade.resources import resolve_resource_path
import arcade.gl as gl
from pyglet.math import Mat3

class Background:
    """
    Backgrounds are large geometries to which a Background texture is rendered.
    By default, the position defines the bottom left corner.
    If the size is larger than the given BackgroundTexture the texture will repeat.
    A shift value can be given when calling draw.
    This can be used to move the background without actually adjusting the position
    You may supply your own shader and geometries.
    The default shader implements 4 uniforms.
        vec2 pos, vec2 size, mat3 pixelTransform, and float blend.
    """

    def __init__(self,
                 texture: BackgroundTexture,
                 pos: tuple[float, float],
                 size: tuple[float, float],
                 shader: gl.Program = None,
                 geometry: gl.Geometry = None):

        if shader is None:
            shader = get_window().ctx.load_program(vertex_shader=":resources:/shaders/background_vs.glsl",
                                                   fragment_shader=":resources:/shaders/background_fs.glsl")
        self.shader = shader

        if geometry is None:
            geometry = gl.geometry.quad_2d(pos=(0.5, 0.5))
        self.geometry = geometry

        self.texture = texture

        self._pos = pos
        try:
            self.shader['pos'] = pos
        except KeyError:
            print("Attempting to set uniform 'pos' when the shader does not have a uniform with that name.")

        self._size = size
        try:
            self.shader['size'] = size
        except KeyError:
            print("Attempting to set uniform 'size' when the shader does not have a uniform with that name.")

    @staticmethod
    def from_file(tex_src: str,
                  pos: tuple[float, float] = (0.0, 0.0),
                  size: tuple[int, int] = None,
                  offset: tuple[float, float] = (0.0, 0.0),
                  scale: float = 1.0,
                  angle: float = 0.0,
                  *,
                  filters=(gl.NEAREST, gl.NEAREST),
                  shader: gl.Program = None,
                  geometry: gl.Geometry = None):
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
        :param shader: The shader used for rendering.
        :param geometry: The geometry used for rendering (a rectangle equal to the size by default).
        :return: The generated Background.
        """
        _context = get_window().ctx

        with Image.open(resolve_resource_path(tex_src)).convert("RGBA") as img:
            texture = _context.texture(img.size, data=img.transpose(Image.FLIP_TOP_BOTTOM).tobytes(),
                                       filter=filters)
            if size is None:
                size = texture.size

        background_texture = BackgroundTexture(texture, offset, scale, angle)
        return Background(background_texture, pos, size, shader, geometry)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value: tuple[float, float]):
        self._pos = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value: tuple[int, int]):
        self._size = value
        try:
            self.shader['size'] = value
        except KeyError:
            print("Attempting to set uniform 'size' when the shader does not have a uniform with that name.")

    def draw(self, shift=(0, 0)):
        try:
            self.shader['pixelTransform'] = self.texture.pixel_transform
        except KeyError:
            print("Attempting to set uniform 'pixelTransform' when the shader does not have a uniform with that name.")

        try:
            self.shader['pos'] = self.pos[0] + shift[0], self.pos[1] + shift[1]
        except KeyError:
            print("Attempting to set uniform 'pos' when the shader does not have a uniform with that name.")

        self.texture.use(0)

        self.geometry.render(self.shader)

    @property
    def blend(self):
        try:
            return self.shader['blend']
        except KeyError:
            print("Attempting to get uniform 'blend' when the shader "
                  "does not have a uniform with that name. Defaulting to 1.")
            return 1

    @blend.setter
    def blend(self, value):
        try:
            self.shader['blend'] = value
        except KeyError:
            print("Attempting to set uniform 'blend' when the shader does not have a uniform with that name.")

    def blend_layer(self, other, percent):
        self.blend = 1 - percent
        other.blend = percent
