from _warnings import warn
from itertools import chain
from typing import Union, List, Optional

import arcade
from arcade import Sprite
from arcade.gui import UIElement, MOUSE_PRESS, MOUSE_MOTION, UIEvent, MOUSE_RELEASE
from arcade.gui.layouts import UILayout
from arcade.gui.layouts.anchor import UIAnchorLayout
from arcade.gui.layouts.utils import valid
from arcade.gui.manager import UIAbstractManager


class UIStack:
    """
    UIStack handles the complexity of multiple UI trees at the same point in time.
    The goal is to forward UIEvents only to the top UILayout on the stack. (Latest pushed.)

    The actual dispatching is implemented by the :py:class:`UILayoutManager` using :py:meth:`UIStack.peek()`

    If the stack is empty a default UIAnchorLayout is used,
    which should be used especially for HUD elements.

    Switching between UILayouts like windows might be added at a later point in time.
    """

    def __init__(self, default_layout: UILayout):
        self.default_layout = default_layout

        self.stack: List[UILayout] = []

    def push(self, layout: UILayout, **kwargs):
        """
        Push a new UILayout on top of the stack.
        """
        self.stack.append(layout)

    def pop(self, element: Optional[UILayout] = None) -> UILayout:
        """
        Removes the top layout and returns it. Returns default layout if stack is empty.

        It is also possible to remove specific elements within the stack, passing the element.
        """
        if element is not None:
            self.stack.remove(element)
            return element
        if self.stack:
            return self.stack.pop()
        return self.default_layout

    def peek(self) -> UILayout:
        """
        :return: Top UILayout of the stack. Returns default layout if stack is empty.
        """
        if self.stack:
            return self.stack[-1]
        return self.default_layout

    def __iter__(self):
        """
        Return stack in draw order, starting with the default_layout
        :return:
        """
        return chain([self.default_layout], self.stack)


class UILayoutManager(UIAbstractManager):
    """
    The UILayoutManager handles the connection between UILayouts, and UIElements and the mouse, and
    keyboard events. It also triggers the underlying UILayouts to position the UIElements.

    To add a new UILayout or UIElement use :py:meth:`UILayoutManager.pack(element)`

    UILayoutManager uses a :py:class:`UIAnchorLayout` as the root layout, which provides simple ways to position
    all elements on screen.

    Advanced usage - overlapping UI
    -------------------------------

    In case you want to provide a window-like experience, which may overlap with the HUD or other
    window-like objects, the UILayoutManager provides a stack function.

    Use :py:meth:`UILayoutManager.push(element)` to place a UIElement or UILayout on the top.
    All UIEvents will be past to the latest pushed element.

    To remove the top element use `UILayoutManager.pop()` or `UILayoutManager.pop(element)`

    """

    def __init__(self, window=None, attach_callbacks=True):
        super().__init__()
        self.window: arcade.Window = window if window else arcade.get_window()

        self._ui_stack = UIStack(UIAnchorLayout(
            self.window.width,
            self.window.height
        ))

        self.do_layout()

        if attach_callbacks:
            self.register_handlers()

    def on_ui_event(self, event):
        self._handle_ui_event(event)
        self._ui_stack.peek().on_ui_event(event)

    def on_draw(self):
        for layout in self._ui_stack:
            layout.draw()

    def on_update(self, dt):
        # FIXME: This might be to slow, let's see
        self.do_layout()

    def pack(self, element: Union[Sprite, UIElement, 'UILayout'], **kwargs):
        """
        Packs an element into the root_layout.

        :param element: Element to pack
        :param kwargs: Pack parameters
        """
        return self.root_layout.pack(element, **kwargs)

    def push(self, layout: UILayout):
        """
        Adds the element to the internal UIStack
        """
        self._ui_stack.push(layout)

    def pop(self, layout: UILayout):
        """
        Adds the element to the internal UIStack
        """
        self._ui_stack.pop(layout)

    def remove(self, element: Union[Sprite, UIElement, 'UILayout']) -> None:
        """
        Removes the element from the root_layout
        """
        self.root_layout.remove(element)

    def _resize_root_layout(self):
        left, right, bottom, top = self.window.get_viewport()
        self.root_layout.top = top
        self.root_layout.left = left
        self.root_layout.width = right - left
        self.root_layout.height = top - bottom

    @property
    def root_layout(self):
        return self._ui_stack.default_layout

    @root_layout.setter
    def root_layout(self, layout: UILayout):
        self._ui_stack.default_layout = layout
        self.do_layout()

    def do_layout(self):
        self._resize_root_layout()

        for layout in self._ui_stack:
            layout.do_layout()

        if not valid(self.root_layout):
            warn('Refresh produced invalid boundaries')

    def _handle_ui_event(self, event: UIEvent):
        """
        Care about hover and focus of elements
        """

        # if mouse event search for ui_elements at pos to handle hover and focus
        if event.type in (MOUSE_PRESS, MOUSE_MOTION, MOUSE_RELEASE):
            pos = event.get('x'), event.get('y')

            current_layout = self._ui_stack.peek()
            elements_at_pos = current_layout.get_elements_at(pos)

            # handle hover
            if event.type == MOUSE_MOTION:
                if len(elements_at_pos) > 0:
                    new_hovered_element = elements_at_pos[-1]
                    if new_hovered_element != self.hovered_element:
                        self.hovered_element = new_hovered_element
                else:
                    self.hovered_element = None

            # handle focus
            if event.type == MOUSE_PRESS:
                if len(elements_at_pos) > 0:
                    new_focused_element = elements_at_pos[-1]
                    if new_focused_element != self.focused_element:
                        self.focused_element = new_focused_element
                else:
                    self.focused_element = None
