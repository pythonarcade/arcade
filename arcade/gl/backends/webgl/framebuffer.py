from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

import js  # type: ignore

from arcade.gl import enums
from arcade.gl.framebuffer import DefaultFrameBuffer, Framebuffer
from arcade.gl.types import pixel_formats
from arcade.types import RGBOrA255, RGBOrANormalized

from .texture import WebGLTexture2D

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGLFramebuffer as JSWebGLFramebuffer

    from arcade.gl.backends.webgl.context import WebGLContext


class WebGLFramebuffer(Framebuffer):
    __slots__ = "_glo"

    def __init__(
        self,
        ctx: WebGLContext,
        *,
        color_attachments: WebGLTexture2D | list[WebGLTexture2D],
        depth_attachment: WebGLTexture2D | None = None,
    ):
        super().__init__(
            ctx,
            color_attachments=color_attachments,
            depth_attachment=depth_attachment,  # type: ignore
        )
        self._ctx = ctx

        self._glo = self._ctx._gl.createFramebuffer()
        self._ctx._gl.bindFramebuffer(enums.FRAMEBUFFER, self._glo)

        for i, tex in enumerate(self._color_attachments):
            self._ctx._gl.framebufferTexture2D(
                enums.FRAMEBUFFER,
                enums.COLOR_ATTACHMENT0 + i,
                tex._target,  # type: ignore
                tex.glo,  # type: ignore
                0,
            )

        if self.depth_attachment:
            self._ctx._gl.framebufferTexture2D(
                enums.FRAMEBUFFER,
                enums.DEPTH_ATTACHMENT,
                self.depth_attachment._target,  # type: ignore
                self.depth_attachment.glo,  # type: ignore
                0,
            )

        self._check_completeness(ctx)

        self._draw_buffers = [
            enums.COLOR_ATTACHMENT0 + i for i, _ in enumerate(self._color_attachments)
        ]

        # Restore the original framebuffer to avoid confusion
        self._ctx.active_framebuffer.use(force=True)

        if self._ctx.gc_mode == "auto" and not self.is_default:
            weakref.finalize(self, WebGLFramebuffer.delete_glo, ctx, self._glo)

    def __del__(self):
        if self._ctx.gc_mode == "context_gc" and not self.is_default and self._glo is not None:
            self._ctx.objects.append(self)

    @property
    def glo(self) -> JSWebGLFramebuffer | None:
        return self._glo

    @Framebuffer.viewport.setter
    def viewport(self, value: tuple[int, int, int, int]):
        if not isinstance(value, tuple) or len(value) != 4:
            raise ValueError("viewport should be a 4-component tuple")

        self._viewport = value

        # If the framebuffer is active we need to set the viewport now
        # Otherwise it will be set when it is activated
        if self._ctx.active_framebuffer == self:
            self._ctx._gl.viewport(*self._viewport)
            if self._scissor is None:
                self._ctx._gl.scissor(*self._viewport)
            else:
                self._ctx._gl.scissor(*self._scissor)

    @Framebuffer.scissor.setter
    def scissor(self, value):
        self._scissor = value

        if self._scissor is None:
            if self._ctx.active_framebuffer == self:
                self._ctx._gl.scissor(*self._viewport)
        else:
            if self._ctx.active_framebuffer == self:
                self._ctx._gl.scissor(*self._scissor)

    @Framebuffer.depth_mask.setter
    def depth_mask(self, value: bool):
        self._depth_mask = value
        if self._ctx.active_framebuffer == self:
            self._ctx._gl.depthMask(self._depth_mask)

    def _use(self, *, force: bool = False):
        if self._ctx.active_framebuffer == self and not force:
            return

        self._ctx._gl.bindFramebuffer(enums.FRAMEBUFFER, self._glo)

        if self._draw_buffers:
            self._ctx._gl.drawBuffers(self._draw_buffers)

        self._ctx._gl.depthMask(self._depth_mask)
        self._ctx._gl.viewport(*self._viewport)
        if self._scissor is not None:
            self._ctx._gl.scissor(*self._scissor)
        else:
            self._ctx._gl.scissor(*self._viewport)

    def clear(
        self,
        *,
        color: RGBOrA255 | None = None,
        color_normalized: RGBOrANormalized | None = None,
        depth: float = 1.0,
        viewport: tuple[int, int, int, int] | None = None,
    ):
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

            self._ctx._gl.clearColor(*clear_color)

            if self.depth_attachment:
                self._ctx._gl.clearDepth(depth)
                self._ctx._gl.clear(enums.COLOR_BUFFER_BIT | enums.DEPTH_BUFFER_BIT)
            else:
                self._ctx._gl.clear(enums.COLOR_BUFFER_BIT)

            self.scissor = scissor_values

    def read(self, *, viewport=None, components=3, attachment=0, dtype="f1") -> bytes:
        try:
            frmt = pixel_formats[dtype]
            base_format = frmt[0][components]
            pixel_type = frmt[2]
            component_size = frmt[3]
        except Exception:
            raise ValueError(f"Invalid dtype '{dtype}'")

        with self.activate():
            if not self.is_default:
                self._ctx._gl.readBuffer(enums.COLOR_ATTACHMENT0 + attachment)

            self._ctx._gl.pixelStorei(enums.PACK_ALIGNMENT, 1)
            self._ctx._gl.pixelStorei(enums.UNPACK_ALIGNMENT, 1)

            if viewport:
                x, y, width, height = viewport
            else:
                x, y, width, height = 0, 0, *self.size

            array_size = components * component_size * width * height
            if pixel_type == enums.UNSIGNED_BYTE:
                js_array_buffer = js.Uint8Array(array_size)
            elif pixel_type == enums.UNSIGNED_SHORT:
                js_array_buffer = js.Uint16Array(array_size)
            elif pixel_type == enums.FLOAT:
                js_array_buffer = js.Float32Array(array_size)
            else:
                raise ValueError(f"Unsupported pixel type {pixel_type} in framebuffer.read")
            self._ctx._gl.readPixels(x, y, width, height, base_format, pixel_type, js_array_buffer)

            if not self.is_default:
                self._ctx._gl.readBuffer(enums.COLOR_ATTACHMENT0)

        # TODO: Is this right or does this need something more for conversion to bytes?
        return js_array_buffer

    def delete(self):
        WebGLFramebuffer.delete_glo(self._ctx, self._glo)
        self._glo = None

    @staticmethod
    def delete_glo(ctx: WebGLContext, glo: JSWebGLFramebuffer | None):
        if glo is not None:
            ctx._gl.deleteFramebuffer(glo)

        ctx.stats.decr("framebuffer")

    @staticmethod
    def _check_completeness(ctx: WebGLContext) -> None:
        # See completeness rules : https://www.khronos.org/opengl/wiki/Framebuffer_Object
        states = {
            enums.FRAMEBUFFER_UNSUPPORTED: "Framebuffer unsupported. Try another format.",
            enums.FRAMEBUFFER_INCOMPLETE_ATTACHMENT: "Framebuffer incomplete attachment.",
            enums.FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: "Framebuffer missing attachment.",
            enums.FRAMEBUFFER_INCOMPLETE_DIMENSIONS: "Framebuffer unsupported dimension.",
            enums.FRAMEBUFFER_INCOMPLETE_MULTISAMPLE: "Framebuffer unsupported multisample.",
            enums.FRAMEBUFFER_COMPLETE: "Framebuffer is complete.",
        }

        status = ctx._gl.checkFramebufferStatus(enums.FRAMEBUFFER)
        if status != enums.FRAMEBUFFER_COMPLETE:
            raise ValueError(
                "Framebuffer is incomplete. {}".format(states.get(status, "Unknown error"))
            )

    def __repr__(self):
        return "<Framebuffer glo={}>".format(self._glo)


class WebGLDefaultFrameBuffer(DefaultFrameBuffer, WebGLFramebuffer):  # type: ignore
    is_default = True

    def __init__(self, ctx: WebGLContext):
        super().__init__(ctx)
        self._ctx = ctx

        x, y, width, height = self._ctx._gl.getParameter(enums.SCISSOR_BOX)

        self._viewport = x, y, width, height
        self._scissor = None
        self._width = width
        self._height = height

        self._glo = None

    @DefaultFrameBuffer.viewport.setter
    def viewport(self, value: tuple[int, int, int, int]):
        # This is very similar to the OpenGL backend setter
        # WebGL backend doesn't need to handle pixel scaling for the
        # default framebuffer like desktop does, the browser does that
        # for us. However we need a separate implementation for the
        # function because of ABC
        if not isinstance(value, tuple) or len(value) != 4:
            raise ValueError("viewport shouldbe a 4-component tuple")

        self._viewport = value

        if self._ctx.active_framebuffer == self:
            self._ctx._gl.viewport(*self._viewport)
            if self._scissor is None:
                self._ctx._gl.scissor(*self._viewport)
            else:
                self._ctx._gl.scissor(*self._scissor)

    @DefaultFrameBuffer.scissor.setter
    def scissor(self, value):
        if value is None:
            self._scissor = None
            if self._ctx.active_framebuffer == self:
                self._ctx._gl.scissor(*self._viewport)
        else:
            self._scissor = value
            if self._ctx.active_framebuffer == self:
                self._ctx._gl.scissor(*self._scissor)
