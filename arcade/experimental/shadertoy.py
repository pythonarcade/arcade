from typing import Tuple
from arcade import get_window
from arcade.gl import geometry


class ShaderToy:
    """A ShaderToy interface for arcade.

    Simply implement the ``mainImage`` glsl method::

        void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
            fragColor = vec4(1.0);
        }
    """
    def __init__(self, source: str):
        self.window = get_window()
        if not self.window:
            raise RuntimeError("No window found")

        self.ctx = self.window.ctx
        self.source: str = source
        self.mouse_pos = 0, 0
        self.quad = geometry.quad_2d_fs()

        self.program = self.ctx.program(
            vertex_shader=(
                "#version 330\n"
                "\n"
                "in vec2 in_vert;\n"
                "in vec2 in_uv;\n"
                "out vec2 v_uv;\n"
                "\n"
                "void main() {\n"
                "    gl_Position = vec4(in_vert, 0.0, 1.0);\n"
                "    v_uv = in_uv;\n"
                "}\n"
            ),
            fragment_shader=(
                "#version 330\n"
                "\n"
                "uniform sampler2D background;\n"
                "uniform float iTime;\n"
                "uniform vec2 iMouse;\n"
                "uniform vec2 iResolution;\n"
                "\n"
                "in vec2 v_uv;\n"
                "out vec4 out_color;\n"
                "\n"
                f"{self.source}\n"
                "\n"
                "void main() {\n"
                "    vec4 color;\n"
                "    mainImage(color, gl_FragCoord.xy);\n"
                "    out_color = color;\n"
                "}\n"
            ),
        )

    def draw(self, time: float = 0, target=None):
        try:
            self.program['iTime'] = time
        except KeyError:
            pass
        try:
            self.program['iMouse'] = self.mouse_pos[0], -self.mouse_pos[1]
        except KeyError:
            pass
        try:
            if self.window is not None:
                self.program['iResolution'] = self.window.get_framebuffer_size()
        except KeyError:
            pass

        self.quad.render(self.program)
