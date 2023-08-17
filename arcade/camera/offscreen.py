from typing import TYPE_CHECKING, Optional, Union, List, Tuple
from contextlib import contextmanager

from arcade.window_commands import get_window
from arcade.camera.types import Projector
from arcade.gl import Framebuffer, Texture2D, Geometry
from arcade.gl.geometry import quad_2d_fs
if TYPE_CHECKING:
    from arcade.application import Window


class OffScreenSpace:
    _geometry: Optional[Geometry] = quad_2d_fs()

    # TODO: Doc String

    def __init__(self, *,
                 window: Optional["Window"] = None,
                 size: Optional[Tuple[int, int]] = None,
                 color_attachments: Optional[Union[Texture2D, List[Texture2D]]] = None,
                 depth_attachment: Optional[Texture2D] = None):
        self._win: "Window" = window or get_window()
        tex_size = size or self._win.size
        near = self._win.ctx.NEAREST
        self._fbo: Framebuffer = self._win.ctx.framebuffer(
            color_attachments=color_attachments or self._win.ctx.texture(tex_size, filter=(near, near)),
            depth_attachment=depth_attachment or None
        )

        if OffScreenSpace._geometry is None:
            OffScreenSpace._geometry = quad_2d_fs()

    def show(self):
        self._fbo.color_attachments[0].use(0)
        OffScreenSpace._geometry.render(self._win.ctx.utility_textured_quad_program)

    @contextmanager
    def activate(self, *, projector: Optional[Projector] = None, show: bool = False, clear: bool = False):
        previous = self._win.ctx.active_framebuffer
        prev_cam = self._win.current_camera if projector is not None else None
        try:
            self._fbo.use()
            if clear:
                self._fbo.clear()
            if projector is not None:
                projector.use()
            yield self._fbo
        finally:
            previous.use()
            if prev_cam is not None:
                prev_cam.use()
            if show:
                self.show()
