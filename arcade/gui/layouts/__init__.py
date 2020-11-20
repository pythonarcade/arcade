from abc import abstractmethod, ABC
from operator import attrgetter
from typing import List, NamedTuple, Union, Dict

from arcade import Sprite, SpriteList
from arcade.gui import UIElement


class PackedElement(NamedTuple):
    element: Union['UIAbstractLayout', Sprite]
    data: Dict


class UIAbstractLayout(ABC):
    def __init__(self,
                 # draw_border=False,
                 id=None,
                 **kwargs):
        super().__init__()
        # self.draw_border = draw_border

        self._elements: List[PackedElement] = []
        self._layer = SpriteList()
        self._child_layouts = []

        # anker for own position
        self._top = 0
        self._left = 0

        self._width = 0
        self._height = 0

        self._id = id

    @property
    def id(self):
        return self._id

    # --------- add element & size hint
    def pack(self, element: Union['UIAbstractLayout', UIElement], **kwargs):
        self._elements.append(PackedElement(element, kwargs))

        if isinstance(element, UIElement):
            self._layer.append(element)
        if isinstance(element, UIAbstractLayout):
            self._child_layouts.append(element)

    def draw(self):
        # TODO fix this!
        # self.draw_border()

        self._layer.draw()
        # self._layer.draw_hit_boxes(arcade.color.LIGHT_RED_OCHRE, 2)
        for child in self._child_layouts:
            child.draw()

    # def draw_border(self):
    #     arcade.draw_lrtb_rectangle_outline(
    #         self.left,
    #         self.right,
    #         self.top,
    #         self.bottom,
    #         arcade.color.LIGHT_RED_OCHRE)

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

    @left.setter
    def left(self, value):
        x_diff = value - self.left
        self.move(x_diff, 0)

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
        return self.left + self.width

    @right.setter
    def right(self, value):
        x_diff = value - self.right
        self.move(x_diff, 0)

    @property
    def bottom(self):
        return self.top - self.height

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

    @abstractmethod
    def place_elements(self):
        raise NotImplementedError()

    def __iter__(self):
        yield from map(attrgetter('element'), self._elements)

    def __len__(self):
        return len(self._elements)
