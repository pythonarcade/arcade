

from __future__ import annotations


class PyMunk:
    """Object used to hold pymunk info for a sprite."""
    __slots__ = (
        "damping",
        "gravity",
        "max_velocity",
        "max_horizontal_velocity",
        "max_vertical_velocity",
    )

    def __init__(self):
        self.damping = None
        self.gravity = None
        self.max_velocity = None
        self.max_horizontal_velocity = None
        self.max_vertical_velocity = None


class PymunkMixin:

    def __init__(self):
        self.pymunk = PyMunk()
        self.force = [0.0, 0.0]

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """Called by the pymunk physics engine if this sprite moves."""
        pass
