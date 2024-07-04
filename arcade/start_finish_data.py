from arcade.draw.rect import draw_texture_rect
from arcade.texture.texture import Texture
from arcade.types import LBWH, AnchorPoint
from arcade.window_commands import get_window


class StartFinishRenderData:
    """
    State data for offscreen rendering with :py:meth:`arcade.start_render` and
    :py:meth:`arcade.finish_render`. This is only meant for simply module level
    drawing like creating a static image we display on the screen.

    :param pixelated: Should the image be pixelated or smooth when scaled?
    :param blend: Should we draw with alpha blending enabled?
    """

    def __init__(self, pixelated: bool = False, blend: bool = True):
        from arcade.texture_atlas.atlas_default import DefaultTextureAtlas

        self.window = get_window()
        self.pixelated = pixelated
        self.blend = blend
        self.atlas = DefaultTextureAtlas(self.window.get_framebuffer_size(), border=0)
        self.texture = Texture.create_empty(
            "start_finish_render_texture", size=self.window.get_framebuffer_size()
        )
        self.atlas.add(self.texture)
        self._generator_func = None
        self.completed = False

    def begin(self):
        """Enable rendering into the buffer"""
        self.generator_func = self.atlas.render_into(self.texture)
        fbo = self.generator_func.__enter__()
        fbo.clear(color=self.window.background_color)

        if self.blend:
            self.window.ctx.enable(self.window.ctx.BLEND)

    def end(self):
        """Switch back to rendering into the window"""
        self.generator_func.__exit__(None, None, None)
        self.completed = True

    def draw(self):
        """Draw the buffer to the screen"""
        # Stretch the texture to the window size with black bars if needed
        w, h = self.window.get_size()
        min_factor = min(w / self.texture.width, h / self.texture.height)
        region = LBWH(0, 0, self.texture.width, self.texture.height).scale(
            min_factor, anchor=AnchorPoint.BOTTOM_LEFT
        )
        region = region.move(dx=(w - region.width) / 2, dy=(h - region.height) / 2)

        draw_texture_rect(
            self.texture, region, pixelated=self.pixelated, blend=False, atlas=self.atlas
        )
