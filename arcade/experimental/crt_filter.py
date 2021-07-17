from arcade.experimental import ShaderToy
from arcade.resources import resolve_resource_path
from arcade.math import Vec2


class CRTFilter(ShaderToy):
    """
    CRT Filter

    :param int width:
    :param int height:
    :param float resolution_down_scale:
    :param float hard_scan: -8.0 soft, -16.0 medium
    :param float hard_pix: Hardness of pixels in the scan line. -2.0 soft, -4.0 medium
    :param Vec2 display_warp: Display warp. 0 = None, 1.0/8.0 = extreme
    """
    def __init__(self,
                 width: int, height: int,
                 resolution_down_scale: float = 6.0,
                 hard_scan: float = -8.0,
                 hard_pix: float = -3.0,
                 display_warp: Vec2 = (1.0 / 32.0, 1.0 / 24.0),
                 mask_dark: float = 0.5,
                 mask_light: float = 1.5):
        shader_sourcecode = resolve_resource_path(":resources:shaders/crt_monitor_filter.glsl").read_text()
        super().__init__(shader_sourcecode)
        self.fbo = self.ctx.framebuffer(color_attachments=[self.ctx.texture((width, height), components=4)])
        self.program['resolutionDownScale'] = resolution_down_scale
        self.program['hardScan'] = hard_scan
        self.program['hardPix'] = hard_pix
        self.program['warp'] = display_warp
        self.program['maskDark'] = mask_dark
        self.program['maskLight'] = mask_light

    def use(self):
        self.fbo.use()

    def clear(self):
        self.fbo.clear()

    def draw(self, time: float = 0, target=None):
        self.fbo.color_attachments[0].use(0)
        super().draw(time, target)
