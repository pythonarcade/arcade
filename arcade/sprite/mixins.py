from typing import Optional, Union

class PyMunk:
    """Object used to hold pymunk info for a sprite."""
    __slots__ = (
        "damping",
        "gravity",
        "max_velocity",
        "max_horizontal_velocity",
        "max_vertical_velocity",
    )

    def __init__(self) -> None:
        self.damping: Optional[float] = None
        self.gravity: Optional[Union[pymunk.Vec2d, Tuple[float, float], Vec2]] = None
        self.max_velocity: Optional[float] = None
        self.max_horizontal_velocity: Optional[float] = None
        self.max_vertical_velocity: Optional[float] = None


class PymunkMixin:
    """Sprite uses this to add pymunk"""

    def __init__(self) -> None:
        self.pymunk = PyMunk()
        self.force = [0.0, 0.0]

    def pymunk_moved(self, physics_engine, dx: float, dy: float, d_angle: float) -> None:
        """Called by the pymunk physics engine if this sprite moves."""
        pass
