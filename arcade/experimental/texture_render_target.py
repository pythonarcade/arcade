from arcade import get_window, get_scaling_factor, Color
from arcade.gl import geometry
from arcade.gl.texture import Texture


class RenderTargetTexture:
    """An alternative render target to the default window/screen.
    This can be used in creative ways.
    """

    def __init__(self, width: int, height: int):
        """Create a RenderTargetTexture.

        :param int width: Width of the render target in pixels
        :param int height: Height of the render target in pixels
        """
        self.window = get_window()
        if not self.window:
            raise RuntimeError("No window found")

        self.width = width
        self.height = height
        self._background_color: Color = (0, 0, 0)

        self.ctx = self.window.ctx

        self._fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((width, height), components=4)])

        self._quad_fs = geometry.quad_2d_fs()

    @property
    def texture(self) -> Texture:
        """The internal OpenGL texture"""
        return self._fbo.color_attachments[0]

    def clear(self):
        """Clear the texture with the configured background color"""
        self._fbo.clear(self._background_color)

    def set_background_color(self, color: Color):
        """Set the background color for the light layer"""
        self._background_color = color

    def resize(self, width: int, height: int):
        """Resize the the internal texture"""
        pixel_scale = get_scaling_factor(self.window)
        self._size = width * pixel_scale, height * pixel_scale
        self._fbo = self.ctx.framebuffer(color_attachments=self.ctx.texture((width, height), components=4))
