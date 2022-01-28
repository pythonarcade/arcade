from contextlib import contextmanager
from typing import Tuple

import arcade
from arcade import Texture
from arcade.gl import Framebuffer
from arcade.gl import geometry


class Surface:
    """
    Holds a :class:`arcade.gl.Framebuffer` and abstracts the drawing on it.
    Used internally for rendering widgets.
    """

    def __init__(
            self,
            *,
            size: Tuple[int, int],
            position: Tuple[int, int] = (0, 0),
            pixel_ratio: float = 1.0,
    ):
        self.ctx = arcade.get_window().ctx
        self._size = size
        self._pos = position
        self._pixel_ratio = pixel_ratio

        self.texture = self.ctx.texture(self.size_scaled, components=4)
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

    @property
    def position(self) -> Tuple[int, int]:
        """Get or set the surface position"""
        return self._pos

    @position.setter
    def position(self, value):
        self._pos = value

    @property
    def size(self):
        """Size of the surface in window coordinates"""
        return self._size

    @property
    def size_scaled(self):
        """The physical size of the buffer"""
        return (
            int(self._size[0] * self._pixel_ratio),
            int(self._size[1] * self._pixel_ratio)
        )

    @property
    def pixel_ratio(self) -> float:
        return self._pixel_ratio

    @property
    def width(self) -> int:
        return self._size[0]

    @property
    def height(self) -> int:
        return self._size[1]

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
        Save and restore projection and activate Surface buffer to draw on.
        Also resets the limit of the surface (viewport).
        """
        proj = self.ctx.projection_2d
        self.limit(0, 0, *self.size)

        with self.fbo.activate():
            yield self

        self.ctx.projection_2d = proj

    def limit(self, x, y, width, height):
        """Reduces the draw area to the given rect"""
        self.fbo.viewport = (
            int(x * self._pixel_ratio),
            int(y * self._pixel_ratio),
            int(width * self._pixel_ratio),
            int(height * self._pixel_ratio),
        )

        width = max(width, 1)
        height = max(height, 1)
        self.ctx.projection_2d = 0, width, 0, height

    def draw(self) -> None:
        """Draws the current buffer on screen"""
        self.texture.use(0)
        self._program["pos"] = self._pos
        self._program["size"] = self._size
        self._quad.render(self._program)

    def resize(self, *, size: Tuple[int, int], pixel_ratio: float) -> None:
        """
        Resize the internal texture by re-allocating a new one

        :param Tuple[int,int] size: The new size in pixels (xy)
        :param float pixel_ratio: The pixel scale of the window
        """
        # Texture re-allocation is expensive so we should block unnecessary calls.
        if self._size == size and self._pixel_ratio == pixel_ratio:
            return
        self._size = size
        self._pixel_ratio = pixel_ratio
        # Create new texture and fbo
        self.texture = self.ctx.texture(self.size_scaled, components=4)
        self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])
        self.fbo.clear()
