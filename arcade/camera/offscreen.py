from typing import TYPE_CHECKING, Optional, Union, List, Tuple
from contextlib import contextmanager

from arcade.window_commands import get_window
from arcade.camera.types import Projector
from arcade.gl import Framebuffer, Texture2D, Geometry, Program
from arcade.gl.geometry import quad_2d_fs
if TYPE_CHECKING:
    from arcade.application import Window


class OffScreenSpace:
    vertex_shader: str = """
    #version 330
    
    in vec2 in_uv;
    in vec2 in_vert;
    
    out vec2 out_uv;
    
    void main(){
        out_uv = in_uv;
        gl_Position = vec4(in_vert, 0.0, 1.0);
    }
    """
    fragment_shader: str = """
    #version 330
    
    uniform sampler2D texture0;
    
    in vec2 out_uv;
    
    out vec4 out_colour;
    
    void main(){
        out_colour = texture(texture0, out_uv);
    }
    """
    geometry: Geometry = None
    program: Program = None

    def __init__(self, *,
                 window: "Window" = None,
                 size: Tuple[int, int] = None,
                 color_attachments: Optional[Union[Texture2D, List[Texture2D]]] = None,
                 depth_attachment: Optional[Texture2D] = None):
        self._win: "Window" = window or get_window()
        tex_size = size or self._win.size
        near = self._win.ctx.NEAREST
        self._fbo: Framebuffer = self._win.ctx.framebuffer(
            color_attachments=color_attachments or self._win.ctx.texture(tex_size, filter=(near, near)),
            depth_attachment=depth_attachment or None
        )

        if OffScreenSpace.geometry is None:
            OffScreenSpace.geometry = quad_2d_fs()
        if OffScreenSpace.program is None:
            OffScreenSpace.program = self._win.ctx.program(
                vertex_shader=OffScreenSpace.vertex_shader,
                fragment_shader=OffScreenSpace.fragment_shader
            )

    def show(self):
        self._fbo.color_attachments[0].use(0)
        OffScreenSpace.geometry.render(OffScreenSpace.program)

    @contextmanager
    def activate(self, *, projector: Projector = None, show: bool = False, clear: bool = False):
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
