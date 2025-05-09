"""
Simple Pygame-Arcade interaction example

We render contents to a pygame surface and write that
to an OpenGL texture. Then we render that texture to
the screen using a simple texture shader. We use NEAREST
interpolation to keep the pixelated look.

This example was tested with Pygame Community Edition
but should work with any recent version of Pygame.

    pip install -I pygame-ce==2.1.3

"""

import math

import pygame  # type: ignore

import arcade
from arcade.gl import geometry


class SurfaceTexture:
    """
    Simple wrapper for a texture and a pygame surface
    making it simple to synchronize the data.
    """

    def __init__(self, ctx: arcade.ArcadeContext, size: tuple[int, int]):
        self._ctx = ctx
        self._size = size
        self._surface = pygame.Surface(size, flags=pygame.SRCALPHA)
        self._texture = self._ctx.texture(size, components=4)
        # Pygame surfaces are BGRA, so we need to swap the channels
        self._texture.swizzle = "BGRA"
        self._texture.filter = ctx.NEAREST, ctx.NEAREST
        self._geometry = geometry.quad_2d_fs()
        self._program = self._ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;

            void main() {
                uv = in_uv;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D surface;
            in vec2 uv;
            out vec4 fragColor;

            void main() {
                // Flip texture y coordinate to get the right orientation
                fragColor = texture(surface, vec2(uv.x, 1 - uv.y));
            }
            """,
        )

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    def draw(self) -> None:
        """Draw the OpenGL texture to the screen"""
        self._texture.use(0)
        self._geometry.render(self._program)

    def write_surface_to_texture(self):
        """Update the texture with the surface data"""
        # This is the fastest way to write a surface to a texture.
        # Using pygame.image 100 x slower due to data conversion
        # and memory allocation.
        # The downside is that the raw surface data is RGBA, so we
        # set a swizzle on the OpenGL texture
        self._texture.write(self._surface.get_view("1"))


class PygameInteraction(arcade.Window):
    def __init__(self):
        super().__init__(512, 512, "Pygame Interaction")
        self.surface_texture = SurfaceTexture(self.ctx, size=(160, 160))

    def on_draw(self):
        self.clear()
        # Draw the pygame surface
        screen = self.surface_texture.surface
        w, h = self.surface_texture.size
        screen.fill((255, 255, 255))
        N = 8
        for i in range(N):
            time_offset = 6.28 / N * i
            pygame.draw.circle(
                screen,
                ((i * 50) % 255, (i * 100) % 255, (i * 20) % 255),
                (
                    math.sin(self.time + time_offset) * 55 + w // 2,
                    math.cos(self.time + time_offset) * 55 + h // 2,
                ),
                math.sin(self.time) * 4 + 15,
            )

        # Write the surface to the texture and draw it
        self.surface_texture.write_surface_to_texture()
        self.surface_texture.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()


if __name__ == "__main__":
    PygameInteraction().run()
