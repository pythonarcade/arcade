from __future__ import annotations

import weakref
from ctypes import Array, c_int, c_uint, string_at
from typing import TYPE_CHECKING

from pyglet import gl

from arcade.gl.framebuffer import DefaultFrameBuffer, Framebuffer
from arcade.gl.types import pixel_formats
from arcade.types import RGBOrA255, RGBOrANormalized

from .texture import OpenGLTexture2D

if TYPE_CHECKING:
    from arcade.gl import Context


class OpenGLFramebuffer(Framebuffer):
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

    __slots__ = "_glo"

    def __init__(
        self,
        ctx: "Context",
        *,
        color_attachments: OpenGLTexture2D | list[OpenGLTexture2D],
        depth_attachment: OpenGLTexture2D | None = None,
    ):
        super().__init__(
            ctx, color_attachments=color_attachments, depth_attachment=depth_attachment
        )
        self._glo = fbo_id = gl.GLuint()  # The OpenGL alias/name

        # Create the framebuffer object
        gl.glGenFramebuffers(1, self._glo)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)

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
        layers = [gl.GL_COLOR_ATTACHMENT0 + i for i, _ in enumerate(self._color_attachments)]
        # pyglet wants this as a ctypes thingy, so let's prepare it
        self._draw_buffers: Array[c_uint] | None = (gl.GLuint * len(layers))(*layers)

        # Restore the original bound framebuffer to avoid confusion
        self.ctx.active_framebuffer.use(force=True)

        if self._ctx.gc_mode == "auto" and not self.is_default:
            weakref.finalize(self, OpenGLFramebuffer.delete_glo, ctx, fbo_id)

    def __del__(self):
        # Intercept garbage collection if we are using Context.gc()
        if self._ctx.gc_mode == "context_gc" and not self.is_default and self._glo.value > 0:
            self._ctx.objects.append(self)

    @property
    def glo(self) -> gl.GLuint:
        """The OpenGL id/name of the framebuffer."""
        return self._glo

    @Framebuffer.viewport.setter
    def viewport(self, value: tuple[int, int, int, int]):
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

    @Framebuffer.scissor.setter
    def scissor(self, value):
        self._scissor = value

        if self._scissor is None:
            if self._ctx.active_framebuffer == self:
                gl.glScissor(*self._viewport)
        else:
            if self._ctx.active_framebuffer == self:
                gl.glScissor(*self._scissor)

    @Framebuffer.depth_mask.setter
    def depth_mask(self, value: bool):
        self._depth_mask = value
        # Set state if framebuffer is active
        if self._ctx.active_framebuffer == self:
            gl.glDepthMask(self._depth_mask)

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
        with self.activate():
            scissor_values = self._scissor

            if viewport:
                self.scissor = viewport
            else:
                self.scissor = None

            clear_color = 0.0, 0.0, 0.0, 0.0
            if color is not None:
                if len(color) == 3:
                    clear_color = color[0] / 255, color[1] / 255, color[2] / 255, 1.0
                elif len(color) == 4:
                    clear_color = color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255
                else:
                    raise ValueError("Color should be a 3 or 4 component tuple")
            elif color_normalized is not None:
                if len(color_normalized) == 3:
                    clear_color = color_normalized[0], color_normalized[1], color_normalized[2], 1.0
                elif len(color_normalized) == 4:
                    clear_color = color_normalized
                else:
                    raise ValueError("Color should be a 3 or 4 component tuple")

            gl.glClearColor(*clear_color)

            if self.depth_attachment:
                if self._ctx.gl_api == "opengl":
                    gl.glClearDepth(depth)
                else:  # gles only supports glClearDepthf
                    gl.glClearDepthf(depth)

                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            else:
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            self.scissor = scissor_values

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
        # TODO: use texture attachment info to determine read format?
        try:
            frmt = pixel_formats[dtype]
            base_format = frmt[0][components]
            pixel_type = frmt[2]
            component_size = frmt[3]
        except Exception:
            raise ValueError(f"Invalid dtype '{dtype}'")

        with self.activate():
            # Configure attachment to read from. Does not work on default framebuffer.
            if not self.is_default:
                gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0 + attachment)

            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

            if viewport:
                x, y, width, height = viewport
            else:
                x, y, width, height = 0, 0, *self.size

            data = (gl.GLubyte * (components * component_size * width * height))(0)
            gl.glReadPixels(x, y, width, height, base_format, pixel_type, data)

            if not self.is_default:
                gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0)  # Reset to default

        return string_at(data, len(data))

    def delete(self):
        """
        Destroy the underlying OpenGL resource.

        .. warning:: Don't use this unless you know exactly what you are doing.
        """
        OpenGLFramebuffer.delete_glo(self._ctx, self._glo)
        self._glo.value = 0

    @staticmethod
    def delete_glo(ctx, framebuffer_id):
        """
        Destroys the framebuffer object

        Args:
            ctx:
                The context this framebuffer belongs to
            framebuffer_id:
                Framebuffer id destroy (glo)
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
                "Framebuffer is incomplete. {}".format(states.get(status, "Unknown error"))
            )

    def __repr__(self):
        return "<Framebuffer glo={}>".format(self._glo.value)


class OpenGLDefaultFrameBuffer(DefaultFrameBuffer, OpenGLFramebuffer):
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
        super().__init__(ctx)

        value = c_int()
        gl.glGetIntegerv(gl.GL_DRAW_FRAMEBUFFER_BINDING, value)
        self._glo = gl.GLuint(value.value)

        # Query viewport values by inspecting the scissor box
        values = (c_int * 4)()
        gl.glGetIntegerv(gl.GL_SCISSOR_BOX, values)
        x, y, width, height = list(values)

        self._viewport = x, y, width, height
        self._scissor = None
        self._width = width
        self._height = height

    @DefaultFrameBuffer.viewport.setter
    def viewport(self, value: tuple[int, int, int, int]):
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

    @DefaultFrameBuffer.scissor.setter
    def scissor(self, value):
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
