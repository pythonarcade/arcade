from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

from arcade.types import RGBOrA255, RGBOrANormalized

from .texture import Texture2D

if TYPE_CHECKING:
    from arcade.gl import Context


class Framebuffer(ABC):
    """
    An offscreen render target also called a Framebuffer Object in OpenGL.
    This implementation is using texture attachments. When creating a
    Framebuffer we supply it with textures we want our scene rendered into.
    The advantage of using texture attachments is the ability we get
    to keep working on the contents of the framebuffer.

    The best way to create framebuffer is through :py:meth:`arcade.gl.Context.framebuffer`::

        # Create a 100 x 100 framebuffer with one attachment
        ctx.framebuffer(color_attachments=[ctx.texture((100, 100), components=4)])

        # Create a 100 x 100 framebuffer with two attachments
        # Shaders can be configured writing to the different layers
        ctx.framebuffer(
            color_attachments=[
                ctx.texture((100, 100), components=4),
                ctx.texture((100, 100), components=4),
            ]
        )

    Args:
        ctx:
            The context this framebuffer belongs to
        color_attachments:
            A color attachment or a list of color attachments
        depth_attachment:
            A depth attachment
    """

    #: Is this the default framebuffer? (window buffer)
    is_default = False
    __slots__ = (
        "_ctx",
        "_width",
        "_height",
        "_color_attachments",
        "_depth_attachment",
        "_samples",
        "_viewport",
        "_scissor",
        "_depth_mask",
        "_draw_buffers",
        "_prev_fbo",
        "__weakref__",
    )

    def __init__(
        self,
        ctx: "Context",
        *,
        color_attachments: Texture2D | list[Texture2D],
        depth_attachment: Texture2D | None = None,
    ):
        self._ctx = ctx
        if not color_attachments:
            raise ValueError("Framebuffer must at least have one color attachment")

        self._color_attachments = (
            color_attachments if isinstance(color_attachments, list) else [color_attachments]
        )
        self._depth_attachment: Texture2D | None = depth_attachment
        self._samples = 0  # Leaving this at 0 for future sample support
        self._depth_mask = True  # Determines if the depth buffer should be affected
        self._prev_fbo = None

        # Ensure all attachments have the same size.
        # OpenGL do actually support different sizes,
        # but let's keep this simple with high compatibility.
        self._width, self._height = self._detect_size()
        self._viewport = 0, 0, self._width, self._height
        self._scissor: tuple[int, int, int, int] | None = None

        self.ctx.stats.incr("framebuffer")

    @property
    def viewport(self) -> tuple[int, int, int, int]:
        """
        Get or set the framebuffer's viewport.

        The viewport parameter are ``(x, y, width, height)``.
        It determines what part of the framebuffer should be rendered to.
        By default the viewport is ``(0, 0, width, height)``.

        The viewport value is persistent all will automatically
        be applies every time the framebuffer is bound.

        Example::

            # 100, x 100 lower left with size 200 x 200px
            fb.viewport = 100, 100, 200, 200
        """
        return self._viewport

    @viewport.setter
    @abstractmethod
    def viewport(self, value: tuple[int, int, int, int]):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    def scissor(self) -> tuple[int, int, int, int] | None:
        """
        Get or set the scissor box for this framebuffer.

        By default the scissor box is disabled and has no effect
        and will have an initial value of ``None``. The scissor
        box is enabled when setting a value and disabled when
        set to ``None``

            # Set and enable scissor box only drawing
            # in a 100 x 100 pixel lower left area
            ctx.scissor = 0, 0, 100, 100
            # Disable scissoring
            ctx.scissor = None

        :type: tuple (x, y, width, height)

        """
        return self._scissor

    @scissor.setter
    @abstractmethod
    def scissor(self, value):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    def ctx(self) -> "Context":
        """The context this object belongs to."""
        return self._ctx

    @property
    def width(self) -> int:
        """The width of the framebuffer in pixels."""
        return self._width

    @property
    def height(self) -> int:
        """The height of the framebuffer in pixels."""
        return self._height

    @property
    def size(self) -> tuple[int, int]:
        """Size as a ``(w, h)`` tuple."""
        return self._width, self._height

    @property
    def samples(self) -> int:
        """Number of samples (MSAA)."""
        return self._samples

    @property
    def color_attachments(self) -> list[Texture2D]:
        """A list of color attachments."""
        return self._color_attachments

    @property
    def depth_attachment(self) -> Texture2D | None:
        """Depth attachment."""
        return self._depth_attachment

    @property
    def depth_mask(self) -> bool:
        """
        Get or set the depth mask (default: ``True``).

        It determines if depth values should be written
        to the depth texture when depth testing is enabled.

        The depth mask value is persistent all will automatically
        be applies every time the framebuffer is bound.
        """
        return self._depth_mask

    @depth_mask.setter
    @abstractmethod
    def depth_mask(self, value: bool):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    def __enter__(self):
        self._prev_fbo = self._ctx.active_framebuffer
        self.use()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._prev_fbo:
            self._prev_fbo.use()

    @contextmanager
    def activate(self) -> Generator[Framebuffer, None, None]:
        """Context manager for binding the framebuffer.

        Unlike the default context manager in this class
        this support nested framebuffer binding.
        """
        prev_fbo = self._ctx.active_framebuffer
        try:
            self.use()
            yield self
        finally:
            prev_fbo.use()

    def use(self, *, force: bool = False):
        """Bind the framebuffer making it the target of all rendering commands

        Args:
            force:
                Force the framebuffer binding even if the system
                already believes it's already bound.
        """
        self._use(force=force)
        self._ctx.active_framebuffer = self

    @abstractmethod
    def _use(self, *, force: bool = False):
        """Internal use that do not change the global active framebuffer"""
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def clear(
        self,
        *,
        color: RGBOrA255 | None = None,
        color_normalized: RGBOrANormalized | None = None,
        depth: float = 1.0,
        viewport: tuple[int, int, int, int] | None = None,
    ):
        """
        Clears the framebuffer::

            # Clear the framebuffer using Arcade's colors (not normalized)
            fb.clear(color=arcade.color.WHITE)

            # Clear framebuffer using the color red in normalized form
            fbo.clear(color_normalized=(1.0, 0.0, 0.0, 1.0))

        If the background color is an ``RGB`` value instead of ``RGBA```
        we assume alpha value 255.

        Args:
            color:
                A 3 or 4 component tuple containing the color
                (prioritized over color_normalized)
            color_normalized:
                A 3 or 4 component tuple containing the color in normalized form
            depth:
                Value to clear the depth buffer (unused)
            viewport:
                The viewport range to clear
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def read(self, *, viewport=None, components=3, attachment=0, dtype="f1") -> bytes:
        """
        Read the raw framebuffer pixels.

        Reading data from a framebuffer is much more powerful than
        reading date from textures. We can specify more or less
        what format we want the data. It's not uncommon to throw
        textures into framebuffers just to get access to this read
        api.

        Args:
            viewport:
                The x, y, with, height area to read.
            components:
                The number of components to read. 1, 2, 3 or 4.
                This will determine the format to read.
            attachment:
                The attachment id to read from
            dtype:
                The data type to read. Pixel data will be converted to this format.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    def resize(self):
        """
        Detects size changes in attachments.

        This will reset the viewport to ``0, 0, width, height``.
        """
        self._width, self._height = self._detect_size()
        self.viewport = 0, 0, self.width, self._height

    @abstractmethod
    def delete(self):
        """
        Destroy the underlying OpenGL resource.

        .. warning:: Don't use this unless you know exactly what you are doing.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    def _detect_size(self) -> tuple[int, int]:
        """Detect the size of the framebuffer based on the attachments"""
        attachments = []

        if self._color_attachments:
            attachments.extend(self._color_attachments)
        elif self._depth_attachment:
            attachments.append(self._depth_attachment)

        if not attachments:
            raise RuntimeError("Framebuffer has no attachments")

        expected_size = attachments[0].size
        for layer in attachments:
            if layer and layer.size != expected_size:
                raise ValueError("All framebuffer attachments should have the same size")
        return expected_size


class DefaultFrameBuffer(Framebuffer, ABC):
    """
    Represents the default framebuffer.

    This is the framebuffer of the window itself and need some special handling.

    We are not allowed to destroy this framebuffer since it's owned by pyglet.
    This framebuffer can also change size and pixel ratio at any point.

    We're doing some initial introspection to guess somewhat sane initial values.
    Since this is a dynamic framebuffer we cannot trust the internal values.
    We can only trust what the pyglet window itself reports related to window size
    and framebuffer size. This should be updated in the ``on_resize`` callback.
    """

    is_default = True
    """Is this the default framebuffer? (window buffer)"""

    def __init__(self, ctx: "Context"):
        self._ctx = ctx
        # TODO: Can we query this?
        self._samples = 0
        # TODO: Maybe we should map renderbuffers?
        self._color_attachments = []
        self._depth_attachment = None
        self._depth_mask = True

        # Query draw buffers. This will most likely return GL_BACK
        # value = c_int()
        # gl.glGetIntegerv(gl.GL_DRAW_BUFFER0, value)
        # print(value.value)  # 1029 GL_BACK 0x405
        # self._draw_buffers = (gl.GLuint * 1)(value.value)
        # NOTE: Don't query for now
        self._draw_buffers = None

        # HACK: Signal the default framebuffer having depth buffer
        self._depth_attachment = True  # type: ignore

    @property
    def size(self) -> tuple[int, int]:
        """Size as a ``(w, h)`` tuple."""
        return self._ctx.window.get_framebuffer_size()

    @property
    def width(self) -> int:
        """The width of the framebuffer in pixels."""
        return self.size[0]

    @property
    def height(self) -> int:
        """The height of the framebuffer in pixels."""
        return self.size[1]

    def _get_framebuffer_size(self) -> tuple[int, int]:
        """Get the framebuffer size of the window"""
        return self._ctx.window.get_framebuffer_size()

    @property
    def viewport(self) -> tuple[int, int, int, int]:
        """
        Get or set the framebuffer's viewport.
        The viewport parameter are ``(x, y, width, height)``.
        It determines what part of the framebuffer should be rendered to.
        By default the viewport is ``(0, 0, width, height)``.

        The viewport value is persistent all will automatically
        be applies every time the framebuffer is bound.

        Example::

            # 100, x 100 lower left with size 200 x 200px
            fb.viewport = 100, 100, 200, 200
        """
        ratio = self.ctx.window.get_pixel_ratio()
        return (
            int(self._viewport[0] / ratio),
            int(self._viewport[1] / ratio),
            int(self._viewport[2] / ratio),
            int(self._viewport[3] / ratio),
        )

    @viewport.setter
    @abstractmethod
    def viewport(self, value: tuple[int, int, int, int]):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    def scissor(self) -> tuple[int, int, int, int] | None:
        """
        Get or set the scissor box for this framebuffer.

        By default the scissor box is disabled and has no effect
        and will have an initial value of ``None``. The scissor
        box is enabled when setting a value and disabled when
        set to ``None``::

            # Set and enable scissor box only drawing
            # in a 100 x 100 pixel lower left area
            ctx.scissor = 0, 0, 100, 100
            # Disable scissoring
            ctx.scissor = None
        """
        if self._scissor is None:
            return None

        ratio = self.ctx.window.get_pixel_ratio()
        return (
            int(self._scissor[0] / ratio),
            int(self._scissor[1] / ratio),
            int(self._scissor[2] / ratio),
            int(self._scissor[3] / ratio),
        )

    @scissor.setter
    @abstractmethod
    def scissor(self, value):
        raise NotImplementedError("The enabled graphics backend does not support this method.")
