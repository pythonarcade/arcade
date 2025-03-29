from array import array
from typing import Iterator, Sequence

from arcade import gl
from arcade.color import WHITE
from arcade.future.texture_render_target import RenderTargetTexture
from arcade.types import RGBOrA255


class Light:
    """
    Create a Light.

    Note: It's important to separate lights that don't change properties
    and static ones with the ``usage`` parameter.

    Args:
        center_x: X position of the light
        center_y: Y position of the light
        radius: Radius of the light
        color: Color of the light
        mode: 'hard' or 'soft' light
    """

    HARD = 1.0
    SOFT = 0.0

    def __init__(
        self,
        center_x: float,
        center_y: float,
        radius: float = 50.0,
        color: RGBOrA255 = WHITE,
        mode: str = "hard",
    ):
        if not (isinstance(color, tuple) or isinstance(color, list)):
            raise ValueError(
                "Color must be a 3-4 element Tuple or List with red-green-blue "
                " and optionally an alpha."
            )

        if not isinstance(mode, str) or not (mode == "soft" or mode == "hard"):
            raise ValueError("Mode must be set to either 'soft' or 'hard'.")

        self._center_x = center_x
        self._center_y = center_y
        self._radius = radius
        self._attenuation = Light.HARD if mode == "hard" else Light.SOFT
        self._color = color[:3]
        self._light_layer: LightLayer | None = None

        if len(self._color) != 3:
            raise ValueError(
                "Color must be a 3-4 element Tuple or List with red-green-blue "
                "and optionally an alpha."
            )

    @property
    def position(self) -> tuple[float, float]:
        """Get or set the light position"""
        return self._center_x, self._center_y

    @position.setter
    def position(self, value):
        if self._light_layer:
            self._light_layer._rebuild = True
        self._center_x, self._center_y = value

    @property
    def radius(self) -> float:
        """Get or set the light size"""
        return self._radius

    @radius.setter
    def radius(self, value):
        if self._light_layer:
            self._light_layer._rebuild = True
        self._radius = value


class LightLayer(RenderTargetTexture):
    """
    Create a LightLayer

    The size of a layer should ideally be of the same size and the screen.

    Args:
        width: Width of light layer
        height: Height of light layer
    """

    def __init__(self, width: int, height: int):
        super().__init__(width, height)

        self._lights: list[Light] = []
        self._prev_target = None
        self._rebuild = False
        self._stride = 28
        self._buffer = self.ctx.buffer(reserve=self._stride * 100)
        self._vao = self.ctx.geometry(
            [
                gl.BufferDescription(
                    self._buffer,
                    "2f 1f 1f 3f",
                    ["in_vert", "in_radius", "in_attenuation", "in_color"],
                ),
            ]
        )
        self._light_program = self.ctx.load_program(
            vertex_shader=":system:shaders/lights/point_lights_vs.glsl",
            geometry_shader=":system:shaders/lights/point_lights_geo.glsl",
            fragment_shader=":system:shaders/lights/point_lights_fs.glsl",
        )
        self._combine_program = self.ctx.load_program(
            vertex_shader=":system:shaders/lights/combine_vs.glsl",
            fragment_shader=":system:shaders/lights/combine_fs.glsl",
        )
        # NOTE: Diffuse buffer created in parent
        self._light_buffer = self.ctx.framebuffer(
            color_attachments=self.ctx.texture((width, height), components=3)
        )

    @property
    def diffuse_texture(self):
        """The diffuse texture"""
        return self.texture

    @property
    def light_texture(self):
        """The light texture"""
        return self._light_buffer.color_attachments[0]

    def resize(self, width, height):
        """Resize the light layer"""
        super().resize(width, height)
        self._light_buffer = self.ctx.framebuffer(
            color_attachments=self.ctx.texture((width, height), components=3)
        )

    def clear(self):
        """Clear the light layer"""
        super().clear()
        self._light_buffer.clear()

    def add(self, light: Light):
        """Add a Light to the layer"""
        self._lights.append(light)
        light._light_layer = self
        self._rebuild = True

    def extend(self, lights: Sequence[Light]):
        """Add a list of lights to the layer"""
        for light in lights:
            self.add(light)

    def remove(self, light: Light):
        """Remove a light to the layer"""
        self._lights.remove(light)
        light._light_layer = None
        self._rebuild = True

    def __len__(self) -> int:
        """Number of lights"""
        return len(self._lights)

    def __iter__(self) -> Iterator[Light]:
        """Return an iterable object of lights"""
        return iter(self._lights)

    def __getitem__(self, i) -> Light:
        return self._lights[i]

    def __enter__(self):
        self._prev_target = self.ctx.active_framebuffer
        self._fbo.use()
        self._fbo.clear(color=self._background_color)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._prev_target.use()

    def draw(
        self,
        position: tuple[float, float] = (0, 0),
        target=None,
        ambient_color: RGBOrA255 = (64, 64, 64),
    ):
        """Draw the lights

        Args:
            position: Position offset (scrolling)
            target: The window or framebuffer we want to render to (default is window)
            ambient_color: The ambient light color
        """
        if target is None:
            target = self.window

        # Re-build light data if needed
        if self._rebuild and len(self._lights) > 0:
            data: list[float] = []
            for light in self._lights:
                data.extend(light.position)
                data.append(light.radius)
                data.append(light._attenuation)
                data.extend(light._color)

            while self._buffer.size < len(data) * self._stride:
                self._buffer.orphan(double=True)

            self._buffer.write(data=array("f", data))
            self._rebuild = False

        # Render to light buffer
        self._light_buffer.use()
        self._light_buffer.clear()
        if len(self._lights) > 0:
            self._light_program["position"] = position
            self.ctx.enable(self.ctx.BLEND)
            self.ctx.blend_func = self.ctx.BLEND_ADDITIVE
            self._vao.render(self._light_program, mode=self.ctx.POINTS, vertices=len(self._lights))
            self.ctx.blend_func = self.ctx.BLEND_DEFAULT

        # Combine pass
        target.use()
        self._combine_program["diffuse_buffer"] = 0
        self._combine_program["light_buffer"] = 1
        self._combine_program["ambient"] = ambient_color[:3]
        self._fbo.color_attachments[0].use(0)
        self._light_buffer.color_attachments[0].use(1)

        self._quad_fs.render(self._combine_program)
