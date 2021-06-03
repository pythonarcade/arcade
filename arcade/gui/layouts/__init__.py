"""

Concept
-------

UILayout can handle UIElements and Sprites. :py:meth:`UILayout.pack` adds a child to a UILayout.
Layout specific ``**kwargs`` might be used.

Sprites, UIElements, and UILayouts have width and height.
These values represent the current size of the element.

Sprites, UIElements and UILayouts may provide `min_size` and `size_hint`.

min_size
    defines the minimal size the element has to get in pixel.

size_hint
    defines how much of the parents space it would like to occupy (range: 0.0-1.0).
    For maximal vertical and horizontal expansion, define `size_hint` of 1 for the axis.

UILayouts are `only` allowed to change the width and height of a child which defines at least one of these properties.
While most of UIElements provide a default behavior to be used in UILayouts, Sprites do **not**.
Sprites, UIElements, and UILayouts which allow size manipulation have to adjust to the new width and height.


Layout Implementations
----------------------

UIAnchorLayout
~~~~~~~~~~~~~~

:class:`~arcade.gui.UIAnchorLayout` provides a layout, which places elements relative to the parents boundaries.
It is many used as the root level layout within the :class:`~arcade.gui.UILayoutManager`.

**Behavior**

- expands to full parents space
- children may overlap

**Supported pack kwargs**

- **top** - place relative to the top
- **bottom** - place relative to the bottom
- **left** - place relative to the left
- **right** - place relative to the right
- **center_y** - place relative to the center_y
- **center_x** - place relative to the center_x
- **space** - extra space between this element and the following

.. note::
    ``top``, ``bottom``, ... do use the according elements edge to aline. That means ``bottom=30`` will place the
    element with 30 pixel distance between viewports bottom and elements bottom edge.

    It is only possible to choose one value per axis. A combination of ``top`` and ``bottom`` is not possible.


UIBoxLayout
~~~~~~~~~~~

:class:`~arcade.gui.UIBoxLayout` provides a layout, which places elements in a vertical or horizontal direction.
To achieve a grid like layout it is possible to use nested  :class:`~arcade.gui.UIBoxLayout`.

**Behavior**

- wraps content
- children will not overlap
- overflow not handled*

**Supported pack kwargs**

space
    extra space between this element and the following

Algorithm
---------

:py:meth:`UILayout.do_layout` starts the layout process. While :py:class:`~arcade.gui.layouts.UILayout` provides
a default implementation, every subclass of UILayout have to implement :py:meth:`UILayout.place_elements`.

Executed steps within :py:class:`~arcade.gui.layout.box.UIBoxLayout`:

1. call :py:meth:`~UILayout.place_elements`
    1. collect min_size (recursively), size_hint and size of all children
    2. calculate the new position and sizes
    3. set position and size of children
2. recursive call `do_layout` on child layouts

.. code-block::

         ┌─────────┐          ┌────────┐                      ┌────────┐
         │UIManager│          │UILayout│                      │children│
         └────┬────┘          └───┬────┘                      └───┬────┘
              │   do_layout()    ┌┴┐                              │
              │─────────────────>│ │                              │
              │                  │ │                              │
              │                  │ │                              │
              │     ╔════════════╪═╪════╤═════════════════════════╪══════════════╗
              │     ║ PLACE_ELEMENTS()  │                         │              ║
              │     ╟────────────────get min_size, size_hint, size│              ║
              │     ║            │ │ <─────────────────────────────              ║
              │     ║            │ │                              │              ║
              │     ║            │ │       set size and pos       │              ║
              │     ║            │ │ ─────────────────────────────>              ║
              │     ╚════════════╪═╪══════════════════════════════╪══════════════╝
              │                  │ │                              │
              │                  │ │                              │
              │     ╔═══════╤════╪═╪══════════════════════════════╪══════════════╗
              │     ║ LOOP  │  sub layouts                        │              ║
              │     ╟───────┘    │ │                              │              ║
              │     ║            │ │          do_layout()         │              ║
              │     ║            │ │ ─────────────────────────────>              ║
              │     ╚════════════╪═╪══════════════════════════════╪══════════════╝
              │                  └┬┘                              │
              │                   │                               │
              │<─ ─ ─ ─ ─ ─ ─ ─ ─ │                               │
         ┌────┴────┐          ┌───┴────┐                      ┌───┴────┐
         │UIManager│          │UILayout│                      │children│
         └─────────┘          └────────┘                      └────────┘

"""

from abc import abstractmethod, ABC
from operator import attrgetter
from pathlib import Path
from typing import List, NamedTuple, Union, Dict, Optional, Tuple

import PIL

from arcade import Sprite, SpriteList, get_sprites_at_point, Color, Texture, Point
from arcade.gui.elements import UIElement
from arcade.gui.events import UIEvent
from arcade.resources import resolve_resource_path


class _PackedElement(NamedTuple):
    element: Union["UILayout", Sprite]
    data: Dict


padding = Union[int, Tuple[int, int], Tuple[int, int, int, int]]


class UILayout(ABC):
    min_size = (0, 0)
    """Minimal size of this UILayout"""

    def __init__(
        self,
        *,
        size_hint: Optional[Tuple],
        id=None,
        bg: Union[Color, str, Path] = None,
        border_color: Optional[Color] = None,
        border_width: int = 2,
        padding: padding = 0,
        **kwargs,
    ):
        """

        :param id: id of this layout
        :param size_hint: The size_hint is a tuple of two floats used by layouts to manage the sizes of their children. It indicates the size relative to the layout’s size (0.0 - 1.0)
        :param bg: background, may be a color for a solid background color or the path to a image file
        :param border_color: color of the border
        :param border_width: width of the border
        :param padding: distance between border and children
        """
        super().__init__()
        self._id = id

        self._elements: List[_PackedElement] = []
        self._layer = SpriteList()
        self._layer._keep_textures = False  # Workaround to prevent OOM
        self._child_layouts: List[UILayout] = []

        self.size_hint = size_hint

        # anker for own position
        self._top = 0
        self._left = 0

        self._padding = padding

        self._border_color = border_color
        self._border_width = border_width
        self._bg_sprite: Optional[Sprite] = None
        self._bg = bg

        ebw = self.effective_border_width()
        self._width = self.padding_horizontal + ebw * 2
        self._height = self.padding_vertical + ebw * 2

        self.refresh_bg()

    # --------- background
    def _create_bg_sprite(self, bg):

        # calc size containing padding
        h_padding = self.padding_left + self.padding_right
        v_padding = self.padding_top + self.padding_bottom
        size = (self._width + v_padding, self._height + h_padding)

        if isinstance(bg, (Path, str)):
            image_path = resolve_resource_path(bg)
            bg_image = PIL.Image.open(image_path)
            bg_image = bg_image.resize(size)
        else:
            # bg should be a color, so we will create a bg image
            bg_image = PIL.Image.new("RGBA", size, bg)

        return bg_image

    def refresh_bg(self):
        # if bg and border not set, we skip the bg_sprite
        if self._bg is None and self._border_color is None:
            self._bg_sprite = None
            return

        bg = self._bg or (255, 0, 0, 0)

        # recreate bg
        bg_image = self._create_bg_sprite(bg)

        # apply border
        if self._border_color:
            bg_image = PIL.ImageOps.expand(
                bg_image, border=self._border_width, fill=self._border_color
            )

        self._bg_sprite = Sprite()
        self._bg_sprite.texture = Texture(f"BG", bg_image, hit_box_algorithm="None")

        self._bg_sprite.position = self.center_x, self.center_y

    @property
    def id(self):
        return self._id

    def on_ui_event(self, event: UIEvent):
        for element in self:
            if hasattr(element, "on_ui_event"):
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

    def collides_with_point(self, point: Point) -> bool:
        """
        Check if point is within the current layout.

        :param Point point: Point to check.
        :return: True if the point is contained within the sprite's boundary.
        :rtype: bool
        """
        from arcade.geometry import is_point_in_polygon

        x, y = point
        return is_point_in_polygon(
            x,
            y,
            [
                (self.left, self.top),
                (self.right, self.top),
                (self.right, self.bottom),
                (self.left, self.bottom),
            ],
        )

    # --------- add element & size hint
    def pack(self, element: Union[Sprite, UIElement, "UILayout"], **kwargs):
        self._elements.append(_PackedElement(element, kwargs))

        if isinstance(element, Sprite):
            self._layer.append(element)
        if isinstance(element, UILayout):
            self._child_layouts.append(element)
        return element

    def remove(self, element: Union[Sprite, UIElement, "UILayout"]):
        for packed_element in self._elements:
            if packed_element.element == element:
                break
        else:
            return

        self._elements.remove(packed_element)
        if isinstance(element, Sprite):
            self._layer.remove(element)
        if isinstance(element, UILayout):
            self._child_layouts.remove(element)

    # --------- draw self and children
    def draw(self):
        if self._bg_sprite:
            self._bg_sprite.draw()

        self._layer.draw()
        for child in self._child_layouts:
            child.draw()

    # --------- padding
    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, value: padding):
        self._padding = value
        self.do_layout()

    @property
    def padding_top(self):
        if isinstance(self._padding, int):
            return self._padding
        if len(self._padding) in [2, 4]:
            return self._padding[0]
        return 0

    @property
    def padding_right(self):
        if isinstance(self._padding, int):
            return self._padding
        if len(self._padding) in [2, 4]:
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

    # --------- border width
    def effective_border_width(self) -> int:
        """
        If a border color is set, returns the border width, else 0.
        """
        if self._border_color:
            return self._border_width
        else:
            return 0

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

    @property
    def size(self):
        return self.width, self.height

    @size.setter
    def size(self, value: Tuple[int, int]):
        width, height = value
        self.width = width
        self.height = height

    # --------- calculated position values
    @property
    def right(self):
        return (
            self.left
            + self.width
            + self.padding_horizontal
            + self.effective_border_width() * 2
        )

    @right.setter
    def right(self, value):
        x_diff = value - self.right
        self.move(x_diff, 0)

    @property
    def bottom(self):
        return (
            self.top
            - self.height
            - self.padding_vertical
            + self.effective_border_width() * 2
        )

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
        """
        self and all children are moved relative by the given x and y values.
        """
        self._top += y
        self._left += x

        for element, data in self._elements:
            element.top += y
            element.left += x

    # ---------- placement and refresh
    def do_layout(self):
        """
        Starts the layouting algorithm.

        1. self.place_elements() is called to set size and position of children
        2. recursive call of do_layout() to sub layouts
        """
        self.place_elements()

        for element in self:
            if isinstance(element, UILayout):
                element.do_layout()

        self.refresh_bg()

    @abstractmethod
    def place_elements(self):
        raise NotImplementedError()

    # --------- iterate through elements
    def __iter__(self):
        yield from map(attrgetter("element"), self._elements)

    def __len__(self):
        return len(self._elements)
