"""
Post-processing shaders.
"""

from arcade import get_window
from arcade.context import ArcadeContext
from arcade.experimental.gaussian_kernel import gaussian_kernel
from arcade.gl import geometry
from arcade.gl.texture import Texture2D


class PostProcessing:
    """Base class"""

    def __init__(self, size: tuple[int, int], *args, **kwargs):
        self._size = size
        window = get_window()
        if not window:
            raise RuntimeError("No window found")
        self._ctx = window.ctx

    @property
    def ctx(self) -> ArcadeContext:
        """Get the shader context."""
        return self._ctx

    @property
    def width(self):
        """Get the width of the buffer."""
        return self._size[0]

    @property
    def height(self):
        """Get the height of the buffer."""
        return self._size[1]

    @property
    def size(self):
        """Get the size of the buffer."""
        return self._size

    # def render(self, *args, **kwargs) -> Texture:
    #     """ Render. Should be over-loaded by the child class. """
    #     pass

    def resize(self, size: tuple[int, int]):
        """
        Resize post processing buffers.
        This is often needed of the screen since changes.
        """
        self._size = size


class GaussianBlurPass(PostProcessing):
    def __init__(self, size, kernel_size=5, sigma=2, multiplier=0, step=1):
        super().__init__(size)
        self._kernel_size = kernel_size
        self._sigma = sigma
        self._multiplier = multiplier
        self._step = step

    def _create_kernel(self):
        """Create kernel and return defines for shader"""
        kernel = gaussian_kernel(self._kernel_size, self._sigma, self._multiplier, self._step)
        if self._multiplier != 1:
            for i in range(self._kernel_size):
                kernel[i] *= self._multiplier

        kernel_string = "("
        for index, item in enumerate(kernel):
            kernel_string += f"{item:.7}"
            if index < len(kernel) - 1:
                kernel_string += ", "
        kernel_string += ")"

        return {"KERNEL_SIZE": str(self._kernel_size), "MY_KERNEL": kernel_string}


class GaussianBlurHorizontal(GaussianBlurPass):
    """Blur the buffer horizontally."""

    def __init__(self, size: tuple[int, int], kernel_size=5, sigma=2, multiplier=1, step=1):
        super().__init__(size, kernel_size=5, sigma=2, multiplier=1, step=1)
        color_attachment = self.ctx.texture(
            size, components=3, wrap_x=self.ctx.CLAMP_TO_EDGE, wrap_y=self.ctx.CLAMP_TO_EDGE
        )
        self._fbo = self.ctx.framebuffer(color_attachments=color_attachment)
        self._program = self.ctx.load_program(
            # defines=self._create_kernel(),
            vertex_shader=":system:shaders/texture_default_projection_vs.glsl",
            fragment_shader=":system:shaders/postprocessing/gaussian_blur_x_fs.glsl",
        )
        self._quad_fs = geometry.quad_2d_fs()

    def render(self, source: Texture2D) -> Texture2D:
        """Render"""
        self._fbo.use()
        source.use(0)
        self._program["target_size"] = self._fbo.size
        self._quad_fs.render(self._program)
        return self._fbo.color_attachments[0]


class GaussianBlurVertical(GaussianBlurPass):
    """Blur the buffer vertically."""

    def __init__(self, size: tuple[int, int], kernel_size=5, sigma=2, multiplier=1, step=1):
        super().__init__(
            size, kernel_size=kernel_size, sigma=sigma, multiplier=multiplier, step=step
        )
        self._fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture(
                size,
                components=3,
                wrap_x=self.ctx.CLAMP_TO_EDGE,
                wrap_y=self.ctx.CLAMP_TO_EDGE,
            )
        )
        self._program = self.ctx.load_program(
            # defines=self._create_kernel(),
            vertex_shader=":system:shaders/texture_default_projection_vs.glsl",
            fragment_shader=":system:shaders/postprocessing/gaussian_blur_y_fs.glsl",
        )
        self._quad_fs = geometry.quad_2d_fs()

    def render(self, source: Texture2D) -> Texture2D:
        """Render"""
        self._fbo.use()
        source.use(0)
        self._program["target_size"] = self._fbo.size
        self._quad_fs.render(self._program)
        return self._fbo.color_attachments[0]


class GaussianBlur(PostProcessing):
    """Do both horizontal and vertical blurs."""

    def __init__(self, size, kernel_size=5, sigma=2, multiplier=0, step=1):
        super().__init__(size)
        self._blur_x = GaussianBlurHorizontal(
            size, kernel_size=kernel_size, sigma=sigma, multiplier=multiplier, step=step
        )
        self._blur_y = GaussianBlurVertical(
            size, kernel_size=kernel_size, sigma=sigma, multiplier=multiplier, step=step
        )

    def render(self, source: Texture2D) -> Texture2D:
        """Render"""
        blurred_x = self._blur_x.render(source)
        return self._blur_y.render(blurred_x)


class BloomEffect(PostProcessing):
    """Post processing to create a bloom/glow effect."""

    def __init__(
        self,
        size,
        kernel_size=5,
        sigma: float = 2,
        mu: float = 0,
        multiplier: float = 5,
        step: int = 1,
    ):
        super().__init__(size, kernel_size=kernel_size)

        self._gaussian_1 = GaussianBlur(
            (size[0], size[1]),
            kernel_size=kernel_size,
            sigma=sigma,
            multiplier=multiplier,
            step=step,
        )
        self._gaussian_2 = GaussianBlur(
            (size[0] // 4, size[1] // 4),
            kernel_size=kernel_size,
            sigma=sigma,
            multiplier=multiplier,
            step=step,
        )
        self._gaussian_3 = GaussianBlur(
            (size[0] // 8, size[1] // 8),
            kernel_size=kernel_size,
            sigma=sigma,
            multiplier=multiplier,
            step=step,
        )

        # Program and buffer doing contrast / brightness / luma
        luma_tex = self.ctx.texture((self.width // 2, self.height // 2), components=3)
        luma_tex.wrap_x = self.ctx.CLAMP_TO_EDGE
        luma_tex.wrap_y = self.ctx.CLAMP_TO_EDGE
        self._cb_luma_buffer = self.ctx.framebuffer(color_attachments=[luma_tex])
        # Buffer for the converted luma values
        self._cb_luma_program = self.ctx.load_program(
            vertex_shader=":system:shaders/postprocessing/glow_filter_vs.glsl",
            fragment_shader=":system:shaders/postprocessing/glow_filter_fs.glsl",
        )

        # Program for combining the original buffer and the blurred buffer
        self._combine_program = self.ctx.load_program(
            vertex_shader=":system:shaders/texture_default_projection_vs.glsl",
            fragment_shader=":system:shaders/postprocessing/gaussian_combine_fs.glsl",
        )
        self._quad_fs = geometry.quad_2d_fs()

    def render(self, source, target):
        """Render"""
        # TODO: support source as fbo or texture
        self._cb_luma_program["contrast"] = 4.0
        # self._cb_luma_program['brightness'] = 0.0
        self._cb_luma_buffer.use()
        self._cb_luma_buffer.clear()
        source.use(0)
        self._quad_fs.render(self._cb_luma_program)

        blurred = self._gaussian_1.render(self._cb_luma_buffer.color_attachments[0])
        blurred = self._gaussian_2.render(blurred)
        blurred = self._gaussian_3.render(blurred)

        # Draw combined result to screen
        target.use()
        source.use(0)
        blurred.use(1)
        self._combine_program["color_buffer"] = 0
        self._combine_program["blur_buffer"] = 1
        self._quad_fs.render(self._combine_program)
