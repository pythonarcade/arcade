"""
Colored tile system using textures
"""

import random
import struct

import arcade
from arcade.gl import geometry


class ColorChunk:
    """An RGBA color chunk."""

    def __init__(
        self,
        ctx: arcade.ArcadeContext,
        size: tuple[int, int],
        data: bytes | None = None,
        colors: bytes | None = None,
    ) -> None:
        self.ctx = ctx

        self.size = size
        self.width = size[0]
        self.height = size[1]
        self.tile_count = self.width * self.height

        # RGBA texture storing the color palette
        self._color_texture = ctx.texture((256, 1), components=4, dtype="f1")

        # ubyte texture storing the tile ids
        self._texture = ctx.texture(self.size, components=1, dtype="u1")
        self._texture.filter = ctx.NEAREST, ctx.NEAREST

        # Quad geometry for drawing the chunk to the screen
        self._quad = geometry.quad_2d(size=(1, 1), pos=(0.5, 0.5))
        # Framebuffer object just for getting the read/write pixel api
        self._fbo = ctx.framebuffer(color_attachments=[self._texture])
        # Shader program for rendering the chunk
        self._program = ctx.program(
            vertex_shader="""
            #version 330

            uniform WindowBlock {
                mat4 projection;
                mat4 view;
            } window;

            uniform vec2 size;
            uniform vec2 position;

            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;

            void main() {
                gl_Position = window.projection * window.view * vec4(
                  (in_vert * size) + position, 0.0, 1.0
                );
                uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D color_texture;
            uniform usampler2D chunk_texture;
            in vec2 uv;
            out vec4 fragColor;

            void main() {
                uint tile_id = texture(chunk_texture, uv).r;
                fragColor = texelFetch(color_texture, ivec2(tile_id, 0), 0);
                //fragColor = vec4(tile_id / 255.0, 0.0, 0.0, 1.0);
            }
            """,
        )
        self._program["color_texture"] = 0  # channel 0
        self._program["chunk_texture"] = 1  # channel 1
        if data:
            self.write(data)
        if colors:
            self.write_colors(colors)

    def read_tile(self, position: tuple[int, int]) -> tuple[int, int, int, int]:
        """Read a pixel."""
        data = self._fbo.read(components=1, dtype="u1", viewport=(position[0], position[1], 1, 1))
        return struct.unpack("B", data)

    def write_tile(self, position: tuple[int, int], tile_id: int):
        """Write a pixel"""
        self._texture.write(
            data=struct.pack("B", tile_id), viewport=(position[0], position[1], 1, 1)
        )

    def read(self) -> bytes:
        """Read the entire chunk"""
        return self._fbo.read(components=1, dtype="u1")

    def write(self, data: bytes):
        """Write the entire chunk"""
        self._texture.write(data=data)

    def write_colors(self, colors: bytes):
        """Write the color palette"""
        self._color_texture.write(data=colors)

    def draw(self, position: tuple[int, int], size: tuple[int, int]):
        """Render the chunk"""
        self._program["position"] = position
        self._program["size"] = size
        self._color_texture.use(unit=0)
        self._texture.use(unit=1)
        self._quad.render(self._program)


class TextureColorMap(arcade.Window):
    def __init__(self) -> None:
        super().__init__(title="Texture Color Map")
        # 256 colors * 4 components (RGBA)
        palette = [random.randint(0, 255) for _ in range(256 * 4)]
        # 160x90 tiles
        tiles = [random.randint(0, 255) for _ in range(160 * 90)]
        self.color_chunk = ColorChunk(
            self.ctx, size=(160, 90), colors=bytes(palette), data=bytes(tiles)
        )

    def on_draw(self):
        self.clear()
        self.color_chunk.draw(position=(0, 0), size=(self.width, self.height))

    def on_update(self, delta_time: float):
        """Randomly change some tiles"""
        for _ in range(10):
            x, y = (
                random.randint(0, self.color_chunk.width - 1),
                random.randint(0, self.color_chunk.height - 1),
            )
            tile_id = random.randint(0, 255)
            self.color_chunk.write_tile(position=(x, y), tile_id=tile_id)


if __name__ == "__main__":
    TextureColorMap().run()
