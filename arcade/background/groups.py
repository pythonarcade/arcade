from PIL import Image

from arcade.context import ArcadeContext
from arcade.window_commands import get_window
from arcade.resources import resolve_resource_path
import arcade.gl as gl
from pyglet.math import Mat3

from .background.background import Background

class BackgroundGroup:
    """
    If you have many backgrounds which you would like to draw together and move together this can help.
    The pos of the Background Group is independent of each Background pos.
    The offset of the BackgroundGroup is the same as each background.
    """

    def __init__(self):
        self.backgrounds: list[Background] = []

        self._pos = [0, 0]
        self._offset = [0, 0]

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        for background in self.backgrounds:
            background.texture.offset = value

    def add(self, item: Background):
        if item not in self.backgrounds:
            self.backgrounds.append(item)
        else:
            print("WARNING: Background already in group")

    def extend(self, items: list[Background]):
        for item in items:
            self.add(item)

    def draw(self):
        for background in self.backgrounds:
            background.draw(self.pos)

    def add_from_file(self,
                      tex_src: str,
                      pos: tuple[float, float] = (0.0, 0.0),
                      size: tuple[int, int] = None,
                      offset: tuple[float, float] = (0.0, 0.0),
                      scale: float = 1.0,
                      angle: float = 0.0,
                      *,
                      filters=(gl.NEAREST, gl.NEAREST),
                      shader: gl.Program = None,
                      geometry: gl.Geometry = None):
        background = Background.from_file(tex_src, pos, size, offset, scale, angle,
                                          filters=filters, shader=shader, geometry=geometry)
        self.add(background)


class ParallaxGroup:
    """
    The ParallaxBackground holds a list of backgrounds and a list of depths.
    When you change the offset through the ParallaxBackground
    each Background's offset will be set inversely proportional to its depth.
    This creates the effect of Backgrounds with greater depths appearing further away.
    The depth does not affect the positioning of layers at all.
    """

    def __init__(self, backgrounds: list[Background] = None, depths: list[float] = None):
        self.backgrounds: list[Background] = [] if backgrounds is None else backgrounds
        self.depths: list[float] = [] if depths is None else backgrounds

        if len(self.backgrounds) != len(self.depths):
            raise ValueError("The number of backgrounds does not equal the number of depth values")

        self._pos = [0, 0]
        self._offset = [0, 0]

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        for index, background in enumerate(self.backgrounds):
            depth = self.depths[index]
            background.texture.offset = value[0] / depth, value[1] / depth

    def add(self, item: Background, depth: float = 1.0):
        if item not in self.backgrounds:
            self.backgrounds.append(item)
            self.depths.append(depth)
        else:
            print("WARNING: Background already in group")

    def remove(self, item: Background):
        index = self.backgrounds.index(item)
        self.backgrounds.remove(item)
        self.depths.pop(index)

    def change_depth(self, item: Background, new_depth: float):
        self.depths[self.backgrounds.index(item)] = new_depth

    def extend(self, items: list[Background], depths: list[float]):
        for index, item in enumerate(items):
            self.add(item, depths[index])

    def draw(self):
        for background in self.backgrounds:
            background.draw(self.pos)

    def add_from_file(self,
                      tex_src: str,
                      pos: tuple[float, float] = (0.0, 0.0),
                      size: tuple[int, int] = None,
                      depth: float = 1,
                      offset: tuple[float, float] = (0.0, 0.0),
                      scale: float = 1.0,
                      angle: float = 0.0,
                      *,
                      filters=(gl.NEAREST, gl.NEAREST),
                      shader: gl.Program = None,
                      geometry: gl.Geometry = None):
        background = Background.from_file(tex_src, pos, size, offset, scale, angle,
                                          filters=filters, shader=shader, geometry=geometry)
        self.add(background, depth)
