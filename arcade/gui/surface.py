from contextlib import contextmanager
from typing import Tuple, Union, Optional

import arcade
from arcade import Texture
from arcade.color import TRANSPARENT_BLACK
from arcade.gl import Framebuffer
from arcade.gl import geometry
from arcade.gui.nine_patch import NinePatchTexture
from arcade.types import Color, Point, Rect


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

        #: Blend modes for when we're drawing into the surface
        self.blend_func_render_into = (
            *self.ctx.BLEND_DEFAULT,
            *self.ctx.BLEND_ADDITIVE,
        )
        #: Blend mode for when we're drawing the surface
        self.blend_func_render = (
            *self.ctx.BLEND_DEFAULT,
            *self.ctx.BLEND_DEFAULT,
        )

        # Create 1 pixel rectangle we scale and move using pos and size
        self._geometry = self.ctx.geometry()
        self._program = self.ctx.program(
            vertex_shader="""
                #version 330

                void main() {
                    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
                }
                """,
            geometry_shader="""
                #version 330

                layout (points) in;
                layout (triangle_strip, max_vertices = 4) out;

                uniform WindowBlock {
                    mat4 projection;
                    mat4 view;
                } window;

                uniform vec2 pos;
                uniform vec2 size;
                uniform vec4 area;

                out vec2 uv;

                void main() {
                    mat4 mvp = window.projection * window.view;    
                
                    // Create the 4 corners of the rectangle
                    vec2 p_ll = pos;
                    vec2 p_lr = pos + vec2(size.x, 0);
                    vec2 p_ul = pos + vec2(0, size.y);
                    vec2 p_ur = pos + size;

                    gl_Position = mvp * vec4(p_ll, 0, 1);
                    uv = vec2(area.x, area.y);
                    EmitVertex();
                    gl_Position = mvp * vec4(p_lr, 0, 1);
                    uv = vec2(area.z, area.y);
                    EmitVertex();
                    gl_Position = mvp * vec4(p_ul, 0, 1);
                    uv = vec2(area.x, area.w);
                    EmitVertex();
                    gl_Position = mvp * vec4(p_ur, 0, 1);
                    uv = vec2(area.z, area.w);
                    EmitVertex();
                    EndPrimitive();
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
    def position(self) -> Point:
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
            int(self._size[1] * self._pixel_ratio),
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

    def clear(self, color: Color = TRANSPARENT_BLACK):
        """Clear the surface"""
        self.fbo.clear(color=color)

    def draw_texture(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        tex: Union[Texture, NinePatchTexture],
        angle=0,
        alpha: int = 255,
    ):
        if isinstance(tex, NinePatchTexture):
            if x != 0 or y != 0:
                raise ValueError("Ninepatch does not support a position != (0,0) yet")

            if x != 0 or y != 0:
                raise ValueError("Ninepatch does not support a angle != 0 yet")

            if x != 0 or y != 0:
                raise ValueError("Ninepatch does not support a alpha != 255 yet")

            tex.draw_sized(size=(width, height))
        else:
            arcade.draw_lrwh_rectangle_textured(
                bottom_left_x=x,
                bottom_left_y=y,
                width=width,
                height=height,
                texture=tex,
                angle=angle,
                alpha=alpha,
            )

    def draw_sprite(self, x, y, width, height, sprite):
        """Draw a sprite to the surface"""
        sprite.position = x + width // 2, y + height // 2
        sprite.width = width
        sprite.height = height
        sprite.draw()

    @contextmanager
    def activate(self):
        """
        Save and restore projection and activate Surface buffer to draw on.
        Also resets the limit of the surface (viewport).
        """
        # Set viewport and projection
        proj = self.ctx.projection_2d
        self.limit(0, 0, *self.size)
        # Set blend function
        blend_func = self.ctx.blend_func
        self.ctx.blend_func = self.blend_func_render_into

        with self.fbo.activate():
            yield self

        # Restore projection and blend function
        self.ctx.projection_2d = proj
        self.ctx.blend_func = blend_func

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

    def draw(
        self,
        area: Optional[Rect] = None,
    ) -> None:
        """
        Draws the contents of the surface.

        The surface will be rendered at the configured ``position``
        and limited by the given ``area``.

        :param Optional[Point] position: The position to draw the surface at.
        :param Optional[Rect] area: The pixel area in the surface to draw.
        """
        # Set blend function
        blend_func = self.ctx.blend_func
        self.ctx.blend_func = self.blend_func_render

        self.texture.use(0)
        self._program["pos"] = self._pos
        self._program["size"] = self._size
        self._program["area"] = area or (0, 0, *self._size)
        self._geometry.render(self._program, vertices=1)

        # Restore blend function
        self.ctx.blend_func = blend_func

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
