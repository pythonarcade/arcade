from array import array

import arcade
import arcade.gl as gl


class NinePatchRenderer:
    """A 9-patch renderer which take a specific texture and two pixel coordinates.
    using these coordinates the texture is split into 9 'patches'.
    each patch is then stretched in specifc ways to keep the edges a specific width/height.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of 9-patch
    :param height: height of 9-patch
    :param start: start coordinate of patch slices
    :param end: end coordinate of patch slices
    :param texture: the texture used for the 9-patch
    :param atlas: the atlas which the texture belongs to (defaults to arcades default atlas)
    """

    def __init__(self, x, y, width, height, start, end, texture, atlas=None):
        ctx = arcade.get_window()

        # ModernGl components for rendering
        self.program = ctx.load_program(vertex_shader=":resources:shaders/gui/nine_patch_vs.glsl",
                                        fragment_shader=":resources:shaders/gui/nine_patch_fs.glsl")

        self.program['uv_texture'] = 0
        self.program['sprite_texture'] = 1

        data = array('f', [0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0])
        self.geometry = ctx.geometry([gl.BufferDescription(ctx.Buffer(data=data), '2f', ['in_uv'])],
                                     mode=ctx.TRIANGLE_STRIP)

        # References for the texture
        self._atlas = ctx.default_atlas if atlas is None else atlas
        if not self._atlas.has_texture(texture) and atlas is not None:
            print("WARNING: given atlas does not contain given texture. "
                  "Adding texture to atlas")
            self._atlas.add(texture)
        self._texture = texture

        self.program['texture_id'] = self._atlas.get_texture_id(self._texture.name)

        # Bottom left position.
        self._x = x
        self._y = y

        # Size, edge inclusive.
        self._width = width
        self._height = height

        self.program['patch_data'] = x, y, width, height

        # pixel texture co-ordinate start and end of central box.
        self._start = start
        self._end = end

        # relative UV texture co-ordinate of end from opposite end
        self._end_diff = self._end[0] - texture.width, self._end[1] - texture.height

        # texture UV co-ordinate of start and end.
        self.program['base_uv'] = (start[0] / texture.width, start[1] / texture.height,
                                   end[0] / texture.width, end[1] / texture.height)

        self.program['var_UV'] = (self._start[0] / width, self._start[1] / height,
                                  1 + (self._end_diff[0] / width), 1 + (self._end_diff[1] / height))

        self._patch_data_changed = False

    def adjust_all(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.width = height
        self._patch_data_changed = True

    def draw(self):
        if self._patch_data_changed:
            self._patch_data_changed = False
            self.program['patch_data'] = self._x, self._y, self._width, self._height
            self.program['var_uv'] = (self._start[0] / self._width, self._start[1] / self._height,
                                      1 + (self._end_diff[0] / self._width), 1 + (self._end_diff[1] / self._height))

        self._atlas.use_uv_texture(0)
        self._atlas.texture.use(1)
        self.geometry.render(self.program)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._patch_data_changed = True

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._patch_data_changed = True

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value >= self._start[0] + self._end[0] + 1:
            self._width = value
        else:
            print(f"WARNING: Attempted to set the width too low. "
                  f"Width has been set to minimum of {self._start[0] + self._end[0] + 1}")
            self._width = self._start[0] + self._end[0] + 1
        self._patch_data_changed = True

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value >= self._start[1] + self._end[1] + 1:
            self._height = value
        else:
            print(f"WARNING: Attempted to set the height too low. "
                  f"Height has been set to minimum of {self._start[1] + self._end[1] + 1}")
            self._height = self._start[1] + self._end[1] + 1
        self._patch_data_changed = True
