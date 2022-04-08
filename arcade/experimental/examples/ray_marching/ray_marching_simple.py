"""
Simple ray marcher.
This can also be created with shadertoy

To make this simpler to follow we've based it on the
"Ray Marching for Dummies!" video from The Art of Code
YouTube channel : https://www.youtube.com/watch?v=PGtv-dBi2wE
"""
from pathlib import Path
import arcade
from arcade.gl import geometry

CURRENT_DIR = Path(__file__).parent.resolve()


class RayMarcherSimple(arcade.Window):

    def __init__(self):
        super().__init__(720, 720, "Simple Ray Marcher", resizable=True)
        self.program = self.ctx.load_program(
            vertex_shader=CURRENT_DIR / "ray_marching_simple_vs.glsl",
            fragment_shader=CURRENT_DIR / "ray_marching_simple_fs.glsl"
        )
        self.quad_fs = geometry.quad_2d_fs()
        self.set_aspect_ratio(*self.get_size())
        self.time = 0

    def on_draw(self):
        self.quad_fs.render(self.program)

    def on_update(self, delta_time: float):
        self.time += delta_time
        self.program["iTime"] = self.time

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.set_aspect_ratio(width, height)

    def set_aspect_ratio(self, width, height):
        self.program["aspect_ratio"] = width / height


RayMarcherSimple().run()
