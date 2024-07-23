"""
N-Body Gravity with Compute Shaders & Buffers
"""
import random
from array import array
from pathlib import Path
from typing import Generator, Tuple

import arcade
from arcade.gl import BufferDescription

# Window dimensions in pixels
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Size of performance graphs in pixels
GRAPH_WIDTH = 200
GRAPH_HEIGHT = 120
GRAPH_MARGIN = 5

NUM_STARS: int = 4000
USE_COLORED_STARS: bool = True


def gen_initial_data(
        screen_size: Tuple[int, int],
        num_stars: int = NUM_STARS,
        use_color: bool = False
) -> array:
    """
    Generate an :py:class:`~array.array` of randomly positioned star data.

    Some of this data is wasted as padding because:

    1. GPUs expect SSBO data to be aligned to multiples of 4
    2. GLSL's vec3 is actually a vec4 with compiler-side restrictions,
       so we have to use 4-length vectors anyway.

    Args:
        screen_size: A (width, height) of the area to generate stars in
        num_stars: How many stars to generate
        use_color: Whether to generate white or randomized pastel stars
    Returns:
     An array of star position data
    """
    width, height = screen_size
    color_channel_min = 0.5 if use_color else 1.0

    def _data_generator() -> Generator[float, None, None]:
        """Inner generator function used to illustrate memory layout"""

        for i in range(num_stars):
            # Position/radius
            yield random.randrange(0, width)
            yield random.randrange(0, height)
            yield 0.0  # z (padding, unused by shaders)
            yield 6.0

            # Velocity (unused by visualization shaders)
            yield 0.0
            yield 0.0
            yield 0.0  # vz (padding, unused by shaders)
            yield 0.0  # vw (padding, unused by shaders)

            # Color
            yield random.uniform(color_channel_min, 1.0)  # r
            yield random.uniform(color_channel_min, 1.0)  # g
            yield random.uniform(color_channel_min, 1.0)  # b
            yield 1.0  # a

    # Use the generator function to fill an array in RAM
    return array('f', _data_generator())


class NBodyGravityWindow(arcade.Window):

    def __init__(self):
        # Ask for OpenGL context supporting version 4.3 or greater when
        # calling the parent initializer to make sure we have compute shader
        # support.
        super().__init__(
            WINDOW_WIDTH, WINDOW_HEIGHT,
            "N-Body Gravity with Compute Shaders & Buffers",
            gl_version=(4, 3),
            resizable=False
        )
        # Attempt to put the window in the center of the screen.
        self.center_window()

        # --- Create buffers

        # Create pairs of buffers for the compute & visualization shaders.
        # We will swap which buffer instance is the initial value and
        # which is used as the current value to write to.

        # ssbo = shader storage buffer object
        initial_data = gen_initial_data(self.get_size(), use_color=USE_COLORED_STARS)
        self.ssbo_previous = self.ctx.buffer(data=initial_data)
        self.ssbo_current = self.ctx.buffer(data=initial_data)

        # vao = vertex array object
        # Format string describing how to interpret the SSBO buffer data.
        # 4f = position and size -> x, y, z, radius
        # 4x4 = Four floats used for calculating velocity. Not needed for visualization.
        # 4f = color -> rgba
        buffer_format = "4f 4x4 4f"

        # Attribute variable names for the vertex shader
        attributes = ["in_vertex", "in_color"]

        self.vao_previous = self.ctx.geometry(
            [BufferDescription(self.ssbo_previous, buffer_format, attributes)],
            mode=self.ctx.POINTS,
        )
        self.vao_current = self.ctx.geometry(
            [BufferDescription(self.ssbo_current, buffer_format, attributes)],
            mode=self.ctx.POINTS,
        )

        # --- Create the visualization shaders

        vertex_shader_source = Path("shaders/vertex_shader.glsl").read_text()
        fragment_shader_source = Path("shaders/fragment_shader.glsl").read_text()
        geometry_shader_source = Path("shaders/geometry_shader.glsl").read_text()

        # Create the complete shader program which will draw the stars
        self.program = self.ctx.program(
            vertex_shader=vertex_shader_source,
            geometry_shader=geometry_shader_source,
            fragment_shader=fragment_shader_source,
        )

        # --- Create our compute shader

        # Load in the raw source code safely & auto-close the file
        compute_shader_source = Path("shaders/compute_shader.glsl").read_text()

        # Compute shaders use groups to parallelize execution.
        # You don't need to understand how this works yet, but the
        # values below should serve as reasonable defaults. Later, we'll
        # preprocess the shader source by replacing the templating token
        # with its corresponding value.
        self.group_x = 256
        self.group_y = 1

        self.compute_shader_defines = {
            "COMPUTE_SIZE_X": self.group_x,
            "COMPUTE_SIZE_Y": self.group_y
        }

        # Preprocess the source by replacing each define with its value as a string
        for templating_token, value in self.compute_shader_defines.items():
            compute_shader_source = compute_shader_source.replace(templating_token, str(value))

        self.compute_shader = self.ctx.compute_shader(source=compute_shader_source)

        # --- Create the FPS graph

        # Enable timings for the performance graph
        arcade.enable_timings()

        # Create a sprite list to put the performance graph into
        self.perf_graph_list = arcade.SpriteList()

        # Create the FPS performance graph
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="FPS")
        graph.position = GRAPH_WIDTH / 2, self.height - GRAPH_HEIGHT / 2
        self.perf_graph_list.append(graph)

    def on_draw(self):
        # Clear the screen
        self.clear()
        # Enable blending so our alpha channel works
        self.ctx.enable(self.ctx.BLEND)

        # Bind buffers
        self.ssbo_previous.bind_to_storage_buffer(binding=0)
        self.ssbo_current.bind_to_storage_buffer(binding=1)

        # If you wanted, you could set input variables for compute shader
        # as in the lines commented out below. You would have to add or
        # uncomment corresponding lines in compute_shader.glsl
        # self.compute_shader["screen_size"] = self.get_size()
        # self.compute_shader["frame_time"] = self.frame_time

        # Run compute shader to calculate new positions for this frame
        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

        # Draw the current star positions
        self.vao_current.render(self.program)

        # Swap the buffer pairs.
        # The buffers for the current state become the initial state,
        # and the data of this frame's initial state will be overwritten.
        self.ssbo_previous, self.ssbo_current = self.ssbo_current, self.ssbo_previous
        self.vao_previous, self.vao_current = self.vao_current, self.vao_previous

        # Draw the graphs
        self.perf_graph_list.draw()



if __name__ == "__main__":
    app = NBodyGravityWindow()
    arcade.run()
