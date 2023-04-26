from typing import Iterable, List, TypeVar, Tuple, Optional

from arcade.gui.property import bind
from arcade.gui.widgets import UIWidget, UILayout

__all__ = [
    "UILayout",
    "UIAnchorLayout",
    "UIBoxLayout",
    "UIGridLayout"
]

W = TypeVar("W", bound="UIWidget")


class UIAnchorLayout(UILayout):
    """
    Places children based on anchor values.

    Defaults to ``size_hint = (1, 1)``.

    Supports the options ``size_hint``, ``size_hint_min``, and
    ``size_hint_max``. Children are allowed to overlap.

    Child are resized based on ``size_hint``. ``size_hint_min/max`` only take effect if a ``size_hint`` is set.

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
    """

    default_anchor_x = "center"
    default_anchor_y = "center"

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        children: Iterable["UIWidget"] = tuple(),
        size_hint=(1, 1),
        size_hint_min=None,
        size_hint_max=None,
        **kwargs
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
            **kwargs
        )

    def do_layout(self):
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
        **kwargs
    ) -> W:
        """
        Add a widget to the layout as a child. Added widgets will receive
        all user-interface events and be rendered.

        By default, the latest added widget will receive events first and will
        be rendered on top of others. The widgets will be automatically placed
        within this widget.

        :param child: Specified child widget to add.
        :param anchor_x: Horizontal anchor. Valid options are ``left``,
                         ``right``, and ``center``.
        :param align_x: Offset or padding for the horizontal anchor.
        :param anchor_y: Vertical anchor. Valid options are ``top``,
                         ``center``, and ``bottom``.
        :param align_y: Offset or padding for the vertical anchor.

        :return: Given child that was just added to the layout.
        """
        return super().add(
            child=child,
            anchor_x=anchor_x,
            align_x=align_x,
            anchor_y=anchor_y,
            align_y=align_y,
            **kwargs
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

        # Stay in bounds
        new_child_rect = new_child_rect.max_size(*self.content_size)

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
    """
    Place widgets next to each other. Depending on the
    :py:class:`~arcade.gui.UIBoxLayout.vertical` attribute, the widgets are
    placed top to bottom or left to right.

    .. hint::

        :py:class:`~arcade.gui.UIBoxLayout` does not adjust its
        own size if children are added. This requires a
        :py:class:`~arcade.gui.UIManager` or a
        :py:class:`~arcade.gui.UIAnchorLayout` as a parent.

        Or use :py:meth:`arcade.gui.UIBoxLayout.fit_content` to resize the layout. The
        bottom-left corner is used as the default anchor point.

    Supports the options: ``size_hint``, ``size_hint_min``, ``size_hint_max``.

    If a child widget provides a ``size_hint`` for a dimension, the child will
    be resized within the given range of ``size_hint_min`` and
    ``size_hint_max`` (unrestricted if not given). If the parameter
    ``vertical`` is True, any available space (``layout size - min_size`` of
    children) will be distributed to the child widgets based on their
    ``size_hint``.

    :param float x: ``x`` coordinate of the bottom left corner.
    :param float y: ``y`` coordinate of the bottom left corner.
    :param vertical: Layout children vertical (True) or horizontal (False).
    :param align: Align children in orthogonal direction::
                  - ``x``: ``left``, ``center``, and ``right``
                  - ``y``: ``top``, ``center``, and ``bottom``
    :param children: Initial list of children. More can be added later.
    :param size_hint: Size hint for the :py:class:`~arcade.gui.UILayout` if
                      the widget would like to grow. Defaults to ``0, 0`` ->
                      minimal size to contain children.
    :param size_hint_min: Minimum width and height in pixels.
    :param size_hint_max: Maximum width and height in pixels.
    :param space_between: Space in pixels between the children.
    """

    def __init__(
        self,
        x=0,
        y=0,
        width=0,
        height=0,
        vertical=True,
        align="center",
        children: Iterable[UIWidget] = tuple(),
        size_hint=(0, 0),
        size_hint_min=None,
        size_hint_max=None,
        space_between=0,
        style=None,
        **kwargs
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
            style=style,
            **kwargs
        )

        self.align = align
        self.vertical = vertical
        self._space_between = space_between

        bind(self, "_children", self._update_size_hints)
        bind(self, "_border_width", self._update_size_hints)

        bind(self, "_padding_left", self._update_size_hints)
        bind(self, "_padding_right", self._update_size_hints)
        bind(self, "_padding_top", self._update_size_hints)
        bind(self, "_padding_bottom", self._update_size_hints)

        # Initially update size hints
        self._update_size_hints()

    @staticmethod
    def _layouting_allowed(child: UIWidget) -> Tuple[bool, bool]:
        """
        Checks if ``size_hint`` is given for the dimension. This would allow
        the layout to resize this widget.

        :return: Horizontal and vertical.
        """
        sh_w, sh_h = child.size_hint or (None, None)
        return sh_w is not None, sh_h is not None

    def _update_size_hints(self):
        required_space_between = max(0, len(self.children) - 1) * self._space_between

        def min_size(child: UIWidget) -> Tuple[float, float]:
            """
            Determine the minimum size of a child widget.

            This can be the minimum size hint (``size_hint_min``). If no size
            hints are provided the child size has to stay the same and the
            minimal size is the current size.
            """
            h_allowed, v_allowed = UIBoxLayout._layouting_allowed(child)
            shmn_w, shmn_h = child.size_hint_min or (None, None)
            shmn_w = shmn_w or 0 if h_allowed else child.width
            shmn_h = shmn_h or 0 if v_allowed else child.height
            return shmn_w, shmn_h

        min_child_sizes = [min_size(child) for child in self.children]

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

    def do_layout(self):
        start_y = self.content_rect.top
        start_x = self.content_rect.left

        if not self.children:
            return

        if self.vertical:
            available_width = self.content_width

            # Determine if some space is available for children to grow
            available_height = max(0, self.height - self.size_hint_min[1])
            total_size_hint_height = (
                sum(
                    child.size_hint[1] or 0
                    for child in self.children
                    if child.size_hint
                )
                or 1
            )  # Prevent division by zero

            for child in self.children:
                new_rect = child.rect

                # Collect all size hints
                sh_w, sh_h = child.size_hint or (None, None)
                shmn_w, shmn_h = child.size_hint_min or (None, None)
                shmx_w, shmx_h = child.size_hint_max or (None, None)

                # Apply y-axis
                if sh_h is not None:
                    min_height_value = shmn_h or 0

                    # Maximal growth to parent.width * shw
                    available_growth_height = min_height_value + available_height * (
                        sh_h / total_size_hint_height
                    )
                    max_growth_height = self.height * sh_h
                    new_rect = new_rect.resize(
                        height=min(available_growth_height, max_growth_height)
                    )

                    if shmn_h is not None:
                        new_rect = new_rect.min_size(height=shmn_h)
                    if shmx_h is not None:
                        new_rect = new_rect.max_size(height=shmx_h)

                # Apply x-axis
                if sh_w is not None:
                    new_rect = new_rect.resize(
                        width=max(available_width * sh_w, shmn_w or 0)
                    )

                    if shmn_w is not None:
                        new_rect = new_rect.min_size(width=shmn_w)
                    if shmx_w is not None:
                        new_rect = new_rect.max_size(width=shmx_w)

                # Align the children
                if self.align == "left":
                    new_rect = new_rect.align_left(start_x)
                elif self.align == "right":
                    new_rect = new_rect.align_right(start_x + self.content_width)
                else:
                    center_x = start_x + self.content_width // 2
                    new_rect = new_rect.align_center_x(center_x)

                new_rect = new_rect.align_top(start_y)
                child.rect = new_rect

                start_y -= child.height
                start_y -= self._space_between
        else:
            center_y = start_y - self.content_height // 2

            available_height = self.content_height

            # Calculate if some space is available for children to grow.
            available_width = max(0, self.width - self.size_hint_min[0])
            total_size_hint_width = (
                sum(
                    child.size_hint[0] or 0
                    for child in self.children
                    if child.size_hint
                )
                or 1
            )  # Prevent division by zero

            # TODO Fix layout algorithm, handle size hints per dimension!
            # 0. check if any hint given, if not, continue with step 4.
            #   1. change size to minimal
            #   2. grow using size_hint
            #   3. ensure size_hint_max
            # 4. place child

            for child in self.children:
                new_rect = child.rect

                # Collect all size hints
                sh_w, sh_h = child.size_hint or (None, None)
                shmn_w, shmn_h = child.size_hint_min or (None, None)
                shmx_w, shmx_h = child.size_hint_max or (None, None)

                # Apply x-axis
                if sh_w is not None:
                    min_width_value = shmn_w or 0

                    # Maximal growth to parent.width * shw
                    available_growth_width = min_width_value + available_width * (
                        sh_w / total_size_hint_width
                    )
                    max_growth_width = self.width * sh_w
                    new_rect = new_rect.resize(
                        width=min(
                            available_growth_width, max_growth_width
                        )   # This does not enforce the minimum width
                    )

                    if shmn_w is not None:
                        new_rect = new_rect.min_size(width=shmn_w)

                    if shmx_w is not None:
                        new_rect = new_rect.max_size(width=shmx_w)

                # Apply vertical axis
                if sh_h is not None:
                    new_rect = new_rect.resize(
                        height=max(available_height * sh_h, shmn_h or 0)
                    )

                    if shmn_h is not None:
                        new_rect = new_rect.min_size(height=shmn_h)

                    if shmx_h is not None:
                        new_rect = new_rect.max_size(height=shmx_h)

                # Align all children
                if self.align == "top":
                    new_rect = new_rect.align_top(start_y)
                elif self.align == "bottom":
                    new_rect = new_rect.align_bottom(start_y - self.content_height)
                else:
                    new_rect = new_rect.align_center_y(center_y)

                new_rect = new_rect.align_left(start_x)
                child.rect = new_rect

                start_x += child.width
                start_x += self._space_between


class UIGridLayout(UILayout):
    """
    Place widgets in a grid layout. This is similar to tkinter's ``grid``
    layout geometry manager.

    Defaults to ``size_hint = (0, 0)``.

    Supports the options ``size_hint``, ``size_hint_min``, and
    ``size_hint_max``.

    Children are resized based on ``size_hint``. Maximum and minimum
    ``size_hint``s only take effect if a ``size_hint`` is given.

    :param float x: ``x`` coordinate of bottom left corner.
    :param float y: ``y`` coordinate of bottom left corner.
    :param str align_horizontal: Align children in orthogonal direction.
                                 Options include ``left``, ``center``, and
                                 ``right``.
    :param str align_vertical: Align children in orthogonal direction. Options
                               include ``top``, ``center``, and ``bottom``.
    :param Iterable[UIWidget] children: Initial list of children. More can be
                                        added later.
    :param size_hint: A size hint for :py:class:`~arcade.gui.UILayout`, if the
                      :py:class:`~arcade.gui.UIWidget` would like to grow.
    :param size_hint_min: Minimum width and height in pixels.
    :param size_hint_max: Maximum width and height in pixels.
    :param horizontal_spacing: Space between columns.
    :param vertical_spacing: Space between rows.
    :param int column_count: Number of columns in the grid. This can be changed
                             later.
    :param int row_count: Number of rows in the grid. This can be changed
                          later.
    """

    def __init__(
        self,
        x=0,
        y=0,
        align_horizontal="center",
        align_vertical="center",
        children: Iterable[UIWidget] = tuple(),
        size_hint=(0, 0),
        size_hint_min=None,
        size_hint_max=None,
        horizontal_spacing: int = 0,
        vertical_spacing: int = 0,
        column_count: int = 1,
        row_count: int = 1,
        style=None,
        **kwargs
    ):

        super(UIGridLayout, self).__init__(
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

    @staticmethod
    def _layouting_allowed(child: UIWidget) -> Tuple[bool, bool]:
        """
        Checks if size_hint is given for the dimension, which would allow the layout to resize this widget

        :return: horizontal, vertical
        """
        sh_w, sh_h = child.size_hint or (None, None)
        return sh_w is not None, sh_h is not None

    def _update_size_hints(self):

        child_sorted_row_wise = [
            [None for _ in range(self.column_count)] for _ in range(self.row_count)
        ]

        max_width_per_column = [
            [(0, 1) for _ in range(self.row_count)] for _ in range(self.column_count)
        ]
        max_height_per_row = [
            [(0, 1) for _ in range(self.column_count)] for _ in range(self.row_count)
        ]

        def min_size(child: UIWidget) -> Tuple[float, float]:
            """
            Determine min size of a child widget
            This can be the size_hint_min. If no size_hints are provided the child size has to stay the same and
            the minimal size is the current size.
            """
            h_allowed, v_allowed = UIGridLayout._layouting_allowed(child)
            shmn_w, shmn_h = child.size_hint_min or (None, None)
            shmn_w = shmn_w or 0 if h_allowed else child.width
            shmn_h = shmn_h or 0 if v_allowed else child.height
            return shmn_w, shmn_h

        for child, data in self._children:
            col_num = data["col_num"]
            row_num = data["row_num"]
            col_span = data["col_span"]
            row_span = data["row_span"]

            shmn_w, shmn_h = min_size(child)

            for i in range(col_num, col_span + col_num):
                max_width_per_column[i][row_num] = (0, 0)

            max_width_per_column[col_num][row_num] = (shmn_w, col_span)

            for i in range(row_num, row_span + row_num):
                max_height_per_row[i][col_num] = (0, 0)

            max_height_per_row[row_num][col_num] = (shmn_h, row_span)

            for row in child_sorted_row_wise[
                row_num : row_num + row_span  # noqa: E203
            ]:
                row[col_num : col_num + col_span] = [child] * col_span  # noqa: E203

        principal_width_ratio_list = []
        principal_height_ratio_list = []

        for row in max_height_per_row:
            principal_height_ratio_list.append(
                max(height / (span or 1) for height, span in row)
            )

        for col in max_width_per_column:
            principal_width_ratio_list.append(
                max(width / (span or 1) for width, span in col)
            )

        base_width = self._padding_left + self._padding_right + 2 * self._border_width
        base_height = self._padding_top + self._padding_bottom + 2 * self._border_width

        content_height = (
            sum(principal_height_ratio_list) + self.row_count * self._vertical_spacing
        )
        content_width = (
            sum(principal_width_ratio_list)
            + self.column_count * self._horizontal_spacing
        )

        self.size_hint_min = (base_width + content_width, base_height + content_height)

    def add(
        self,
        child: W,
        col_num: int = 0,
        row_num: int = 0,
        col_span: int = 1,
        row_span: int = 1,
        **kwargs
    ) -> W:
        """
        Add a widget to the grid layout.

        :param UIWidget child: Specified child widget to add.
        :param int col_num: Column index in which the widget is to be added.
                            The first column is numbered 0; which is the top
                            left corner.
        :param int row_num: The row number in which the widget is to be added.
                            The first row is numbered 0; which is the
        :param int col_span: Number of columns the widget will stretch for.
        :param int row_span: Number of rows the widget will stretch for.
        """
        return super().add(
            child,
            col_num=col_num,
            row_num=row_num,
            col_span=col_span,
            row_span=row_span,
            **kwargs
        )

    def do_layout(self):
        initial_left_x = self.content_rect.left
        start_y = self.content_rect.top

        if not self.children:
            return

        child_sorted_row_wise = [
            [None for _ in range(self.column_count)] for _ in range(self.row_count)
        ]

        max_width_per_column = [
            [(0, 1) for _ in range(self.row_count)] for _ in range(self.column_count)
        ]
        max_height_per_row = [
            [(0, 1) for _ in range(self.column_count)] for _ in range(self.row_count)
        ]

        for child, data in self._children:
            col_num = data["col_num"]
            row_num = data["row_num"]
            col_span = data["col_span"]
            row_span = data["row_span"]

            for i in range(col_num, col_span + col_num):
                max_width_per_column[i][row_num] = (0, 0)

            max_width_per_column[col_num][row_num] = (child.width, col_span)

            for i in range(row_num, row_span + row_num):
                max_height_per_row[i][col_num] = (0, 0)

            max_height_per_row[row_num][col_num] = (child.height, row_span)

            for row in child_sorted_row_wise[
                row_num : row_num + row_span  # noqa: E203
            ]:
                row[col_num : col_num + col_span] = [child] * col_span  # noqa: E203

        principal_height_ratio_list = []
        principal_width_ratio_list = []

        # Making cell height same for each row.
        for row in max_height_per_row:
            principal_height_ratio = max((height + self._vertical_spacing) / (span or 1) for height, span in row)
            principal_height_ratio_list.append(principal_height_ratio)
            for i, (height, span) in enumerate(row):
                if (height + self._vertical_spacing) / (span or 1) < principal_height_ratio:
                    row[i] = (principal_height_ratio * span, span)

        # Making cell width same for each column.
        for col in max_width_per_column:
            principal_width_ratio = max((width + self._horizontal_spacing) / (span or 1) for width, span in col)
            principal_width_ratio_list.append(principal_width_ratio)
            for i, (width, span) in enumerate(col):
                if (width + self._horizontal_spacing) / (span or 1) < principal_width_ratio:
                    col[i] = (principal_width_ratio * span, span)

        content_height = sum(principal_height_ratio_list) + self.row_count * self._vertical_spacing
        content_width = sum(principal_width_ratio_list) + self.column_count * self._horizontal_spacing

        def ratio(dimensions: List) -> List:
            """
            Used to calculate ratio of the elements based on the minimum value in the parameter.
            :param dimension: List containing max height or width of the cells.
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
                        new_rect = new_rect.align_center_y(center_y)

                    if self.align_horizontal == "left":
                        new_rect = new_rect.align_left(start_x - cell_width)
                    elif self.align_horizontal == "right":
                        new_rect = new_rect.align_right(start_x)
                    else:
                        new_rect = new_rect.align_center_x(center_x)

                    child.rect = new_rect

                    # done due to row-wise rendering as start_y doesn't resets like start_x, specific to row span.
                    row_span = max_height_per_row[row_num][col_num][1] or 1
                    actual_row_height = cell_height / row_span
                    if actual_row_height > max_height_row:
                        max_height_row = actual_row_height

            start_y -= max_height_row
