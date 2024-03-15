from typing import Tuple, Optional
from contextlib import contextmanager
from math import cos, pi
from random import uniform, randint
from arcade import Window, SpriteSolidColor, SpriteList

from arcade.gl import geometry, NEAREST
from arcade.experimental.postprocessing import GaussianBlur
from arcade import get_window, draw_text


class DepthOfField:

    def __init__(self, size: Optional[Tuple[int, int]] = None):
        self._geo = geometry.quad_2d_fs()
        self._win = get_window()
        size = size or self._win.size

        self.stale = True

        self._render_target = self._win.ctx.framebuffer(
            color_attachments=[
                self._win.ctx.texture(
                    size,
                    components=4,
                    filter=(NEAREST, NEAREST),
                    wrap_x=self._win.ctx.REPEAT,
                    wrap_y=self._win.ctx.REPEAT
                ),
            ],
            depth_attachment=self._win.ctx.depth_texture(
                size
            )
        )

        self._blur_process = GaussianBlur(
            size,
            10,
            2.0,
            2.0,
            step=4
        )

        self._blurred = None

        self._blur_target = self._win.ctx.framebuffer(
            color_attachments=[
                self._win.ctx.texture(
                    size,
                    components=4,
                    filter=(NEAREST, NEAREST),
                    wrap_x=self._win.ctx.REPEAT,
                    wrap_y=self._win.ctx.REPEAT
                )
            ]
        )

        self._render_program = self._win.ctx.program(
            vertex_shader=(
                "#version 330\n"
                "\n"
                "in vec2 in_vert;\n"
                "in vec2 in_uv;\n"
                "\n"
                "out vec2 out_uv;\n"
                "\n"
                "void main(){\n"
                "   gl_Position = vec4(in_vert, 0.0, 1.0);\n"
                "   out_uv = in_uv;\n"
                "}\n"
            ),
            fragment_shader=(
                "#version 330\n"
                "\n"
                "uniform sampler2D texture_0;\n"
                "uniform sampler2D texture_1;\n"
                "uniform sampler2D depth_0;\n"
                "\n"
                "uniform float focus_depth;\n"
                "\n"
                "in vec2 out_uv;\n"
                "\n"
                "out vec4 frag_colour;\n"
                "\n"
                "void main() {\n"
                "   float depth_val = texture(depth_0, out_uv).x;\n"
                "   float depth_adjusted = min(1.0, 2.0 * abs(depth_val - focus_depth));\n"
                "   vec4 crisp_tex = texture(texture_0, out_uv);\n"
                "   vec3 blur_tex = texture(texture_1, out_uv).rgb;\n"
                "   frag_colour = mix(crisp_tex, vec4(blur_tex, crisp_tex.a), depth_adjusted);\n"
                "   //if (depth_adjusted < 0.1){frag_colour = vec4(1.0, 0.0, 0.0, 1.0);}\n"
                "}\n"
            )
        )
        self._render_program['texture_0'] = 0
        self._render_program['texture_1'] = 1
        self._render_program['depth_0'] = 2

    @contextmanager
    def draw_into(self):
        self.stale = True
        previous_fbo = self._win.ctx.active_framebuffer
        try:
            self._win.ctx.enable(self._win.ctx.DEPTH_TEST)
            self._render_target.clear((155.0, 155.0, 155.0, 255.0))
            self._render_target.use()
            yield self._render_target
        finally:
            self._win.ctx.disable(self._win.ctx.DEPTH_TEST)
            previous_fbo.use()

    def process(self):
        self._blurred = self._blur_process.render(self._render_target.color_attachments[0])
        self._win.use()

        self.stale = False

    def render(self):
        if self.stale:
            self.process()

        self._render_target.color_attachments[0].use(0)
        self._blurred.use(1)
        self._render_target.depth_attachment.use(2)
        self._geo.render(self._render_program)


class App(Window):

    def __init__(self):
        super().__init__()
        self.t = 0.0
        self.l: SpriteList = SpriteList()
        for _ in range(100):
            d = uniform(-100, 100)
            c = int(255 * (d + 100) / 200)
            s = SpriteSolidColor(
                randint(100, 200), randint(100, 200),
                uniform(20, self.width - 20), uniform(20, selfheight - 20),
                (c, c, c, 255),
                uniform(0, 360)
            )
            s.depth = d
            self.l.append(s)
        self.dof = DepthOfField()

    def on_update(self, delta_time: float):
        self.t += delta_time
        self.dof._render_program["focus_depth"] = round(16 * (cos(pi * 0.1 * self.t)*0.5 + 0.5)) / 16

    def on_draw(self):
        self.clear()
        with self.dof.draw_into():
            self.l.draw(pixelated=True)
        self.use()

        self.dof.render()
        draw_text(str(self.dof._render_program["focus_depth"]), self.width / 2, self.height / 2, (255, 0, 0, 255),
                  align="center")


if __name__ == '__main__':
    App().run()

