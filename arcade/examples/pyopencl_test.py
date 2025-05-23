"""
Using pyopencl enables high-performance large-scale computations, 
such as frequent destruction and creation of interfaces, and large-scale position calculations.
More information about pyopencl:
https://mathema.tician.de/software/pyopencl/
The following example demonstrates how to quickly and easily use pyopencl within arcade to run kernel code.
"""
import arcade
import pyopencl as cl
import numpy as np

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PARTICLE_COUNT = 1000

# Initialize OpenCL
nvidia_platform = [platform for platform in cl.get_platforms() if platform.name == "NVIDIA CUDA"][0]
nvidia_devices = nvidia_platform.get_devices()
nvidia_context = cl.Context(devices=nvidia_devices)
queue = cl.CommandQueue(nvidia_context)

# OpenCL kernel: simple position update
kernel_code = """
__kernel void update_particles(__global float2 *positions, float dt) {
    int gid = get_global_id(0);
    float2 pos = positions[gid];
    pos.y -= dt * 100.0f;  // Falling down
    if (pos.y < 0.0f) pos.y = 600.0f;
    positions[gid] = pos;
}
"""
program = cl.Program(nvidia_context, kernel_code).build()

# Initialize particle data
positions_np = np.random.rand(PARTICLE_COUNT, 2).astype(np.float32)
positions_np[:, 0] *= WINDOW_WIDTH
positions_np[:, 1] *= WINDOW_HEIGHT
positions_cl = cl.Buffer(nvidia_context, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=positions_np)

class ParticleWindow(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "Arcade + OpenCL Particle Example")
        self.particles = []

    def on_draw(self):
        self.clear()
        for pos in positions_np:
            arcade.draw_circle_filled(pos[0], pos[1], 2, arcade.color.WHITE)

    def on_update(self, delta_time: float):
        # Run the OpenCL kernel to update particles
        global_size = (PARTICLE_COUNT,)
        program.update_particles(queue, global_size, None, positions_cl, np.float32(delta_time))
        cl.enqueue_copy(queue, positions_np, positions_cl)

if __name__ == "__main__":
    window = ParticleWindow()
    arcade.run()
