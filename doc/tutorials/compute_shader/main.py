"""
Compute shader with buffers
"""
import random
from array import array
from typing import Generator

import arcade
from arcade.gl import BufferDescription

# Window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Size of performance graphs
GRAPH_WIDTH = 200
GRAPH_HEIGHT = 120
GRAPH_MARGIN = 5

NUM_STARS = 4000


class MyWindow(arcade.Window):

    def __init__(self):
        # Call parent constructor
        # Ask for OpenGL 4.3 context, as we need that for compute shader support.
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT,
                         "Star Gravity with a Compute Shader",
                         gl_version=(4, 3),
                         resizable=False)
        self.center_window()

        # --- Class instance variables

        # Number of stars to move
        self.num_stars = NUM_STARS

        # This has something to do with how we break the calculations up
        # and parallelize them.
        self.group_x = 256
        self.group_y = 1

        # --- Create buffers

        # Format of the buffer data.
        # 4f = position and size -> x, y, z, radius
        # 4x4 = Four floats used for calculating velocity. Not needed for visualization.
        # 4f = color -> rgba
        buffer_format = "4f 4x4 4f"

        # Attribute variable names for the vertex shader
        attributes = ["in_vertex", "in_color"]

        # Create pairs of data buffers for the compute & vertex shaders.
        # We will swap which buffer instance is the initial value and
        # which is used as the current value to write to.

        # ssbo = shader storage buffer object
        self.ssbo_initial = self.ctx.buffer(data=self.gen_initial_data())
        self.ssbo_current = self.ctx.buffer(reserve=self.ssbo_initial.size)

        # vao = vertex array object
        self.vao_initial = self.ctx.geometry(
            [BufferDescription(self.ssbo_initial, buffer_format, attributes)],
            mode=self.ctx.POINTS,
        )
        self.vao_current = self.ctx.geometry(
            [BufferDescription(self.ssbo_current, buffer_format, attributes)],
            mode=self.ctx.POINTS,
        )

        # --- Create shaders

        # Load in the shader source code safely & auto-close files
        with open("shaders/compute_shader.glsl") as file:
            compute_shader_source = file.read()
        with open("shaders/vertex_shader.glsl") as file:
            vertex_shader_source = file.read()
        with open("shaders/fragment_shader.glsl") as file:
            fragment_shader_source = file.read()
        with open("shaders/geometry_shader.glsl") as file:
            geometry_shader_source = file.read()

        # Create our compute shader.
        # Search/replace to set up our compute groups
        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_X",
                                                              str(self.group_x))
        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_Y",
                                                              str(self.group_y))
        self.compute_shader = self.ctx.compute_shader(source=compute_shader_source)

        # Program for visualizing the stars
        self.program = self.ctx.program(
            vertex_shader=vertex_shader_source,
            geometry_shader=geometry_shader_source,
            fragment_shader=fragment_shader_source,
        )

        # --- Create FPS graph

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
        self.ssbo_initial.bind_to_storage_buffer(binding=0)
        self.ssbo_current.bind_to_storage_buffer(binding=1)

        # Set input variables for compute shader
        # These are examples, although this example doesn't use them
        # self.compute_shader["screen_size"] = self.get_size()
        # self.compute_shader["force"] = force
        # self.compute_shader["frame_time"] = self.run_time

        # Run compute shader to calculate new positions for this frame
        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

        # Draw the current star positions
        self.vao_current.render(self.program)

        # Swap the buffer pairs.
        # The buffers for the current state become the initial state,
        # and the data of this frame's initial state will be overwritten.
        self.ssbo_initial, self.ssbo_current = self.ssbo_current, self.ssbo_initial
        self.vao_initial, self.vao_current = self.vao_current, self.vao_initial

        # Draw the graphs
        self.perf_graph_list.draw()

    def gen_initial_data(self) -> array:

        def _data_generator() -> Generator[float, None, None]:
            """
            A generator function yielding floats.

            Although generators are usually a way to avoid storing all
            data in memory at once, this example uses one as a way to
            legibly describe the layout of data in the buffer.
            """
            for i in range(self.num_stars):
                # Position/radius
                yield random.randrange(0, self.width)
                yield random.randrange(0, self.height)
                yield 0.0  # z (padding, unused by shaders)
                yield 6.0

                # Velocity
                yield 0.0
                yield 0.0
                yield 0.0  # vz (padding, unused by shaders)
                yield 0.0  # vw (padding, unused by shaders)

                # Color
                yield 1.0  # r
                yield 1.0  # g
                yield 1.0  # b
                yield 1.0  # a

        return array('f', _data_generator())

app = MyWindow()
arcade.run()
