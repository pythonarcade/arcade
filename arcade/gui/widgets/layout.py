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
