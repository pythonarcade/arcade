"""
Compute shader with buffers
"""
import random
import math
from array import array

import arcade
from arcade.gl import BufferDescription


class App(arcade.Window):

    def __init__(self):
        # Call parent constructor
        super().__init__(720, 720, "Compute Shader", gl_version=(4, 3), resizable=True, vsync=True)

        # --- Class instance variables
        # How long we have been running, in seconds
        self.run_time = 0
        # Number of balls to move
        self.num_balls = 650

        # This has something to do with how we break the calculations up
        # and parallelize them.
        self.group_x = 256
        self.group_y = 1

        # --- Create buffers

        # Buffers with data for the compute shader (We ping-pong render between these)
        # ssbo = shader storage buffer object
        initial_data = self.gen_initial_data()
        self.ssbo_1 = self.ctx.buffer(data=array('f', initial_data))
        self.ssbo_2 = self.ctx.buffer(reserve=self.ssbo_1.size)

        # Geometry for buffers
        buffer_format = "4f 4x4 4f"
        # Attribute variable names
        attributes = ["in_vert", "in_col"]
        self.vao_1 = self.ctx.geometry(
            [BufferDescription(self.ssbo_1, buffer_format, attributes)],
            mode=self.ctx.POINTS,
        )
        self.vao_2 = self.ctx.geometry(
            [BufferDescription(self.ssbo_2, buffer_format, attributes)],
            mode=self.ctx.POINTS,
        )

        # --- Create shaders

        # Load in the shader source code
        file = open("compute_1/compute_shader.glsl")
        compute_shader_source = file.read()
        file = open("compute_1/vertex_shader.glsl")
        vertex_shader_source = file.read()
        file = open("compute_1/geometry_shader.glsl")
        geometry_shader_source = file.read()
        file = open("compute_1/fragment_shader.glsl")
        fragment_shader_source = file.read()

        # Create our compute shader
        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_X", str(self.group_x))
        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_Y", str(self.group_y))
        self.compute_shader = self.ctx.compute_shader(source=compute_shader_source)

        # Program for visualizing the balls
        self.program = self.ctx.program(
            vertex_shader=vertex_shader_source,
            geometry_shader=geometry_shader_source,
            fragment_shader=fragment_shader_source,
        )

    def on_draw(self):
        self.clear()

        # Change the force
        force = math.sin(self.run_time / 10) / 2, math.cos(self.run_time / 10) / 2
        force = 0.0, 0.0

        # Bind buffers
        self.ssbo_1.bind_to_storage_buffer(binding=0)
        self.ssbo_2.bind_to_storage_buffer(binding=1)

        # Set input variables for compute shader
        self.compute_shader["screen_size"] = self.get_size()
        self.compute_shader["force"] = force
        self.compute_shader["frame_time"] = self.run_time

        # Run compute shader
        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

        # Draw the balls
        self.vao_2.render(self.program)

        # Swap the buffers around (we are ping-ping rendering between two buffers)
        self.ssbo_1, self.ssbo_2 = self.ssbo_2, self.ssbo_1
        # Swap what geometry we draw
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1

    def on_update(self, delta_time: float):
        self.run_time = delta_time

    def gen_initial_data(self):
        for i in range(self.num_balls):
            # Position/radius
            radius = 3  # random.random() * 10 + 3
            yield random.randrange(0, self.width)
            yield random.randrange(0, self.height)
            yield 0.0  # z (padding)
            yield radius  # w / radius

            # Velocity
            v = random.random() * 1.0 + 0.1
            angle = (i / self.num_balls) * math.pi * 2.0
            yield math.cos(angle) * v  # vx
            yield math.sin(angle) * v  # vy
            yield 0.0  # vz (padding)
            yield 0.0  # vw (padding)

            # Color
            yield 1.0 * random.random()  # r
            yield 1.0 * random.random()  # g
            yield 1.0 * random.random()  # b
            yield 1.0  # a


app = App()
arcade.run()
