from contextlib import contextmanager
from typing import Tuple

import arcade
from arcade import Texture
from arcade.gl import Framebuffer
from arcade.gl import geometry


class Surface:
    """
    Holds a FBO and abstracts the drawing on it.
    """

    def __init__(self, *, pos: Tuple[int, int], size: Tuple[int, int]):
        self.ctx = arcade.get_window().ctx

        self._pos = pos
        self._size = size

        self.texture = self.ctx.texture(self._size, components=4)
        self.fbo: Framebuffer = self.ctx.framebuffer(color_attachments=[self.texture])
        self.fbo.clear()

        # Create 1 pixel rectangle we scale and move using pos and size
        self._quad = geometry.screen_rectangle(0, 0, 1, 1)
        self._program = self.ctx.program(
            vertex_shader="""
                    #version 330

                    uniform Projection {
                        uniform mat4 matrix;
                    } proj;
                    uniform vec2 pos;
                    uniform vec2 size;

                    in vec2 in_vert;
                    in vec2 in_uv;

                    out vec2 uv;

                    void main() {
                        gl_Position = proj.matrix * vec4((in_vert * size) + pos, 0.0, 1.0);
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
        self._program["pos"] = self._pos
        self._program["size"] = self._size

    def clear(self, color: arcade.Color = (0, 0, 0, 0)):
        """Clear the surface"""
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
        """Draw a sprite to the surface"""
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

    def draw(self) -> None:
        """Draws the current buffer on screen"""
        self.texture.use(0)
        self._quad.render(self._program)

    def resize(self, size: Tuple[int, int]) -> None:
        """
        Resize the internal texture by re-allocating a new one

        :param Tuple[int,int] size: The new size in pixels (xy)
        """
        # Texture re-allocation is expensive so we should block unnecessary calls.
        if self._size == size:
            return
        self._size = size
        # Create new texture and fbo
        self.texture = self.ctx.texture(self._size, components=4)
        self.fbo: Framebuffer = self.ctx.framebuffer(color_attachments=[self.texture])
        # Set size uniforms
        self._program["pos"] = self._pos
        self._program["size"] = self._size
