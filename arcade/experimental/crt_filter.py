from pyglet.math import Vec2

from arcade.experimental import Shadertoy


class CRTFilter:
    """
    CRT Filter

    Args:
        width: Width of the screen
        height: Height of the screen
        resolution_down_scale:
        hard_scan: -8.0 soft, -16.0 medium
        hard_pix: Hardness of pixels in the scan line. -2.0 soft, -4.0 medium
        display_warp: Display warp. 0 = None, 1.0/8.0 = extreme
    """

    def __init__(
        self,
        width: int,
        height: int,
        resolution_down_scale: float = 6.0,
        hard_scan: float = -8.0,
        hard_pix: float = -3.0,
        display_warp: Vec2 = Vec2(1.0 / 32.0, 1.0 / 24.0),
        mask_dark: float = 0.5,
        mask_light: float = 1.5,
    ):
        self.shadertoy = Shadertoy.create_from_file(
            (width, height), ":resources:shaders/shadertoy/crt_monitor_filter.glsl"
        )
        self.fbo = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture((width, height), components=4)]
        )
        self.shadertoy.channel_0 = self.fbo.color_attachments[0]

        self.shadertoy.program["resolutionDownScale"] = resolution_down_scale
        self.shadertoy.program["hardScan"] = hard_scan
        self.shadertoy.program["hardPix"] = hard_pix
        self.shadertoy.program["warp"] = display_warp
        self.shadertoy.program["maskDark"] = mask_dark
        self.shadertoy.program["maskLight"] = mask_light

    def use(self):
        self.fbo.use()

    def clear(self):
        self.fbo.clear()

    def draw(self, time: float = 0, target=None):
        self.shadertoy.render()
