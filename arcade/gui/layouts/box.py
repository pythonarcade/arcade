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
        super().__init__(size_hint=(0.0, 0.0), **kwargs)
        self.align = align
        self.vertical = vertical

    @property
    def min_size(self):
        """
        Calculate min_size: content size + padding
        """
        ebw = self.effective_border_width()

        width = self.padding_horizontal + ebw * 2
        height = self.padding_vertical + ebw * 2

        for element, data in self._elements:
            min_width, min_height = self._min_size_of(element)

            if self.vertical:
                height += element.height
                height += data.get('space', 0)
                width = max(width, min_width + self.padding_horizontal + ebw * 2)
            else:
                width += element.width
                width += data.get('space', 0)
                height = max(height, min_height + self.padding_vertical + ebw * 2)

        return width, height

    def _size_hint_elements(self):
        for element, data in self._elements:
            if getattr(element, 'size_hint', None):
                yield element, element.size_hint

    def _min_size_of(self, element):
        min_size = getattr(element, 'min_size', None)
        return min_size if min_size else (element.width, element.height)

    def place_elements(self):
        # Places elemens next to each other in one direction
        # Algorithm uses self.left/self.top as the start point to place elements
        # 'cursor' marks the next placeable position (relative)

        if len(self) == 0:
            return

        # distribute left space
        # FIXME handle if self is to small
        min_width, min_height = self.min_size
        left_width = self.width - min_width
        left_height = self.height - min_height

        # only if elements provide size_hints
        size_hint_elements = list(self._size_hint_elements())
        if size_hint_elements:
            elements, size_hints = zip(*size_hint_elements)
            hints_x, hints_y = zip(*size_hints)
            hints_x_sum = sum(hints_x)
            hints_y_sum = sum(hints_y)

            # resize elements on primary axis
            if self.vertical:
                factor = left_height / hints_y_sum
                for element, hint in zip(elements, hints_x):
                    min_height = self._min_size_of(element)[1]
                    element.height = int(min_height + factor * hint)
            else:
                factor = left_width / hints_x_sum
                for element, hint in zip(elements, hints_x):
                    min_width = self._min_size_of(element)[0]
                    element.width = int(min_width + factor * hint)

            # resize elements on orthogonal axis
            if self.vertical:
                for element, hint in zip(elements, hints_x):
                    element.width = int(self.width * hint)
            else:
                for element, hint in zip(elements, hints_y):
                    element.height = int(self.height * hint)

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
        ebw = self.effective_border_width()
        cursor = start_x + self.padding_left + ebw, start_y + self.padding_top + ebw

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
