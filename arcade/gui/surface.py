from contextlib import contextmanager
from typing import Generator

from PIL import Image
from typing_extensions import Self

import arcade
from arcade import Texture
from arcade.camera import CameraData, OrthographicProjectionData, OrthographicProjector
from arcade.color import TRANSPARENT_BLACK
from arcade.gl import Framebuffer
from arcade.gui.nine_patch import NinePatchTexture
from arcade.types import LBWH, RGBA255, Point, Rect


class Surface:
    """Internal abstraction for widget rendering.

    Holds a :class:`arcade.gl.Framebuffer` and provides helper methods
    and properties for drawing to it.

    Args:
        size: The size of the surface in window coordinates
        position: The position of the surface in window
        pixel_ratio: The pixel scale of the window
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
        self._pixelated = False

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
        """The pixel ratio of the surface"""
        return self._pixel_ratio

    @property
    def width(self) -> int:
        """Width of the surface"""
        return self._size[0]

    @property
    def height(self) -> int:
        """Height of the surface"""
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
        """Draw a texture to the surface.

        Args:
            x: The x coordinate of the texture.
            y: The y coordinate of the texture.
            width: The width of the texture.
            height: The height of the texture.
            tex: The texture to draw, also supports NinePatchTexture.
            angle: The angle of the texture.
            alpha: The alpha value of the texture.
        """
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
            arcade.draw_texture_rect(
                tex, LBWH(x, y, width, height), angle=angle, alpha=alpha, pixelated=self._pixelated
            )

    def draw_sprite(self, x: float, y: float, width: float, height: float, sprite: arcade.Sprite):
        """Draw a sprite to the surface

        Args:
            x: The x coordinate of the sprite.
            y: The y coordinate of the sprite.
            width: The width of the sprite.
            height: The height of the sprite.
            sprite: The sprite to draw.
        """
        sprite.position = x + width // 2, y + height // 2
        sprite.width = width
        sprite.height = height
        arcade.draw_sprite(sprite, pixelated=self._pixelated)

    @contextmanager
    def activate(self) -> Generator[Self, None, None]:
        """Context manager for rendering safely to this :py:class:`Surface`.

        It does the following:

        #. Apply this surface's viewport, projection, and blend settings
        #. Allow any rendering to take place
        #. Restore the old OpenGL context settings

        Use it in ``with`` blocks like other managers:

        .. code-block:: python

           with surface.activate():
               # draw stuff here

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

    def limit(self, rect: Rect | None = None):
        """Reduces the draw area to the given rect, or resets it to the full surface."""

        if rect is None:
            rect = LBWH(0, 0, *self.size)

        l, b, w, h = rect.lbwh
        w = max(w, 1)
        h = max(h, 1)

        # round to nearest pixel, to avoid off by 1-pixel errors in ui
        viewport_rect = LBWH(
            round(l * self._pixel_ratio),
            round(b * self._pixel_ratio),
            round(w * self._pixel_ratio),
            round(h * self._pixel_ratio),
        )
        self.fbo.viewport = viewport_rect.lbwh_int

        self._cam.projection.rect = LBWH(0, 0, w, h)
        self._cam.viewport = viewport_rect

        self._cam.use()

    def draw(
        self,
        area: Rect | None = None,
    ) -> None:
        """Draws the contents of the surface.

        The surface will be rendered at the configured ``position``
        and limited by the given ``area``. The area can be out of bounds.

        Args:
            area: Limit the area in the surface we're drawing
                (l, b, w, h)
        """
        # Set blend function
        blend_func = self.ctx.blend_func
        self.ctx.blend_func = self.blend_func_render

        # Handle the pixelated shortcut if filter is not set
        if self._pixelated:
            self.texture.filter = self.ctx.NEAREST, self.ctx.NEAREST
        else:
            self.texture.filter = self.ctx.LINEAR, self.ctx.LINEAR

        self.texture.use(0)
        self._program["pos"] = self._pos
        self._program["size"] = self._size
        self._program["area"] = (0, 0, *self._size) if not area else area.lbwh
        self._geometry.render(self._program, vertices=1)

        # Restore blend function
        self.ctx.blend_func = blend_func

    def resize(self, *, size: tuple[int, int], pixel_ratio: float) -> None:
        """Resize the internal texture by re-allocating a new one

        Args:
            size: The new size in pixels (xy)
            pixel_ratio: The pixel scale of the window
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

    def to_image(self) -> Image.Image:
        """Convert the surface to an PIL image"""
        return self.ctx.get_framebuffer_image(self.fbo)
