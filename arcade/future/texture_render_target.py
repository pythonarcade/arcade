from arcade import get_window
from arcade.color import TRANSPARENT_BLACK
from arcade.gl import geometry
from arcade.gl.texture import Texture2D
from arcade.types import RGBA255


class RenderTargetTexture:
    """
    An alternative render target to the default window/screen.
    This can be used in creative ways.

    Args:
        width: Width of the render target in pixels
        height: Height of the render target in pixels
    """

    def __init__(self, width: int, height: int):
        self.window = get_window()
        if not self.window:
            raise RuntimeError("No window found")

        self.width = width
        self.height = height
        self._background_color: RGBA255 = TRANSPARENT_BLACK

        self.ctx = self.window.ctx

        self._fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((width, height), components=4)]
        )

        self._quad_fs = geometry.quad_2d_fs()

    @property
    def texture(self) -> Texture2D:
        """The internal OpenGL texture"""
        return self._fbo.color_attachments[0]

    def clear(self):
        """Clear the texture with the configured background color"""
        self._fbo.clear(color=self._background_color)

    def set_background_color(self, color: RGBA255):
        """Set the background color for the light layer"""
        self._background_color = color

    def resize(self, width: int, height: int):
        """Resize the the internal texture"""
        pixel_scale = self.window.get_pixel_ratio()
        self._size = width * pixel_scale, height * pixel_scale
        self._fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture((width, height), components=4)
        )
