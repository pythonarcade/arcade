import math
from typing import Tuple

import arcade
from pyglet.math import Mat4


class OrthographicCamera:

    def __init__(self, left: int, right: int, bottom: int, top: int):
        self._identity: Mat4 = Mat4()
        self._window = arcade.get_window()
        
        self.viewport = (left, right, bottom, top)
        self.projection_matrix: Mat4 = Mat4.orthogonal_projection(left, right, bottom, top, -1.0, 1.0)

        self._scale: float = 0.0
        self._position: Tuple[float, float] = (0.0, 0.0)
        self.scroll(0, 0)
        self.zoom(1.0)

    def resize(self, left: int, right: int, bottom: int, top: int):
        self.viewport = (left, right, bottom, top)
        self.projection_matrix = Mat4.orthogonal_projection(left, right, bottom, top, -1.0, 1.0)

    @property
    def scale(self):
        return self._scale

    def zoom(self, value: float):
        self._scale += value
        if self._scale < 0:
            self._scale = 0.0001
        self.scale_matrix = self._identity.scale(x=self._scale, y=self._scale)

    @property
    def position(self) -> Tuple[int, int]:
        x = self._position[0] * self.width
        y = self._position[1] * self.height
        return (int(x), int(y))

    def scroll(self, x: int, y: int):
        x_scaled = x / self.width
        y_scaled = y / self.height
        x_scaled = self._position[0] + x_scaled
        y_scaled = self._position[1] + y_scaled
        self._position = (x_scaled, y_scaled)
        self.translate_matrix = self._identity.translate(x_scaled, y_scaled, 0)

    @property
    def position_relative(self):
        return self._position

    def scroll_relative(self, x: float, y: float):
        x = self._position[0] + x
        y = self._position[1] + y
        self._position = (x, y)
        self.translate_matrix = self._identity.translate(x, y, 0)

    @property
    def width(self) -> int:
        return self.viewport[1] - self.viewport[0]
    
    @property
    def height(self) -> int:
        return self.viewport[3] - self.viewport[2]

    def use(self):
        transform_matrix = self.translate_matrix @ self.scale_matrix
        view_matrix = transform_matrix.__invert__()
        self._window.ctx.projection_2d_matrix = self.projection_matrix @ view_matrix
