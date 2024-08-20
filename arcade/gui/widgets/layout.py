from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, TypeVar, cast, List

from typing_extensions import override, Literal

from arcade.gui.property import bind, unbind
from arcade.gui.widgets import UILayout, UIWidget

__all__ = ["UILayout", "UIAnchorLayout", "UIBoxLayout", "UIGridLayout"]

W = TypeVar("W", bound="UIWidget")


class UIAnchorLayout(UILayout):
    """Places children based on anchor values.

    Defaults to ``size_hint = (1, 1)``.

    Supports the options ``size_hint``, ``size_hint_min``, and
    ``size_hint_max``. Children are allowed to overlap.

    Child are resized based on ``size_hint``. ``size_hint_min/max`` only take effect
    if a ``size_hint`` is set.

    Allowed keyword options for
    :py:meth:`~arcade.gui.UIAnchorLayout.add`:

    - ``anchor_x``: ``str`` = ``None``

      Horizontal anchor position for the layout. The class constant
      :py:attr:`~arcade.gui.UIAnchorLayout.default_anchor_x` is used as
      default.

    - ``anchor_y``: ``str`` = ``None``

      Vertical anchor position for the layout. The class constant
      :py:attr:`~arcade.gui.UIAnchorLayout.default_anchor_y` is used as
      default.

    - ``align_x``: ``float`` = 0

      Horizontal alignment for the layout.

    - ``align_y``: ``float`` = 0

      Vertical alignement for the layout.

    Args:
        x: ``x`` coordinate of the bottom left corner.
        y: ``y`` coordinate of the bottom left corner.
        width: Width of the layout.
        height: Height of the layout.
        children: Initial list of children. More can be added later.
        size_hint: Size hint for :py:class:`~arcade.gui.UILayout`
        size_hint_min: Minimum width and height in pixels.
        size_hint_max: Maximum width and height in pixels.
        **kwargs: Additional keyword arguments passed to UILayout.
    """

    default_anchor_x = "center"
    default_anchor_y = "center"

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 1,
        height: float = 1,
        children: Iterable["UIWidget"] = tuple(),
        size_hint=(1, 1),
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            children=children,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )

    def do_layout(self):
        """Executes the layout algorithm.

        Children are placed based on their anchor values."""
        for child, data in self._children:
            self._place_child(child, **data)

    def add(
        self,
        child: W,
        *,
        anchor_x: Optional[str] = None,
        align_x: float = 0,
        anchor_y: Optional[str] = None,
        align_y: float = 0,
        **kwargs,
    ) -> W:
        """Add a widget to the layout as a child. Added widgets will receive
        all user-interface events and be rendered.

        By default, the latest added widget will receive events first and will
        be rendered on top of others. The widgets will be automatically placed
        within this widget.

        Args:
            child: Specified child widget to add.
            anchor_x: Horizontal anchor. Valid options are ``left``,
                ``right``, and ``center``.
            align_x: Offset or padding for the horizontal anchor.
            anchor_y: Vertical anchor. Valid options are ``top``,
                ``center``, and ``bottom``.
            align_y: Offset or padding for the vertical anchor.

        Returns:
            Given child that was just added to the layout.
        """
        return super().add(
            child=child,
            anchor_x=anchor_x,
            align_x=align_x,
            anchor_y=anchor_y,
            align_y=align_y,
            **kwargs,
        )

    def _place_child(
        self,
        child: UIWidget,
        anchor_x: Optional[str] = None,
        align_x: float = 0,
        anchor_y: Optional[str] = None,
        align_y: float = 0,
    ):
        anchor_x = anchor_x or self.default_anchor_x
        anchor_y = anchor_y or self.default_anchor_y

        # Handle size_hints
        new_child_rect = child.rect

        sh_w, sh_h = child.size_hint or (None, None)
        shmn_w, shmn_h = child.size_hint_min or (None, None)
        shmx_w, shmx_h = child.size_hint_max or (None, None)

        if sh_w is not None:
            new_child_rect = new_child_rect.resize(width=self.content_width * sh_w)

            if shmn_w:
                new_child_rect = new_child_rect.min_size(width=shmn_w)
            if shmx_w:
                new_child_rect = new_child_rect.max_size(width=shmx_w)

        if sh_h is not None:
            new_child_rect = new_child_rect.resize(height=self.content_height * sh_h)

            if shmn_h:
                new_child_rect = new_child_rect.min_size(height=shmn_h)
            if shmx_h:
                new_child_rect = new_child_rect.max_size(height=shmx_h)

        # Calculate position
        content_rect = self.content_rect

        anchor_x = "center_x" if anchor_x == "center" else anchor_x
        child_anchor_x_value = getattr(new_child_rect, anchor_x)
        own_anchor_x_value = getattr(content_rect, anchor_x)
        diff_x = own_anchor_x_value + align_x - child_anchor_x_value

        anchor_y = "center_y" if anchor_y == "center" else anchor_y
        child_anchor_y_value = getattr(new_child_rect, anchor_y)
        own_anchor_y_value = getattr(content_rect, anchor_y)
        diff_y = own_anchor_y_value + align_y - child_anchor_y_value

        # Check if changes are required
        if diff_x or diff_y or child.rect != new_child_rect:
            child.rect = new_child_rect.move(diff_x, diff_y)


class UIBoxLayout(UILayout):
    """Place widgets next to each other. Depending on the
    :py:class:`~arcade.gui.UIBoxLayout.vertical` attribute, the widgets are
    placed top to bottom or left to right.

    .. hint::

        :py:class:`~arcade.gui.UIBoxLayout` does not adjust its
        own size if children are added. This requires a
        :py:class:`~arcade.gui.UIManager` or a
        :py:class:`~arcade.gui.UIAnchorLayout` as a parent.

        Or use :py:meth:`arcade.gui.UIBoxLayout.fit_content` to resize the layout. The
        bottom-left corner is used as the default anchor point.

    Supports the options: ``size_hint``, ``size_hint_min``, ``size_hint_max``. ``size_hint_min``
    is automatically updated based on the minimal required space by children.

    If a child widget provides a ``size_hint`` for a dimension, the child will
    be resized within the given range of ``size_hint_min`` and
    ``size_hint_max`` (unrestricted if not given). If the parameter
    ``vertical`` is True, any available space (``layout size - min_size`` of
    children) will be distributed to the child widgets based on their
    ``size_hint``.

    Args:
        x: ``x`` coordinate of the bottom left corner.
        y: ``y`` coordinate of the bottom left corner.
        vertical: Layout children vertical (True) or horizontal (False).
        align: Align children in orthogonal direction:: - ``x``:
            ``left``, ``center``, and ``right`` - ``y``: ``top``,
            ``center``, and ``bottom``
        children: Initial list of children. More can be added later.
        size_hint: Size hint for the :py:class:`~arcade.gui.UILayout` if
            the widget would like to grow. Defaults to ``0, 0`` ->
            minimal size to contain children.
        size_hint_max: Maximum width and height in pixels.
        space_between: Space in pixels between the children.
    """

    def __init__(
        self,
        *,
        x=0,
        y=0,
        width=1,
        height=1,
        vertical=True,
        align="center",
        children: Iterable[UIWidget] = tuple(),
        size_hint=(0, 0),
        size_hint_max=None,
        space_between=0,
        style=None,
        **kwargs,
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            children=children,
            size_hint=size_hint,
            size_hint_max=size_hint_max,
            style=style,
            **kwargs,
        )

        self.align = align
        self.vertical = vertical
        self._space_between = space_between

        self._size_hint_requires_update = True

        bind(self, "_children", self._update_size_hints)
        bind(self, "_border_width", self._update_size_hints)

        bind(self, "_padding_left", self._update_size_hints)
        bind(self, "_padding_right", self._update_size_hints)
        bind(self, "_padding_top", self._update_size_hints)
        bind(self, "_padding_bottom", self._update_size_hints)

        self._update_size_hints()

    @override
    def add(self, child: W, **kwargs) -> W:
        """Add a widget to this layout

        Args:
            child: The widget to add to the layout.
        """
        # subscribe to child's changes, which might affect the own size hint
        bind(child, "_children", self._trigger_size_hint_update)
        bind(child, "rect", self._trigger_size_hint_update)
        bind(child, "size_hint", self._trigger_size_hint_update)
        bind(child, "size_hint_min", self._trigger_size_hint_update)
        bind(child, "size_hint_max", self._trigger_size_hint_update)

        return super().add(child, **kwargs)

    @override
    def remove(self, child: "UIWidget"):
        """Remove a child from the layout."""
        # unsubscribe from child's changes
        unbind(child, "_children", self._trigger_size_hint_update)
        unbind(child, "rect", self._trigger_size_hint_update)
        unbind(child, "size_hint", self._trigger_size_hint_update)
        unbind(child, "size_hint_min", self._trigger_size_hint_update)
        unbind(child, "size_hint_max", self._trigger_size_hint_update)

        return super().remove(child)

    def _trigger_size_hint_update(self):
        self._size_hint_requires_update = True

    def _update_size_hints(self):
        self._size_hint_requires_update = False

        required_space_between = max(0, len(self.children) - 1) * self._space_between
        min_child_sizes = [UILayout.min_size_of(child) for child in self.children]

        if len(self.children) == 0:
            width = 0
            height = 0
        elif self.vertical:
            width = max(size[0] for size in min_child_sizes)
            height_of_children = sum(size[1] for size in min_child_sizes)
            height = height_of_children + required_space_between
        else:
            width_of_children = sum(size[0] for size in min_child_sizes)
            width = width_of_children + required_space_between
            height = max(size[1] for size in min_child_sizes)

        base_width = self._padding_left + self._padding_right + 2 * self._border_width
        base_height = self._padding_top + self._padding_bottom + 2 * self._border_width
        self.size_hint_min = base_width + width, base_height + height

    def fit_content(self):
        """Resize the layout to fit the content.
        This will take the minimal required size into account."""
        self._update_size_hints()
        self.rect = self.rect.resize(self.size_hint_min[0], self.size_hint_min[1])

    def prepare_layout(self):
        """Updates the size hints if required."""
        super().prepare_layout()

        if self._size_hint_requires_update:
            self._update_size_hints()

    def do_layout(self):
        """Executes the layout algorithm.

        This method is called by the parent layout to place the children, after the rect was set.

        The layout algorithm will place the children based on the size hints next to each other.
        Depending on the vertical attribute, the children are placed top to bottom or left to right.
        """
        start_y = self.content_rect.top
        start_x = self.content_rect.left

        if not self.children:
            return

        # main axis
        constraints = [
            _C.from_widget_height(child) if self.vertical else _C.from_widget_width(child)
            for child, _ in self._children
        ]

        available_space = (
            self.content_height if self.vertical else self.content_width
        ) - self._space_between * (len(self.children) - 1)
        main_sizes = _box_axis_algorithm(constraints, available_space)

        # orthogonal axis
        constraints = [
            _C.from_widget_width(child) if self.vertical else _C.from_widget_height(child)
            for child, _ in self._children
        ]
        orthogonal_sizes = _box_orthogonal_algorithm(
            constraints, self.content_width if self.vertical else self.content_height
        )

        for (child, data), main_size, ortho_size in zip(
            self._children, main_sizes, orthogonal_sizes
        ):
            new_rect = child.rect.resize(
                height=main_size if self.vertical else ortho_size,
                width=ortho_size if self.vertical else main_size,
            )
            new_rect = (
                new_rect.align_x(start_x + self.content_width / 2)
                if self.vertical
                else new_rect.align_y(start_y - self.content_height // 2)
            )

            # align on main and orthogonal axis and update start position
            if self.vertical:
                if self.align == "left":
                    new_rect = new_rect.align_left(start_x)
                elif self.align == "right":
                    new_rect = new_rect.align_right(start_x + self.content_width)
                else:
                    center_x = start_x + self.content_width // 2
                    new_rect = new_rect.align_x(center_x)
                new_rect = new_rect.align_top(start_y)
                start_y -= main_size + self._space_between
            else:
                if self.align == "top":
                    new_rect = new_rect.align_top(start_y)
                elif self.align == "bottom":
                    new_rect = new_rect.align_bottom(start_y - self.content_height)
                else:
                    center_y = start_y - self.content_height // 2
                    new_rect = new_rect.align_y(center_y)
                new_rect = new_rect.align_left(start_x)
                start_x += main_size + self._space_between

            # update child rect
            child.rect = new_rect


class UIGridLayout(UILayout):
    """Place widgets in a grid layout. This is similar to tkinter's ``grid``
    layout geometry manager.

    Defaults to ``size_hint = (0, 0)``.

    Supports the options ``size_hint``, ``size_hint_min``, and
    ``size_hint_max``.

    Children are resized based on ``size_hint``. Maximum and minimum
    ``size_hint``s only take effect if a ``size_hint`` is given. ``size_hint_min`` is automatically
    updated based on the minimal required space by children.

    Args:
        x: ``x`` coordinate of bottom left corner.
        y: ``y`` coordinate of bottom left corner.
        align_horizontal: Align children in orthogonal direction.
            Options include ``left``, ``center``, and ``right``.
        align_vertical: Align children in orthogonal direction. Options
            include ``top``, ``center``, and ``bottom``.
        children: Initial list of children. More can be added later.
        size_hint: A size hint for :py:class:`~arcade.gui.UILayout`, if
            the :py:class:`~arcade.gui.UIWidget` would like to grow.
        size_hint_max: Maximum width and height in pixels.
        horizontal_spacing: Space between columns.
        vertical_spacing: Space between rows.
        column_count: Number of columns in the grid. This can be changed
            later.
        row_count: Number of rows in the grid. This can be changed
            later.
    """

    def __init__(
        self,
        *,
        x=0,
        y=0,
        align_horizontal="center",
        align_vertical="center",
        children: Iterable[UIWidget] = tuple(),
        size_hint=(0, 0),
        size_hint_max=None,
        horizontal_spacing: int = 0,
        vertical_spacing: int = 0,
        column_count: int = 1,
        row_count: int = 1,
        **kwargs,
    ):
        super(UIGridLayout, self).__init__(
            x=x,
            y=y,
            width=1,
            height=1,
            children=children,
            size_hint=size_hint,
            size_hint_max=size_hint_max,
            **kwargs,
        )
        self._size_hint_requires_update = True
        self._horizontal_spacing = horizontal_spacing
        self._vertical_spacing = vertical_spacing

        self.column_count = column_count
        self.row_count = row_count

        self.align_horizontal = align_horizontal
        self.align_vertical = align_vertical

        bind(self, "_children", self._update_size_hints)
        bind(self, "_border_width", self._update_size_hints)

        bind(self, "_padding_left", self._update_size_hints)
        bind(self, "_padding_right", self._update_size_hints)
        bind(self, "_padding_top", self._update_size_hints)
        bind(self, "_padding_bottom", self._update_size_hints)

        # initially update size hints
        self._update_size_hints()

    def add(
        self,
        child: W,
        column: int = 0,
        row: int = 0,
        column_span: int = 1,
        row_span: int = 1,
        **kwargs,
    ) -> W:
        """Add a widget to the grid layout.

        Args:
            child: Specified widget to add as a child of the layout.
            column: Column index in which the widget is to be added.
                The first column at the left of the widget starts at 0.
            row: The row number in which the widget is to be added.
                The first row at the top of the layout is numbered 0.
            column_span: Number of columns the widget will stretch for.
            row_span: Number of rows the widget will stretch for.
        """
        # subscribe to child's changes, which might affect the own size hint
        bind(child, "_children", self._trigger_size_hint_update)
        bind(child, "rect", self._trigger_size_hint_update)
        bind(child, "size_hint", self._trigger_size_hint_update)
        bind(child, "size_hint_min", self._trigger_size_hint_update)
        bind(child, "size_hint_max", self._trigger_size_hint_update)

        return super().add(
            child,
            column=column,
            row=row,
            column_span=column_span,
            row_span=row_span,
            **kwargs,
        )

    def remove(self, child: "UIWidget"):
        """Remove a child from the layout."""
        # unsubscribe from child's changes
        unbind(child, "_children", self._trigger_size_hint_update)
        unbind(child, "rect", self._trigger_size_hint_update)
        unbind(child, "size_hint", self._trigger_size_hint_update)
        unbind(child, "size_hint_min", self._trigger_size_hint_update)
        unbind(child, "size_hint_max", self._trigger_size_hint_update)

        return super().remove(child)

    def _trigger_size_hint_update(self):
        self._size_hint_requires_update = True

    def prepare_layout(self):
        """Updates the size hints if required."""
        super().prepare_layout()

        if self._size_hint_requires_update:
            self._update_size_hints()

    def _update_size_hints(self):
        self._size_hint_requires_update = False

        max_width_per_column: list[list[tuple[int, int]]] = [
            [(0, 1) for _ in range(self.row_count)] for _ in range(self.column_count)
        ]
        max_height_per_row: list[list[tuple[int, int]]] = [
            [(0, 1) for _ in range(self.column_count)] for _ in range(self.row_count)
        ]

        for child, data in self._children:
            col_num = data["column"]
            row_num = data["row"]
            col_span = data["column_span"]
            row_span = data["row_span"]

            shmn_w, shmn_h = UILayout.min_size_of(child)

            for i in range(col_num, col_span + col_num):
                max_width_per_column[i][row_num] = (0, 0)

            max_width_per_column[col_num][row_num] = (shmn_w, col_span)

            for i in range(row_num, row_span + row_num):
                max_height_per_row[i][col_num] = (0, 0)

            max_height_per_row[row_num][col_num] = (shmn_h, row_span)

        principal_width_ratio_list = []
        principal_height_ratio_list = []

        for row in max_height_per_row:
            principal_height_ratio_list.append(max(height / (span or 1) for height, span in row))

        for col in max_width_per_column:
            principal_width_ratio_list.append(max(width / (span or 1) for width, span in col))

        base_width = self._padding_left + self._padding_right + 2 * self._border_width
        base_height = self._padding_top + self._padding_bottom + 2 * self._border_width

        content_height = sum(principal_height_ratio_list) + self.row_count * self._vertical_spacing
        content_width = (
            sum(principal_width_ratio_list) + self.column_count * self._horizontal_spacing
        )

        self.size_hint_min = (base_width + content_width, base_height + content_height)

    def do_layout(self):
        """Executes the layout algorithm.

        Children are placed in a grid layout based on the size hints."""
        initial_left_x = self.content_rect.left
        start_y = self.content_rect.top

        if not self.children:
            return

        child_sorted_row_wise = cast(
            list[list[UIWidget]],
            [[None for _ in range(self.column_count)] for _ in range(self.row_count)],
        )

        max_width_per_column: list[list[tuple[float, int]]] = [
            [(0, 1) for _ in range(self.row_count)] for _ in range(self.column_count)
        ]
        max_height_per_row: list[list[tuple[float, int]]] = [
            [(0, 1) for _ in range(self.column_count)] for _ in range(self.row_count)
        ]

        for child, data in self._children:
            col_num = data["column"]
            row_num = data["row"]
            col_span = data["column_span"]
            row_span = data["row_span"]

            for i in range(col_num, col_span + col_num):
                max_width_per_column[i][row_num] = (0, 0)

            max_width_per_column[col_num][row_num] = (child.width, col_span)

            for i in range(row_num, row_span + row_num):
                max_height_per_row[i][col_num] = (0, 0)

            max_height_per_row[row_num][col_num] = (child.height, row_span)

            for row in child_sorted_row_wise[row_num : row_num + row_span]:
                row[col_num : col_num + col_span] = [child] * col_span

        principal_height_ratio_list = []
        principal_width_ratio_list = []

        # Making cell height same for each row.
        for row in max_height_per_row:
            principal_height_ratio = max(
                (height + self._vertical_spacing) / (span or 1) for height, span in row
            )
            principal_height_ratio_list.append(principal_height_ratio)
            for i, (height, span) in enumerate(row):
                if (height + self._vertical_spacing) / (span or 1) < principal_height_ratio:
                    row[i] = (principal_height_ratio * span, span)

        # Making cell width same for each column.
        for col in max_width_per_column:
            principal_width_ratio = max(
                (width + self._horizontal_spacing) / (span or 1) for width, span in col
            )
            principal_width_ratio_list.append(principal_width_ratio)
            for i, (width, span) in enumerate(col):
                if (width + self._horizontal_spacing) / (span or 1) < principal_width_ratio:
                    col[i] = (principal_width_ratio * span, span)

        content_height = sum(principal_height_ratio_list) + self.row_count * self._vertical_spacing
        content_width = (
            sum(principal_width_ratio_list) + self.column_count * self._horizontal_spacing
        )

        def ratio(dimensions: list) -> list:
            """Used to calculate ratio of the elements based on the minimum value in the parameter.

            Args:
                dimension: List containing max height or width of the
                    cells.
            """
            ratio_value = sum(dimensions) or 1
            return [dimension / ratio_value for dimension in dimensions]

        expandable_height_ratio = ratio(principal_width_ratio_list)
        expandable_width_ratio = ratio(principal_height_ratio_list)

        total_available_height = self.content_rect.top - content_height - self.content_rect.bottom
        total_available_width = self.content_rect.right - content_width - self.content_rect.left

        # Row wise rendering children
        for row_num, row in enumerate(child_sorted_row_wise):
            max_height_row = 0
            start_x = initial_left_x

            for col_num, child in enumerate(row):
                constant_height = max_height_per_row[row_num][col_num][0]
                height_expand_ratio = expandable_height_ratio[col_num]
                available_height = constant_height + total_available_height * height_expand_ratio

                constant_width = max_width_per_column[col_num][row_num][0]
                width_expand_ratio = expandable_width_ratio[row_num]
                available_width = constant_width + total_available_width * width_expand_ratio

                if child is not None and constant_width != 0 and constant_height != 0:
                    new_rect = child.rect
                    sh_w, sh_h = 0, 0

                    if child.size_hint:
                        sh_w, sh_h = (child.size_hint[0] or 0), (child.size_hint[1] or 0)
                    shmn_w, shmn_h = child.size_hint_min or (None, None)
                    shmx_w, shmx_h = child.size_hint_max or (None, None)

                    new_height = max(shmn_h or 0, sh_h * available_height or child.height)
                    if shmx_h:
                        new_height = min(shmx_h, new_height)

                    new_width = max(shmn_w or 0, sh_w * available_width or child.width)
                    if shmx_w:
                        new_width = min(shmx_w, new_width)

                    new_rect = new_rect.resize(width=new_width, height=new_height)

                    cell_height = constant_height + self._vertical_spacing
                    cell_width = constant_width + self._horizontal_spacing

                    center_y = start_y - (cell_height / 2)
                    center_x = start_x + (cell_width / 2)

                    start_x += cell_width

                    if self.align_vertical == "top":
                        new_rect = new_rect.align_top(start_y)
                    elif self.align_vertical == "bottom":
                        new_rect = new_rect.align_bottom(start_y - cell_height)
                    else:
                        new_rect = new_rect.align_y(center_y)

                    if self.align_horizontal == "left":
                        new_rect = new_rect.align_left(start_x - cell_width)
                    elif self.align_horizontal == "right":
                        new_rect = new_rect.align_right(start_x)
                    else:
                        new_rect = new_rect.align_x(center_x)

                    child.rect = new_rect

                    # done due to row-wise rendering as start_y doesn't resets
                    # like start_x, specific to row span.
                    row_span = max_height_per_row[row_num][col_num][1] or 1
                    actual_row_height = cell_height / row_span
                    if actual_row_height > max_height_row:
                        max_height_row = actual_row_height

            start_y -= max_height_row


@dataclass
class _C:
    """Constrain values for the box algorithm"""

    min: float | None
    max: float | None
    hint: float | None
    final_size: float = 0
    """The final size of the entry which will be returned by the algorithm"""

    @staticmethod
    def from_widget(widget: UIWidget, dimension: Literal["width", "height"]) -> _C:
        index = 0 if dimension == "width" else 1
        shmin = widget.size_hint_min[index] if widget.size_hint_min else None
        shmax = widget.size_hint_max[index] if widget.size_hint_max else None
        sh = widget.size_hint[index] if widget.size_hint else None
        return _C(
            min=widget.size[index] if sh is None else shmin,
            max=widget.size[index] if sh is None else shmax,
            hint=sh,
        )

    @staticmethod
    def from_widget_width(widget: UIWidget) -> _C:
        return _C.from_widget(widget, "width")

    @staticmethod
    def from_widget_height(widget: UIWidget) -> _C:
        return _C.from_widget(widget, "height")


def _box_orthogonal_algorithm(constraints: list[_C], container_size: float) -> List[float]:
    """Calculate the 1 dimensional size of each entry based on the hint value and the available
    space in the container.

    This calculation is done for the orthogonal axis of the box layout, which only applies the size
    hint to the orthogonal axis.

    Args:
        constraints: List of constraints with hint, min and max values
        container_size: The total size of the container
    """
    # fix hint when None
    for c in constraints:
        c.hint = c.hint or 0

    # calculate the width of each entry based on the hint
    for c in constraints:
        size = container_size * c.hint
        c.min = c.min or 0
        c.max = container_size if c.max is None else c.max

        c.final_size = min(max(c.min, size), c.max)  # clamp width to min and max values

    return [c.final_size for c in constraints]


def _box_axis_algorithm(constraints: list[_C], container_size: float) -> List[float]:
    """
    The box algorithm calculates the 1 dimensional size of each entry based on the hint value and
    the available space in the container.

    Args:
        constraints: List of constraints with hint, min and max values
        container_size: The total size of the container

    Returns:
        List of tuples with the sizes of each element
    """
    # fix hint when None
    for c in constraints:
        c.hint = c.hint or 0

    # normalize hint - which will cover cases, where the sum of the hints is greater than 1
    # children will get a relative size based on their hint
    total_hint = sum(c.hint for c in constraints)
    if total_hint > 1:
        for c in constraints:
            c.hint /= total_hint

    # calculate the width of each entry based on the hint
    for c in constraints:
        size = container_size * c.hint
        c.min = c.min or 0
        c.max = container_size if c.max is None else c.max

        c.final_size = min(max(c.min, size), c.max)  # clamp width to min and max values

    # ---- Constantin
    # calculate scaling factor
    total_size = sum(c.final_size for c in constraints)
    growth_diff = total_size - sum(c.min for c in constraints)  # calculate available space
    total_adjustable_size = container_size - sum(c.min for c in constraints)

    if growth_diff != 0:
        scaling_factor = total_adjustable_size / growth_diff

        # adjust final_width based on scaling factor if scaling factor is less than 1
        if scaling_factor < 1:
            for c in constraints:
                c.final_size *= scaling_factor

    # recheck min constraints
    for c in constraints:
        c.final_size = max(c.final_size, c.min)

    # recheck max constraints
    for c in constraints:
        c.final_size = min(c.final_size, c.max)

    return [c.final_size for c in constraints]
