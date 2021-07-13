"""
Camera class
"""

from arcade.window_commands import get_scaling_factor
import math

import arcade
from arcade.math import Mat4, Vec2


class Camera:
    def __init__(
        self,
        window,
        viewport_width: int = 0,
        viewport_height: int = 0,
    ):
        # Window
        if isinstance(window, arcade.View):
            raise ValueError("The first parameter must be an instance of arcade.Window, not arcade.View. "
                             "Try passing in 'myview.window' instead of 'myview'.")
        if not isinstance(window, arcade.Window):
            raise ValueError("The first parameter must be an instance of arcade.Window.")
        self._window = window

        # Position
        self.position = Vec2(0, 0)

        # Projection Matrix
        self.projection_matrix = None

        # Near and Far
        self.near = -100
        self.far = 100

        # Shake
        self.shake_velocity = Vec2()
        self.shake_offset = Vec2()
        self.shake_decay = Vec2()

        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

        # Initial Update
        self.resize(viewport_width, viewport_height)

    def update(self):
        # Apply Camera Shake

        self.shake_offset += self.shake_velocity

        if self.shake_offset[0] or self.shake_offset[1]:
            velocity_change_x = 0
            velocity_change_y = 0

            if self.shake_offset[0] > 0:
                velocity_change_x = -1
            elif self.shake_offset[0] < 0:
                velocity_change_x = 1

            if self.shake_offset[1] > 0:
                velocity_change_y = -1
            elif self.shake_offset[1] < 0:
                velocity_change_y = 1

            self.shake_velocity += Vec2(velocity_change_x, velocity_change_y)
            self.shake_velocity *= self.shake_decay

            if abs(self.shake_velocity[0]) < 0.5 and abs(self.shake_offset[0]) < 0.5:
                self.shake_velocity = Vec2(0, self.shake_velocity[1])
                self.shake_offset = Vec2(0, self.shake_offset[1])

            if abs(self.shake_velocity[1]) < 0.5 and abs(self.shake_offset[1]) < 0.5:
                self.shake_velocity = Vec2(self.shake_velocity[0], 0)
                self.shake_offset = Vec2(self.shake_offset[0], 0)

            self.position += Vec2(self.shake_offset[0], self.shake_offset[1])

        self.projection_matrix = Mat4.orthogonal_projection(
            math.floor(self.position[0]),
            self.viewport_width + math.floor(self.position[0]),
            math.floor(self.position[1]),
            self.viewport_height + math.floor(self.position[1]),
            self.near,
            self.far,
        )

    def resize(self, viewport_width: int, viewport_height: int):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

    def shake(self, velocity: Vec2, decay: Vec2 = Vec2(0.9, 0.9)):
        self.shake_velocity += velocity
        decay = Vec2(decay[0], decay[1])
        self.shake_decay = decay.clamp(0.9, 0.9)

    def move_to(self, vector: Vec2, speed: float = 1.0):
        pos = Vec2(vector[0], vector[1])
        self.position = self.position.lerp(pos, speed)

    def zoom(self, change: float):
        raise NotImplementedError("Camera Zooming is not yet supported")

    def use(self):
        self.update()
        fbo = self._window.ctx.fbo
        scaling = get_scaling_factor(self._window) if fbo.is_default else 1.0
        fbo.ctx.viewport = (
            0,
            0,
            int(self.viewport_width * scaling),
            int(self.viewport_height * scaling),
        )
        self._window.ctx.projection_2d_matrix = self.projection_matrix
