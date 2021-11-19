"""
Example showing a simple geometry shader.
We generate a bunch of random points and draw them using POINTS mode.
The geometry shader if configured to receive points and emit triangle strip.
We generate two triangles on the fly displaying a quad.
"""
import random
from array import array
import arcade
from arcade.gl import BufferDescription

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Geometry Shader"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        self.time = 0
        super().__init__(width, height, title, resizable=True)
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            """,
            geometry_shader="""
            #version 330

            layout (points) in;
            // Emit 4 vertices per point (Makes two triangles with a triangle strip)
            layout (triangle_strip, max_vertices = 4) out;

            uniform float time;
            out vec3 gs_color;

            void main() {
                // Get the position emitted from the vertex shader
                // We get the 0th element because point primitives only have 1 position.
                vec4 pos = gl_in[0].gl_Position;
                float offset = 0.02 + sin(time * 5.0 + gl_PrimitiveIDIn) / 200.0;

                float rot = time + length(pos) * 10.0;
                mat2 rotate = mat2(
                    cos(rot), -sin(rot),
                    sin(rot),  cos(rot)
                );
                vec3 color = vec3(
                    (sin(time + gl_PrimitiveIDIn) + 1.0) / 2.0,
                    (sin(time + 2 + gl_PrimitiveIDIn) + 1.0) / 2.0,
                    (sin(time + 3 + gl_PrimitiveIDIn) + 1.0) / 2.0
                );
                // Emit 4 vertices around the original vertex position making a quad
                gl_Position = pos + vec4(rotate * vec2(-offset, offset), 0.0, 0.0);
                gs_color = color;
                EmitVertex();

                gl_Position = pos + vec4(rotate * vec2(-offset, -offset), 0.0, 0.0);
                gs_color = color;
                EmitVertex();

                gl_Position = pos + vec4(rotate * vec2(offset, offset), 0.0, 0.0);
                gs_color = color;
                EmitVertex();

                gl_Position = pos + vec4(rotate * vec2(offset, -offset), 0.0, 0.0);
                gs_color = color;
                EmitVertex();

                // Done with the primitive
                EndPrimitive();
            }
            """,
            fragment_shader="""
            #version 330
            out vec4 out_color;
            in vec3 gs_color;
            void main() {
                out_color = vec4(gs_color, 1.0);
            }
            """,
        )
        num_points = 1000
        self.points = self.ctx.geometry([BufferDescription(
            self.ctx.buffer(data=array('f', [random.uniform(-1.0, 1.0) for _ in range(num_points * 2)])),
            '2f',
            ['in_vert'],
        )])

    def on_draw(self):
        self.clear()
        try:
            self.program['time'] = self.time
            self.points.render(self.program, mode=self.ctx.POINTS)
        except Exception:
            import traceback
            traceback.print_exc()
            exit(1)

    def on_update(self, dt):
        self.time += dt


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
