"""
Post-processing shaders.
"""
from pathlib import Path
from pyglet import gl
from typing import Tuple
from arcade.gl import Context
from arcade.gl.texture import Texture
from arcade import get_window
from arcade.experimental import geometry
from arcade.experimental.gaussian_kernel import gaussian_kernel

TEXTURE_VAO = None


def render_texture(texture):
    """Render a texture"""
    global TEXTURE_VAO
    if TEXTURE_VAO is None:
        ctx = get_window().ctx
        texture_prog = ctx.load_program(
            vertex_shader_filename=':resources:shaders/texture_ndc_vs.glsl',
            fragment_shader_filename=':resources:shaders/texture_fs.glsl',
        )
        TEXTURE_VAO = geometry.quad_fs(texture_prog, size=(2.0, 2.0))

    texture.use(0)
    TEXTURE_VAO.render()


class PostProcessing:
    """Base class"""
    def __init__(self, size: Tuple[int, int], *args, **kwargs):
        self._size = size
        window = get_window()
        if not window:
            raise RuntimeError("No window found")
        self._ctx = window.ctx

    @property
    def ctx(self) -> Context:
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

    # def render(self, *args, **kwargs) -> Texture:
    #     """ Render. Should be over-loaded by the child class. """
    #     pass

    def resize(self, size: Tuple[int, int]):
        """
        Resize post processing buffers.
        This is often needed of the screen since changes.
        """
        self._size = size


class GaussianBlurHorizontal(PostProcessing):
    """ Blur the buffer horizontally. """
    def __init__(self, size: Tuple[int, int], defines):
        super().__init__(size)
        color_attachment = self.ctx.texture(size,
                                            components=3,
                                            wrap_x=gl.GL_CLAMP_TO_EDGE,
                                            wrap_y=gl.GL_CLAMP_TO_EDGE)
        self._fbo = self.ctx.framebuffer(color_attachments=color_attachment)
        self._program = self.ctx.load_program(
            defines=defines,
            vertex_shader=':resources:shaders/texture_default_projection_vs.glsl',
            fragment_shader=':resources:shaders/gaussian_blur_x_fs.glsl',
        )
        self._quad_fs = geometry.quad_fs(size=(2.0, 2.0))

    def render(self, source: Texture) -> Texture:
        """ Render """
        self._fbo.use()
        source.use(0)
        self._program['target_size'] = self._fbo.size
        self._quad_fs.render(self._program)
        return self._fbo.color_attachments[0]


class GaussianBlurVertical(PostProcessing):
    """ Blur the buffer vertically. """

    def __init__(self, size: Tuple[int, int], defines):
        super().__init__(size)
        self._fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture(size,
                                               components=3,
                                               wrap_x=gl.GL_CLAMP_TO_EDGE,
                                               wrap_y=gl.GL_CLAMP_TO_EDGE))
        self._program = self.ctx.load_program(
            defines=defines,
            vertex_shader=':resources:shaders/texture_default_projection_vs.glsl',
            fragment_shader=':resources:shaders/gaussian_blur_y_fs.glsl',
        )
        self._quad_fs = geometry.quad_fs(size=(2.0, 2.0))

    def render(self, source: Texture) -> Texture:
        """ Render """
        self._fbo.use()
        source.use(0)
        self._program['target_size'] = self._fbo.size
        self._quad_fs.render(self._program)
        return self._fbo.color_attachments[0]


class GaussianBlur(PostProcessing):
    """ Do both horizontal and vertical blurs. """
    def __init__(self, size, defines):
        super().__init__(size)
        self._blur_x = GaussianBlurHorizontal(size, defines=defines)
        self._blur_y = GaussianBlurVertical(size, defines=defines)

    def render(self, source: Texture) -> Texture:
        """ Render """
        blurred_x = self._blur_x.render(source)
        return self._blur_y.render(blurred_x)


class BloomEffect(PostProcessing):
    """ Post processing to create a bloom/glow effect. """
    def __init__(self,
                 size,
                 kernel_size=21,
                 sigma: float = 4,
                 mu: float = 0,
                 multiplier: float = 5,
                 step: int = 1):
        super().__init__(size, kernel_size=kernel_size)

        kernel = gaussian_kernel(kernel_size, sigma, mu, step)
        if multiplier != 1:
            for i in range(kernel_size):
                kernel[i] *= multiplier

        kernel_string = "("
        for index, item in enumerate(kernel):
            kernel_string += f"{item:.7}"
            if index < len(kernel) - 1:
                kernel_string += ", "
        kernel_string += ")"

        defines = {'KERNEL_SIZE': str(kernel_size), 'MY_KERNEL': kernel_string}
        self._gaussian = GaussianBlur(size, defines=defines)
        self._combine_program = self.ctx.load_program(
            defines=defines,
            vertex_shader=':resources:shaders/texture_default_projection_vs.glsl',
            fragment_shader=':resources:shaders/gaussian_combine_fs.glsl'
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
