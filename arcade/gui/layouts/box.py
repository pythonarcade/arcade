from operator import attrgetter
from typing import Union

from arcade import Sprite
from arcade.gui import UIElement
from arcade.gui.layouts import UIAbstractLayout


class UIBoxLayout(UIAbstractLayout):
    def __init__(
            self,
            vertical=True,
            align='left',
            **kwargs
    ):
        """

        :param vertical:
        :param align: top|start|left|center|bottom|end|right
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.align = align
        self.vertical = vertical

    def pack(self, element: Union[Sprite, UIElement, 'UIAbstractLayout'], **kwargs):
        super().pack(element, **kwargs)

        # TODO this change could be reflected in sizehint not in actual changed properties
        space = kwargs.get('space', 0)
        if self.vertical:
            self.width = max(map(attrgetter('width'), self)) + self.padding_horizontal
            self.height += element.height + space
        else:
            self.height = max(map(attrgetter('height'), self)) + self.padding_vertical
            self.width += element.width + space

    def place_elements(self):
        # Places elemens next to each other in one direction
        # Algorithm uses self.left/self.top as the start point to place elements
        # 'cursor' marks the next placeable position (relative)

        # get min size and calc alignment offsets
        min_width, min_height = self.min_size()

        start_x = 0
        start_y = 0

        if self.vertical:
            if self.align in ('top', 'start', 'left'):
                pass
            elif self.align in ('center',):
                start_y = (self.height - min_height) // 2
            elif self.align in ('bottom', 'end', 'right'):
                start_y = (self.height - min_height)
        else:  # horizontal
            start_y = (self.height - min_height)

            if self.align in ('top', 'start', 'left'):
                pass
            elif self.align in ('center',):
                start_x = (self.width - min_width) // 2
            elif self.align in ('bottom', 'end', 'right'):
                start_x = (self.width - min_width)

        # cursor: placeable position relative to self.left, self.top
        cursor = start_x + self.padding_left, start_y + self.padding_top

        # place elements
        for element, data in self._elements:
            cx, cy = cursor
            space = data.get('space', 0)

            # update cursor
            if self.vertical:
                cy += space
                cursor = cx, cy + element.height
            else:
                cx += space
                cursor = cx + element.width, cy

            # place element, invert bottom-top direction of arcade/OpenGL
            element.left = self.left + cx
            element.top = self.top - cy

    def min_size(self):
        width = self.padding_horizontal
        height = self.padding_vertical
        for element, data in self._elements:

            if self.vertical:
                height += element.height
                height += data.get('space', 0)
                width = max(width, element.width + self.padding_horizontal)
            else:
                width += element.width
                width += data.get('space', 0)
                height = max(height, element.height + self.padding_vertical)

        return width, height

#
# class UIVerticalLayout(UIBoxLayout):
#     def __init__(
#             self,
#             **kwargs
#     ) -> None:
#         super().__init__(vertical=True, **kwargs)
#
#
# class UIHorizontalLayout(UIBoxLayout):
#     def __init__(
#             self,
#             **kwargs
#     ) -> None:
#         super().__init__(vertical=False, **kwargs)
