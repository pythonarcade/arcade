"""
See: https://www.shadertoy.com/view/lsBfRc
"""

from __future__ import annotations

from arcade.experimental import Shadertoy


class BloomFilter:
    """
    CRT Filter

    :param width:
    :param height:

    """

    def __init__(self, width: int, height: int, intensity: float):
        self.shadertoy = Shadertoy.create_from_file(
            (width, height), ":system:shaders/bloom/bloom_filter_image.glsl"
        )
        self.fbo = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture((width, height), components=4)]
        )

        self.shadertoy.buffer_a = self.shadertoy.create_buffer_from_file(
            ":system:shaders/bloom/bloom_filter_a.glsl"
        )
        self.shadertoy.buffer_a.program["intensity"] = intensity
        self.shadertoy.buffer_a.channel_0 = self.fbo.color_attachments[0]

        self.shadertoy.buffer_b = self.shadertoy.create_buffer_from_file(
            ":system:shaders/bloom/bloom_filter_b.glsl"
        )
        self.shadertoy.buffer_b.channel_0 = self.shadertoy.buffer_a.texture

        self.shadertoy.channel_0 = self.shadertoy.buffer_a.texture
        self.shadertoy.channel_1 = self.shadertoy.buffer_b.texture

    def use(self):
        self.fbo.use()

    def clear(self):
        self.fbo.clear()

    def draw(self, time: float = 0, target=None):
        self.shadertoy.render()
