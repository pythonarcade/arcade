"""
Transforming to multiple buffers.

This examples hows how we can configure a program
to transform into multiple buffers. This is done
by specifying the varyings capture mode. By default
transforms output all data interlaved to one buffer.

Each out value in the vertex shader will end up
in a separate buffer with separate capture mode.
"""
import struct
import arcade


class App(arcade.Window):

    def __init__(self):
        super().__init__(800, 600)
        self.num_invocations = 20

        # Simple transform program outputing the vertex id
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            out float out_a;
            out float out_b;

            void main() {
                out_a = float(gl_VertexID + 1);
                out_b = float((gl_VertexID + 1) * 2);
            }
            """,
            varyings_capture_mode="separate",
        )
        # Buffer for out_a data
        self.buffer_a = self.ctx.buffer(reserve=self.num_invocations * 4)
        # Buffer for out_b data
        self.buffer_b = self.ctx.buffer(reserve=self.num_invocations * 4)

        # Create an empty geomtry instance since we don't have
        # inputs in our vertex shader
        self.geometry = self.ctx.geometry()
        # Force the vertex shader to run 10 times (vertices=10)
        self.geometry.transform(
            self.program,
            [self.buffer_a, self.buffer_b],
            vertices=self.num_invocations,
            # buffer_offset=4,  # We can play with offsets if needed
            # first=4,  # Test skipping vertices
        )
        # Read the buffer data from vram and print it
        print(struct.unpack(f"{self.num_invocations}f", self.buffer_a.read()))
        print(struct.unpack(f"{self.num_invocations}f", self.buffer_b.read()))

    def on_update(self, delta_time: float):
        # Close the window instantly since we only care about the prints
        self.close()


App().run()
