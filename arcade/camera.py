"""
Camera class
"""
import math
from typing import Optional

import arcade
from arcade.math import Mat4, Vec2
from arcade.window_commands import get_scaling_factor


class Camera:
    """
    The Camera class is used for controlling the visible viewport.
    It is very useful for separating a scrolling screen of sprites, and a GUI overlay.
    For an example of this in action, see :ref:`sprite_move_scrolling`.

    :param int viewport_width: Width of the viewport
    :param int viewport_height: Height of the viewport
    :param Window window: Window to associate with this camera, if working with a multi-window program.

    """
    def __init__(
        self,
        viewport_width: int = 0,
        viewport_height: int = 0,
        window: Optional[arcade.Window] = None,
    ):
        # Reference to Context, used to update projection matrix
        self._window = window or arcade.get_window()

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
        """
        Update the camera's viewport to the current settings.
        """
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
        """
        Resize the camera's viewport. Call this when the window resizes.

        :param int viewport_width: Width of the viewport
        :param int viewport_height: Height of the viewport

        """

        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

    def shake(self, velocity: Vec2, decay: Vec2 = Vec2(0.9, 0.9)):
        """
        Add a camera shake.

        :param Vec2 velocity: Vector to start moving the camera
        :param Vec2 decay: How fast to stop shaking
        """
        self.shake_velocity += velocity
        decay = Vec2(decay[0], decay[1])
        self.shake_decay = decay.clamp(0.9, 0.9)

    def move_to(self, vector: Vec2, speed: float = 1.0):
        """
        Move the camera to a new position

        :param Vec2 vector: Vector to move the camera to. (Lower left corner.)
        :param Vec2 speed: How fast to move the camera there. 1.0 is instance. 0.1 gives it a smooth transition.
        """
        pos = Vec2(vector[0], vector[1])
        self.position = self.position.lerp(pos, speed)

    def zoom(self, change: float):
        """
        Zoom the camera in or out. Or not.
        """
        raise NotImplementedError("Camera Zooming is not yet supported")

    def use(self):
        """
        Select this camera for use. Do this right before you draw.
        """
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
