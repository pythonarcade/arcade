"""Packets of data and base types supporting cameras.

These are placed in their own module to simplify imports due to their
wide usage throughout Arcade's camera code.
"""

from contextlib import contextmanager
from typing import Final, Generator, Protocol

from pyglet.math import Vec2, Vec3
from typing_extensions import Self

from arcade.types import LRBT, AsFloat, Point, Point3, Rect

__all__ = [
    "CameraData",
    "DEFAULT_FAR",
    "DEFAULT_NEAR_ORTHO",
    "OrthographicProjectionData",
    "PerspectiveProjectionData",
    "Projection",
    "Projector",
    "ZeroProjectionDimension",
    "constrain_camera_data",
    "duplicate_camera_data",
]

DEFAULT_NEAR_ORTHO: Final[float] = -100.0
"""The default backward-facing depth cutoff for orthographic rendering.

Unless an orthographic camera is provided a different value, this will be
used as the near cutoff for its point of view.

The :py:class:`~arcade.camera.perspective.PerspectiveProjector` uses
``0.01`` as its default near value to avoid division by zero.
"""

DEFAULT_FAR: Final[float] = 100.0
"""The default forward-facing depth cutoff for all Arcade cameras.

Unless a camera is provided a different value, anything further away than this
value will not be drawn.
"""


class ZeroProjectionDimension(ValueError):
    """A projection's dimensions were zero along at least one axis.

    This usually happens because code tried to set one of the following:

    * ``left`` equal to ``right``
    * ``bottom`` equal to ``top``

    You can handle this error as a :py:class:`ValueError`.
    """

    ...


class CameraData:
    """Stores position, orientation, and zoom for a camera.

    This is like where a camera is placed in 3D space.

    Args:
        position:
            The camera's location in 3D space.
        up:
            The direction which is considered "up" for the camera.
        forward:
            The direction the camera is facing.
        zoom:
            How much the camera is zoomed in or out.
    """

    __slots__ = ("position", "up", "forward", "zoom")

    def __init__(
        self,
        position: Point3 = (0.0, 0.0, 0.0),
        up: Point3 = (0.0, 1.0, 0.0),
        forward: Point3 = (0.0, 0.0, -1.0),
        zoom: float = 1.0,
    ):
        self.position: tuple[float, float, float] = position
        """A 3D vector which describes where the camera is located."""

        self.up: tuple[float, float, float] = up
        """A 3D vector which describes which direction is up (+y)."""

        self.forward: tuple[float, float, float] = forward
        """
        A scalar which describes which direction the camera is pointing.

        While this affects the projection matrix, it also allows camera
        controllers to access zoom functionality without interacting with
        projection data.
        """

        self.zoom: float = zoom
        """A scalar which describes how much the camera is zoomed in or out."""

    def __str__(self):
        return f"CameraData<{self.position=}, {self.up=}, {self.forward=}, {self.zoom=}>"

    def __repr__(self):
        return self.__str__()


def duplicate_camera_data(origin: CameraData):
    """
    Clone camera data

    Args:
        origin: The camera data to clone
    """
    return CameraData(origin.position, origin.up, origin.forward, float(origin.zoom))


def constrain_camera_data(data: CameraData, forward_priority: bool = False):
    """
    Ensure that the camera data forward and up vectors are length one,
    and are perpendicular

    Args:
        data: the camera data to constrain
        forward_priority: whether up or forward gets constrained
    """
    forward_vec = Vec3(*data.forward).normalize()
    up_vec = Vec3(*data.up).normalize()
    right_vec = forward_vec.cross(up_vec).normalize()
    if forward_priority:
        up_vec = right_vec.cross(forward_vec)
    else:
        forward_vec = up_vec.cross(right_vec)

    data.forward = (forward_vec.x, forward_vec.y, forward_vec.z)
    data.up = (up_vec.x, up_vec.y, up_vec.z)


class OrthographicProjectionData:
    """Describes an Orthographic projection.

    This is by default a Left-handed system. with the X axis going from left to
    right, The Y axis going from bottom to top, and the Z axis going from towards
    the screen to away from the screen. This can be made right-handed by making
    the near value greater than the far value.

    Args:
        left: Left limit of the projection
        right: Right limit of the projection
        bottom: Bottom limit of the projection
        top: Top limit of the projection
        near: Near plane
        far: Far plane
    """

    __slots__ = ("rect", "near", "far")

    def __init__(
        self, left: float, right: float, bottom: float, top: float, near: float, far: float
    ):
        self.rect: Rect = LRBT(left, right, bottom, top)
        """Rectangle defining the projection area."""

        self.near: float = near
        """
        The 'closest' visible position along the forward direction.

        It will get mapped to z = -1.0. Anything closer than this value
        is not visible.
        """

        self.far: float = far
        """
        The 'farthest' visible position along the forward direction.

        It will get mapped to z = 1.0. Anything father than this value
        is not visible.
        """

    @property
    def left(self) -> float:
        """
        The left-side cutoff value, which gets mapped to x = -1.0.

        Anything to the left of this value is not visible.
        """
        return self.rect.left

    @left.setter
    def left(self, new_left: AsFloat):
        r = self.rect
        dl = new_left - r.left
        self.rect = Rect(
            new_left, r.right, r.bottom, r.top, r.width + dl, r.height, r.x + dl / 2.0, r.y
        )

    @property
    def right(self) -> float:
        """
        The right-side cutoff value, which gets mapped to x = 1.0.

        Anything to the left of this value is not visible.
        """
        return self.rect.right

    @right.setter
    def right(self, new_right: AsFloat):
        r = self.rect
        dr = new_right - r.right
        self.rect = Rect(
            r.left, new_right, r.bottom, r.top, r.width + dr, r.height, r.x + dr / 2.0, r.y
        )

    @property
    def bottom(self) -> float:
        """
        The bottom-side cutoff value, which gets mapped to -y = 1.0.

        Anything to the left of this value is not visible.
        """
        return self.rect.bottom

    @bottom.setter
    def bottom(self, new_bottom: AsFloat):
        r = self.rect
        db = new_bottom - r.bottom
        self.rect = Rect(
            r.left, r.right, new_bottom, r.top, r.width, r.height + db, r.x, r.y + db / 2.0
        )

    @property
    def top(self) -> float:
        """
        The top-side cutoff value, which gets mapped to y = 1.0.

        Anything to the left of this value is not visible.
        """
        return self.rect.top

    @top.setter
    def top(self, new_top: AsFloat):
        r = self.rect
        dt = new_top - r.top
        self.rect = Rect(
            r.left, r.right, r.bottom, new_top, r.width, r.height + dt, r.x, r.y + dt / 2.0
        )

    @property
    def lrbt(self) -> tuple[float, float, float, float]:
        """The left, right, bottom, and top values of the projection."""
        return self.rect.lrbt

    @lrbt.setter
    def lrbt(self, new_lrbt: tuple[float, float, float, float]):
        self.rect = LRBT(*new_lrbt)

    def __str__(self):
        return f"OrthographicProjection<LRBT={self.rect.lrbt}, {self.near=}, {self.far=}>"

    def __repr__(self):
        return self.__str__()


def orthographic_from_rect(rect: Rect, near: float, far: float) -> OrthographicProjectionData:
    """
    Create an orthographic projection from a rectangle.

    Args:
        rect: The rectangle to create the projection from.
        near: The near plane of the projection.
        far: The far plane of the projection.
    """
    return OrthographicProjectionData(rect.left, rect.right, rect.bottom, rect.top, near, far)


class PerspectiveProjectionData:
    """
    Data for perspective projection.

    Args:
        aspect: The aspect ratio of the screen (width over height).
        fov: The field of view in degrees.
        near: The 'closest' visible position along the forward direction.
        far: The 'farthest' visible position along the forward
    """

    __slots__ = ("aspect", "fov", "near", "far")

    def __init__(self, aspect: float, fov: float, near: float, far: float):
        self.aspect: float = aspect
        """The aspect ratio of the screen (width over height)."""

        self.fov: float = fov
        """
        The field of view in degrees.

        Together with the aspect ratio, it defines the size of the
        perspective projection for any given depth.
        """

        self.near: float = near
        """
        The 'closest' visible position along the forward direction.

        It will get mapped to z = -1.0. Anything closer than this value
        is not visible.
        """

        self.far: float = far
        """"
        The 'farthest' visible position along the forward direction.

        It will get mapped to z = 1.0. Anything father than this value
        is not visible.
        """

    def __str__(self) -> str:
        return f"PerspectiveProjection<{self.aspect=}, {self.fov=}, {self.near=}, {self.far=}>"

    def __repr__(self) -> str:
        return self.__str__()


class Projection(Protocol):
    """Matches the data universal in Arcade's projection data objects.

    There are multiple types of projections used in games, but all the
    common ones share key features. This :py:class:`~typing.Protocol`:

    #. Defines those shared elements
    #. Annotates these in code for both humans and automated type
       checkers

    The specific implementations which match it are used inside of
    implementations of Arcade's :py:class:`.Projector` behavior. All
    of these projectors rely on a ``viewport`` as well as ``near`` and
    ``far`` values.

    The ``viewport`` is measured in screen pixels. By default, the
    conventions for this are the same as the rest of Arcade and
    OpenGL:

    * X is measured rightward from left of the screen
    * Y is measured up from the bottom of the screen

    Although the ``near`` and ``far`` values are describe the cutoffs
    for what the camera sees in world space, the exact meaning differs
    between projection type.

    .. list-table::
       :header-rows: 1

       * - Common Projection Type
         - Meaning of ``near`` & ``far``

       * - Simple Orthographic
         - The Z position in world space

       * - Perspective & Isometric
         - Where the rear and front clipping planes sit along a
           camera's :py:attr:`.CameraData.forward` vector.

    """

    near: float
    far: float


class Projector(Protocol):
    """Projects from world coordinates to viewport pixel coordinates.

    Projectors also support converting in the opposite direction from
    screen pixel coordinates to world space coordinates.

    The two key spatial methods which do this are:

    .. list-table::
       :header-rows: 1

       * - Method
         - Action

       * - :py:meth:`.project`
         - Turn world coordinates into pixel coordinates relative
           to the origin (bottom left by default).

       * - :py:meth:`.unproject`
         - Convert screen pixel coordinates into world space.

    .. note: Every :py:class:`.Camera` is also a kind of projector.

    The other required methods are for helping manage which camera is
    currently used to draw.

    """

    def use(self) -> None:
        """Set the GL context to use this projector and its settings.

        .. warning:: You may be looking for:py:meth:`.activate`!

                     This method only sets rendering state for a given
                     projector. Since it doesn't restore any afterward,
                     it's easy to misuse in ways which can cause bugs
                     or temporarily break a game's rendering until
                     relaunch. For reliable, automatic clean-up see
                     the :py:meth:`.activate` method instead.

        If you are implementing your own custom projector, this method
        should only:

        #. Set the Arcade :py:class:`~arcade.Window`'s
           :py:attr:`~arcade.Window.current_camera` to this object
        #. Calculate any required view and projection matrices
        #. Set any resulting values on the current
           :py:class:`~arcade.ArcadeContext`, including the:

           * :py:attr:`~arcade.ArcadeContext.viewport`
           * :py:attr:`~arcade.ArcadeContext.view_matrix`
           * :py:attr:`~arcade.ArcadeContext.projection_matrix`

        This method should **never** handle cleanup. That is the
        responsibility of :py:attr:`.activate`.
        """
        ...

    @contextmanager
    def activate(self) -> Generator[Self, None, None]:
        """
        Activate this projector for rendering.

        This is a context manager and should be used with a ``with`` statement::

            with projector.activate():
                # Render with this projector
        """
        ...

    def project(self, world_coordinate: Point) -> Vec2:
        """
        Take a Vec2 or Vec3 of coordinates and return the related screen coordinate
        """
        ...

    def unproject(self, screen_coordinate: Point) -> Vec3:
        """
        Take in a pixel coordinate and return the associated world coordinate

        Essentially reverses the effects of the projector.

        Args:
            screen_coordinate: A 2D position in pixels should generally be inside
                the range of the active viewport.
        Returns:
            A 3D vector in world space.
        """
        ...
