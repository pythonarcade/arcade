"""
When doing offscreen rendering we sometimes also want anti-aliasing with MSAA.

Framebuffers can have attachments for MSAA, but these are somewhat harder
to read from with a shader. Instead we simply copy the MSAA framebuffer to
the screen directly. This is allowed to easily read from the MSAA framebuffer.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.multisample_fbo
"""

import math
import arcade
from arcade.color import WHITE

SAMPLES = 8


class MultisampleFramebuffer(arcade.Window):

    def __init__(self, width, height):
        super().__init__(width, height, "Multisampled Framebuffer", samples=SAMPLES)
        # Create a MSAA texture and framebuffer
        self.texture = self.ctx.texture(self.get_framebuffer_size(), samples=SAMPLES)
        self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])

    def on_draw(self):
        self.clear()

        # Draw to MSAA framebuffer
        self.fbo.use()
        self.fbo.clear()
        arcade.draw_line(0, 0, self.width, self.height, WHITE)
        arcade.draw_line(0, self.height, self.width, 0, WHITE)
        arcade.draw_circle_outline(
            self.width / 2,
            self.height / 2,
            100 + math.sin(self.time) * 50,
            WHITE,
        )
        arcade.draw_circle_outline(
            self.width / 2,
            self.height / 2,
            200 + math.sin(self.time) * 50,
            WHITE,
        )

        # Activate screen and copy the MSAA framebuffer to it
        # NOTE: It might be safer with a shader
        self.ctx.screen.use()
        self.ctx.copy_framebuffer(self.fbo, self.ctx.screen)


MultisampleFramebuffer(800, 600).run()
