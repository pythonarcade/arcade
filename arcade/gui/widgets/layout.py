from typing import Iterable, TypeVar

import arcade
from arcade.gui.widgets import UIWidget, UIWrapper, Rect, UILayout

W = TypeVar("W", bound="UIWidget")


class UIAnchorWidget(UIWrapper):
    """
    Widget, which places itself relative to the parent.

    :param child: Child of this wrapper
    :param anchor_x: Which anchor to use for x axis (left, center, right)
    :param align_x: offset for x value (- = left, + = right)
    :param anchor_y: Which anchor to use for y axis (top, center, bottom)
    :param align_y: offset for y value (- = down, + = up)
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(
            self,
            *,
            child: UIWidget,
            anchor_x: str = "center",
            align_x: float = 0,
            anchor_y: str = "center",
            align_y: float = 0,
            **kwargs
    ):
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.align_x = align_x
        self.align_y = align_y
        super().__init__(child=child)

    def do_layout(self):
        # calc rect to place (child width and height + border & padding)
        child_width, child_height = self.child.rect.size
        width = child_width + self.padding_right + self.padding_left + 2 * self.border_width
        height = child_height + self.padding_top + self.padding_bottom + 2 * self.border_width
        rect = Rect(0, 0, width, height)

        # TODO support size_hint_min
        # Handle min size hint (e.g. UIBoxLayout)
        # if hasattr(self.child, "size_hint_min") and self.child.size_hint_min:
        #     print("Size hint min", self.child.size_hint_min)
        #     min_width, min_height = self.child.size_hint_min
        #
        #     current_width, current_height = rect.size
        #     new_width = min_width if min_width > current_width else current_width
        #     new_height = min_height if min_height > current_height else current_height
        #
        #     rect = rect.resize(new_width, new_height)

        # calculate wanted position
        parent_rect = (
            self.parent.rect
            if self.parent
            else Rect(0, 0, *arcade.get_window().get_size())
        )

        anchor_x = "center_x" if self.anchor_x == "center" else self.anchor_x
        own_anchor_x_value = getattr(rect, anchor_x)
        par_anchor_x_value = getattr(parent_rect, anchor_x)
        diff_x = par_anchor_x_value + self.align_x - own_anchor_x_value

        anchor_y = "center_y" if self.anchor_y == "center" else self.anchor_y
        own_anchor_y_value = getattr(rect, anchor_y)
        par_anchor_y_value = getattr(parent_rect, anchor_y)
        diff_y = par_anchor_y_value + self.align_y - own_anchor_y_value

        # check if changes are required
        if diff_x or diff_y or self.rect.size != rect.size:
            # update own rect
            self.rect = rect.move(diff_x, diff_y)

            # set child rect to self.content_rect
            self.child.rect = self.content_rect


class UIBoxLayout(UILayout):
    """
    Places widgets next to each other.
    Depending on the vertical attribute, the Widgets are placed top to bottom or left to right.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param vertical: Layout children vertical (True) or horizontal (False)
    :param align: Align children in orthogonal direction (x: left, center, right / y: top, center, bottom)
    :param children: Initial children, more can be added
    :param size_hint: A hint for :class:`UILayout`, if this :class:`UIWidget` would like to grow
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param space_between: Space between the children
    """

    def __init__(
            self,
            x=0,
            y=0,
            vertical=True,
            align="center",
            children: Iterable[UIWidget] = tuple(),
            size_hint=None,
            size_hint_min=None,
            size_hint_max=None,
            space_between=0,
            style=None,
            **kwargs
    ):
        self.align = align
        self.vertical = vertical
        self._space_between = space_between
        super().__init__(
            x=x,
            y=y,
            width=0,
            height=0,
            children=children,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=style,
            **kwargs
        )

    def add(self, child: W, **kwargs) -> W:
        add = super().add(child, **kwargs)
        self.update_size_hints()
        return add

    def update_size_hints(self):
        required_space_between = max(0, len(self.children) - 1) * self._space_between

        if self.vertical:
            width = max(child.width for child in self.children)
            height_of_children = sum(child.height for child in self.children)
            height = height_of_children + required_space_between
        else:
            width_of_children = sum(child.width for child in self.children)
            width = width_of_children + required_space_between
            height = max(child.height for child in self.children)

        base_width = self.padding_left + self.padding_right + 2 * self.border_width
        base_height = self.padding_top + self.padding_bottom + 2 * self.border_width
        self.size_hint_min = base_width + width, base_height + height

    def do_layout(self):
        # TODO Provide required size information before -> size_hint_min
        # FIXME react can not be modified!

        base_width = self.padding_left + self.padding_right + 2 * self.border_width
        base_height = self.padding_top + self.padding_bottom + 2 * self.border_width

        initial_top = self.content_rect.top
        start_y = self.content_rect.top
        start_x = self.content_rect.left

        if not self.children:
            base_width = self.padding_left + self.padding_right + 2 * self.border_width
            base_height = self.padding_top + self.padding_bottom + 2 * self.border_width
            self.rect = Rect(self.left, self.right, base_width, base_height)
            return

        required_space_between = max(0, len(self.children) - 1) * self._space_between

        if self.vertical:
            new_height = (
                    sum(child.height for child in self.children) + required_space_between
            )
            new_width = max(child.width for child in self.children)
            center_x = start_x + new_width // 2
            for child in self.children:
                if self.align == "left":
                    new_rect = child.rect.align_left(start_x)
                elif self.align == "right":
                    new_rect = child.rect.align_right(start_x + new_width)
                else:
                    new_rect = child.rect.align_center_x(center_x)

                new_rect = new_rect.align_top(start_y)
                if new_rect != child.rect:
                    child.rect = new_rect
                start_y -= child.height
                start_y -= self._space_between
        else:
            new_height = max(child.height for child in self.children)
            new_width = (
                    sum(child.width for child in self.children) + required_space_between
            )
            center_y = start_y - new_height // 2

            for child in self.children:
                if self.align == "top":
                    new_rect = child.rect.align_top(start_y)
                elif self.align == "bottom":
                    new_rect = child.rect.align_bottom(start_y - new_height)
                else:
                    new_rect = child.rect.align_center_y(center_y)

                new_rect = new_rect.align_left(start_x)
                if new_rect != child.rect:
                    child.rect = new_rect
                start_x += child.width
                start_x += self._space_between

        self.rect = Rect(self.left, self.bottom, base_width + new_width, base_height + new_height).align_top(
            initial_top
        )


class UIGridLayout(UILayout):
    """
    Places widget in a grid layout.
    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param float align_horizontal: Align children in orthogonal direction (x: left, center, right)
    :param float align_vertical: Align children in orthogonal direction (y: top, center, bottom)
    :param Iterable[UIWidget] children: Initial children, more can be added
    :param size_hint: A hint for :class:`UILayout`, if this :class:`UIWidget` would like to grow
    :param size_hint_min: Min width and height in pixel
    :param size_hint_max: Max width and height in pixel
    :param horizontal_spacing: Space between columns
    :param vertical_spacing: Space between rows
    :param int column_count: Number of columns in the grid, can be changed
    :param int row_count: Number of rows in the grid, can be changed
    """
    def __init__(self, x=0,
                 y=0,
                 align_horizontal="center",
                 align_vertical="center",
                 children: Iterable[UIWidget] = tuple(),
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 horizontal_spacing: int = 0,
                 vertical_spacing: int = 0,
                 column_count: int = 1,
                 row_count: int = 1, style=None, **kwargs):

        super(UIGridLayout, self).__init__(x=x, y=y, width=0, height=0, children=children,
                                           size_hint=size_hint, size_hint_min=size_hint_min,
                                           size_hint_max=size_hint_max, style=style, **kwargs)

        self._horizontal_spacing = horizontal_spacing
        self._vertical_spacing = vertical_spacing

        self._child_dict = {}

        self.column_count = column_count
        self.row_count = row_count

        self.align_horizontal = align_horizontal
        self.align_vertical = align_vertical

    def add_widget(self, child: "UIWidget", col_num: int, row_num: int) -> "UIWidget":
        """
        Adds widgets in the grid.
        :param UIWidget child: The widget which is to be addded in the grid
        :param int col_num: The column number in which the widget is to be added (first column is numbered 0)
        :param int row_num: The row number in which the widget is to be added (first row is numbered 0)
        """
        self._child_dict[child] = (col_num, row_num)
        super(UILayout, self).add(child)

    def do_layout(self):
        initial_top = self.top
        initial_left_x = self.left
        start_y = self.top

        if not self._child_dict:
            self.rect = Rect(self.left, self.bottom, 0, 0)
            return

        max_width_per_column = [0 for _ in range(self.column_count)]
        max_height_per_row = [0 for _ in range(self.row_count)]

        child_sorted_row_wise = [[] for _ in range(self.row_count)]

        for child, (col_num, row_num) in self._child_dict.items():

            if child.width > max_width_per_column[col_num]:
                max_width_per_column[col_num] = child.width

            if child.height > max_height_per_row[row_num]:
                max_height_per_row[row_num] = child.height

            child_sorted_row_wise[row_num].append(child)

        # row wise rendering children
        new_height = sum(max_height_per_row) + (self.row_count - 1) * self._vertical_spacing
        new_width = sum(max_width_per_column) + (self.column_count - 1) * self._horizontal_spacing

        for row_num, row in enumerate(child_sorted_row_wise):
            max_height = max_height_per_row[row_num] + self._vertical_spacing
            center_y = start_y - (max_height // 2)

            start_x = initial_left_x

            for col_num, child in enumerate(row):
                max_width = max_width_per_column[col_num] + self._horizontal_spacing
                center_x = start_x + max_width // 2

                if self.align_vertical == "top":
                    new_rect = child.rect.align_top(start_y)
                elif self.align_vertical == "bottom":
                    new_rect = child.rect.align_bottom(start_y - max_height)
                else:
                    new_rect = child.rect.align_center_y(center_y)

                if self.align_horizontal == "left":
                    new_rect = new_rect.align_left(start_x)
                elif self.align_horizontal == "right":
                    new_rect = new_rect.align_right(start_x + max_width)
                else:
                    new_rect = new_rect.align_center_x(center_x)

                if new_rect != child.rect:
                    child.rect = new_rect
                start_x += max_width

            start_y -= max_height

        self.rect = Rect(self.left, initial_top - new_height, new_width, new_height).align_top(initial_top)
