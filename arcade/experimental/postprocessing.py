"""
Post-processing shaders.
"""
from pathlib import Path
from pyglet import gl
from typing import Tuple
from arcade import shader
from arcade import get_window
from arcade.experimental import geometry

SHADER_PATH = (Path(__file__).parent / 'shaders').resolve()
TEXTURE_VAO = None


def render_texture(texture):
    """Render a texture"""
    global TEXTURE_VAO
    if TEXTURE_VAO is None:
        ctx = get_window().ctx
        texture_prog = ctx.load_program(
            vertex_shader_filename=SHADER_PATH / 'texture_ndc_vs.glsl',
            fragment_shader_filename=SHADER_PATH / 'texture_fs.glsl',
        )
        TEXTURE_VAO = geometry.quad_fs(texture_prog, size=(2.0, 2.0))

    texture.use(0)
    TEXTURE_VAO.render()


class PostProcessing:
    """Base class"""
    def __init__(self, size: Tuple[int, int], *args, **kwargs):
        self._size = size
        self._ctx = get_window().ctx

    @property
    def ctx(self) -> shader.Context:
        """ Get the shader context. """
        return self._ctx

    @property
    def width(self):
        """ Get the width of the buffer. """
        return self._size[0]

    @property
    def height(self):
        """ Get the height of the buffer. """
        return self._size[1]

    @property
    def size(self):
        """ Get the size of the buffer. """
        return self._size

    def render(self, *args, **kwargs) -> shader.Texture:
        """ Render. Should be over-loaded by the child class. """
        pass

    def resize(self, size: Tuple[int, int]):
        """
        Resize post processing buffers.
        This is often needed of the screen since changes.
        """
        self._size = size


class GaussianBlurHorizontal(PostProcessing):
    """ Blur the buffer horizontally. """
    def __init__(self, size: Tuple[int, int], kernel_size=5):
        super().__init__(size)
        self._kernel_size = kernel_size
        color_attachment = self.ctx.texture(size, components=3, wrap_x=gl.GL_CLAMP_TO_EDGE, wrap_y=gl.GL_CLAMP_TO_EDGE)
        self._fbo = self.ctx.framebuffer(color_attachments=color_attachment)
        self._program = self.ctx.load_program(
            vertex_shader=SHADER_PATH / 'texture_ndc_vs.glsl',
            fragment_shader=SHADER_PATH / 'gaussian_blurx_fs.glsl',
        )
        self._quad_fs = geometry.quad_fs(size=(2.0, 2.0))

    def render(self, source: shader.Texture) -> shader.Texture:
        """ Render """
        self._fbo.use()
        source.use(0)
        self._program['target_size'] = self._fbo.size
        self._quad_fs.render(self._program)
        return self._fbo.color_attachments[0]


class GaussianBlurVertical(PostProcessing):
    """ Blur the buffer vertically. """

    def __init__(self, size: Tuple[int, int], kernel_size=5):
        super().__init__(size)
        self._kernel_size = kernel_size
        self._fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture(size, components=3, wrap_x=gl.GL_CLAMP_TO_EDGE, wrap_y=gl.GL_CLAMP_TO_EDGE))
        self._program = self.ctx.load_program(
            vertex_shader=SHADER_PATH / 'texture_ndc_vs.glsl',
            fragment_shader=SHADER_PATH / 'gaussian_blury_fs.glsl',
        )
        self._quad_fs = geometry.quad_fs(size=(2.0, 2.0))

    def render(self, source: shader.Texture) -> shader.Texture:
        """ Render """
        self._fbo.use()
        source.use(0)
        self._program['target_size'] = self._fbo.size
        self._quad_fs.render(self._program)
        return self._fbo.color_attachments[0]


class GaussianBlur(PostProcessing):
    """ Do both horizontal and vertical blurs. """
    def __init__(self, size, kernel_size=5):
        super().__init__(size, kernel_size=kernel_size)
        self._blur_x = GaussianBlurHorizontal(size, kernel_size=kernel_size)
        self._blur_y = GaussianBlurVertical(size, kernel_size=kernel_size)

    def render(self, source: shader.Texture) -> shader.Texture:
        """ Render """
        blurred_x = self._blur_x.render(source)
        return self._blur_y.render(blurred_x)


class Glow(PostProcessing):
    """ Post processing to create a bloom/glow effect. """
    def __init__(self, size, kernel_size=5):
        super().__init__(size, kernel_size=kernel_size)
        self._gaussian = GaussianBlur(size, kernel_size=kernel_size)
        self._combine_program = self.ctx.load_program(
            vertex_shader=SHADER_PATH / 'texture_ndc_vs.glsl',
            fragment_shader=SHADER_PATH / 'glow_combine_fs.glsl',
        )
        self._quad_fs = geometry.quad_fs(size=(2.0, 2.0))

    def render(self, source, target):
        """ Render """
        # source.build_mipmaps()
        blurred = self._gaussian.render(source)
        target.use()
        source.use(0)
        blurred.use(1)
        self._combine_program['color_buffer'] = 0
        self._combine_program['blur_buffer'] = 1
        self._quad_fs.render(self._combine_program)
