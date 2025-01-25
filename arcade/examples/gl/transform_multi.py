"""
Transforming to multiple buffers.

This examples hows how we can configure a program
to transform into multiple buffers. This is done
by specifying the varyings capture mode. By default
transforms output all data interleaved to one buffer.

Each out value in the vertex shader will end up
in a separate buffer with separate capture mode.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.transform_multi
"""

import struct
import arcade

def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(1280, 720, "Transform Multi - GPU")

    num_invocations = 20
    ctx = window.ctx


    # Simple transform program outputting the vertex id
    program = ctx.program(
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
    buffer_a = ctx.buffer(reserve=num_invocations * 4)
    # Buffer for out_b data
    buffer_b = ctx.buffer(reserve=num_invocations * 4)

    # Create an empty geometry instance since we don't have
    # inputs in our vertex shader
    geometry = ctx.geometry()
    # Force the vertex shader to run 10 times (vertices=10)
    geometry.transform(
        program,
        [buffer_a, buffer_b],
        vertices=num_invocations,
        # buffer_offset=4,  # We can play with offsets if needed
        # first=4,  # Test skipping vertices
    )
    # Read the buffer data from vram and print it
    print(struct.unpack(f"{num_invocations}f", buffer_a.read()))
    print(struct.unpack(f"{num_invocations}f", buffer_b.read()))


if __name__ == "__main__":
    main()
