from ctypes import c_int
from typing import Tuple, List, Union, TYPE_CHECKING
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
        "_depth_mask",
        "_draw_buffers",
        "_prev_fbo",
        "__weakref__",
    )

    def __init__(
        self, ctx: "Context", *, color_attachments=None, depth_attachment=None
    ):
        """
        :param Context ctx: The context this framebuffer belongs to
        :param List[arcade.gl.Texture] color_attachments: List of color attachments.
        :param arcade.gl.Texture depth_attachment: A depth attachment (optional)
        """
        if not color_attachments:
            raise ValueError("Framebuffer must at least have one color attachment")

        self._ctx = ctx
        self._color_attachments = (
            color_attachments
            if isinstance(color_attachments, list)
            else [color_attachments]
        )
        self._depth_attachment = depth_attachment
        self._glo = fbo_id = gl.GLuint()  # The OpenGL alias/name
        self._samples = 0  # Leaving this at 0 for future sample support
        self._depth_mask = True  # Determines if the depth buffer should be affected
        self._prev_fbo = None

        # Create the framebuffer object
        gl.glGenFramebuffers(1, self._glo)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)

        # Ensure all attachments have the same size.
        # OpenGL do actually support different sizes,
        # but let's keep this simple with high compatibility.
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

        self._width, self._height = expected_size
        self._viewport = 0, 0, self._width, self._height

        # Attach textures to it
        for i, tex in enumerate(self._color_attachments):
            # TODO: Possibly support attaching a specific mipmap level
            #       but we can read from specific mip levels from shaders.
            gl.glFramebufferTexture2D(
                gl.GL_FRAMEBUFFER,
                gl.GL_COLOR_ATTACHMENT0 + i,
                gl.GL_TEXTURE_2D,
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
        self.ctx.active_framebuffer.use()

        self.ctx.stats.incr("framebuffer")
        weakref.finalize(self, Framebuffer.release, ctx, fbo_id)

    @property
    def glo(self) -> gl.GLuint:
        """
        The OpenGL id/name of the framebuffer

        :type: GLuint
        """
        return self._glo

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """
        Get or set the framebuffer's viewport.
        The viewport parameter are ``(x, y, width, height)``.
        It determines what part of the framebuffer should be redered to.
        By default the viewport is ``(0, 0, width, height)``.

        The viewport value is persistent all will automatically
        be applies every time the framebuffer is bound.

        Two or four integer values can be assigned::

            # Explicitly set x, y, width, height
            fb.viewport = 100, 100, 200, 200
            # Implies 0, 0, 100, 100
            fb.viewport = 100, 100
        """
        return self._viewport

    @viewport.setter
    def viewport(self, value: Tuple[int, int, int, int]):
        if not isinstance(value, tuple) or len(value) != 4:
            raise ValueError("viewport should be a 4-component tuple")

        self._viewport = value

        # If the framebuffer is bound we need to set the viewport.
        # Otherwise it will be set on use()
        if self._ctx.active_framebuffer == self:
            gl.glViewport(*self._viewport)
            gl.glScissor(*self._viewport)

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

    def use(self):
        """Bind the framebuffer making it the target of all redering commands"""
        self._use()
        self._ctx.active_framebuffer = self

    def _use(self):
        """Internal use that do not change the global active framebuffer"""
        if self.ctx.active_framebuffer == self:
            return

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)

        # NOTE: gl.glDrawBuffer(GL_NONE) if no texture attachments (future)
        # NOTE: Default framebuffer currently has this set to None
        if self._draw_buffers:
            gl.glDrawBuffers(len(self._draw_buffers), self._draw_buffers)

        gl.glDepthMask(self._depth_mask)
        gl.glViewport(*self._viewport)
        gl.glScissor(*self._viewport)

    def clear(
        self,
        color=(0.0, 0.0, 0.0, 0.0),
        *,
        depth: float = 1.0,
        normalized: bool = False,
    ):
        """
        Clears the framebuffer::

            # Clear framebuffer using the color red in normalized form
            fbo.clear(color=(1.0, 0.0, 0.0, 1.0), normalized=True)
            # Clear the framebuffer using arcade's colors (not normalized)
            fb.clear(color=arcade.color.WHITE)

        :param tuple color: A 3 or 4 component tuple containing the color
        :param float depth: Value to clear the depth buffer (unused)
        :param bool normalized: If the color values are normalized or not
        """
        with self:
            if normalized:
                # If the colors are already normalized we can pass them right in
                if len(color) == 3:
                    gl.glClearColor(*color, 0.0)
                else:
                    gl.glClearColor(*color)
            else:
                # OpenGL wants normalized colors (0.0 -> 1.0)
                if len(color) == 3:
                    gl.glClearColor(color[0] / 255, color[1] / 255, color[2] / 255, 0.0)
                else:
                    gl.glClearColor(
                        color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255
                    )

            if self.depth_attachment:
                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            else:
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def read(
        self, *, viewport=None, components=3, attachment=0, dtype="f1"
    ) -> bytearray:
        """Read framebuffer pixels"""
        # TODO: use texture attachment info to determine read format?
        try:
            frmt = pixel_formats[dtype]
            base_format = frmt[0][components]
            pixel_type = frmt[2]
        except Exception:
            raise ValueError(f"Invalid dtype '{dtype}'")

        with self:
            # Configure attachment to read from
            # gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0 + attachment)
            x, y, width, height = 0, 0, self._width, self._height
            data = (gl.GLubyte * (components * width * height))(0)
            gl.glReadPixels(x, y, width, height, base_format, pixel_type, data)

        return bytearray(data)

    @staticmethod
    def release(ctx, framebuffer_id):
        """
        Destroys the framebuffer object

        :param ctx: OpenGL context
        :param framebuffer_id: Framebuffer to destroy (glo)
        """
        if gl.current_context is None:
            return

        gl.glDeleteFramebuffers(1, framebuffer_id)
        ctx.stats.decr("framebuffer")

    @staticmethod
    def _check_completeness() -> None:
        """
        Checks the completeness of the framebuffer.
        If the framebuffer is not complete, we cannot continue.
        """
        # See completness rules : https://www.khronos.org/opengl/wiki/Framebuffer_Object
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
    """Represents the default framebuffer"""

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
        self._width = width
        self._height = height

        # HACK: Signal the default framebuffer having depth buffer
        self._depth_attachment = True
