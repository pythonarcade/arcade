"""
GPU version of bouncing coins.

The downside of manipulating spritelists
with shaders is that the data in the sprites
are stale, but it can still be a useful tool.

GPU collision checking can potentially be used if needed.

The window can be resized.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.spritelist_interaction_bouncing_coins
"""

from array import array
from random import randint, uniform
from typing import cast

import arcade
from arcade.gl import BufferDescription, Buffer
from arcade import hitbox

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

NUM_COINS = 10_000


class GPUBouncingCoins(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, resizable=True)

        # Generate lots of coins in random positions
        self.coins = arcade.SpriteList(use_spatial_hash=False)
        texture = arcade.load_texture(
            ":resources:images/items/coinGold.png",
            hit_box_algorithm=hitbox.algo_bounding_box,
        )
        for _ in range(NUM_COINS):
            self.coins.append(
                arcade.Sprite(
                    texture,
                    scale=0.25,
                    center_x=randint(0, WINDOW_WIDTH),
                    center_y=randint(0, WINDOW_HEIGHT),
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

            in vec4 in_pos_angle;
            in vec2 in_vel;

            out vec4 out_pos_angle;
            out vec2 out_vel;

            void main() {
                vec2 pos = in_pos_angle.xy + in_vel * 100.0 * delta_time;
                vec2 vel = in_vel;
                if (pos.x > size.x) {
                    pos.x = size.x;
                    vel.x *= -1.0;
                }
                else if (pos.x < 0.0) {
                    pos.x = 0.0;
                    vel.x *= -1.0;
                }
                if (pos.y > size.y) {
                    pos.y = size.y;
                    vel.y *= -1.0;
                }
                else if (pos.t < 0.0) {
                    pos.y = 0.0;
                    vel.y *= -1.0;
                }
                out_pos_angle = vec4(pos, in_pos_angle.zw);
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
            data=array("f", [uniform(-1, 1) for _ in range(NUM_COINS * 2)])
        )
        # Second velocity buffer
        self.buffer_velocity_2 = self.ctx.buffer(reserve=self.buffer_velocity_1.size)
        # Create a buffer with the same size as the position buffer in  the spritelist.
        # It's important that these match because we're copying that buffer into this one.
        self.buffer_pos_angle = cast(Buffer, self.coins.data.storage_positions_angle)
        self.buffer_pos_angle_copy = self.ctx.buffer(reserve=self.buffer_pos_angle.size)

        # Geometry input: Copied positions and first velocity buffer
        self.geometry_1 = self.ctx.geometry(
            [
                BufferDescription(self.buffer_pos_angle_copy, "4f", ["in_pos_angle"]),
                BufferDescription(self.buffer_velocity_1, "2f", ["in_vel"]),
            ]
        )
        # Geometry input: Copied positions and second velocity buffer
        self.geometry_2 = self.ctx.geometry(
            [
                BufferDescription(self.buffer_pos_angle_copy, "4f", ["in_pos_angle"]),
                BufferDescription(self.buffer_velocity_2, "2f", ["in_vel"]),
            ]
        )

    def on_draw(self):
        self.clear()

        # Copy the position buffer. This happens on the gpu side.
        self.buffer_pos_angle_copy.copy_from_buffer(self.buffer_pos_angle)

        # Run the transform writing new positions and velocities
        self.geometry_1.transform(
            self.program,
            [
                self.buffer_pos_angle,
                self.buffer_velocity_2,
            ],
        )

        self.coins.draw()

        # Swap things around for next frame
        (self.buffer_velocity_1, self.buffer_velocity_2) = self.buffer_velocity_2, self.buffer_velocity_1  # noqa
        self.geometry_1, self.geometry_2 = self.geometry_2, self.geometry_1

    def on_update(self, delta_time: float):
        self.program["delta_time"] = delta_time
        self.program["size"] = self.get_size()


GPUBouncingCoins().run()
