from pathlib import Path
from typing import Tuple
from arcade import shader
from arcade.experimental import geometry

SHADER_PATH = (Path(__file__).parent / 'shaders').resolve()
TEXTURE_VAO = None


def render_texture(texture):
    """Render a texture"""
    global TEXTURE_VAO
    if TEXTURE_VAO is None:
        texture_prog = shader.load_program(
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

    @property
    def width(self):
        return self._size[0]

    @property
    def height(self):
        return self._size[1]

    @property
    def size(self):
        return self._size

    def render(self, *args, **kwargs) -> shader.Texture:
        pass

    def resize(self, size: Tuple[int, int]):
        """
        Resize post processing buffers.
        This is often needed of the screen since changes.
        """
        self._size = size


class GaussianBlurHorizontal(PostProcessing):

    def __init__(self, size: Tuple[int, int], kernel_size=5):
        super().__init__(size)
        self._kernel_size = kernel_size
        self._fbo = shader.framebuffer(color_attachments=shader.Texture(size, 3))
        self._program = shader.load_program(
            vertex_shader_filename=SHADER_PATH / 'texture_ndc_vs.glsl',
            fragment_shader_filename=SHADER_PATH / 'gaussian_blurx_fs.glsl',
        )
        self._quad_fs = geometry.quad_fs(self._program, size=(2.0, 2.0))

    def render(self, source: shader.Texture) -> shader.Texture:
        self._fbo.use()
        source.use(0)
        self._program['target_size'] = self._fbo.size
        self._quad_fs.render()
        return self._fbo.color_attachments[0]


class GaussianBlurVertical(PostProcessing):

    def __init__(self, size: Tuple[int, int], kernel_size=5):
        super().__init__(size)
        self._kernel_size = kernel_size
        self._fbo = shader.framebuffer(color_attachments=shader.Texture(size, 3))
        self._program = shader.load_program(
            vertex_shader_filename=SHADER_PATH / 'texture_ndc_vs.glsl',
            fragment_shader_filename=SHADER_PATH / 'gaussian_blury_fs.glsl',
        )
        self._quad_fs = geometry.quad_fs(self._program, size=(2.0, 2.0))

    def render(self, source: shader.Texture) -> shader.Texture:
        self._fbo.use()
        source.use(0)
        self._program['target_size'] = self._fbo.size
        self._quad_fs.render()
        return self._fbo.color_attachments[0]


class GaussianBlur(PostProcessing):

    def __init__(self, size, kernel_size=5):
        super().__init__(size, kernel_size=kernel_size)
        self._blur_x = GaussianBlurHorizontal(size, kernel_size=kernel_size)
        self._blur_y = GaussianBlurVertical(size, kernel_size=kernel_size)

    def render(self, source: shader.Texture) -> shader.Texture:
        blurred_x = self._blur_x.render(source)
        return self._blur_y.render(blurred_x)


class Glow(PostProcessing):

    def __init__(self, size, kernel_size=5):
        super().__init__(size,kernel_size=kernel_size)
        self._gaussian = GaussianBlur(size, kernel_size=kernel_size)
        self._combine_program = shader.load_program(
            vertex_shader_filename=SHADER_PATH / 'texture_ndc_vs.glsl',
            fragment_shader_filename=SHADER_PATH / 'glow_combine_fs.glsl',
        )
        self._quad_fs = geometry.quad_fs(self._combine_program, size=(2.0, 2.0))

    def render(self, source, target):
        # source.build_mipmaps()
        blurred = self._gaussian.render(source)
        target.use()
        source.use(0)
        blurred.use(1)
        self._combine_program['color_buffer'] = 0
        self._combine_program['blur_buffer'] = 1
        self._quad_fs.render()
