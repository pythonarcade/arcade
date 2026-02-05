"""
Render sprites that are backed by Numpy arrays of RGBA data

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.numpy_sprite
"""

from array import array
from typing import Optional

import arcade
import numpy as np

from arcade.gl import BufferDescription, enums

VERTEX_SHADER_SRC = """
#version 330

// Input from buffers
in vec2 in_position;
in vec2 in_size;

// Outputs to geometry shader
out vec2 position;
out vec2 size;

void main() {
    position = in_position;
    size = in_size;
}
"""

FRAGMENT_SHADER_SRC = """
#version 330

uniform sampler2D sprite_texture;

in vec2 uv;

out vec4 fragColor;

void main() {
    fragColor = texture(sprite_texture, uv);
}
"""

GEOMETRY_SHADER_SRC = """
#version 330

// Configure inputs and outputs for the geometry shader
// We are taking single points form the vertex shader per invocation
// and emitting 4 new vertices creating a quad/sprites
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;            

// A uniform buffer that will automagically contain arcade's projection matrix
uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

// Receive the outputs from the vertex shader.
// Since geometry shader can take multiple values from a vertex
// shader we need to define the inputs as arrays.
// We're only getting one vertex at the time in this example,
// but we make an unsized array leaving the rest up to the shader compiler.
in vec2 position[];
in vec2 size[];

// Texture coordinate to fragment shader
out vec2 uv;

void main() {
    // Create some more convenient variables for the input
    vec2 center = position[0];
    vec2 hsize = size[0] / 2.0;

    // Emit a triangle strip of 4 vertices making a triangle.
    // The fragment shader will then fill these triangles in the next stage.

    mat4 mvp = window.projection * window.view;

    // Upper left
    gl_Position = mvp * vec4(vec2(-hsize.x, hsize.y) + center, 0.0, 1.0);
    uv = vec2(0, 1);
    EmitVertex();

    // lower left
    gl_Position = mvp * vec4(vec2(-hsize.x, -hsize.y) + center, 0.0, 1.0);
    uv = vec2(0, 0);
    EmitVertex();

    // upper right
    gl_Position = mvp * vec4(vec2(hsize.x, hsize.y) + center, 0.0, 1.0);
    uv = vec2(1, 1);
    EmitVertex();

    // lower right
    gl_Position = mvp * vec4(vec2(hsize.x, -hsize.y) + center, 0.0, 1.0);
    uv = vec2(1, 0);
    EmitVertex();

    EndPrimitive();
}
"""
class NumpySprite:
    def __init__(
            self,
            ctx: arcade.ArcadeContext,
            center_x: float,
            center_y: float,
            texture_width: int,
            texture_height: int,
            width: int = 0,
            height: int = 0,
            data: Optional[np.ndarray] = None,
            filter: int = enums.NEAREST,
    ):
        self.ctx = ctx

        self._position = (center_x, center_y)
        self._texture_width = texture_width
        self._texture_height = texture_height

        if not width:
            width = self._texture_width

        if not height:
            height = self._texture_height

        self._width = width
        self._height = height

        self._position_changed = False
        self._size_changed = False

        self._program = self.ctx.program(
            vertex_shader=VERTEX_SHADER_SRC,
            fragment_shader=FRAGMENT_SHADER_SRC,
            geometry_shader=GEOMETRY_SHADER_SRC
        )
        self._program["sprite_texture"] = 0

        self._texture = self.ctx.texture(
            (self._texture_width, self._texture_height),
            filter=(filter, filter)
        )

        if data is None:
            data = np.zeros(
                (self._texture_width, self._texture_height, 4), dtype=np.uint8
            )

        self._texture.write(data)

        self._vertex_buffer = self.ctx.buffer(
            data=array(
                "f",
                (
                    self._position[0],
                    self._position[1],
                    self._width,
                    self._height
                )
            )
        )

        self._geometry = self.ctx.geometry(
            content=[
                BufferDescription(
                    self._vertex_buffer, "2f 2f", ["in_position", "in_size"]
                )
            ]
        )

    @property
    def position(self) -> tuple[float, float]:
        return self._position

    @position.setter
    def position(self, new_value: tuple[float, float]):
        if new_value[0] != self._position[0] or new_value[1] != self._position[1]:
            self._position = new_value
            self._position_changed = True

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_value: int):
        if new_value != self._width:
            self._width = new_value
            self._size_changed = True

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, new_value: int):
        if new_value != self._height:
            self._height = new_value
            self._size_changed = True

    def _write_buffers_to_gpu(self):
        if self._size_changed or self._position_changed:
            self._vertex_buffer.write(
                data=array(
                    "f",
                    (
                        self._position[0],
                        self._position[1],
                        self._width,
                        self._height,
                    ),
                )
            )
            self._size_changed = False
            self._position_changed = False

    def draw(self):
        self._write_buffers_to_gpu()
        self.ctx.enable(self.ctx.BLEND)

        self._texture.use(unit=0)
        self._geometry.render(self._program)

    def write(self, data: np.ndarray):
        self._texture.write(data)  # type: ignore


class NumpyWindow(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Numpy Sprite Example")
        arcade.set_background_color(arcade.color.BLACK)

        self.sprite_one_np = np.full((32, 32, 4), (255, 0, 0, 255), dtype=np.uint8)
        self.sprite_one = NumpySprite(
            self.ctx, 200, 300, 32, 32, 200, 200, self.sprite_one_np
        )

        self.sprite_two_np = np.full((32, 32, 4), (0, 0, 255, 255), dtype=np.uint8)
        self.sprite_two = NumpySprite(
            self.ctx, 500, 400, 32, 32, 200, 200, self.sprite_two_np
        )

        self._time = 0.0

    def on_draw(self):
        self.clear()
        self.sprite_one.draw()
        self.sprite_two.draw()

    def on_update(self, delta_time: float):
        self._time += delta_time

        g = int((np.sin(self._time * 2.0) * 0.5 + 0.5) * 255)

        self.sprite_one_np[:, :, 1] = g
        self.sprite_one.write(self.sprite_one_np)

        self.sprite_two_np[:, :, 1] = g
        self.sprite_two.write(self.sprite_two_np)


if __name__ == "__main__":
    NumpyWindow()
    arcade.run()