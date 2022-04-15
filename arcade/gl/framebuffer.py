from ctypes import c_int
from contextlib import contextmanager
from typing import Optional, Tuple, List, TYPE_CHECKING
import weakref


from pyglet import gl

from .texture import Texture
from .types import pixel_formats

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.gl import Context


class Framebuffer:
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

    :param Context ctx: The context this framebuffer belongs to
    :param List[arcade.gl.Texture] color_attachments: List of color attachments.
    :param arcade.gl.Texture depth_attachment: A depth attachment (optional)
    """

    #: Is this the default framebuffer? (window buffer)
    is_default = False
    __slots__ = (
        "_ctx",
        "_glo",
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
        self, ctx: "Context", *, color_attachments=None, depth_attachment=None
    ):
        self._glo = fbo_id = gl.GLuint()  # The OpenGL alias/name
        self._ctx = ctx
        if not color_attachments:
            raise ValueError("Framebuffer must at least have one color attachment")

        self._color_attachments = (
            color_attachments
            if isinstance(color_attachments, list)
            else [color_attachments]
        )
        self._depth_attachment = depth_attachment
        self._samples = 0  # Leaving this at 0 for future sample support
        self._depth_mask = True  # Determines if the depth buffer should be affected
        self._prev_fbo = None

        # Create the framebuffer object
        gl.glGenFramebuffers(1, self._glo)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)

        # Ensure all attachments have the same size.
        # OpenGL do actually support different sizes,
        # but let's keep this simple with high compatibility.
        self._width, self._height = self._detect_size()
        self._viewport = 0, 0, self._width, self._height
        self._scissor: Optional[Tuple[int, int, int, int]] = None

        # Attach textures to it
        for i, tex in enumerate(self._color_attachments):
            # TODO: Possibly support attaching a specific mipmap level
            #       but we can read from specific mip levels from shaders.
            gl.glFramebufferTexture2D(
                gl.GL_FRAMEBUFFER,
                gl.GL_COLOR_ATTACHMENT0 + i,
                tex._target,
                tex.glo,
                0,  # Level 0
            )

        if self.depth_attachment:
            gl.glFramebufferTexture2D(
                gl.GL_FRAMEBUFFER,
                gl.GL_DEPTH_ATTACHMENT,
                self.depth_attachment._target,
                self.depth_attachment.glo,
                0,
            )

        # Ensure the framebuffer is sane!
        self._check_completeness()

        # Set up draw buffers. This is simply a prepared list of attachments enums
        # we use in the use() method to activate the different color attachment layers
        layers = [
            gl.GL_COLOR_ATTACHMENT0 + i for i, _ in enumerate(self._color_attachments)
        ]
        # pyglet wants this as a ctypes thingy, so let's prepare it
        self._draw_buffers = (gl.GLuint * len(layers))(*layers)

        # Restore the original bound framebuffer to avoid confusion
        self.ctx.active_framebuffer.use(force=True)

        if self._ctx.gc_mode == "auto" and not self.is_default:
            weakref.finalize(self, Framebuffer.delete_glo, ctx, fbo_id)

        self.ctx.stats.incr("framebuffer")

    def __del__(self):
        # Intercept garbage collection if we are using Context.gc()
        if self._ctx.gc_mode == "context_gc" and not self.is_default and self._glo.value > 0:
            self._ctx.objects.append(self)

    @property
    def glo(self) -> gl.GLuint:
        """
        The OpenGL id/name of the framebuffer

        :type: GLuint
        """
        return self._glo

    def _get_viewport(self) -> Tuple[int, int, int, int]:
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

    def _set_viewport(self, value: Tuple[int, int, int, int]):
        if not isinstance(value, tuple) or len(value) != 4:
            raise ValueError("viewport should be a 4-component tuple")

        self._viewport = value

        # If the framebuffer is bound we need to set the viewport.
        # Otherwise it will be set on use()
        if self._ctx.active_framebuffer == self:
            gl.glViewport(*self._viewport)
            if self._scissor is None:
                gl.glScissor(*self._viewport)
            else:
                gl.glScissor(*self._scissor)

    viewport = property(_get_viewport, _set_viewport)

    def _get_scissor(self) -> Optional[Tuple[int, int, int, int]]:
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

    def _set_scissor(self, value):
        self._scissor = value

        if self._scissor is not None:
            # If the framebuffer is bound we need to set the scissor box.
            # Otherwise it will be set on use()
            if self._ctx.active_framebuffer == self:
                gl.glScissor(*self._scissor)

    scissor = property(_get_scissor, _set_scissor)

    @property
    def ctx(self) -> "Context":
        """
        The context this object belongs to.

        :type: :py:class:`arcade.gl.Context`
        """
        return self._ctx

    @property
    def width(self) -> int:
        """
        The width of the framebuffer in pixels

        :type: int
        """
        return self._width

    @property
    def height(self) -> int:
        """
        The height of the framebuffer in pixels

        :type: int
        """
        return self._height

    @property
    def size(self) -> Tuple[int, int]:
        """
        Size as a ``(w, h)`` tuple

        :type: tuple (int, int)
        """
        return self._width, self._height

    @property
    def samples(self) -> int:
        """
        Number of samples (MSAA)

        :type: int
        """
        return self._samples

    @property
    def color_attachments(self) -> List[Texture]:
        """
        A list of color attachments

        :type: list of :py:class:`arcade.gl.Texture`
        """
        return self._color_attachments

    @property
    def depth_attachment(self) -> Texture:
        """
        Depth attachment

        :type: :py:class:`arcade.gl.Texture`
        """
        return self._depth_attachment

    @property
    def depth_mask(self) -> bool:
        """
        Get or set the depth mask (default: ``True``).
        It determines if depth values should be written
        to the depth texture when depth testing is enabled.

        The depth mask value is persistent all will automatically
        be applies every time the framebuffer is bound.

        :type: bool
        """
        return self._depth_mask

    @depth_mask.setter
    def depth_mask(self, value: bool):
        self._depth_mask = value
        # Set state if framebuffer is active
        if self._ctx.active_framebuffer == self:
            gl.glDepthMask(self._depth_mask)

    def __enter__(self):
        self._prev_fbo = self._ctx.active_framebuffer
        self.use()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._prev_fbo.use()

    @contextmanager
    def activate(self):
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

        :param bool force: Force the framebuffer binding even if the system
                           already believes it's already bound.
        """
        self._use(force=force)
        self._ctx.active_framebuffer = self

    def _use(self, *, force: bool = False):
        """Internal use that do not change the global active framebuffer"""
        if self.ctx.active_framebuffer == self and not force:
            return

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)

        # NOTE: gl.glDrawBuffer(GL_NONE) if no texture attachments (future)
        # NOTE: Default framebuffer currently has this set to None
        if self._draw_buffers:
            gl.glDrawBuffers(len(self._draw_buffers), self._draw_buffers)

        gl.glDepthMask(self._depth_mask)
        gl.glViewport(*self._viewport)
        if self._scissor is not None:
            gl.glScissor(*self._scissor)
        else:
            gl.glScissor(*self._viewport)

    def clear(
        self,
        color=(0.0, 0.0, 0.0, 0.0),
        *,
        depth: float = 1.0,
        normalized: bool = False,
        viewport: Tuple[int, int, int, int] = None,
    ):
        """
        Clears the framebuffer::

            # Clear framebuffer using the color red in normalized form
            fbo.clear(color=(1.0, 0.0, 0.0, 1.0), normalized=True)
            # Clear the framebuffer using arcade's colors (not normalized)
            fb.clear(color=arcade.color.WHITE)

        If the background color is an ``RGB`` value instead of ``RGBA```
        we assume alpha value 255.

        :param tuple color: A 3 or 4 component tuple containing the color
        :param float depth: Value to clear the depth buffer (unused)
        :param bool normalized: If the color values are normalized or not
        :param Tuple[int, int, int, int] viewport: The viewport range to clear
        """
        with self.activate():
            if viewport:
                gl.glScissor(*viewport)

            if normalized:
                # If the colors are already normalized we can pass them right in
                if len(color) == 3:
                    gl.glClearColor(*color, 1.0)
                else:
                    gl.glClearColor(*color)
            else:
                # OpenGL wants normalized colors (0.0 -> 1.0)
                if len(color) == 3:
                    gl.glClearColor(color[0] / 255, color[1] / 255, color[2] / 255, 1.0)
                else:
                    gl.glClearColor(
                        color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255
                    )

            if self.depth_attachment:
                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            else:
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            if viewport:
                if self._scissor is None:
                    gl.glScissor(*self._viewport)
                else:
                    gl.glScissor(*self._scissor)

    def read(
        self, *, viewport=None, components=3, attachment=0, dtype="f1"
    ) -> bytearray:
        """
        Read framebuffer pixels

        :param Tuple[int,int,int,int] viewport: The x, y, with, height to read
        :param int components:
        :param int attachment: The attachment id to read from
        :param str dtype: The data type to read
        :return: pixel data as a bytearray
        """
        # TODO: use texture attachment info to determine read format?
        try:
            frmt = pixel_formats[dtype]
            base_format = frmt[0][components]
            pixel_type = frmt[2]
            component_size = frmt[3]
        except Exception:
            raise ValueError(f"Invalid dtype '{dtype}'")

        with self:
            # Configure attachment to read from
            # gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0 + attachment)
            if viewport:
                x, y, width, height = viewport
            else:
                x, y, width, height = 0, 0, self._width, self._height
            data = (gl.GLubyte * (components * component_size * width * height))(0)
            gl.glReadPixels(x, y, width, height, base_format, pixel_type, data)

        return bytearray(data)

    def resize(self):
        """
        Detects size changes in attachments.
        This will reset the viewport to ``0, 0, width, height``.
        """
        self._width, self._height = self._detect_size()
        self.viewport = 0, 0, self.width, self._height

    def delete(self):
        """
        Destroy the underlying OpenGL resource.
        Don't use this unless you know exactly what you are doing.
        """
        Framebuffer.delete_glo(self._ctx, self._glo)
        self._glo.value = 0

    @staticmethod
    def delete_glo(ctx, framebuffer_id):
        """
        Destroys the framebuffer object

        :param ctx: OpenGL context
        :param framebuffer_id: Framebuffer to destroy (glo)
        """
        if gl.current_context is None:
            return

        gl.glDeleteFramebuffers(1, framebuffer_id)
        ctx.stats.decr("framebuffer")

    def _detect_size(self) -> Tuple[int, int]:
        """Detect the size of the framebuffer based on the attachments"""
        expected_size = (
            self._color_attachments[0]
            if self._color_attachments
            else self._depth_attachment
        ).size
        for layer in [*self._color_attachments, self._depth_attachment]:
            if layer and layer.size != expected_size:
                raise ValueError(
                    "All framebuffer attachments should have the same size"
                )
        return expected_size

    @staticmethod
    def _check_completeness() -> None:
        """
        Checks the completeness of the framebuffer.
        If the framebuffer is not complete, we cannot continue.
        """
        # See completeness rules : https://www.khronos.org/opengl/wiki/Framebuffer_Object
        states = {
            gl.GL_FRAMEBUFFER_UNSUPPORTED: "Framebuffer unsupported. Try another format.",
            gl.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT: "Framebuffer incomplete attachment.",
            gl.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: "Framebuffer missing attachment.",
            gl.GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT: "Framebuffer unsupported dimension.",
            gl.GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT: "Framebuffer incomplete formats.",
            gl.GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER: "Framebuffer incomplete draw buffer.",
            gl.GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER: "Framebuffer incomplete read buffer.",
            gl.GL_FRAMEBUFFER_COMPLETE: "Framebuffer is complete.",
        }

        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            raise ValueError(
                "Framebuffer is incomplete. {}".format(
                    states.get(status, "Unknown error")
                )
            )

    def __repr__(self):
        return "<Framebuffer glo={}>".format(self._glo.value)


class DefaultFrameBuffer(Framebuffer):
    """
    Represents the default framebuffer.
    This is the framebuffer of the window itself and need
    some special handling.

    We are not allowed to destroy this framebuffer since
    it's owned by pyglet. This framebuffer can also change
    size and pixel ratio at any point.

    We're doing some initial introspection to guess
    somewhat sane initial values. Since this is a
    dynamic framebuffer we cannot trust the internal
    values. We can only trust what the pyglet window
    itself reports related to window size and 
    framebuffer size. This should be updated in the
    ``on_resize`` callback.
    """

    #: Is this the default framebuffer? (window buffer)
    is_default = True
    __slots__ = ()

    def __init__(self, ctx: "Context"):
        """Detect the default framebuffer"""
        self._ctx = ctx
        # TODO: Can we query this?
        self._samples = 0
        # TODO: Maybe we should map renderbuffers?
        self._color_attachments = []
        self._depth_attachment = None
        self._depth_mask = True

        value = c_int()
        gl.glGetIntegerv(gl.GL_DRAW_FRAMEBUFFER_BINDING, value)
        self._glo = gl.GLuint(value.value)

        # Query draw buffers. This will most likely return GL_BACK
        # value = c_int()
        # gl.glGetIntegerv(gl.GL_DRAW_BUFFER0, value)
        # print(value.value)  # 1029 GL_BACK 0x405
        # self._draw_buffers = (gl.GLuint * 1)(value.value)
        # NOTE: Don't query for now
        self._draw_buffers = None

        # Query viewport values by inspecting the scissor box
        values = (c_int * 4)()
        gl.glGetIntegerv(gl.GL_SCISSOR_BOX, values)
        x, y, width, height = list(values)

        self._viewport = x, y, width, height
        self._scissor = None
        self._width = width
        self._height = height

        # HACK: Signal the default framebuffer having depth buffer
        self._depth_attachment = True

    def _get_viewport(self) -> Tuple[int, int, int, int]:
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

    def _set_viewport(self, value: Tuple[int, int, int, int]):
        if not isinstance(value, tuple) or len(value) != 4:
            raise ValueError("viewport should be a 4-component tuple")

        ratio = self.ctx.window.get_pixel_ratio()
        self._viewport = (
            int(value[0] * ratio),
            int(value[1] * ratio),
            int(value[2] * ratio),
            int(value[3] * ratio),
        )

        # If the framebuffer is bound we need to set the viewport.
        # Otherwise it will be set on use()
        if self._ctx.active_framebuffer == self:
            gl.glViewport(*self._viewport)
            if self._scissor is None:
                # FIXME: Probably should be set to the framebuffer size
                gl.glScissor(*self._viewport)
            else:
                gl.glScissor(*self._scissor)

    viewport = property(_get_viewport, _set_viewport)

    def _get_scissor(self) -> Optional[Tuple[int, int, int, int]]:
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
        if self._scissor is None:
            return None

        ratio = self.ctx.window.get_pixel_ratio()
        return (
            int(self._scissor[0] / ratio),
            int(self._scissor[1] / ratio),
            int(self._scissor[2] / ratio),
            int(self._scissor[3] / ratio),
        )

    def _set_scissor(self, value):
        if value is None:
            # FIXME: Do we need to reset something here?
            self._scissor = None
            if self._ctx.active_framebuffer == self:
                gl.glScissor(*self._viewport)
        else:
            ratio = self.ctx.window.get_pixel_ratio()
            self._scissor = (
                int(value[0] * ratio),
                int(value[1] * ratio),
                int(value[2] * ratio),
                int(value[3] * ratio),
            )

            # If the framebuffer is bound we need to set the scissor box.
            # Otherwise it will be set on use()
            if self._ctx.active_framebuffer == self:
                gl.glScissor(*self._scissor)

    scissor = property(_get_scissor, _set_scissor)
