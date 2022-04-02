"""
GPU version of bouncing coins.

The downside of manipulating spritelists
with shaders is that the data in the sprites
are stale, but it can still be a useful tool.

GPU collision checking can potentially be used if needed.

The window can be resized.
"""
from array import array
from random import randint, uniform

import arcade
from arcade.gl.types import BufferDescription

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

NUM_COINS = 10_000


class GPUBouncingCoins(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, resizable=True)

        # Genreate lots of coins in random positions
        self.coins = arcade.SpriteList(use_spatial_hash=None)
        for _ in range(NUM_COINS):
            self.coins.append(
                arcade.Sprite(
                    ":resources:images/items/coinGold.png",
                    scale=0.25,
                    center_x=randint(0, WINDOW_WIDTH),
                    center_y=randint(0, WINDOW_HEIGHT),
                    hit_box_algorithm=None,
                )
            )
        # Ensure internal buffer data are up to date
        self.coins.write_sprite_buffers_to_gpu()

        # Transform shader writing each out value to separate buffers.
        # We're simply moving the sprites based on velocity and
        # reversing direction if outside the screen
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform float delta_time;
            uniform vec2 size;

            in vec2 in_pos;
            in vec2 in_vel;

            out vec2 out_pos;
            out vec2 out_vel;

            void main() {
                vec2 pos = in_pos + in_vel * 100.0 * delta_time;
                vec2 vel = in_vel;
                if (pos.x > size.x) {
                    pos.x = size.x;
                    vel.x *= -1;
                }
                else if (pos.x < 0) {
                    pos.x = 0;
                    vel.x *= -1;
                }
                if (pos.y > size.y) {
                    pos.y = size.y;
                    vel.y *= -1;
                }
                else if (pos.t < 0) {
                    pos.y = 0;
                    vel.y *= -1;
                }
                out_pos = pos;
                out_vel = vel;
            }
            """,
            varyings_capture_mode="separate",
        )
        # We need two position buffers and two velocity buffers
        # because we can't safely write to buffers we are reading from.
        # We create two velocity buffers because spritelist don't have velocity buffers
        # We only create one position buffer because the second one is in the spritelist

        # Buffer with some quick random velocities for our coins
        self.buffer_velocity_1 = self.ctx.buffer(
            data=array('f', [uniform(-1, 1) for _ in range(NUM_COINS * 2)])
        )
        # Second velocity buffer
        self.buffer_velocity_2 = self.ctx.buffer(reserve=self.buffer_velocity_1.size)
        # Create a buffer with the same size as the position buffer in  the spritelist.
        # It's important that these match because we're copying that buffer into this one.
        self.buffer_pos_copy = self.ctx.buffer(reserve=self.coins.buffer_positions.size)

        # Geometry input: Copied positions and first velocity buffer
        self.geometry_1 = self.ctx.geometry(
            [
                BufferDescription(self.buffer_pos_copy, "2f", ["in_pos"]),
                BufferDescription(self.buffer_velocity_1, "2f", ["in_vel"]),
            ]
        )
        # Geometry input: Copied positions and second velocity buffer
        self.geometry_2 = self.ctx.geometry(
            [
                BufferDescription(self.buffer_pos_copy, "2f", ["in_pos"]),
                BufferDescription(self.buffer_velocity_2, "2f", ["in_vel"]),
            ]
        )

    def on_draw(self):
        self.clear()

        # Copy the position buffer. This happens on the gpu side.
        self.buffer_pos_copy.copy_from_buffer(self.coins.buffer_positions)

        # Run the transform writing new positions and velocities
        self.geometry_1.transform(
            self.program,
            [
                self.coins.buffer_positions,
                self.buffer_velocity_2,
            ]
        )

        self.coins.draw()

        # Swap things around for next frame
        self.buffer_velocity_1, self.buffer_velocity_2 = self.buffer_velocity_2, self.buffer_velocity_1
        self.geometry_1, self.geometry_2 = self.geometry_2, self.geometry_1

    def on_update(self, delta_time: float):
        self.program["delta_time"] = delta_time
        self.program["size"] = self.get_size()


GPUBouncingCoins().run()
