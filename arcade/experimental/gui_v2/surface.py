from contextlib import contextmanager
from typing import Tuple

import arcade
from arcade import Texture
from arcade.gl import Framebuffer
from arcade.gl.geometry import quad_2d_fs


class Surface:
    """
    Holds a FBO and abstracts the drawing on it.
    """

    def __init__(self, *, pos: Tuple[int, int], size: Tuple[int, int]):
        self.ctx = arcade.get_window().ctx

        self.pos = pos
        self.size = size

        self.texture = self.ctx.texture(size, components=4)
        self.fbo: Framebuffer = self.ctx.framebuffer(color_attachments=[self.texture])
        self.fbo.clear()

        # fullscreen quad geometry
        self._quad = quad_2d_fs()
        self._program = self.ctx.program(
            vertex_shader="""
                    #version 330
                    in vec2 in_vert;
                    in vec2 in_uv;
                    out vec2 uv;
                    void main() {
                        gl_Position = vec4(in_vert, 0.0, 1.0);
                        uv = in_uv;                
                    }
                    """,
            fragment_shader="""
                    #version 330
                    uniform sampler2D ui_texture;
                    in vec2 uv;
                    out vec4 fragColor;
                    void main() {
                        fragColor = texture(ui_texture, uv);
                    }
                    """,
        )

    def clear(self, color: arcade.Color = (0, 0, 0, 0)):
        self.fbo.clear(color=color)

    def draw_texture(self, x: float, y: float, width: float, height: float, tex: Texture, angle=0, alpha: int = 255):
        arcade.draw_lrwh_rectangle_textured(bottom_left_x=x,
                                            bottom_left_y=y,
                                            width=width,
                                            height=height,
                                            texture=tex,
                                            angle=angle,
                                            alpha=alpha)

    def draw_sprite(self, x, y, width, height, sprite):
        sprite.set_position(x + width // 2, y + height // 2)
        sprite.width = width
        sprite.height = height
        sprite.draw()

    @contextmanager
    def activate(self):
        """
        Save and restore projection and viewport, activate Surface Buffer to draw on.
        """
        proj = self.ctx.projection_2d
        vx, vy, vw, vh = self.fbo.ctx.viewport

        with self.fbo.activate():
            yield self

        fbo = self.fbo
        scaling = arcade.get_scaling_factor(self.window) if fbo.is_default else 1.0
        fbo.ctx.viewport = (
            int(vx * scaling),
            int(vy * scaling),
            int(vw * scaling),
            int(vh * scaling),
        )
        self.ctx.projection_2d = proj

    def limit(self, x, y, width, height):
        """Reduces the draw area to the given rect"""
        self.fbo.viewport = x, y, width, height
        self.ctx.projection_2d = 0, width, 0, height

    def draw(self):
        """Draws the current buffer on screen"""
        self.texture.use(0)
        self._quad.render(self._program)

    # def draw_surface(self, x: float, y: float, width: float, height: float, tex: Texture, angle=0, alpha: int = 255):
    #     # TODO einarf implement draw this surface on another
    #     pass

    def resize(self, size: Tuple[int, int]):
        """Resize the internal texture by re-allocating a new one"""
        if self.size == size:
            return
        self.size = size
        self.texture = self.ctx.texture(size, components=4)
        self.fbo: Framebuffer = self.ctx.framebuffer(color_attachments=[self.texture])
