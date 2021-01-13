from abc import abstractmethod, ABC
from operator import attrgetter
from pathlib import Path
from typing import List, NamedTuple, Union, Dict, Optional, Tuple

import PIL

from arcade import Sprite, SpriteList, get_sprites_at_point, Color, Texture
from arcade.gui import UIElement, UIEvent
from arcade.resources import resolve_resource_path


class PackedElement(NamedTuple):
    element: Union['UIAbstractLayout', Sprite]
    data: Dict


padding = Union[
    int,
    Tuple[int, int],
    Tuple[int, int, int, int]
]


class UIAbstractLayout(ABC):
    def __init__(self,
                 id=None,
                 bg: Union[Color, str, Path] = None,
                 border_color: Optional[Color] = None,
                 border_width: int = 2,
                 padding: padding = 0,
                 **kwargs):
        """

        :param id: id of the
        :param bg:
        :param border_color:
        :param border_width:
        :param kwargs:
        """
        super().__init__()
        # self.draw_border = draw_border

        self._elements: List[PackedElement] = []
        self._layer = SpriteList()
        self._child_layouts: List[UIAbstractLayout] = []

        # anker for own position
        self._top = 0
        self._left = 0

        self._padding = padding

        self._width = self.padding_horizontal
        self._height = self.padding_vertical

        self._id = id

        self._border_color = border_color
        self._border_width = border_width
        self._bg_sprite: Optional[Sprite] = None

        self._bg = bg
        self.refresh_bg()

    def _create_bg_sprite(self, bg):

        # calc size containing padding
        h_padding = self.padding_left + self.padding_right
        v_padding = self.padding_top + self.padding_bottom
        size = (self._width + v_padding, self._height + h_padding)

        if isinstance(bg, Path) or isinstance(bg, str):
            image_path = resolve_resource_path(bg)
            bg_image = PIL.Image.open(image_path)
            bg_image = bg_image.resize(size)
        else:
            # bg should be a color, so we will create a bg image
            bg_image = PIL.Image.new('RGBA', size, bg)

        return bg_image

    def refresh_bg(self):
        # if bg and border not set, we skip the bg_sprite
        if self._bg is None and self._border_color is None:
            self._bg_sprite = None
            return

        bg = self._bg if self._bg else (255, 0, 0, 0)

        # recreate bg
        bg_image = self._create_bg_sprite(bg)

        # apply border
        if self._border_color:
            bg_image = PIL.ImageOps.expand(
                bg_image,
                border=self._border_width,
                fill=self._border_color
            )

        self._bg_sprite = Sprite()
        self._bg_sprite.texture = Texture(f"BG", bg_image, hit_box_algorithm='None')

        off_y = (self.padding_top - self.padding_bottom) // 2
        off_x = (self.padding_right - self.padding_left) // 2
        self._bg_sprite.position = self.center_x + off_x, self.center_y + off_y

    @property
    def id(self):
        return self._id

    def on_ui_event(self, event: UIEvent):
        for element in self:
            if hasattr(element, 'on_ui_event'):
                element.on_ui_event(event)

    def get_elements_at(self, pos) -> List[Union[Sprite]]:
        """
        Search for Sprites containing given position
        :param pos: x, y position
        :return: List of elements in draw order
        """
        elements_at_pos = get_sprites_at_point(pos, self._layer)

        for layout in self._child_layouts:
            elements_at_pos.extend(layout.get_elements_at(pos))

        return elements_at_pos

    # --------- add element & size hint
    def pack(self, element: Union[Sprite, UIElement, 'UIAbstractLayout'], **kwargs):
        self._elements.append(PackedElement(element, kwargs))

        if isinstance(element, Sprite):
            self._layer.append(element)
        if isinstance(element, UIAbstractLayout):
            self._child_layouts.append(element)

    def draw(self):
        if self._bg_sprite:
            self._bg_sprite.draw()

        self._layer.draw()
        for child in self._child_layouts:
            child.draw()

    # padding values
    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, value: padding):
        self._padding = value
        self.refresh()

    @property
    def padding_top(self):
        if isinstance(self._padding, int):
            return self._padding
        if len(self._padding) == 2:
            return self._padding[0]
        elif len(self._padding) == 4:
            return self._padding[0]
        return 0

    @property
    def padding_right(self):
        if isinstance(self._padding, int):
            return self._padding
        if len(self._padding) == 2:
            return self._padding[1]
        elif len(self._padding) == 4:
            return self._padding[1]
        return 0

    @property
    def padding_bottom(self):
        if isinstance(self._padding, int):
            return self._padding
        if len(self._padding) == 2:
            return self._padding[0]
        elif len(self._padding) == 4:
            return self._padding[2]
        return 0

    @property
    def padding_left(self):
        if isinstance(self._padding, int):
            return self._padding
        if len(self._padding) == 2:
            return self._padding[1]
        elif len(self._padding) == 4:
            return self._padding[3]
        return 0

    @property
    def padding_vertical(self):
        return self.padding_top + self.padding_bottom

    @property
    def padding_horizontal(self):
        return self.padding_right + self.padding_left

    # --------- position - fixed
    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, value):
        y_diff = value - self.top
        self.move(0, y_diff)

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        self._left = value

    # @left.setter
    # def left(self, value):
    #     x_diff = value - self.left
    #     self.move(x_diff, 0)

    @property
    def width(self):
        """ minimal width """
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        """ minimal height """
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    # --------- position - calc
    @property
    def right(self):
        return self.left + self.width + self.padding_horizontal

    @right.setter
    def right(self, value):
        x_diff = value - self.right
        self.move(x_diff, 0)

    @property
    def bottom(self):
        return self.top - self.height - self.padding_vertical

    @bottom.setter
    def bottom(self, value):
        y_diff = value - self.bottom
        self.move(0, y_diff)

    @property
    def center_x(self):
        return self.left + (self.right - self.left) // 2

    @center_x.setter
    def center_x(self, value):
        x_diff = value - self.center_x
        self.move(x_diff, 0)

    @property
    def center_y(self):
        return self.bottom + (self.top - self.bottom) // 2

    @center_y.setter
    def center_y(self, value):
        y_diff = value - self.center_y
        self.move(0, y_diff)

    def move(self, x, y):
        self._top += y
        self._left += x

        for element, data in self._elements:
            element.top += y
            element.left += x

    # ---------- placement and refresh
    def refresh(self):
        for element in self:
            if isinstance(element, UIAbstractLayout):
                element.refresh()
        self.place_elements()

        self.refresh_bg()

    @abstractmethod
    def place_elements(self):
        raise NotImplementedError()

    def __iter__(self):
        yield from map(attrgetter('element'), self._elements)

    def __len__(self):
        return len(self._elements)
