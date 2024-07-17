from __future__ import annotations

from typing import Optional


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
        self.damping: Optional[float] = None
        self.gravity: Optional[tuple[float, float]] = None
        self.max_velocity: Optional[float] = None
        self.max_horizontal_velocity: Optional[float] = None
        self.max_vertical_velocity: Optional[float] = None


class PymunkMixin:

    def __init__(self) -> None:
        self.pymunk = PyMunk()
        self.force = [0.0, 0.0]
        """force vector used by pymunk"""

    def pymunk_moved(self, physics_engine, dx: float, dy: float, d_angle: float) -> None:
        """
        Called by the pymunk physics engine if this sprite moves.

        Args:
            physics_engine (PymunkPhysicsEngine): The physics engine that is calling this method.
            dx (float): The change in x position.
            dy (float): The change in y position.
            d_angle (float): The change in angle.
        """
        pass
