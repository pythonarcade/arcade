from arcade.draw.rect import draw_texture_rect
from arcade.texture.texture import Texture
from arcade.types import LBWH, AnchorPoint
from arcade.window_commands import get_window


class StartFinishRenderData:
    """
    State data for offscreen rendering with :py:meth:`arcade.start_render` and
    :py:meth:`arcade.finish_render`. This is only meant for simple module level
    drawing like creating a static image we display repeatedly once the module
    has executed.

    Example::

        import arcade
        arcade.open_window(500, 500, "Picture")
        arcade.set_background_color(arcade.color.WHITE)
        # This renderer is permanently enabled here
        arcade.start_render()
        arcade.draw_text("Hello World", 190, 50, arcade.color.BLACK, 20)
        arcade.draw_circle_filled(250, 250, 100, arcade.color.RED)
        arcade.finish_render()
        # Repeatedly display the image produced between start and finish render
        arcade.run()

    This renderer is enabled by calling :py:meth:`arcade.start_render`. It's
    an irreversible action.

    Args:
        pixelated: Should the image be pixelated or smooth when scaled?
        blend: Should we draw with alpha blending enabled?
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
        """
        Enable rendering into the buffer.

        Should only be called once followed by a call to :py:meth:`end`.
        """
        self.generator_func = self.atlas.render_into(
            self.texture,
            projection=(0, self.window.width, 0, self.window.height),
        )
        fbo = self.generator_func.__enter__()
        fbo.clear(color=self.window.background_color)

        if self.blend:
            self.window.ctx.enable(self.window.ctx.BLEND)

    def end(self):
        """Switch back to rendering into the window"""
        self.generator_func.__exit__(None, None, None)
        self.completed = True

    def draw(self):
        """
        Draw the buffer to the screen attempting to preserve the aspect ratio.
        """
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
