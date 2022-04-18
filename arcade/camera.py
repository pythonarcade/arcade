"""
Camera class
"""
import math
from typing import Optional

from pyglet.math import Mat4, Vec2, Vec3

import arcade


class Camera:
    """
    The Camera class is used for controlling the visible viewport.
    It is very useful for separating a scrolling screen of sprites, and a GUI overlay.
    For an example of this in action, see :ref:`sprite_move_scrolling`.

    :param int viewport_width: Width of the viewport. If not set the window width will be used.
    :param int viewport_height: Height of the viewport. If not set the window height will be used.
    :param Window window: Window to associate with this camera, if working with a multi-window program.

    """

    def __init__(
        self,
        viewport_width: int = 0,
        viewport_height: int = 0,
        window: Optional["arcade.Window"] = None,
    ):
        # Reference to Context, used to update projection matrix
        self._window = window or arcade.get_window()

        # Position
        self.position = Vec2(0, 0)
        self.goal_position = Vec2(0, 0)

        # Movement Speed, 1.0 is instant
        self.move_speed = 1.0

        # Matrixes
        # Projection Matrix is used to apply the camera viewport size
        self.projection_matrix = None
        # View Matrix is what the camera is looking at(position)
        self.view_matrix = None
        # We multiple projection and view matrices to get combined, this is what actually gets sent to GL context
        self.combined_matrix = None

        # Near and Far
        self.near = -1
        self.far = 1

        # Shake
        self.shake_velocity = Vec2()
        self.shake_offset = Vec2()
        self.shake_speed = 0.0
        self.shake_damping = 0.0

        self.scale = 1.0

        self.viewport_width = viewport_width or self._window.width
        self.viewport_height = viewport_height or self._window.height
        self.set_projection()

    def update(self):
        """
        Update the camera's viewport to the current settings.
        """
        # Apply Goal Position
        self.position = self.position.lerp(self.goal_position, self.move_speed)

        # Apply Camera Shake

        # Move our offset based on shake velocity
        self.shake_offset += self.shake_velocity

        # Get x and ys
        vx = self.shake_velocity[0]
        vy = self.shake_velocity[1]

        ox = self.shake_offset[0]
        oy = self.shake_offset[1]

        # Calculate the angle our offset is at, and how far out
        angle = math.atan2(ox, oy)
        distance = arcade.get_distance(0, 0, ox, oy)
        velocity_mag = arcade.get_distance(0, 0, vx, vy)

        # Ok, what's the reverse? Pull it back in.
        reverse_speed = min(self.shake_speed, distance)
        opposite_angle = angle + math.pi
        opposite_vector = Vec2(
            math.sin(opposite_angle) * reverse_speed,
            math.cos(opposite_angle) * reverse_speed,
        )

        # Shaking almost done? Zero it out
        if velocity_mag < self.shake_speed and distance < self.shake_speed:
            self.shake_velocity = Vec2(0, 0)
            self.shake_offset = Vec2(0, 0)

        # Come up with a new velocity, pulled by opposite vector and damped
        self.shake_velocity += opposite_vector
        self.shake_velocity *= Vec2(self.shake_damping, self.shake_damping)

        # Figure out our 'real' position plus the shake
        result_position = self.position + self.shake_offset
        result_position = Vec3(
            (result_position[0] / ((self.viewport_width * self.scale) / 2)),
            (result_position[1] / ((self.viewport_height * self.scale) / 2)),
            0
        )

        self.view_matrix = ~(Mat4.from_translation(result_position) @ Mat4().scale(
            (self.scale, self.scale, 1.0)))
        self.combined_matrix = self.projection_matrix @ self.view_matrix

    def set_projection(self):
        """
        Update the projection matrix of the camera. This creates an orthogonal
        projection based on the viewport size of the camera.
        """
        self.projection_matrix = Mat4.orthogonal_projection(
            0,
            self.scale * self.viewport_width,
            0,
            self.scale * self.viewport_height,
            self.near,
            self.far
        )

    def resize(self, viewport_width: int, viewport_height: int):
        """
        Resize the camera's viewport. Call this when the window resizes.

        :param int viewport_width: Width of the viewport
        :param int viewport_height: Height of the viewport

        """

        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.set_projection()

    def shake(self, velocity: Vec2, speed: float = 1.5, damping: float = 0.9):
        """
        Add a camera shake.

        :param Vec2 velocity: Vector to start moving the camera
        :param float speed: How fast to shake
        :param float damping: How fast to stop shaking
        """
        self.shake_velocity += velocity
        self.shake_speed = speed
        self.shake_damping = damping

    def move_to(self, vector: Vec2, speed: float = 1.0):
        """
        Sets the goal position of the camera.

        The camera will lerp towards this position based on the provided speed,
        updating its position everytime the use() function is called.

        :param Vec2 vector: Vector to move the camera towards.
        :param Vec2 speed: How fast to move the camera, 1.0 is instant, 0.1 moves slowly
        """
        pos = Vec2(vector[0], vector[1])
        self.goal_position = pos
        self.move_speed = speed

    def move(self, vector: Vec2):
        """
        Moves the camera with a speed of 1.0, aka instant move

        This is equivalent to calling move_to(my_pos, 1.0)
        """
        self.move_to(vector, 1.0)

    def zoom(self, change: float):
        """
        Zoom the camera in or out. Or not.
        This will currently raise an error
        TODO implement
        """
        raise NotImplementedError("Zooming the camera is currently un-supported, but will be in a later release.")

    def use(self):
        """
        Select this camera for use. Do this right before you draw.
        """
        self._window.current_camera = self
        self.update()
        self._window.ctx.viewport = 0, 0, int(self.viewport_width), int(self.viewport_height)
        self._window.ctx.projection_2d_matrix = self.combined_matrix
