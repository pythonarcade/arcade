from typing import Tuple, Sequence
from arcade.gl import Context
from arcade import Color

class Light:

    def __init__(self, position: Tuple[float, float], radius: float = 50.0, usage: str = 'dynamic'):
        """Create a Light.

        Note: It's important to separate lights that don' change properties
        and static ones with the `usage` parameter.

        :param Tuple[float, float] position: the position of the light
        :param float radius: The radius of the light
        :param str usage: `static` or `dynamic`.
        """
        self._center_x = position[0]
        self._center_y = position[1]
        self._radius = radius

    @property
    def position(self) -> Tuple[float, float]:
        """Get or set the light position"""
        return self._center_x, self._center_y

    @position.setter
    def position(self, value):
        self._center_x, self._center_y = value

    @property
    def radius(self) -> float:
        """Get or set the light size"""
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value


class LightLayer:

    def __init__(self, ctx: Context, size: Tuple[int, int]):
        """Create a LightLayer

        The size of a layer should ideally be of the same size and the screen.

        :param Tuple[int, int] size: Width and height of light layer
        """
        self.ctx = ctx
        self._lights = []
        self._light_buffer = self.ctx.framebuffer(color_attachments=self.ctx.texture(size, components=4))
        self._diffuse_buffer = self.ctx.framebuffer(color_attachments=self.ctx.texture(size, components=4))
        self._prev_target = None

    def add(self, light: Light):
        """Add a Light to the layer"""
        self._lights.append(light)

    def extend(self, lights: Sequence[Light]):

    def remove(self, light: Light):
        """Remove a light to the layer"""
        self._lights.remove(light)

    def __enter__(self):
        self._prev_target = self.ctx.active_framebuffer
        self._diffuse_buffer.use()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._prev_target.use()

    def draw(self, target=None, ambient_color: Color = (64, 64, 64)):
        pass
