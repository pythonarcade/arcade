"""
Custom sprites with geometry shader

In some situations we could need some sprite-like geometry
that doesn't need the features of a sprite list. Initializing
structures for this kind of geometry is also less complex
and much faster than creation lots of sprite objects.

We are also free to design our own sprite layout with
any attribute we need. This data can be used to move
as much logic as possible into your shaders instead
of doing the logic in python.

In this example we're just using textured rectangles
to mimic sprites, but it could be circles or other
types of shapes with some imagination. We'll also be
limiting the number of attributes to make it simple.
Things like rotation, color, anchor etc can be added.

Hold and drag the mouse to scroll around.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.custom_sprite
"""

from random import randint
from array import array

import arcade
from arcade.gl.types import BufferDescription


class GeoSprites(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Custom Sprites", resizable=True)
        self.camera = arcade.camera.Camera2D()
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            // Input from our buffers
            in vec2 in_position;
            in vec2 in_size;

            // Outputs to our geometry shader
            out vec2 position;
            out vec2 size;

            void main() {
                // We just the information down unmodified
                position = in_position;
                size = in_size;
            }
            """,
            geometry_shader="""
            #version 330

            // Configure inputs and outputs for the geometry shader
            // We are taking single points form the vertex shader per invocation
            // and emitting 4 new vertices creating a quad/sprites
            layout (points) in;
            layout (triangle_strip, max_vertices = 4) out;

            // A uniform buffer that will automagically contain pyglet's projection matrix
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
                // The fragment shader will then fill these to triangles in the next stage.

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

                // We are done with this triangle strip now
                EndPrimitive();
            }
            """,
            fragment_shader="""
            #version 330

            // Fragment shader runs once for each pixel the triangles consists of.
            // The texture coordinate be an interpolated value based on
            // the location of the pixel in the triangle.

            // A sampler that can read from a texture channel
            uniform sampler2D sprite_texture;

            // Interpolated texture coordinates
            in vec2 uv;

            // The pixel that will be rendered to the screen
            out vec4 fragColor;

            void main() {
                // Look up a pixel in the texture and write to screen
                fragColor = texture(sprite_texture, uv);
            }
            """,
        )
        # Configure sampler to read from channel 0
        self.program["sprite_texture"] = 0
        # Load a image as an OpenGL texture
        self.texture = self.ctx.load_texture(":resources:images/tiles/boxCrate_double.png")

        self.num_sprites = 1000
        # Make an interleaved buffer with positions and sizes
        self.vertex_buffer = self.ctx.buffer(data=array("f", self.gen_sprites(self.num_sprites)))
        # Mage a geometry object describing the buffer contents for our shader
        self.geometry = self.ctx.geometry(
            content=[BufferDescription(self.vertex_buffer, "2f 2f", ["in_position", "in_size"])]
        )

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.camera.match_window(position=True)

    def on_draw(self):
        self.clear()
        self.camera.use()
        # Bind our sprite texture to channel 0
        self.texture.use(unit=0)
        # Render the sprite data with our shader
        self.geometry.render(self.program)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        """Make it easier to explore the geometry by scrolling"""
        self.camera.position = self.camera.position[0] - dx, self.camera.position[1] - dy

    def gen_sprites(self, count: int):
        """Quickly generate some random sprite data"""
        for _ in range(count):
            # Position
            yield randint(0, self.width * 4)
            yield randint(0, self.height * 4)
            # Size (make squares for now, not rectangles)
            size = randint(20, 100)
            yield size
            yield size


GeoSprites().run()
