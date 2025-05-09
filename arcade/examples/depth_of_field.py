"""An experimental depth-of-field example.

It uses the depth attribute of along with blurring and shaders to
roughly approximate depth-based blur effects. The focus bounces
back forth automatically between a maximum and minimum depth value
based on time. Change the speed and focus via either the constants
at the top of the file or the arguments passed to it at the bottom of
the file.

This example works by doing the following for each frame:

1. Render a depth value for pixel into a buffer
2. Render a gaussian blurred version of the scene
3. For each pixel, use the current depth value to lerp between the
   blurred and un-blurred versions of the scene.

This is more expensive than rendering the scene directly, but it's
both easier and more performant than more accurate blur approaches.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.depth_of_field
"""

from contextlib import contextmanager
from math import cos, pi
from random import randint, uniform
from textwrap import dedent
from typing import cast

from pyglet.graphics import Batch

import arcade
from arcade import get_window, SpriteList, SpriteSolidColor, Text, Window, View
from arcade.camera.data_types import DEFAULT_NEAR_ORTHO, DEFAULT_FAR
from arcade.color import RED
from arcade.experimental.postprocessing import GaussianBlur
from arcade.gl import NEAREST, Program, Texture2D, geometry
from arcade.types import RGBA255, Color

WINDOW_TITLE = "Depth of Field Example"

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
BACKGROUND_GRAY = Color(155, 155, 155, 255)


class DepthOfField:
    """A depth-of-field effect we can use as a render context manager.

    Args:
        size:
            The size of the buffers.
        clear_color:
            The color which will be used as the background.
    """

    def __init__(
        self,
        size: tuple[int, int] | None = None,
        clear_color: RGBA255 = BACKGROUND_GRAY
    ):
        self._geo = geometry.quad_2d_fs()
        self._win: Window = get_window()

        size = cast(tuple[int, int], size or self._win.size)
        self._clear_color: Color = Color.from_iterable(clear_color)

        self.stale = True

        # Set up our depth buffer to hold per-pixel depth
        self._render_target = self._win.ctx.framebuffer(
            color_attachments=[
                self._win.ctx.texture(
                    size,
                    components=4,
                    filter=(NEAREST, NEAREST),
                    wrap_x=self._win.ctx.REPEAT,
                    wrap_y=self._win.ctx.REPEAT,
                ),
            ],
            depth_attachment=self._win.ctx.depth_texture(size),
        )

        # Set up everything we need to perform blur and store results.
        # This includes the blur effect, a framebuffer, and an instance
        # variable to store the returned texture holding blur results.
        self._blur_process = GaussianBlur(size, kernel_size=10, sigma=2.0, multiplier=2.0, step=4)
        self._blur_target = self._win.ctx.framebuffer(
            color_attachments=[
                self._win.ctx.texture(
                    size,
                    components=4,
                    filter=(NEAREST, NEAREST),
                    wrap_x=self._win.ctx.REPEAT,
                    wrap_y=self._win.ctx.REPEAT,
                )
            ]
        )
        self._blurred: Texture2D | None = None

        # To keep this example in one file, we use strings for our
        # our shaders. You may want to use pathlib.Path.read_text in
        # your own code instead.
        self._render_program = self._win.ctx.program(
            vertex_shader=dedent(
                """#version 330

                in vec2 in_vert;
                in vec2 in_uv;

                out vec2 out_uv;

                void main(){
                   gl_Position = vec4(in_vert, 0.0, 1.0);
                   out_uv = in_uv;
                }"""
            ),
            fragment_shader=dedent(
                """#version 330

                uniform sampler2D texture_0;
                uniform sampler2D texture_1;
                uniform sampler2D depth_0;

                uniform float focus_depth;

                in vec2 out_uv;

                out vec4 frag_colour;

                void main() {
                   float depth_val = texture(depth_0, out_uv).x;
                   float depth_adjusted = min(1.0, 2.0 * abs(depth_val - focus_depth));
                   vec4 crisp_tex = texture(texture_0, out_uv);
                   vec3 blur_tex = texture(texture_1, out_uv).rgb;
                   frag_colour = mix(crisp_tex, vec4(blur_tex, crisp_tex.a), depth_adjusted);
                   //if (depth_adjusted < 0.1){frag_colour = vec4(1.0, 0.0, 0.0, 1.0);}
                }"""
            ),
        )

        # Set the buffers the shader program will use
        self._render_program["texture_0"] = 0
        self._render_program["texture_1"] = 1
        self._render_program["depth_0"] = 2

    @property
    def render_program(self) -> Program:
        """The compiled shader for this effect."""
        return self._render_program

    @contextmanager
    def draw_into(self):
        self.stale = True
        previous_fbo = self._win.ctx.active_framebuffer
        try:
            self._win.ctx.enable(self._win.ctx.DEPTH_TEST)
            self._render_target.clear(color=self._clear_color)
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


class GameView(View):
    """Window subclass to hold sprites and rendering helpers.

    To keep the code simpler, this example uses a default camera. That means
    that any sprite outside Arcade's default camera near and far render cutoffs
    (``-100.0`` to ``100.0``) will not be drawn.

    Args:
        text_color:
            The color of the focus indicator.
        focus_range:
            The range the focus value will oscillate between.
        focus_change_speed:
            How fast the focus bounces back and forth
            between the ``-focus_range`` and ``focus_range``.
        min_sprite_depth:
            The minimum sprite depth we'll generate sprites between
         max_sprite_depth:
            The maximum sprite depth we'll generate sprites between.
    """

    def __init__(
        self,
        text_color: RGBA255 = RED,
        focus_range: float = 16.0,
        focus_change_speed: float = 0.1,
        min_sprite_depth: float = DEFAULT_NEAR_ORTHO,
        max_sprite_depth: float = DEFAULT_FAR
    ):
        super().__init__()
        self.sprites: SpriteList = SpriteList()
        self._batch = Batch()
        self.focus_range: float = focus_range
        self.focus_change_speed: float = focus_change_speed
        self.indicator_label = Text(
            f"Focus depth: {0:.3f} / {focus_range}",
            self.width / 2,
            self.height / 2,
            text_color,
            align="center",
            anchor_x="center",
            batch=self._batch,
        )

        # Randomize sprite depth, size, and angle, but set color from depth.
        for _ in range(100):
            depth = uniform(min_sprite_depth, max_sprite_depth)
            color = Color.from_gray(int(255 * (depth + 100) / 200))
            s = SpriteSolidColor(
                randint(100, 200),
                randint(100, 200),
                uniform(20, self.width - 20),
                uniform(20, self.height - 20),
                color,
                uniform(0, 360),
            )
            s.depth = depth
            self.sprites.append(s)

        self.dof = DepthOfField()

    def on_update(self, delta_time: float):
        time = self.window.time
        raw_focus = self.focus_range * (cos(pi * self.focus_change_speed * time) * 0.5 + 0.5)
        self.dof.render_program["focus_depth"] = raw_focus / self.focus_range
        self.indicator_label.value = f"Focus depth: {raw_focus:.3f} / {self.focus_range}"

    def on_draw(self):
        self.clear()

        # Render the depth-of-field layer's frame buffer
        with self.dof.draw_into():
            self.sprites.draw(pixelated=True)

        # Draw the blurred frame buffer and then the focus display
        window = self.window
        window.use()
        self.dof.render()
        self._batch.draw()


def main():
    # Create a Window to show the view defined above.
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the view
    app = GameView()

    # Show GameView on screen
    window.show_view(app)

    # Start the arcade game loop
    window.run()


if __name__ == "__main__":
    main()
