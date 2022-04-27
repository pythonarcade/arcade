import arcade.gl as gl
from pyglet.math import Mat3

class BackgroundTexture:
    """
    BackgroundTextures are PODs (packet of data) types. They have very little functionality by themselves,
    but are used by Backgrounds. They hold an arcade.gl.Texture and 3 Pyglet.Maths.Mat3s.
    The Mat3s define the scaling, rotation, and translation of the pixel data in the texture.
    see background_fs.glsl in resources/shaders for an implementation of this.
    """

    def __init__(self, texture: gl.Texture,
                 offset: tuple[float, float] = (0.0, 0.0),
                 scale: float = 1.0, angle: float = 0.0):
        self.texture = texture

        self._scale = scale
        self._scale_transform = Mat3().scale(scale, scale)

        self._angle = angle
        self._angle_transform = Mat3().rotate(angle)

        self._offset = offset
        self._offset_transform = Mat3().translate(offset[0], offset[1])

    @property
    def pixel_transform(self):
        return self._offset_transform @ self._angle_transform @ self._scale_transform

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value: float):
        self._scale = value
        self._scale_transform = Mat3().scale(value, value)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value: float):
        self._angle = value
        self._angle_transform = Mat3().rotate(value)

    @property
    def offset(self):
        return self._scale

    @offset.setter
    def offset(self, value: tuple[float, float]):
        self._offset = value
        self._offset_transform = Mat3().translate(-value[0], value[1])

    @property
    def wrap_x(self) -> int:
        """
        Get or set the horizontal wrapping of the texture. This decides how textures
        are read when texture coordinates are outside the ``[0.0, 1.0]`` area.
        Default value is ``REPEAT``.
        Valid options are::
            # Note: Enums can also be accessed in arcade.gl.
            # Repeat pixels on the y-axis.
            texture.wrap_x = ctx.REPEAT
            # Repeat pixels on the y-axis mirrored.
            texture.wrap_x = ctx.MIRRORED_REPEAT
            # Repeat the edge pixels when reading outside the texture.
            texture.wrap_x = ctx.CLAMP_TO_EDGE
            # Use the border color (black by default) when reading outside the texture.
            texture.wrap_x = ctx.CLAMP_TO_BORDER
        :type: int
        """
        return self.texture.wrap_x

    @wrap_x.setter
    def wrap_x(self, value: int):
        self.texture.wrap_x = value

    @property
    def wrap_y(self) -> int:
        """
        Get or set the horizontal wrapping of the texture. This decides how textures
        are read when texture coordinates are outside the ``[0.0, 1.0]`` area.
        Default value is ``REPEAT``.
        Valid options are::
            # Note: Enums can also be accessed in arcade.gl.
            # Repeat pixels on the y-axis.
            texture.wrap_y = ctx.REPEAT
            # Repeat pixels on the y-axis mirrored.
            texture.wrap_y = ctx.MIRRORED_REPEAT
            # Repeat the edge pixels when reading outside the texture.
            texture.wrap_y = ctx.CLAMP_TO_EDGE
            # Use the border color (black by default) when reading outside the texture.
            texture.wrap_y = ctx.CLAMP_TO_BORDER
        :type: int
        """
        return self.texture.wrap_y

    @wrap_y.setter
    def wrap_y(self, value: int):
        self.texture.wrap_y = value

    def use(self, unit: int = 0) -> None:
        """Bind the texture to a channel,
        :param int unit: The texture unit to bind the texture.
        """
        self.texture.use(unit)

    def render_target(self, context: ArcadeContext, color_attachments=None, depth_attachment=None):
        if color_attachments is None:
            color_attachments = []
        return context.framebuffer(color_attachments=[self.texture] + color_attachments,
                                   depth_attachment=depth_attachment)
