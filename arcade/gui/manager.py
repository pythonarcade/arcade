from typing import Optional, Dict, cast

from arcade import SpriteList
from pyglet.event import EventDispatcher
from pyglet.window import Window

from arcade.gui import UIElement, UIException, UIEvent, MOUSE_PRESS, MOUSE_RELEASE, MOUSE_SCROLL, KEY_PRESS, \
    KEY_RELEASE, TEXT_INPUT, TEXT_MOTION, TEXT_MOTION_SELECTION
from arcade.gui.core import MOUSE_MOTION


class UIManager(EventDispatcher):
    def __init__(self, window: Window, *args, **kwargs):
        super().__init__()
        self.window: Window = window

        self._focused_element: Optional[UIElement] = None
        self._hovered_element: Optional[UIElement] = None

        self._ui_elements: SpriteList = SpriteList(use_spatial_hash=True)
        self._id_cache: Dict[str, UIElement] = {}

        self.register_event_type('on_ui_event')

        # self.window.push_handlers(self) # Not as explicit as following
        self.window.push_handlers(
            self.on_draw,
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_scroll,
            self.on_mouse_motion,
            self.on_key_press,
            self.on_key_release,
            self.on_text,
            self.on_text_motion,
            self.on_text_motion_select,
        )

    @property
    def focused_element(self):
        return self._focused_element

    @focused_element.setter
    def focused_element(self, new_focus: UIElement):

        if self._focused_element is not None:
            self._focused_element.on_unfocus()
            self._focused_element = None

        if new_focus is not None:
            new_focus.on_focus()

        self._focused_element = new_focus

    @property
    def hovered_element(self):
        return self._hovered_element

    @hovered_element.setter
    def hovered_element(self, new_hover: UIElement):
        if self._hovered_element is not None:
            self._hovered_element.on_unhover()
            self._hovered_element = None

        if new_hover is not None:
            new_hover.on_hover()

        self._hovered_element = new_hover

    def purge_ui_elements(self):
        self._ui_elements = SpriteList()
        self._id_cache = {}

    def add_ui_element(self, ui_element: UIElement):
        if not hasattr(ui_element, 'id'):
            raise UIException('UIElement seems not to be properly setup, please check if you'
                              ' overwrite the constructor and forgot "super().__init__(**kwargs)"')

        self._ui_elements.append(ui_element)
        ui_element.mng = self

        # Add elements with id to lookup
        if ui_element.id is not None:
            if ui_element.id in self._id_cache:
                raise UIException(f'duplicate id "{ui_element.id}"')

            self._id_cache[ui_element.id] = ui_element

    def find_by_id(self, ui_element_id: str) -> Optional[UIElement]:
        return self._id_cache.get(ui_element_id)

    def on_draw(self):
        self._ui_elements.draw()

    def disptach_ui_event(self, event: UIEvent):
        self.dispatch_event('on_ui_event', event)

    def on_ui_event(self, event: UIEvent):
        """
        Processes UIEvents, forward events to registered elements and manages focused element
        """
        for ui_element in self._ui_elements:
            ui_element = cast(UIElement, ui_element)

            if event.type == MOUSE_PRESS:
                if ui_element.collides_with_point((event.get('x'), event.get('y'))):
                    self.focused_element = ui_element

                elif ui_element is self.focused_element:
                    # TODO does this work like expected?
                    self.focused_element = None

            if event.type == MOUSE_MOTION:
                if ui_element.collides_with_point((event.get('x'), event.get('y'))):
                    self.hovered_element = ui_element

                elif ui_element is self.hovered_element:
                    self.hovered_element = None

            ui_element.on_ui_event(event)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.disptach_ui_event(UIEvent(MOUSE_PRESS, x=x, y=y, button=button, modifiers=modifiers))

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.disptach_ui_event(UIEvent(MOUSE_RELEASE, x=x, y=y, button=button, modifiers=modifiers))

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.disptach_ui_event(UIEvent(MOUSE_SCROLL,
                                       x=x,
                                       y=y,
                                       scroll_x=scroll_x,
                                       scroll_y=scroll_y,
                                       ))

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.disptach_ui_event(UIEvent(MOUSE_MOTION,
                                       x=x,
                                       y=y,
                                       dx=dx,
                                       dy=dy,
                                       ))

    def on_key_press(self, symbol: int, modifiers: int):
        self.disptach_ui_event(UIEvent(KEY_PRESS,
                                       symbol=symbol,
                                       modifiers=modifiers
                                       ))

    def on_key_release(self, symbol: int, modifiers: int):
        self.disptach_ui_event(UIEvent(KEY_RELEASE,
                                       symbol=symbol,
                                       modifiers=modifiers
                                       ))

    def on_text(self, text):
        self.disptach_ui_event(UIEvent(TEXT_INPUT,
                                       text=text,
                                       ))

    def on_text_motion(self, motion):
        self.disptach_ui_event(UIEvent(TEXT_MOTION,
                                       motion=motion,
                                       ))

    def on_text_motion_select(self, selection):
        self.disptach_ui_event(UIEvent(TEXT_MOTION_SELECTION,
                                       selection=selection,
                                       ))
