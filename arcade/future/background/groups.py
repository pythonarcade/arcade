import arcade.gl as gl
from arcade.future.background import Background


class BackgroundGroup:
    """
    If you have many backgrounds which you would like to draw together and move
    together this can help.
    The pos of the Background Group is independent of each Background pos.
    The offset of the BackgroundGroup is the same as each background.
    """

    def __init__(self, backgrounds: list[Background] | None = None):
        self._backgrounds: list[Background] = [] if backgrounds is None else backgrounds

        self._pos = (0.0, 0.0)
        self._offset = (0.0, 0.0)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value: tuple[float, float]):
        self._pos = value

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        for background in self._backgrounds:
            background.texture.offset = value

    def __getitem__(self, item: int):
        return self._backgrounds[item]

    def __setitem__(self, key: int, value: Background):
        self._backgrounds[key] = value

    def __iter__(self):
        return iter(self._backgrounds)

    def add(self, item: Background):
        if item not in self._backgrounds:
            self._backgrounds.append(item)
            item.texture.offset = self._offset
        else:
            print("WARNING: Background already in group")

    def extend(self, items: list[Background]):
        for item in items:
            self.add(item)

    def draw(self):
        for background in self._backgrounds:
            background.draw(self.pos)

    def add_from_file(
        self,
        tex_src: str,
        pos: tuple[float, float] = (0.0, 0.0),
        size: tuple[int, int] | None = None,
        offset: tuple[float, float] = (0.0, 0.0),
        scale: float = 1.0,
        angle: float = 0.0,
        *,
        filters=(gl.NEAREST, gl.NEAREST),
        color: tuple[int, int, int] | None = None,
        color_norm: tuple[float, float, float] | None = None,
        shader: gl.Program | None = None,
        geometry: gl.Geometry | None = None,
    ):
        background = Background.from_file(
            tex_src,
            pos,
            size,
            offset,
            scale,
            angle,
            filters=filters,
            color=color,
            color_norm=color_norm,
            shader=shader,
            geometry=geometry,
        )
        self.add(background)


class ParallaxGroup:
    """
    The ParallaxBackground holds a list of backgrounds and a list of depths.
    When you change the offset through the ParallaxBackground
    each Background's offset will be set inversely proportional to its depth.
    This creates the effect of Backgrounds with greater depths appearing further away.
    The depth does not affect the positioning of layers at all.
    """

    def __init__(
        self,
        backgrounds: list[Background] | None = None,
        depths: list[float] | None = None,
    ):
        self._backgrounds: list[Background] = [] if backgrounds is None else backgrounds
        self._depths: list[float] = [] if depths is None else depths

        if len(self._backgrounds) != len(self._depths):
            raise ValueError("The number of backgrounds does not equal the number of depth values")

        self._pos = (0.0, 0.0)
        self._offset = (0.0, 0.0)

    @property
    def pos(self) -> tuple[float, float]:
        return self._pos

    @pos.setter
    def pos(self, value: tuple[float, float]):
        self._pos = value

    @property
    def offset(self) -> tuple[float, float]:
        return self._offset

    @offset.setter
    def offset(self, value: tuple[float, float]):
        self._offset = value
        for index, background in enumerate(self._backgrounds):
            depth = self._depths[index]
            background.texture.offset = value[0] / depth, value[1] / depth

    def __getitem__(self, item: int):
        return self._backgrounds[item], self._depths[item]

    def __setitem__(self, key: int, value: Background | float):
        if isinstance(value, float | int):
            self._depths[key] = value
        else:
            self._backgrounds[key] = value

    def add(self, item: Background, depth: float = 1.0):
        if item not in self._backgrounds:
            self._backgrounds.append(item)
            self._depths.append(depth)
        else:
            print("WARNING: Background already in group")

    def remove(self, item: Background):
        index = self._backgrounds.index(item)
        self._backgrounds.remove(item)
        self._depths.pop(index)

    def change_depth(self, item: Background, new_depth: float):
        self._depths[self._backgrounds.index(item)] = new_depth

    def extend(self, items: list[Background], depths: list[float]):
        for index, item in enumerate(items):
            self.add(item, depths[index])

    def draw(self):
        for background in self._backgrounds:
            background.draw(self.pos)

    def add_from_file(
        self,
        tex_src: str,
        pos: tuple[float, float] = (0.0, 0.0),
        size: tuple[int, int] | None = None,
        depth: float = 1,
        offset: tuple[float, float] = (0.0, 0.0),
        scale: float = 1.0,
        angle: float = 0.0,
        *,
        filters=(gl.NEAREST, gl.NEAREST),
        color: tuple[int, int, int] | None = None,
        color_norm: tuple[float, float, float] | None = None,
        shader: gl.Program | None = None,
        geometry: gl.Geometry | None = None,
    ):
        background = Background.from_file(
            tex_src,
            pos,
            size,
            offset,
            scale,
            angle,
            filters=filters,
            color=color,
            color_norm=color_norm,
            shader=shader,
            geometry=geometry,
        )
        self.add(background, depth)
