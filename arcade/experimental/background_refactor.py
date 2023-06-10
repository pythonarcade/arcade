from typing import TYPE_CHECKING, Optional

from arcade.gl import Program, Geometry

from arcade.experimental.camera_refactor import CameraData


class BackgroundTexture:

    def __init__(self):
        pass


class Background:

    def __init__(self, data: CameraData, texture: BackgroundTexture, color,
                 shader: Optional[Program] = None, geometry: Optional[Geometry] = None):
        pass
