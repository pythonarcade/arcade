"""Packets of data and base types supporting cameras.

These are placed in their own module to simplify imports due to their
wide usage throughout Arcade's camera code.
"""
from __future__ import annotations
from typing import Protocol, Tuple, Iterator, Optional, Generator
from contextlib import contextmanager

from typing_extensions import Self
from pyglet.math import Vec3


__all__ = [
    'CameraData',
    'OrthographicProjectionData',
    'PerspectiveProjectionData',
    'Projection',
    'Projector',
    'Camera',
    'ZeroProjectionDimension',
]


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

    Attributes:
        position: A 3D vector which describes where the camera is located.
        up: A 3D vector which describes which direction is up (+y).
        forward: a 3D vector which describes which direction is forwards (+z).
        zoom: A scaler that records the zoom of the camera. While this most often affects the projection matrix
              it allows camera controllers access to the zoom functionality
              without interacting with the projection data.
    """

    __slots__ = ("position", "up", "forward", "zoom")

    def __init__(self,
                 position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 up: Tuple[float, float, float] = (0.0, 1.0, 0.0),
                 forward: Tuple[float, float, float] = (0.0, 0.0, -1.0),
                 zoom: float = 1.0):

        # View matrix data
        self.position: Tuple[float, float, float] = position
        self.up: Tuple[float, float, float] = up
        self.forward: Tuple[float, float, float] = forward

        # Zoom
        self.zoom: float = zoom

    def __str__(self):
        return f"CameraData<{self.position=}, {self.up=}, {self.forward=}, {self.zoom=}>"

    def __repr__(self):
        return self.__str__()


def duplicate_camera_data(origin: CameraData):
    return CameraData(origin.position, origin.up, origin.forward, float(origin.zoom))


def constrain_camera_data(data: CameraData, forward_priority: bool = False):
    """
    Ensure that the camera data forward and up vectors are length one,
    and are perpendicular

    :param data: the camera data to constrain
    :param forward_priority: whether up or forward gets constrained
    """
    forward_vec = Vec3(*data.forward).normalize()
    up_vec = Vec3(*data.up).normalize()
    right_vec = forward_vec.cross(up_vec).normalize()
    if forward_priority:
        up_vec = right_vec.cross(forward_vec)
    else:
        forward_vec = right_vec.cross(up_vec)

    data.forward = (forward_vec.x, forward_vec.y, forward_vec.z)
    data.up = (up_vec.x, up_vec.y, up_vec.z)


class OrthographicProjectionData:
    """Describes an Orthographic projection.

    This is by default a Left-handed system. with the X axis going from left to right, The Y axis going from
    bottom to top, and the Z axis going from towards the screen to away from the screen. This can be made
    right-handed by making the near value greater than the far value.

    Attributes:
        left: The left most value, which gets mapped to x = -1.0 (anything below this value is not visible).
        right: The right most value, which gets mapped to x = 1.0 (anything above this value is not visible).
        bottom: The bottom most value, which gets mapped to y = -1.0 (anything below this value is not visible).
        top: The top most value, which gets mapped to y = 1.0 (anything above this value is not visible).
        near: The 'closest' value, which gets mapped to z = -1.0 (anything below this value is not visible).
        far: The 'furthest' value, Which gets mapped to z = 1.0 (anything above this value is not visible).
        viewport: The pixel bounds which will be drawn onto. (left, bottom, width, height)
    """

    __slots__ = ("left", "right", "bottom", "top", "near", "far", "viewport")

    def __init__(
            self,
            left: float,
            right: float,
            bottom: float,
            top: float,
            near: float,
            far: float,
            viewport: Tuple[int, int, int, int]):

        # Data for generating Orthographic Projection matrix
        self.left: float = left
        self.right: float = right
        self.bottom: float = bottom
        self.top: float = top
        self.near: float = near
        self.far: float = far

        # Viewport for setting which pixels to draw to
        self.viewport: Tuple[int, int, int, int] = viewport

    def __str__(self):
        return (f"OrthographicProjection<"
                f"LRBT={(self.left, self.right, self.bottom, self.top)}, "
                f"{self.near=}, "
                f"{self.far=}, "
                f"{self.viewport=}>")

    def __repr__(self):
        return self.__str__()


class PerspectiveProjectionData:
    """Describes a perspective projection.

    Attributes:
        aspect: The aspect ratio of the screen (width over height).
        fov: The field of view in degrees. With the aspect ratio defines
                the size of the projection at any given depth.
        near: The 'closest' value, which gets mapped to z = -1.0 (anything below this value is not visible).
        far: The 'furthest' value, Which gets mapped to z = 1.0 (anything above this value is not visible).
        viewport: The pixel bounds which will be drawn onto. (left, bottom, width, height)
    """
    __slots__ = ("aspect", "fov", "near", "far", "viewport")

    def __init__(self,
                 aspect: float,
                 fov: float,
                 near: float,
                 far: float,

                 viewport: Tuple[int, int, int, int]):
        # Data for generating Perspective Projection matrix
        self.aspect: float = aspect
        self.fov: float = fov
        self.near: float = near
        self.far: float = far

        # Viewport for setting which pixels to draw to
        self.viewport: Tuple[int, int, int, int] = viewport

    def __str__(self):
        return f"PerspectiveProjection<{self.aspect=}, {self.fov=}, {self.near=}, {self.far=}, {self.viewport=}>"

    def __repr__(self):
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
    viewport: Tuple[int, int, int, int]
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
           :py:class:`~arcade.context.ArcadeContext`, including the:

           * :py:attr:`~arcade.context.ArcadeContext.viewport`
           * :py:attr:`~arcade.context.ArcadeContext.view_matrix`
           * :py:attr:`~arcade.context.ArcadeContext.projection_matrix`

        This method should **never** handle cleanup. That is the
        responsibility of :py:attr:`.activate`.

        """
        ...

    @contextmanager
    def activate(self) -> Generator[Self, None, None]:
        ...

    def map_screen_to_world_coordinate(
            self,
            screen_coordinate: Tuple[float, float],
            depth: Optional[float] = None
    ) -> Tuple[float, ...]:
        ...


class Camera(Protocol):

    def use(self) -> None:
        ...

    @contextmanager
    def activate(self) -> Iterator[Projector]:
        ...
