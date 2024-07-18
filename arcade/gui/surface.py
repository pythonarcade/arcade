from __future__ import annotations

from contextlib import contextmanager
from typing import Optional

import arcade
from arcade import Texture
from arcade.camera import CameraData, OrthographicProjectionData, OrthographicProjector
from arcade.color import TRANSPARENT_BLACK
from arcade.gl import Framebuffer
from arcade.gui.nine_patch import NinePatchTexture
from arcade.types import LBWH, RGBA255, Point, Rect


class Surface:
    """
    Holds a :class:`arcade.gl.Framebuffer` and abstracts the drawing on it.
    Used internally for rendering widgets.
    """

    def __init__(
        self,
        *,
        size: tuple[int, int],
        position: tuple[int, int] = (0, 0),
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

        self._geometry = self.ctx.geometry()
        self._program = self.ctx.load_program(
            vertex_shader=":system:shaders/gui/surface_vs.glsl",
            geometry_shader=":system:shaders/gui/surface_gs.glsl",
            fragment_shader=":system:shaders/gui/surface_fs.glsl",
        )

        self._cam = OrthographicProjector(
            view=CameraData(),
            projection=OrthographicProjectionData(0.0, self.width, 0.0, self.height, -100, 100),
            viewport=LBWH(0, 0, self.width, self.height),
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

    def clear(self, color: RGBA255 = TRANSPARENT_BLACK):
        """Clear the surface"""
        self.fbo.clear(color=color)

    def draw_texture(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        tex: Texture | NinePatchTexture,
        angle: float = 0.0,
        alpha: int = 255,
    ):
        if isinstance(tex, NinePatchTexture):
            if angle != 0.0:
                raise NotImplementedError(
                    f"Ninepatch does not support an angle != 0 yet, but got {angle}"
                )

            if alpha != 255:
                raise NotImplementedError(
                    f"Ninepatch does not support an alpha != 255 yet, but got {alpha}"
                )

            tex.draw_rect(rect=LBWH(0, 0, width, height))
        else:
            arcade.draw_texture_rect(tex, LBWH(x, y, width, height), angle=angle, alpha=alpha)

    def draw_sprite(self, x: float, y: float, width: float, height: float, sprite: arcade.Sprite):
        """Draw a sprite to the surface"""
        sprite.position = x + width // 2, y + height // 2
        sprite.width = width
        sprite.height = height
        arcade.draw_sprite(sprite)

    @contextmanager
    def activate(self):
        """
        Save and restore projection and activate Surface buffer to draw on.
        Also resets the limit of the surface (viewport).
        """
        # Set viewport and projection
        self.limit(LBWH(0, 0, *self.size))
        # Set blend function
        prev_blend_func = self.ctx.blend_func

        try:
            self.ctx.blend_func = self.blend_func_render_into
            with self.fbo.activate():
                yield self
        finally:
            # Restore blend function.
            self.ctx.blend_func = prev_blend_func

    def limit(self, rect: Rect):  # TODO track limit usage
        """Reduces the draw area to the given rect"""

        l, b, w, h = rect.lbwh
        w = max(w, 1)
        h = max(h, 1)

        viewport_rect = LBWH(
            int(l * self._pixel_ratio),
            int(b * self._pixel_ratio),
            int(w * self._pixel_ratio),
            int(h * self._pixel_ratio),
        )
        self.fbo.viewport = viewport_rect.viewport

        self._cam.projection.rect = LBWH(0, 0, w, h)
        self._cam.viewport = viewport_rect

        self._cam.use()

    def draw(
        self,
        area: Optional[Rect] = None,
    ) -> None:
        """
        Draws the contents of the surface.

        The surface will be rendered at the configured ``position``
        and limited by the given ``area``. The area can be out of bounds.

        :param area: Limit the area in the surface we're drawing (l, b, w, h)
        """
        # Set blend function
        blend_func = self.ctx.blend_func
        self.ctx.blend_func = self.blend_func_render

        self.texture.use(0)
        self._program["pos"] = self._pos
        self._program["size"] = self._size
        self._program["area"] = (0, 0, *self._size) if not area else area.lbwh
        self._geometry.render(self._program, vertices=1)

        # Restore blend function
        self.ctx.blend_func = blend_func

    def resize(self, *, size: tuple[int, int], pixel_ratio: float) -> None:
        """
        Resize the internal texture by re-allocating a new one

        :param size: The new size in pixels (xy)
        :param pixel_ratio: The pixel scale of the window
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
