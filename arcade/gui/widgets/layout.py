from __future__ import annotations

import warnings
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, TypeVar

from typing_extensions import override

from arcade.gui.property import bind, unbind
from arcade.gui.widgets import UILayout, UIWidget, _ChildEntry

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
    _restrict_child_size = False
    """Whether to restrict the child size to the layout size.
    For scroll use cases this is not wanted, but for UITextWidgets it is.
    """

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 1,
        height: float = 1,
        children: Iterable[UIWidget] = tuple(),
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
        anchor_x: str | None = None,
        align_x: float = 0,
        anchor_y: str | None = None,
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
        anchor_x: str | None = None,
        align_x: float = 0,
        anchor_y: str | None = None,
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

            if self._restrict_child_size:
                new_child_rect = new_child_rect.max_size(width=self.content_width)

        if sh_h is not None:
            new_child_rect = new_child_rect.resize(height=self.content_height * sh_h)

            if shmn_h:
                new_child_rect = new_child_rect.min_size(height=shmn_h)
            if shmx_h:
                new_child_rect = new_child_rect.max_size(height=shmx_h)

            if self._restrict_child_size:
                new_child_rect = new_child_rect.max_size(height=self.content_height)

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

        bind(self, "_children", UIBoxLayout._trigger_size_hint_update)
        bind(self, "_border_width", UIBoxLayout._trigger_size_hint_update)

        bind(self, "_padding_left", UIBoxLayout._trigger_size_hint_update)
        bind(self, "_padding_right", UIBoxLayout._trigger_size_hint_update)
        bind(self, "_padding_top", UIBoxLayout._trigger_size_hint_update)
        bind(self, "_padding_bottom", UIBoxLayout._trigger_size_hint_update)

        self._update_size_hints()

    @override
    def add(self, child: W, **kwargs) -> W:
        """Add a widget to this layout

        Args:
            child: The widget to add to the layout.
        """
        # subscribe to child's changes, which might affect the own size hint
        bind(child, "_children", self._trigger_size_hint_update, weak=True)
        bind(child, "rect", self._trigger_size_hint_update, weak=True)
        bind(child, "size_hint", self._trigger_size_hint_update, weak=True)
        bind(child, "size_hint_min", self._trigger_size_hint_update, weak=True)
        bind(child, "size_hint_max", self._trigger_size_hint_update, weak=True)

        return super().add(child, **kwargs)

    @override
    def remove(self, child: UIWidget):
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
        min_child_sizes = [
            UILayout.min_size_of(child) for child in self.children if child.visible is not None
        ]

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

        children_to_render = [
            (child, data) for child, data in self._children if child.visible is not None
        ]

        # main axis
        constraints = [
            _C.from_widget_height(child) if self.vertical else _C.from_widget_width(child)
            for child, _ in children_to_render
        ]

        available_space = (
            self.content_height if self.vertical else self.content_width
        ) - self._space_between * (len(self.children) - 1)
        main_sizes = _box_axis_algorithm(constraints, available_space)

        # orthogonal axis
        constraints = [
            _C.from_widget_width(child) if self.vertical else _C.from_widget_height(child)
            for child, _ in children_to_render
        ]
        orthogonal_sizes = _box_orthogonal_algorithm(
            constraints, self.content_width if self.vertical else self.content_height
        )

        for (child, data), main_size, ortho_size in zip(
            children_to_render, main_sizes, orthogonal_sizes
        ):
            # apply calculated sizes, condition regarding existing size_hint
            # are already covered in calculation input
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

    def __str__(self):
        return f"UIBoxLayout(vertical={self.vertical})"


class UIGridLayout(UILayout):
    """Arranges each child widget over one or more columns and rows.

    The layout's ``size_hint`` requests a target size as a :py:class:`tuple`
    of ``(x, y)`` floats as ratios relative to the layout's parent:

    * The default of ``(0, 0)`` requests the minimum possible space
    * ``(1.0, 1.0)`` requests the maximum possible space
    * ``(0.1, 0.1)`` requests 10% of the layout parent's total size

    Each child widget's ``size_hint`` value will be used to:

    * control its size within the layout
    * automatically re-calculate the layout's ``size_hint_min``

    The width of each column and height of each row will be calculated
    on update by reading the sizing data of each child widget. For each
    row/column, the corresponding values along its axis will be read
    from widgets along its axis:

    * the maximum ``size_hint_min`` of its widgets
    * the minimum ``size_hint_max`` of its widgets

    If any widget lacks size hint data, its "actual" will be used instead.
    See :py:meth:`~.do_layout` to learn more.

    .. note::

       Maximum and minimum size hints only take effect when a ``size_hint``
       is set.

    Args:
        x: ``x`` coordinate of bottom left corner.
        y: ``y`` coordinate of bottom left corner.
        width: Width of the layout.
        height: Height of the layout.
        align_horizontal: Align children in along the X axis to the
            ``"left"``, ``"center"``, or ``"right"``.
        align_vertical: Align children in along the Y axis to the
            ``"top"``, ``"center"``, or ``"bottom"``.
        children: An initial iterable of children. More can be added later.
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
        width=1,
        height=1,
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
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
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

        bind(self, "_children", UIGridLayout._trigger_size_hint_update)
        bind(self, "_border_width", UIGridLayout._trigger_size_hint_update)

        bind(self, "_padding_left", UIGridLayout._trigger_size_hint_update)
        bind(self, "_padding_right", UIGridLayout._trigger_size_hint_update)
        bind(self, "_padding_top", UIGridLayout._trigger_size_hint_update)
        bind(self, "_padding_bottom", UIGridLayout._trigger_size_hint_update)

        # initially update size hints
        # TODO is this required?
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
        bind(child, "_children", self._trigger_size_hint_update, weak=True)
        bind(child, "rect", self._trigger_size_hint_update, weak=True)
        bind(child, "size_hint", self._trigger_size_hint_update, weak=True)
        bind(child, "size_hint_min", self._trigger_size_hint_update, weak=True)
        bind(child, "size_hint_max", self._trigger_size_hint_update, weak=True)

        return super().add(
            child,
            column=column,
            row=row,
            column_span=column_span,
            row_span=row_span,
            **kwargs,
        )

    def remove(self, child: UIWidget):
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

        if not self.children:
            self.size_hint_min = (0, 0)
            return

        # 0. generate list for all rows and columns
        columns = []
        for i in range(self.column_count):
            columns.append([])
        rows = []
        for i in range(self.row_count):
            rows.append([])

        for entry in self._children:
            col_num = entry.data["column"]
            row_num = entry.data["row"]
            col_span = entry.data["column_span"]
            row_span = entry.data["row_span"]

            # we put the entry in all columns and rows it spans
            for c in range(col_span):
                columns[col_num + c].append(entry)

                for r in range(row_span):
                    rows[row_num + r].append(entry)

        # 1.a per column, collect max of size_hint_min and max size_hint
        minimal_width_per_column = []
        for col in columns:
            min_width = 0
            max_sh = 0
            for entry in col:
                col_span = entry.data["column_span"]
                # if the cell spans multiple columns,
                # we need to reduce the minimal required width by the horizontal spacing
                consumed_space = self._horizontal_spacing if col_span > 1 else 0

                min_w, _ = UILayout.min_size_of(entry.child)
                min_width = max(min_width, min_w / col_span - consumed_space)

                shw, _ = entry.child.size_hint or (0, 0)
                max_sh = max(max_sh, shw) if shw else max_sh

            minimal_width_per_column.append(min_width)

        # 1.b per row, collect max of size_hint_min and max size_hint
        minimal_height_per_row = []
        for row in rows:
            min_height = 0
            max_sh = 0
            for entry in row:
                row_span = entry.data["row_span"]
                # if the cell spans multiple rows,
                # we need to reduce the minimal required height by the vertical spacing
                consumed_space = self._vertical_spacing if row_span > 1 else 0

                _, min_h = UILayout.min_size_of(entry.child)
                min_height = max(min_height, min_h / row_span - consumed_space)

                _, shh = entry.child.size_hint or (0, 0)
                max_sh = max(max_sh, shh) if shh else max_sh

            minimal_height_per_row.append(min_height)

        base_width = self._padding_left + self._padding_right + 2 * self._border_width
        base_height = self._padding_top + self._padding_bottom + 2 * self._border_width

        self.size_hint_min = (
            base_width
            + sum(minimal_width_per_column)
            + (self.column_count - 1) * self._horizontal_spacing,
            base_height
            + sum(minimal_height_per_row)
            + (self.row_count - 1) * self._vertical_spacing,
        )

    def do_layout(self):
        """Arrange children in the grid based on their size hints.

        Algorithm
        ---------

        0. Generate lists of child widgets for each row and column
        1. For each column, calculate the following values:

           * If a widget lacks size hints, substitute the "actual" width instead
           * The :py:func:`max` of all its child ``size_hint_min[0]`` values
           * The :py:func:`max` of all its child ``size_hint[0]`` values

        2. For each row, calculate the following values:

           * If a widget lacks size hints, substitute the "actual" height instead
           * The :py:func:`max` of all its child ``size_hint_min[1]`` values
           * The :py:func:`max` of all its child ``size_hint[1]`` values

        3.  Use box layout algorithm to allocate on-screen space
        4.  Re-size and place the widgets to match the calculated grid layout

        """

        # skip if no children
        if not self.children:
            return

        # 0. generate list for all rows and columns
        columns = []
        for i in range(self.column_count):
            columns.append([])
        rows = []
        for i in range(self.row_count):
            rows.append([])

        lookup: dict[tuple[int, int], _ChildEntry] = {}
        for entry in self._children:
            col_num = entry.data["column"]
            row_num = entry.data["row"]
            col_span = entry.data["column_span"]
            row_span = entry.data["row_span"]

            # we put the entry in all columns and rows it spans
            for c in range(col_span):
                columns[col_num + c].append(entry)

                for r in range(row_span):
                    rows[row_num + r].append(entry)

            lookup[(col_num, row_num)] = entry

        # 1.a per column, collect max of size_hint_min and max size_hint
        minimal_width_per_column = []
        max_size_hint_per_column = []
        for col in columns:
            min_width = 0
            max_sh = 0
            for entry in col:
                col_span = entry.data["column_span"]
                # if the cell spans multiple columns,
                # we need to reduce the minimal required width by the horizontal spacing
                consumed_space = self._horizontal_spacing if col_span > 1 else 0

                min_w, _ = UILayout.min_size_of(entry.child)
                min_width = max(min_width, min_w / col_span - consumed_space)

                shw, _ = entry.child.size_hint or (0, 0)
                max_sh = max(max_sh, shw) if shw else max_sh

            minimal_width_per_column.append(min_width)
            max_size_hint_per_column.append(max_sh)

        # 1.b per row, collect max of size_hint_min and max size_hint
        minimal_height_per_row = []
        max_size_hint_per_row = []
        for row in rows:
            min_height = 0
            max_sh = 0
            for entry in row:
                row_span = entry.data["row_span"]
                # if the cell spans multiple rows,
                # we need to reduce the minimal required height by the vertical spacing
                consumed_space = self._vertical_spacing if row_span > 1 else 0

                _, min_h = UILayout.min_size_of(entry.child)
                min_height = max(min_height, min_h / row_span - consumed_space)

                _, shh = entry.child.size_hint or (0, 0)
                max_sh = max(max_sh, shh) if shh else max_sh

            minimal_height_per_row.append(min_height)
            max_size_hint_per_row.append(max_sh)

        # 2. use box layout algorithm to distribute space
        column_constraints = [
            _C(minimal_width_per_column[i], None, max_size_hint_per_column[i])
            for i in range(self.column_count)
        ]
        column_sizes = _box_axis_algorithm(
            column_constraints,
            self.content_width - (self.column_count - 1) * self._horizontal_spacing,
        )

        row_constraints = [
            _C(minimal_height_per_row[i], None, max_size_hint_per_row[i])
            for i in range(self.row_count)
        ]
        row_sizes = _box_axis_algorithm(
            row_constraints, self.content_height - (self.row_count - 1) * self._vertical_spacing
        )

        # 3. place widgets in grid layout
        start_y = self.content_rect.top
        for row_num in range(self.row_count):
            start_x = self.content_rect.left
            for col_num in range(self.column_count):
                entry = lookup.get((col_num, row_num))
                if not entry:
                    # still need to update start_x
                    start_x += column_sizes[col_num] + self._horizontal_spacing
                    continue

                # TODO handle row_span and col_span
                child = entry.child
                new_rect = child.rect

                # combine size of cells this entry spans and add spacing
                column_span = entry.data["column_span"]
                cell_width: float = sum(column_sizes[col_num : col_num + column_span])
                cell_width += (column_span - 1) * self._horizontal_spacing

                row_span = entry.data["row_span"]
                cell_height: float = sum(row_sizes[row_num : row_num + row_span])
                cell_height += (row_span - 1) * self._vertical_spacing

                # apply calculated sizes, when size_hint is given
                shw, shh = child.size_hint or (None, None)
                shmn_w, shmn_h = child.size_hint_min or (None, None)
                shmx_w, shmx_h = child.size_hint_max or (None, None)

                new_width = child.width
                if shw is not None:
                    new_width = min(cell_width, shw * self.content_width)
                    new_width = max(new_width, shmn_w or 0)
                    if shmx_w is not None:
                        new_width = min(new_width, shmx_w)

                new_height = child.height
                if shh is not None:
                    new_height = min(cell_height, shh * self.content_height)
                    new_height = max(new_height, shmn_h or 0)
                    if shmx_h is not None:
                        new_height = min(new_height, shmx_h)

                new_rect = new_rect.resize(width=new_width, height=new_height)

                # align within cell
                center_y = start_y - (cell_height / 2)
                center_x = start_x + (cell_width / 2)

                if self.align_vertical == "top":
                    new_rect = new_rect.align_top(start_y)
                elif self.align_vertical == "bottom":
                    new_rect = new_rect.align_bottom(start_y - row_sizes[row_num])
                else:
                    new_rect = new_rect.align_y(center_y)

                if self.align_horizontal == "left":
                    new_rect = new_rect.align_left(start_x)
                elif self.align_horizontal == "right":
                    new_rect = new_rect.align_right(start_x + cell_width)
                else:
                    new_rect = new_rect.align_x(center_x)

                # update child rect
                child.rect = new_rect

                start_x += column_sizes[col_num] + self._horizontal_spacing
            start_y -= row_sizes[row_num] + self._vertical_spacing


@dataclass
class _C:
    """Constrain values for the box algorithm.

    size_hint and min values of None are resolved to 0.0.
    """

    min: float
    max: float | None
    hint: float
    _final_size: float = 0.0
    """The final size of the entry which will be returned by the algorithm"""

    @staticmethod
    def from_widget(widget: UIWidget, dimension: Literal["width", "height"]) -> _C:
        index = 0 if dimension == "width" else 1

        # get hint values from different formats None and (float|None, float|None)
        sh = widget.size_hint[index] if widget.size_hint else None
        sh_min = widget.size_hint_min[index] if widget.size_hint_min else None
        sh_max = widget.size_hint_max[index] if widget.size_hint_max else None

        # resolve min and max values if no size hint is given
        min_value = widget.size[index] if sh is None else sh_min
        max_value = widget.size[index] if sh is None else sh_max

        # clean up None values
        min_value = min_value or 0
        sh = sh or 0.0

        return _C(
            min=min_value,
            max=max_value,
            hint=sh,
        )

    @staticmethod
    def from_widget_width(widget: UIWidget) -> _C:
        return _C.from_widget(widget, "width")

    @staticmethod
    def from_widget_height(widget: UIWidget) -> _C:
        return _C.from_widget(widget, "height")


def _box_orthogonal_algorithm(constraints: list[_C], container_size: float) -> list[float]:
    """Calculate the 1 dimensional size of each entry based on the hint value and the available
    space in the container.

    This calculation is done for the orthogonal axis of the box layout, which only applies the size
    hint to the orthogonal axis.

    Args:
        constraints: List of constraints with hint, min and max values
        container_size: The total size of the container
    """
    # calculate the width of each entry based on the hint
    for c in constraints:
        size = container_size * c.hint
        c.max = container_size if c.max is None else c.max

        c._final_size = min(max(c.min, size), c.max)  # clamp width to min and max values

    return [c._final_size for c in constraints]


def _box_axis_algorithm(constraints: list[_C], container_size: float) -> list[float]:
    """
    The box algorithm calculates the 1 dimensional size of each entry based on the hint value and
    the available space in the container.

    Args:
        constraints: List of constraints with hint, min and max values
        container_size: The total size of the container

    Returns:
        List of tuples with the sizes of each element
    """

    # if there is no space, return the min value of each constraint
    # this will cause a overflow, so we give a warning
    if container_size <= 0:
        warnings.warn("Container size is 0, cannot calculate sizes for children.")
        return [c.min for c in constraints]

    # adjust hint value based on min and max values
    for c in constraints:
        c.hint = max(c.min / container_size, c.hint)
        if c.max is not None:
            c.hint = min(c.hint, c.max / container_size)

    # normalize hint - which will cover cases, where the sum of the hints is greater than 1.
    # children will get a relative size based on their hint
    total_hint = sum(c.hint for c in constraints)
    if total_hint > 1:
        for c in constraints:
            c.hint /= total_hint

        # adjust hint value based on min values, again
        for c in constraints:
            c.hint = max(c.min / container_size, c.hint)

    # check if the total hint is greater than 1, again (caused by reapplied min values)
    total_hint = sum(c.hint for c in constraints)
    if total_hint > 1:
        # calculate the total hint value of all adjustable constraints
        total_adjustable_hint = sum(c.hint - c.min / container_size for c in constraints)

        # check if we have any adjustable constraints
        if total_adjustable_hint > 0:
            # reduce hint values of adjustable constraints to fit the container size
            required_adjustment = total_hint - 1
            possible_adjustment = min(required_adjustment, total_adjustable_hint)
            for c in constraints:
                adjustable_size = c.hint - c.min / container_size
                c.hint -= possible_adjustment * (adjustable_size / total_adjustable_hint)

    # calculate the width of each entry based on the hint
    for c in constraints:
        c._final_size = container_size * c.hint

    # return the calculated sizes, round to avoid floating point errors
    return [round(c._final_size, 5) for c in constraints]
